#!/usr/bin/env python3
"""Check the register of Persian text: formal vs colloquial.

Scores a Persian text on a 0 to 100 colloquial scale, using signals from
three sources:

- Informal verb forms, generated from every verb in shekar verbs.csv
  (see data/verb_forms_informal.txt and data/verb_forms_formal.txt).
- Informal words from shekar informal_words.csv (data/informal_words.csv).
- The informal word list from MahtaFetrat's Persian-Informal-Text-Detector,
  plus discourse markers and common chat words (embedded below).

Stdlib only. No third-party dependencies.

Usage:
    python check_register.py --text "سلام، چطوری؟ دیروز رفتم دانشگاه."
    python check_register.py message.txt
    python check_register.py --text "..." --json
    python check_register.py --text "..." --rhythm
    python check_register.py --text "..." --register 5
    cat message.txt | python check_register.py

Besides the score, the checker reports mechanical issues: em/en dashes,
Arabic ي/ك, Latin punctuation inside Persian text, missing or fake
tanvin, probable هکسره (ezafe written as ـه), bureaucratic verbs,
missing ZWNJ, and fixed AI-tell phrases. See references/orthography.md
for the rules.

Scores from fewer than 4 markers are shrunk toward 50 and labeled a
weak signal: one colloquial word in a long formal text is not a
colloquial text. Pass --register 1-5 when checking against a target
register; at levels 4-5 the missing-tanvin check is skipped, because
colloquial writing does not use tanvin.
"""
import argparse
import json
import re
import statistics
import sys
from pathlib import Path

# Informal words from MahtaFetrat/Persian-Informal-Text-Detector
# (https://github.com/MahtaFetrat/Persian-Informal-Text-Detector).
MAHTA_WORDS = {
    "توش", "آتیش", "چطوره", "خوبه", "آخه", "توی", "همونطور", "اگه", "تیکه",
    "یهو", "واسه", "واسم", "واست", "واسش", "واسمون", "واستون", "واسشون",
    "رمضون", "دیگه", "اینا", "اونا", "بهش", "هیچی", "برام", "برات",
    "برامون", "براشون", "براتون", "براش", "والا", "دوس", "ایش", "هرچی",
    "چی", "آره", "چطوری", "چه‌طوری", "چقد", "یه", "بارون", "ازم", "ازت",
    "ازش", "ازمون", "ازتون", "ازشون", "اصن", "اینو", "اونو", "اینارو",
    "اونارو", "زبون", "بابا", "بابام", "بابات", "باباش", "بابامون",
    "باباتون", "باباشون", "ماما", "مامان", "مامانم", "مامانت", "مامانمون",
    "مامانتون", "مامانشون", "آسون", "دیگه‌ای", "بهت", "بهمون", "بهتون",
    "بهشون", "خونه", "جون", "ایشالا", "ماشالا", "ایشون", "اونه", "اینجوری",
    "بازم", "باهام", "باهات", "باهاش", "باهامون", "باهاتون", "باهاشون",
    "تموم", "چجوری", "چیه", "کدوم", "آروم", "ایرونی", "بادمجون", "بچگونه",
    "بیابون", "تهرون", "دندون", "خودتون", "خودشون", "خودمون", "خودمونی",
    "خیابون", "داره", "داروخونه", "داغون", "دخترونه", "رودخونه", "زمونه",
    "زنونه", "قلیون", "مردونه", "مهمون", "میونه", "میون", "نشونه", "نشون",
    "نیستن", "هستن", "همزبون", "همشون", "پسرونه", "کوچیک", "تمومه", "انقد",
}

# Extra colloquial words and discourse markers not in the source lists.
# Note: نه is NOT here. It is standard in formal writing too
# («نه تنها ... بلکه ...»), so counting it would inflate formal texts.
EXTRA_COLLOQUIAL = {
    "اون", "بهم", "چیکار", "کجایی", "خوبی", "ببین", "مگه", "ینی", "راستی",
    "هی", "وای", "خب", "داداش", "آبجی", "رفیق", "مرسی", "خدافظ", "بای",
}

# Formal marker words. Formal verb forms come from the data files.
# Includes admin/legal markers (احتراماً، اینجانب): they count as
# formal markers in the checker, and suggest_register.py uses them
# as the gate for level 1.
FORMAL_WORDS = {
    "را", "است", "می‌باشد", "می‌باشم", "می‌باشی", "می‌باشیم", "می‌باشید",
    "می‌باشند", "گردد", "می‌گردد", "زیرا", "بله", "آن‌ها", "ایشان",
    "خواهد", "خواهم", "خواهی", "خواهیم", "خواهید", "خواهند", "بسیار",
    "لذا", "بنابراین", "همچنین",
    "احتراماً", "اینجانب", "بدین‌وسیله", "خواهشمند", "مستدعی",
    "استحضار", "عطف", "پیرو",
}

# Words that need tanvin in formal writing (missing-tanvin check).
MISSING_TANVIN = {
    "لطفا": "لطفاً", "حتما": "حتماً", "واقعا": "واقعاً",
    "قطعا": "قطعاً", "اصلا": "اصلاً", "کاملا": "کاملاً",
    "دقیقا": "دقیقاً", "کلا": "کلاً", "قبلا": "قبلاً",
    "بعدا": "بعداً", "فعلا": "فعلاً", "مثلا": "مثلاً",
    "احتمالا": "احتمالاً", "معمولا": "معمولاً",
}

# Fake tanvin on Persian words (checked against the surface form,
# because normalize() strips the tanvin diacritic).
FAKE_TANVIN = {
    "گاهاً": "گاهی", "دوماً": "دوم اینکه",
    "سوماً": "سوم اینکه", "ناچاراً": "به‌ناچار",
}

# Bureaucratic verbs (normalized forms, ZWNJ removed): use است/می‌شود/شد.
BUREAUCRATIC_VERBS = {
    "میباشد": "است", "میباشند": "هستند",
    "میگردد": "می‌شود", "میگردند": "می‌شوند",
    "گردد": "شود", "گردند": "شوند", "گردید": "شد",
}

# Common words that genuinely end in ه: «خونه من» is not هکسره.
# Includes prepositions (درباره), common nouns, and -گاه/-خانه words.
HEKASRE_STOPLIST = {
    "خونه", "خانه", "مدرسه", "نامه", "جاده", "پنجره", "بچه",
    "گربه", "سکه", "دونه", "چرخه", "لحظه", "هفته", "دقیقه",
    "ثانیه", "قفسه", "کاسه", "بشقابه",
    "درباره", "برنامه", "مسئله", "وظیفه", "نتیجه", "ادامه",
    "تجربه", "پروژه", "مقاله", "ناحیه", "رابطه", "ضابطه",
    "قاعده", "فایده", "حافظه", "خاطره", "سابقه", "جامعه",
    "دسته", "پسته", "میوه", "بنده", "زنده", "مرده", "خسته",
    "شیشه", "ستاره", "سیاره", "دایره", "زاویه", "نقطه",
    "صحنه", "جلوه", "حومه", "خانواده", "مدیره",
    "دانشگاه", "باشگاه", "فرودگاه", "ایستگاه", "نمایشگاه",
    "کارگاه", "آموزشگاه", "آزمایشگاه", "کتابخانه", "داروخانه",
}

# Common nouns that never end in ه. Used by the possible-hekasre check:
# «ماشینه سفید» is suspect because ماشین is a known stem, while
# «خانه سفید» is fine because خانه is in the stoplist above.
COMMON_STEMS = {
    "کتاب", "ماشین", "مورد", "روز", "ماه", "سال", "کار", "وقت",
    "راه", "مردم", "دولت", "کشور", "شهر", "پول", "دست", "سر",
    "چشم", "گوش", "پا", "دل", "جان", "نام", "نور", "برق", "آب",
    "خاک", "سنگ", "چوب", "طلا", "شعر", "داستان", "فیلم", "آهنگ",
    "عکس", "تلفن", "اداره", "شرکت", "بازار", "خیابان", "پل",
    "کوه", "دریا", "جنگل", "باغ", "پرنده", "سگ", "درس",
    "امتحان", "کلاس", "استاد", "دانشجو", "معلم", "دکتر",
    "مهندس", "مادر", "پدر", "برادر", "خواهر", "پسر", "دختر",
    "دوست", "دشمن", "همسایه", "مشتری", "مدیر", "کارمند",
    "سرباز", "پلیس", "دزد",
}

# Words that may follow a ه-word without it being ezafe: pronouns are
# handled by the high-confidence pattern, verbs and conjunctions mean
# the ه is a copula or part of another construction.
HEKASRE_PRONOUNS = {
    "من", "تو", "او", "ما", "شما", "آنها", "ایشان", "این", "آن",
}
HEKASRE_FOLLOW_EXCLUDE = {
    "است", "بود", "هست", "شد", "رفت", "آمد", "کرد", "میشود",
    "میکند", "میرود", "میآید", "دارد", "داشت", "خواهد", "باید",
    "شاید", "توانست", "میتواند",
    "که", "تا", "و", "یا", "اما", "ولی", "چون", "اگر", "نه",
    "بله", "هم", "پس", "بعد", "قبل", "هنوز", "دیگر", "دیگه",
    "فقط", "حتی", "مگر", "کاش", "را", "از", "در", "با", "به",
    "برای",
}

# Fixed AI-tell phrases from references/ai-tells.md (matched after
# normalization, so ZWNJ variants are caught). Only high-precision
# phrases: a match is almost always a tell.
AI_TELL_PHRASES = {
    "لازم به ذکر است": "delete it; just say the thing",
    "در راستای": "use برای",
    "از اهمیت ویژه‌ای برخوردار است": "say مهم است، چون…",
    "نقش بسزایی": "say what it actually does",
    "در نهایت می‌توان گفت": "end on a fact or a next step",
    "در دنیای امروز": "start with the actual subject",
    "امیدوارم مفید بوده باشد": "end on the content, not a bow",
    "نه تنها": "split into two short sentences",
    "کارشناسان معتقدند": "name the source or drop it",
}

# Common words that collide with verb stems (نه is also the present stem
# of نهادن). Never count these as verb matches.
AMBIGUOUS_VERB_FORMS = {
    "به", "نه", "که", "چه", "تو", "ما", "او", "من", "این", "آن", "یا",
    "و", "را", "از", "در", "با", "تا", "پس", "هم", "وی", "ای",
}

# Words ending in مون or تون that are formal or neutral, not possessives.
# The suffix rule also requires a stem of 3+ letters, which already
# excludes زیتون، خاتون، میمون and most others; the list covers the
# longer ones (پروتون، افلاطون، کارتون) as well.
POSSESSIVE_STOPLIST = {
    "آزمون", "پیرامون", "مضمون", "هرمون", "ستون",
    "پروتون", "فوتون", "کتون", "نپتون", "پلوتون", "پانتون",
    "خاتون", "افلاطون", "مامون", "هامون", "زیتون", "توتون",
    "کارتون", "میمون", "نوترون", "الکترون",
}

# Suffixes stripped from a token before a second lookup, so attached
# pronouns do not hide a verb form (می‌خوامت -> می‌خوام).
STRIP_SUFFIXES = ("مون", "تون", "شون", "م", "ت", "ش")

ZWNJ = "\u200c"
ARABIC_DIACRITICS = "ًٌٍَُِّْ"


def normalize(text):
    """Normalize Persian text for matching: unify Arabic letters, drop
    diacritics and the ZWNJ, collapse whitespace."""
    text = text.replace("ي", "ی").replace("ك", "ک")
    for ch in ARABIC_DIACRITICS:
        text = text.replace(ch, "")
    text = text.replace(ZWNJ, "")
    text = text.strip("؟،؛.!?\"'«»()[]{}:;")
    return " ".join(text.split())


def tokenize(text):
    """Split text into word tokens, keeping their spans for reporting."""
    return [(m.group(0), m.start(), m.end())
            for m in re.finditer(r"[\w\u0600-\u06FF\u200c]+", text)]


def load_word_set(path):
    words = set()
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                words.add(normalize(line))
    return words


def load_informal_words_csv(path):
    words = set()
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            informal = line.split(",", 1)[0].strip()
            if informal:
                words.add(normalize(informal))
    return words


class RegisterChecker:
    def __init__(self, data_dir=None):
        if data_dir is None:
            data_dir = Path(__file__).resolve().parent.parent / "data"
        self.data_dir = Path(data_dir)
        self.data_loaded = self._load_data()

    def _load_data(self):
        formal_path = self.data_dir / "verb_forms_formal.txt"
        informal_path = self.data_dir / "verb_forms_informal.txt"
        words_path = self.data_dir / "informal_words.csv"
        if not (formal_path.exists() and informal_path.exists()
                and words_path.exists()):
            print("warning: data files not found in %s; using embedded "
                  "word lists only" % self.data_dir, file=sys.stderr)
            self.informal_verbs = set()
            self.formal_verbs = set()
            self.informal_words = set()
        else:
            formal_forms = load_word_set(formal_path)
            informal_forms = load_word_set(informal_path)
            # Only forms that differ between registers are signals.
            self.formal_verbs = {w for w in formal_forms
                                 if " " not in w} - informal_forms
            self.informal_verbs = {w for w in informal_forms
                                   if " " not in w} - formal_forms
            self.informal_words = load_informal_words_csv(words_path)
            self.formal_verbs -= AMBIGUOUS_VERB_FORMS
            self.informal_verbs -= AMBIGUOUS_VERB_FORMS
        self.informal_words |= {normalize(w) for w in MAHTA_WORDS}
        self.informal_words |= {normalize(w) for w in EXTRA_COLLOQUIAL}
        self.formal_words = {normalize(w) for w in FORMAL_WORDS}
        return True

    def check(self, text, register=None):
        tokens = tokenize(text)
        colloquial = []  # (surface form, kind)
        formal = []
        for surface, _start, _end in tokens:
            token = normalize(surface)
            if not token:
                continue
            hit = self._classify(token)
            base = token
            if hit is None:
                # Try again without an attached pronoun suffix.
                for suffix in STRIP_SUFFIXES:
                    if token.endswith(suffix) and len(token) - len(suffix) >= 2:
                        stripped = token[:-len(suffix)]
                        if len(suffix) == 1:
                            # Single-letter strips (م/ت/ش) only count
                            # when the remainder is a verb form
                            # (می‌خوامت -> می‌خوام). Stripping to a
                            # bare word collides: چیت -> چی and
                            # نهش -> نه are not colloquial words.
                            if stripped in self.informal_verbs:
                                hit = "colloquial"
                            elif stripped in self.formal_verbs:
                                hit = "formal"
                        else:
                            hit = self._classify(stripped)
                        if hit is not None:
                            base = stripped
                            break
            if hit == "colloquial":
                colloquial.append((surface, self._kind(base, "colloquial")))
            elif hit == "formal":
                formal.append((surface, self._kind(base, "formal")))
        total_markers = len(colloquial) + len(formal)
        if total_markers == 0:
            score = 50
            verdict = "neutral (no register markers found)"
        else:
            raw = 100 * len(colloquial) / total_markers
            # A lone marker in a long text is weak evidence: shrink
            # scores from fewer than 4 markers toward 50, in
            # proportion. One یه in a formal report scores ~62 with
            # a weak-signal label, not 100.
            shrink = min(1.0, total_markers / 4)
            score = round(50 + (raw - 50) * shrink)
            if score <= 20:
                verdict = "formal"
            elif score <= 40:
                verdict = "mostly formal"
            elif score <= 60:
                verdict = "semi-formal"
            elif score <= 80:
                verdict = "colloquial"
            else:
                verdict = "heavily colloquial"
            if total_markers < 4:
                verdict += f" (weak signal: {total_markers} markers)"
        return {
            "words": len(tokens),
            "colloquial_count": len(colloquial),
            "formal_count": len(formal),
            "score": score,
            "verdict": verdict,
            "register": register,
            "colloquial_spans": colloquial,
            "formal_spans": formal,
            "issues": self._issues(text, tokens, register),
        }

    def _issues(self, text, tokens, register=None):
        """Mechanical issues: orthography problems the score ignores.

        Each issue is {"kind", "text", "suggestion"}. See
        references/orthography.md and references/ai-tells.md.
        `register` is the target level (1-5) when known: at levels 4-5
        the missing-tanvin check is skipped, and the ها suggestion
        points at the colloquial short form.
        """
        issues = []

        def add(kind, found, suggestion):
            issues.append({"kind": kind, "text": found,
                           "suggestion": suggestion})

        for m in re.finditer(r"[—–]", text):
            add("dash", m.group(0),
                "use ، or start a new sentence; dashes are an AI tell")
        for m in re.finditer(r"(?<![\w\u200c])(می|نمی) ", text):
            add("zwnj-mi", m.group(0).strip(),
                "join the prefix with ZWNJ: می‌روم, not می روم")
        for m in re.finditer(r"(\S+)\s+ها(?![\w\u200c])", text):
            after = text[m.end():m.end() + 1]
            if after == "" or after in "؟!?.،\n":
                continue  # emphasis particle: چی گفتی ها؟ / نکن ها!
            if register is not None and register >= 4:
                suggestion = ("shorten to the colloquial form: کتابا "
                              "(or کتاب‌ها in formal text)")
            else:
                suggestion = ("join with ZWNJ: کتاب‌ها (or drop ها if "
                              "it is the emphasis particle)")
            add("zwnj-ha", m.group(0), suggestion)
        for m in re.finditer(
                r"(\S{3,}ه)\s+(من|تو|او|ما|شما|آنها|ایشان|این|آن)\b", text):
            word = m.group(1)
            if word not in HEKASRE_STOPLIST and not word.endswith("انه"):
                add("hekasre", m.group(0),
                    "probable هکسره: ezafe is a kasre, not ـه — test by "
                    "substituting است")
        for i in range(len(tokens) - 1):
            surface1, _s1, e1 = tokens[i]
            surface2, s2, _e2 = tokens[i + 1]
            w1 = normalize(surface1)
            w2 = normalize(surface2)
            if not w1.endswith("ه") or len(w1) < 3:
                continue
            if w1 in HEKASRE_STOPLIST or w1.endswith("انه"):
                continue
            if w1[:-1] not in COMMON_STEMS:
                continue
            if w2 in HEKASRE_PRONOUNS:
                continue  # the high-confidence pattern covers these
            if w2 in HEKASRE_FOLLOW_EXCLUDE:
                continue
            if w2 in self.informal_verbs or w2 in self.formal_verbs:
                continue
            if text[e1:s2].strip():
                continue  # not adjacent words
            add("possible-hekasre", f"{surface1} {surface2}",
                "check whether the ه is ezafe (use a kasre, as in "
                "ماشین سفید) or part of the word")
        # Latin punctuation only counts when a Persian word precedes
        # it: in «React, Vue, و Angular» the comma belongs to the
        # Latin list, not to the Persian text.
        for m in re.finditer(r"[\u0600-\u06FF]\s*[,;?]", text):
            add("latin-punct", m.group(0).strip(),
                "use Persian punctuation: ، ؛ ؟")
        flat = normalize(text)
        for phrase, fix in AI_TELL_PHRASES.items():
            if normalize(phrase) in flat:
                add("ai-tell", phrase, fix)
        hamanchenan = sum(1 for surface, _s, _e in tokens
                          if normalize(surface) == "همچنین")
        if hamanchenan >= 2:
            add("ai-tell", "همچنین (x%d)" % hamanchenan,
                "vary the connector or cut it")
        for surface, _start, _end in tokens:
            token = normalize(surface)
            if "ي" in surface or "ك" in surface:
                add("arabic-char", surface,
                    "use Persian ی and ک, not Arabic ي and ك")
            if token in MISSING_TANVIN:
                # Colloquial writing does not use tanvin: کلا is fine
                # at levels 4-5, so only flag it for formal targets.
                if register is None or register < 4:
                    add("missing-tanvin", surface,
                        f"use {MISSING_TANVIN[token]}")
            if surface in FAKE_TANVIN:
                add("fake-tanvin", surface,
                    f"use {FAKE_TANVIN[surface]}")
            if token in BUREAUCRATIC_VERBS:
                add("bureaucratic-verb", surface,
                    f"use {BUREAUCRATIC_VERBS[token]}")
        seen = set()
        unique = []
        for issue in issues:
            key = (issue["kind"], issue["text"])
            if key not in seen:
                seen.add(key)
                unique.append(issue)
        return unique

    def _classify(self, token):
        if token in self.informal_words or token in self.informal_verbs:
            return "colloquial"
        if token in self.formal_words or token in self.formal_verbs:
            return "formal"
        for suffix in ("مون", "تون", "شون"):
            if token.endswith(suffix):
                # The stem before the suffix must be a real word of
                # 3+ letters: زیتون (stem زی) and خاتون (stem خا) are
                # not possessives. This misses short-stem possessives
                # like دلمون, a deliberate trade: false negatives cost
                # one marker, false positives corrupt the score.
                stem = token[:-len(suffix)]
                if len(stem) >= 3 and token not in POSSESSIVE_STOPLIST:
                    return "colloquial"
                return None
        return None

    def _kind(self, token, register):
        if register == "colloquial":
            if token in self.informal_words:
                return "informal word"
            if token in self.informal_verbs:
                return "informal verb"
            return "colloquial suffix"
        if token in self.formal_words:
            return "formal word"
        if token in self.formal_verbs:
            return "formal verb"
        return "formal marker"


def report(result, text):
    lines = []
    lines.append("Register check")
    lines.append("Words: %d" % result["words"])
    lines.append("Colloquial markers: %d" % result["colloquial_count"])
    lines.append("Formal markers: %d" % result["formal_count"])
    lines.append("Colloquial score: %d / 100" % result["score"])
    lines.append("Verdict: %s" % result["verdict"])
    if result.get("register") is not None:
        lines.append("Target register: level %d" % result["register"])
    if result["colloquial_spans"]:
        lines.append("")
        lines.append("Colloquial spans:")
        for surface, kind in result["colloquial_spans"]:
            lines.append("  - %s (%s)" % (surface, kind))
    if result["formal_spans"]:
        lines.append("")
        lines.append("Formal spans:")
        for surface, kind in result["formal_spans"]:
            lines.append("  - %s (%s)" % (surface, kind))
    if result["issues"]:
        lines.append("")
        lines.append("Issues:")
        for issue in result["issues"]:
            lines.append("  - %s: %s (%s)" % (
                issue["kind"], issue["text"], issue["suggestion"]))
    return "\n".join(lines)


def rhythm_report(text):
    """Flag flat rhythm: uniform sentence length and repeated openings.

    A secondary signal; lexical tells matter far more. Returns lines.
    """
    # A terminator only ends a sentence when followed by whitespace or
    # the end of the text: decimal points (۳.۵) and domains
    # (github.com) are not sentence ends.
    sentences = [s.strip() for s in
                 re.split(r"[.؟!…]+(?=\s|$)|[\n]+", text) if s.strip()]
    lengths = [len(s.split()) for s in sentences]
    lines = ["", "Rhythm:"]
    if len(sentences) < 4:
        lines.append("  too few sentences to judge rhythm")
        return lines
    mean = statistics.fmean(lengths)
    cv = statistics.pstdev(lengths) / mean if mean else 0
    lines.append("  sentences: %d, mean length: %.1f words, CV: %.2f"
                 % (len(sentences), mean, cv))
    if cv < 0.35:
        lines.append("  - flat rhythm: sentence lengths are too uniform "
                     "(CV < 0.35); vary them")
    if min(lengths) >= 8:
        lines.append("  - no short sentence: add one under 8 words")
    openings = {}
    for s in sentences:
        first = s.split()[0] if s.split() else ""
        openings[first] = openings.get(first, 0) + 1
    repeated = {w: n for w, n in openings.items() if n >= 3}
    if repeated:
        lines.append("  - repeated openings: %s"
                     % ", ".join("%s (x%d)" % (w, n)
                                 for w, n in repeated.items()))
    if len(lines) == 2:
        lines.append("  ok")
    return lines


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Score Persian text on a formal to colloquial scale.")
    parser.add_argument("path", nargs="?",
                        help="path to a text file to check")
    parser.add_argument("--text", help="text to check directly")
    parser.add_argument("--json", action="store_true",
                        help="print the result as JSON")
    parser.add_argument("--rhythm", action="store_true",
                        help="also report on sentence rhythm")
    parser.add_argument("--register", type=int, choices=[1, 2, 3, 4, 5],
                        help="target register level; at 4-5 the "
                        "missing-tanvin check is skipped")
    args = parser.parse_args(argv)

    if args.text is not None:
        text = args.text
    elif args.path:
        text = Path(args.path).read_text(encoding="utf-8")
    else:
        text = sys.stdin.read()

    checker = RegisterChecker()
    result = checker.check(text, register=args.register)
    if args.json:
        out = dict(result)
        out["colloquial_spans"] = [
            {"text": s, "kind": k} for s, k in result["colloquial_spans"]]
        out["formal_spans"] = [
            {"text": s, "kind": k} for s, k in result["formal_spans"]]
        if args.rhythm:
            out["rhythm"] = rhythm_report(text)
        print(json.dumps(out, ensure_ascii=False, indent=2))
    else:
        output = report(result, text)
        if args.rhythm:
            output += "\n" + "\n".join(rhythm_report(text))
        print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
