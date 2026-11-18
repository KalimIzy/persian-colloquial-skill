#!/usr/bin/env python3
"""Suggest the right register for a Persian reply.

Decision engine for the persian-colloquial skill. It combines five
signals in a fixed precedence order:

1. Explicit --level (the user overrides everything).
2. Deliverable type (--deliverable): when the user asks for an
   artifact, the artifact decides, not the tone of the request. A
   casual «یه پروپوزال بنویس» still needs a formal proposal.
3. Mirroring: the register of the incoming message (--incoming),
   scored with check_register.py. A live message beats a stored
   default. Mirroring applies to replies, not artifacts, and never
   to the user's own request (--prompt): the user may ask casually
   for a formal text, and that must not drag the reply colloquial.
4. Contact profile: the stored level for --contact (--profile file).
5. Audience x channel matrix, adjusted by topic.

Falls back to level 3 (semi-formal, the safest) when nothing is known.

Levels: 1 very formal, 2 formal, 3 semi-formal, 4 mild colloquial,
5 full colloquial. See references/register-levels.md for what each
level sounds like, and references/register-decision.md for the rules.

Stdlib only. No third-party dependencies.

Usage:
    python suggest_register.py --incoming "سلام چطوری؟ خوبی؟"
    python suggest_register.py --audience teacher --channel email --topic admin
    python suggest_register.py --contact مامان --profile contacts.yaml --incoming "..."
    python suggest_register.py --prompt "یه پروپوزال واسه مشتری بنویس" --deliverable proposal
    python suggest_register.py --audience friend --channel private-chat --json
    python suggest_register.py --set "مامان:5" --profile contacts.yaml
"""
import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
try:
    from check_register import RegisterChecker, normalize, tokenize
except ImportError:  # pragma: no cover - mirroring disabled without it
    RegisterChecker = None
    normalize = None
    tokenize = None

LEVELS = {
    1: ("very-formal", "خیلی رسمی"),
    2: ("formal", "رسمی"),
    3: ("semi-formal", "نیمه‌رسمی"),
    4: ("mild-colloquial", "محاوره‌ای ملایم"),
    5: ("full-colloquial", "محاوره‌ای کامل"),
}
LEVEL_BY_LABEL = {label: n for n, (label, _fa) in LEVELS.items()}

# Baseline level by audience (before channel and topic adjustments).
AUDIENCE_BASELINE = {
    "close-friend": 5,
    "friend": 4,
    "family": 4,  # family spans elders and peers; polite colloquial
    "family-elder": 4,   # polite colloquial: شما with colloquial verbs
    "colleague": 3,
    "boss": 2,
    "teacher": 2,
    "client": 3,
    "stranger": 3,
    "public": 3,
}

# Channel adjustments, applied to the audience baseline.
CHANNEL_MODIFIER = {
    "email": -1,
    "document": -1,
    "letter": -1,
    "work-chat": 0,
    "private-chat": 0,
    "group-chat": 0,
    "sms": 0,
    "call": 0,
    "voice-message": 1,
    "comment": 0,
    "caption": 1,
}

# Topic adjustments, applied after the channel.
TOPIC_MODIFIER = {
    "admin": -1,
    "academic": -1,
    "legal": -1,
    "complaint": -1,
    "condolence": -1,
    "work": 0,
    "planning": 0,
    "favor": 0,
    "casual": 1,
    "joke": 1,
    "catch-up": 1,
}

# Deliverable types: the artifact decides the register, not the tone
# of the request. Outranks mirroring; see register-decision.md.
DELIVERABLE_LEVEL = {
    "admin-letter": 1,
    "thesis": 1,
    "contract": 1,
    "proposal": 2,
    "letter": 2,
    "email": 2,
    "report": 2,
    "essay": 2,
    "cv": 2,
    "cover-letter": 2,
    "announcement": 3,
    "newsletter": 3,
    "caption": 4,
    "post": 4,
    "ad": 4,
    "tweet": 4,
    "story": 5,
    "dialogue": 5,
    "script": 5,
}

# Markers that actually indicate level 1 (admin/legal), in normalized
# form. Ordinary formal words (را، است) only indicate level 2: a
# formal message is not an admin letter.
LEVEL1_MARKERS = {
    "احتراما", "اینجانب", "بدینوسیله", "خواهشمند", "مستدعی",
    "استحضار", "عطف", "پیرو",
}


def clamp(level):
    return max(1, min(5, level))


def score_to_level(score, has_level1_marker=False):
    """Map a colloquial score (0-100) to a level. Level 1 needs a
    level-1 marker; a merely formal score maps to level 2."""
    if score <= 20:
        return 1 if has_level1_marker else 2
    if score <= 40:
        return 2
    if score <= 60:
        return 3
    if score <= 80:
        return 4
    return 5


def has_level1_marker(text):
    """True when the text contains an admin/legal marker word."""
    if tokenize is None:
        return False
    return any(normalize(surface) in LEVEL1_MARKERS
               for surface, _s, _e in tokenize(text))


def parse_level(value):
    """Parse a level given as 1-5 or as a label like 'formal'."""
    value = str(value).strip().lower()
    if value.isdigit() and 1 <= int(value) <= 5:
        return int(value)
    if value in LEVEL_BY_LABEL:
        return LEVEL_BY_LABEL[value]
    return None


def _strip_comment(line):
    """Strip a YAML-style comment: # at the start of a line or after
    whitespace. A # inside a name (C#Dev) is kept."""
    if line.lstrip().startswith("#"):
        return ""
    return re.split(r"\s+#", line, maxsplit=1)[0]


def _unquote(name):
    name = name.strip()
    if len(name) >= 2 and name[0] == name[-1] and name[0] in "\"'":
        return name[1:-1]
    return name


def parse_profile(path):
    """Parse a contacts profile: one `name: level` per line, `#` comments.

    Levels are 1-5 or labels (very-formal, formal, semi-formal,
    mild-colloquial, full-colloquial). A `default:` line sets the level
    for contacts not listed. Names may be quoted ("مامان": 5), may
    contain : or #, and may sit under a `contacts:` parent key.
    """
    profile = {}
    default = None
    for raw_line in Path(path).read_text(encoding="utf-8").splitlines():
        line = _strip_comment(raw_line).strip()
        if not line or ":" not in line:
            continue
        # Split on the LAST colon: a name may contain one.
        name, _, raw = line.rpartition(":")
        level = parse_level(raw)
        if level is None:
            continue
        name = _unquote(name)
        if name.lower() == "default":
            default = level
        else:
            profile[name] = level
    return profile, default


def set_profile_level(path, name, level):
    """Set one contact's level in the profile file, preserving the rest."""
    path = Path(path)
    lines = path.read_text(encoding="utf-8").splitlines() if path.exists() else []
    updated = False
    out = []
    for line in lines:
        body = _strip_comment(line)
        if ":" in body and _unquote(body.rpartition(":")[0]) == name:
            comment = line[len(body):]  # keep the original comment
            out.append(f"{name}: {level}{comment}")
            updated = True
        else:
            out.append(line)
    if not updated:
        out.append(f"{name}: {level}")
    path.write_text("\n".join(out) + "\n", encoding="utf-8")
    return updated


def suggest(incoming=None, audience=None, channel=None, topic=None,
            contact=None, profile_path=None, explicit_level=None,
            deliverable=None, prompt=None, text=None):
    """Decide a register level. Returns a dict with level, confidence,
    source and reasons. `text` is the deprecated alias for `incoming`."""
    if incoming is None:
        incoming = text
    reasons = []
    profile_level = None
    profile = {}
    if profile_path:
        try:
            profile, default = parse_profile(profile_path)
            if contact and contact in profile:
                profile_level = profile[contact]
                reasons.append(f"profile: {contact} is stored at level "
                               f"{profile_level} ({LEVELS[profile_level][0]})")
            elif default is not None:
                profile_level = default
                reasons.append(f"profile default is level {default}")
        except OSError as e:
            reasons.append(f"profile file not readable: {e}")

    if explicit_level is not None:
        return {"level": explicit_level, "confidence": 100,
                "source": "explicit",
                "reasons": ["explicit --level overrides everything"] + reasons,
                "mirror": None}

    mirror = None
    mirror_level = None
    if incoming and RegisterChecker is not None:
        result = RegisterChecker().check(incoming)
        markers = result["colloquial_count"] + result["formal_count"]
        mirror = {"score": result["score"], "verdict": result["verdict"],
                  "markers": markers}
        if markers >= 3:
            mirror_level = score_to_level(result["score"],
                                          has_level1_marker(incoming))
            reasons.append(
                f"incoming message scored {result['score']} "
                f"({result['verdict']}, {markers} markers) -> level "
                f"{mirror_level}")
        else:
            reasons.append("incoming message has too few register markers "
                           f"({markers}); ignoring it")
    if prompt:
        reasons.append("the request text (--prompt) is never mirrored; "
                       "only the incoming message (--incoming) is")

    if deliverable in DELIVERABLE_LEVEL:
        level = DELIVERABLE_LEVEL[deliverable]
        reasons.append(
            f"deliverable {deliverable} needs level {level} "
            f"({LEVELS[level][0]}); the artifact decides, not the "
            f"request tone")
        if mirror_level is not None and abs(mirror_level - level) >= 2:
            reasons.append(
                f"request tone suggests level {mirror_level}, but the "
                f"deliverable outranks mirroring")
        return {"level": level, "confidence": 85,
                "source": "deliverable", "reasons": reasons,
                "mirror": mirror}

    if mirror_level is not None:
        # Confidence grows with evidence: 60 at 3 markers, +5 per
        # extra marker, capped at 90. A thin mirror that disagrees
        # with the profile can land below 60, which is when the
        # low-confidence rule fires.
        confidence = 60 + min(30, (mirror["markers"] - 3) * 5)
        if (profile_level is not None
                and abs(mirror_level - profile_level) >= 2):
            confidence -= 10
            reasons.append(
                f"live message (level {mirror_level}) disagrees with the "
                f"stored profile (level {profile_level}); following the "
                f"live message")
        return {"level": mirror_level, "confidence": confidence,
                "source": "mirror", "reasons": reasons, "mirror": mirror}

    if profile_level is not None:
        return {"level": profile_level, "confidence": 80,
                "source": "profile", "reasons": reasons, "mirror": mirror}

    if audience in AUDIENCE_BASELINE:
        level = AUDIENCE_BASELINE[audience]
        reasons.append(f"audience {audience} starts at level {level}")
        known = 1
        if channel in CHANNEL_MODIFIER:
            delta = CHANNEL_MODIFIER[channel]
            level = clamp(level + delta)
            reasons.append(f"channel {channel} adjusts by {delta:+d} -> "
                           f"level {level}")
            known += 1
        if topic in TOPIC_MODIFIER:
            delta = TOPIC_MODIFIER[topic]
            level = clamp(level + delta)
            reasons.append(f"topic {topic} adjusts by {delta:+d} -> "
                           f"level {level}")
            known += 1
        confidence = 70 if known >= 2 else 60
        return {"level": level, "confidence": confidence,
                "source": "matrix", "reasons": reasons, "mirror": mirror}

    reasons.append("no audience, contact, or usable message; defaulting to "
                   "level 3 (semi-formal), the safest choice")
    return {"level": 3, "confidence": 50, "source": "default",
            "reasons": reasons, "mirror": mirror}


def report(result):
    level = result["level"]
    label, label_fa = LEVELS[level]
    lines = [
        f"Suggested register: level {level} ({label}, {label_fa})",
        f"Confidence: {result['confidence']} / 100",
        f"Decided by: {result['source']}",
        "",
        "Reasons:",
    ]
    lines += [f"  - {r}" for r in result["reasons"]]
    if result["confidence"] < 60:
        lines += ["",
                  "Low confidence: confirm the register with the user "
                  "when it matters."]
    return "\n".join(lines)


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Suggest a register level (1-5) for a Persian reply.")
    parser.add_argument("--incoming", "--text", dest="incoming",
                        help="incoming message to mirror "
                        "(--text is a deprecated alias)")
    parser.add_argument("--prompt",
                        help="the user's request; never mirrored")
    parser.add_argument("--audience", choices=sorted(AUDIENCE_BASELINE),
                        help="who the reply goes to")
    parser.add_argument("--channel", choices=sorted(CHANNEL_MODIFIER),
                        help="where the reply goes")
    parser.add_argument("--topic", choices=sorted(TOPIC_MODIFIER),
                        help="what the reply is about")
    parser.add_argument("--deliverable", choices=sorted(DELIVERABLE_LEVEL),
                        help="artifact being written (outranks mirroring)")
    parser.add_argument("--contact", help="contact name to look up")
    parser.add_argument("--profile", help="contacts profile file")
    parser.add_argument("--level", type=int, choices=[1, 2, 3, 4, 5],
                        help="explicit level (overrides everything)")
    parser.add_argument("--set", metavar="NAME:LEVEL",
                        help="store a contact's level in the profile file")
    parser.add_argument("--json", action="store_true",
                        help="print the result as JSON")
    args = parser.parse_args(argv)

    if args.set:
        if ":" not in args.set:
            parser.error("--set needs NAME:LEVEL, e.g. --set مامان:5")
        name, _, raw = args.set.rpartition(":")
        level = parse_level(raw)
        if level is None:
            parser.error(f"bad level in --set: {raw!r} (use 1-5 or a label)")
        if not args.profile:
            parser.error("--set needs --profile")
        updated = set_profile_level(args.profile, name.strip(), level)
        print(f"{'Updated' if updated else 'Added'} {name.strip()}: "
              f"level {level} ({LEVELS[level][0]}) in {args.profile}")
        return 0

    result = suggest(incoming=args.incoming, audience=args.audience,
                     channel=args.channel, topic=args.topic,
                     contact=args.contact, profile_path=args.profile,
                     explicit_level=args.level,
                     deliverable=args.deliverable, prompt=args.prompt)
    if args.json:
        out = dict(result)
        out["label"], out["label_fa"] = LEVELS[result["level"]]
        print(json.dumps(out, ensure_ascii=False, indent=2))
    else:
        print(report(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
