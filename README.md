# Persian Colloquial Skill

Convert formal Persian into widely understood Tehran colloquial Persian, and check the register of any Persian text. Built for AI agents, useful for humans too.

![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)
![Python 3.9+](https://img.shields.io/badge/Python-3.9%2B-blue.svg)
![Verbs: 341](https://img.shields.io/badge/Verbs-341-orange.svg)

Formal Persian and spoken Persian are not the same language with different spelling. Verbs contract (`می‌روم` → `می‌رم`), the copula attaches (`خوب است` → `خوبه`), the object marker shrinks (`را` → `رو`), vowels shift (`خانه` → `خونه`), and whole words change (`اگر` → `اگه`, `برای` → `واسه`). This skill teaches an agent all of it, with rules grounded in real data instead of vibes.

## Quick example

Formal:

> سلام، چطور هستی؟ من دیروز به دانشگاه رفتم و استاد گفت که امتحان به هفته آینده موکول شده است.

Colloquial:

> سلام، چطوری؟ دیروز رفتم دانشگاه، استاد گفت امتحان افتاده هفته دیگه.

## What is inside

| File | What it holds |
| --- | --- |
| `SKILL.md` | The agent skill: conversion rules, register consistency, politeness, checking |
| `references/verb-tables.md` | Full formal vs colloquial tables for the top 40 verbs, hand-checked |
| `references/verb-tables-full.md` | All 341 verbs with stems and colloquial present tense |
| `references/word-pairs.md` | 195+ colloquial to formal word pairs, grouped by pattern |
| `references/discourse-markers.md` | خب, دیگه, آخه, که, بابا, والا and more, with function and examples |
| `references/chat-style.md` | Chat conventions: short sentences, Finglish, spelling variation |
| `examples/before-after.md` | 8 worked conversions, plus a mixed-register bad example with fixes |
| `scripts/check_register.py` | Stdlib-only register checker: scores any Persian text 0 to 100 |
| `data/verbs.csv` | All verb stems (source: shekar) |
| `data/informal_words.csv` | Informal word list (source: shekar) |
| `data/verb_forms_formal.txt` | 20,241 generated formal verb forms |
| `data/verb_forms_informal.txt` | 17,905 generated colloquial verb forms |

## Install

**Claude Code / any agent that reads skills:** copy `SKILL.md` (and `references/`, `scripts/`, `data/`) into your skills folder.

**Muse:** this repo is also a Muse custom skill. Copy the whole folder to `~/workspace/custom-skills/persian_colloquial/`.

**Register checker only:** no install needed, Python 3.9+ and nothing else.

```bash
python scripts/check_register.py --text "نمی‌دونم اونا می‌تونن این مشکلو حل کنن یا نه."
python scripts/check_register.py message.txt
python scripts/check_register.py --text "..." --json
```

## The register scale

| Score | Verdict | Typical text |
| --- | --- | --- |
| 0–20 | Formal | Essay, news, official message |
| 21–40 | Mostly formal | Careful email, lecture |
| 41–60 | Mixed | Check for accidental register jumps |
| 61–80 | Colloquial | Friendly chat, voice message |
| 81–100 | Heavily colloquial | Close friends, slang-heavy chat |

The checker counts colloquial markers (informal verb forms, informal words, discourse markers, possessive endings) against formal markers (full verb forms, `را`, `است`, `زیرا`, `بسیار`) and reports the spans it found, so you can see exactly what pushed the score.

## Verb coverage

341 unique infinitives, from 352 stem pairs in the shekar verb data. The top 40 verbs carry full tables: present, past, subjunctive, and imperative, formal and colloquial side by side. The rest carry stems plus the full colloquial present tense. Generation used the shekar Conjugator 1.8.0; the top 40 were verified by hand.

## What this skill does not do

- It targets **Tehran-based colloquial Persian**, the variety heard in national media. Dari, Tajik, and regional Iranian varieties differ and are not covered.
- **Politeness is not formality.** Colloquial `شما` with plural verbs (`شما می‌خواین؟`) is polite. The skill keeps them separate.
- Colloquial Persian has **no single enforced spelling standard**. `می‌رم` and `میرم` are the same word; the skill accepts both and never calls one wrong.
- Register is a **continuum**, not a switch. Real speakers mix features; the skill teaches consistency, not purity.

## Sources and credits

- [shekar](https://github.com/amirivojdan/shekar) (MIT) — verb stems, informal word list, conjugator, and the rule-based informal classifier this checker builds on.
- [Persian-Informal-Text-Detector](https://github.com/MahtaFetrat/Persian-Informal-Text-Detector) — informal word list and verb-pattern regexes.
- [Degarbayan-SC](https://github.com/mut-deep/Degarbayan-SC) — 1.5M colloquial paraphrase pairs from movie subtitles.
- [LSCP](https://iasbs.ac.ir/~ansari/lscp/) — Large-Scale Colloquial Persian, 120M sentences from 27M casual tweets.
- [Settemila Lingue Persian grammar](https://www.settemilalingue.com/en/languages/fa/grammar/colloquial-vs-formal-register) — colloquial vs formal register reference.

## License

MIT. See [LICENSE](LICENSE).
