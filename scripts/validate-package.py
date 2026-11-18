#!/usr/bin/env python3
"""Validate the persian-colloquial-skill package (stdlib only).

Checks the Agent Skills frontmatter, the plugin manifests, the required
files, the Codex copy drift, and the register checker on two known texts.
Run from the repo root, or anywhere: paths resolve from this file.
"""

import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILL_DIR = ROOT / "skills" / "persian-colloquial"
CODEX_COPY = ROOT / "plugins" / "persian-colloquial" / "skills" / "persian-colloquial"
FAILURES = []


def check(label, ok, detail=""):
    print(("ok  " if ok else "FAIL") + f" {label}" + (f" — {detail}" if detail and not ok else ""))
    if not ok:
        FAILURES.append(label)


def parse_frontmatter(text):
    match = re.match(r"^---\n(.*?)\n---\n", text, re.DOTALL)
    if not match:
        return None
    fields = {}
    for line in match.group(1).splitlines():
        if re.match(r"^[a-z-]+:", line):
            key, _, value = line.partition(":")
            fields[key.strip()] = value.strip().strip('"')
    return fields


def main():
    skill_md = SKILL_DIR / "SKILL.md"
    check("SKILL.md exists", skill_md.is_file())
    text = skill_md.read_text(encoding="utf-8") if skill_md.is_file() else ""
    fm = parse_frontmatter(text)
    check("frontmatter present", fm is not None)
    if fm:
        check("name matches directory", fm.get("name") == SKILL_DIR.name,
              f"name={fm.get('name')!r} dir={SKILL_DIR.name!r}")
        check("name is kebab-case",
              bool(re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", fm.get("name", ""))))
        desc = fm.get("description", "")
        check("description present (1-1024 chars)", 1 <= len(desc) <= 1024,
              f"len={len(desc)}")
        check("license is MIT", fm.get("license") == "MIT")
    body = text.split("---", 2)[-1] if fm else text
    check("body under 500 lines", body.count("\n") < 500,
          f"lines={body.count(chr(10))}")

    # Every version string in the repo must match the skill version.
    version_match = re.search(
        r'metadata:\s*\n\s+version:\s*"([^"]+)"', text)
    skill_version = version_match.group(1) if version_match else None
    check("skill version present", skill_version is not None)
    if skill_version:
        for rel in (".claude-plugin/marketplace.json",
                    ".claude-plugin/plugin.json",
                    ".cursor-plugin/plugin.json", "package.json",
                    ".agents/plugins/marketplace.json",
                    "plugins/persian-colloquial/.codex-plugin/plugin.json"):
            content = (ROOT / rel).read_text(encoding="utf-8")
            versions = re.findall(r'"version"\s*:\s*"([^"]+)"', content)
            check(f"version matches in {rel}",
                  versions and all(v == skill_version for v in versions),
                  f"found {versions}, want {skill_version}")

    for rel in ("references/verb-tables.md", "references/verb-tables-full.md",
                "references/word-pairs.md", "references/discourse-markers.md",
                "references/chat-style.md", "references/register-levels.md",
                "references/register-decision.md",
                "references/orthography.md", "references/ai-tells.md",
                "examples/before-after.md",
                "examples/contacts.example.yaml",
                "scripts/check_register.py", "scripts/suggest_register.py",
                "data/verbs.csv",
                "data/informal_words.csv", "data/verb_forms_formal.txt",
                "data/verb_forms_informal.txt"):
        check(f"skill file {rel}", (SKILL_DIR / rel).is_file())

    for rel in (".claude-plugin/marketplace.json", ".claude-plugin/plugin.json",
                ".cursor-plugin/plugin.json", "package.json",
                ".agents/plugins/marketplace.json",
                "plugins/persian-colloquial/.codex-plugin/plugin.json"):
        path = ROOT / rel
        try:
            json.loads(path.read_text(encoding="utf-8"))
            check(f"valid JSON {rel}", True)
        except (OSError, json.JSONDecodeError) as e:
            check(f"valid JSON {rel}", False, str(e))
    check("root LICENSE exists", (ROOT / "LICENSE").is_file())

    # Codex copy must be identical to the canonical skill.
    if CODEX_COPY.is_dir():
        src_files = sorted(p.relative_to(SKILL_DIR) for p in SKILL_DIR.rglob("*") if p.is_file())
        dst_files = sorted(p.relative_to(CODEX_COPY) for p in CODEX_COPY.rglob("*") if p.is_file())
        same = src_files == dst_files and all(
            (SKILL_DIR / f).read_bytes() == (CODEX_COPY / f).read_bytes()
            for f in src_files
        )
        check("codex copy in sync", same,
              "run scripts/sync-codex-plugins.sh" if not same else "")
    else:
        check("codex copy in sync", False, "missing plugins/persian-colloquial/skills/")

    # Register checker smoke test on two known texts.
    checker = SKILL_DIR / "scripts" / "check_register.py"
    cases = [
        ("من فردا به دانشگاه می‌روم و اگر استاد بیاید، می‌خواهم درباره پروژه با او صحبت کنم. استاد گزارش را خواهد خواند.", 0, 20),
        ("فردا می‌رم دانشگاه، اگه استاد بیاد می‌خوام درباره پروژه باهاش حرف بزنم.", 81, 100),
    ]
    for sample, lo, hi in cases:
        proc = subprocess.run(
            [sys.executable, str(checker), "--text", sample, "--json"],
            capture_output=True, text=True)
        try:
            score = json.loads(proc.stdout)["score"]
            check(f"checker score {score} in [{lo},{hi}]", lo <= score <= hi,
                  f"got {score}")
        except (json.JSONDecodeError, KeyError):
            check(f"checker runs on sample", False, proc.stderr.strip()[:200])

    # Register suggester smoke tests.
    suggester = SKILL_DIR / "scripts" / "suggest_register.py"
    example_profile = str(SKILL_DIR / "examples" / "contacts.example.yaml")
    suggest_cases = [
        (["--incoming", "سلام چطوری؟ خوبی؟ کجایی؟"], 5),
        (["--incoming", "من فردا به دانشگاه می‌روم و اگر استاد بیاید، می‌خواهم درباره پروژه با او صحبت کنم. استاد گزارش را خواهد خواند."], 2),
        (["--audience", "teacher", "--channel", "email", "--topic", "admin"], 1),
        (["--contact", "مامان", "--profile", example_profile], 5),
        (["--prompt", "یه پروپوزال واسه مشتری بنویس",
          "--deliverable", "proposal"], 2),
        ([], 3),
    ]
    for argv, want in suggest_cases:
        proc = subprocess.run(
            [sys.executable, str(suggester), *argv, "--json"],
            capture_output=True, text=True)
        try:
            got = json.loads(proc.stdout)["level"]
            check(f"suggest_register {argv or ['(default)']} -> {want}",
                  got == want, f"got {got}")
        except (json.JSONDecodeError, KeyError):
            check(f"suggest_register {argv}", False,
                  proc.stderr.strip()[:200])

    # Evals: runnable cases in evals/evals.json.
    evals_path = ROOT / "evals" / "evals.json"
    check("evals/evals.json exists", evals_path.is_file())
    if evals_path.is_file():
        for case in json.loads(evals_path.read_text(encoding="utf-8")):
            if case["kind"] == "suggest":
                proc = subprocess.run(
                    [sys.executable, str(suggester), *case["args"], "--json"],
                    capture_output=True, text=True)
                try:
                    got = json.loads(proc.stdout)["level"]
                    check(f"eval {case['id']} -> {case['expect_level']}",
                          got == case["expect_level"], f"got {got}")
                except (json.JSONDecodeError, KeyError):
                    check(f"eval {case['id']}", False,
                          proc.stderr.strip()[:200])
            elif case["kind"] in ("check", "check-absent",
                                  "check-score", "check-span-absent"):
                proc = subprocess.run(
                    [sys.executable, str(checker), "--text", case["text"],
                     *case.get("args", []), "--json"],
                    capture_output=True, text=True)
                try:
                    out = json.loads(proc.stdout)
                except json.JSONDecodeError:
                    check(f"eval {case['id']}", False,
                          proc.stderr.strip()[:200])
                    continue
                if case["kind"] == "check":
                    kinds = [i["kind"] for i in out["issues"]]
                    check(f"eval {case['id']} flags {case['expect_issue']}",
                          case["expect_issue"] in kinds, f"got {kinds}")
                elif case["kind"] == "check-absent":
                    kinds = [i["kind"] for i in out["issues"]]
                    check(f"eval {case['id']} omits {case['expect_issue']}",
                          case["expect_issue"] not in kinds, f"got {kinds}")
                elif case["kind"] == "check-score":
                    score = out["score"]
                    check(f"eval {case['id']} score in "
                          f"[{case['expect_min']},{case['expect_max']}]",
                          case["expect_min"] <= score <= case["expect_max"],
                          f"got {score}")
                elif case["kind"] == "check-span-absent":
                    spans = [s["text"] for s in out["colloquial_spans"]]
                    check(f"eval {case['id']} omits span "
                          f"{case['expect_word']}",
                          case["expect_word"] not in spans, f"got {spans}")

    # Profile round-trip: --set writes, --contact reads back.
    with tempfile.TemporaryDirectory() as tmp:
        profile = Path(tmp) / "contacts.yaml"
        proc = subprocess.run(
            [sys.executable, str(suggester), "--set", "مامان:5",
             "--profile", str(profile)],
            capture_output=True, text=True)
        check("--set writes a profile", proc.returncode == 0
              and profile.exists(), proc.stderr.strip()[:200])
        proc = subprocess.run(
            [sys.executable, str(suggester), "--contact", "مامان",
             "--profile", str(profile), "--json"],
            capture_output=True, text=True)
        try:
            got = json.loads(proc.stdout)["level"]
            check("profile round-trip reads back level 5", got == 5,
                  f"got {got}")
        except (json.JSONDecodeError, KeyError):
            check("profile round-trip", False, proc.stderr.strip()[:200])

    # Rhythm flag: flat sentences are reported.
    proc = subprocess.run(
        [sys.executable, str(checker), "--text",
         "این یک جمله نسبتاً طولانی است که درباره موضوع صحبت می‌کند. "
         "این یک جمله نسبتاً طولانی است که درباره موضوع صحبت می‌کند. "
         "این یک جمله نسبتاً طولانی است که درباره موضوع صحبت می‌کند. "
         "این یک جمله نسبتاً طولانی است که درباره موضوع صحبت می‌کند.",
         "--rhythm", "--json"],
        capture_output=True, text=True)
    try:
        rhythm = json.loads(proc.stdout)["rhythm"]
        check("--rhythm flags flat rhythm",
              any("flat rhythm" in line for line in rhythm),
              f"got {rhythm}")
    except (json.JSONDecodeError, KeyError):
        check("--rhythm", False, proc.stderr.strip()[:200])

    print(f"\n{len(FAILURES)} failure(s)" if FAILURES else "\nAll checks passed.")
    return 1 if FAILURES else 0


if __name__ == "__main__":
    raise SystemExit(main())
