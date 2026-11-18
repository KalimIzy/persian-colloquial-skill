# Persian Colloquial Skill

Convert formal Persian into widely understood Tehran colloquial Persian, and check the register of any Persian text. Built for AI agents, useful for humans too.

![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)
![Python 3.9+](https://img.shields.io/badge/Python-3.9%2B-blue.svg)
![Verbs: 341](https://img.shields.io/badge/Verbs-341-orange.svg)

Formal Persian and spoken Persian are not the same language with different spelling. Verbs contract (`می‌روم` → `میرم`), the copula attaches (`خوب است` → `خوبه`), the object marker shrinks (`را` → `رو`), vowels shift (`خانه` → `خونه`), and whole words change (`اگر` → `اگه`, `برای` → `واسه`). This skill teaches an agent all of it, with rules grounded in real data instead of vibes.

## Quick example

Formal:

> سلام، چطور هستی؟ من دیروز به دانشگاه رفتم و استاد گفت که امتحان به هفته آینده موکول شده است.

Colloquial:

> سلام، چطوری؟ دیروز رفتم دانشگاه، استاد گفت امتحان افتاده هفته دیگه.

## Choosing the register

The skill does not only convert — it decides which register fits. Five levels, from very formal to full colloquial, and a decision engine that combines the incoming message (mirroring), a stored contact profile, and an audience × channel matrix:

```bash
python skills/persian-colloquial/scripts/suggest_register.py --incoming "سلام چطوری؟ خوبی؟"
python skills/persian-colloquial/scripts/suggest_register.py --audience teacher --channel email --topic admin
python skills/persian-colloquial/scripts/suggest_register.py --contact مامان --profile contacts.yaml
python skills/persian-colloquial/scripts/suggest_register.py --prompt "یه پروپوزال واسه مشتری بنویس" --deliverable proposal
```

The deliverable type beats the request tone (a casual request for a proposal still needs a formal proposal); the live message beats the stored profile, the profile beats the matrix, and level 3 (semi-formal) is the safe default when nothing is known. The user's own request (`--prompt`) is never mirrored: asking casually for a formal text must not drag the reply colloquial. See `references/register-decision.md` for the full rules and `references/register-levels.md` for what each level sounds like.

## What is inside

| File | What it holds |
| --- | --- |
| `skills/persian-colloquial/SKILL.md` | The agent skill: conversion rules, register consistency, politeness, checking |
| `skills/persian-colloquial/references/register-levels.md` | The five register levels, with rules and one message at all five |
| `skills/persian-colloquial/references/register-decision.md` | How the register is decided: precedence, matrix, confidence |
| `skills/persian-colloquial/references/orthography.md` | ZWNJ, Persian characters, digits, punctuation, هکسره, tanvin |
| `skills/persian-colloquial/references/ai-tells.md` | Bureaucratic and AI tells in Persian, with fixes |
| `skills/persian-colloquial/scripts/suggest_register.py` | Decision engine: mirror, profile, matrix → level + confidence |
| `skills/persian-colloquial/examples/contacts.example.yaml` | Example contacts profile (copy to contacts.yaml, gitignored) |
| `skills/persian-colloquial/references/verb-tables.md` | Full formal vs colloquial tables for the top 40 verbs, hand-checked |
| `skills/persian-colloquial/references/verb-tables-full.md` | All 341 verbs with stems and colloquial present tense |
| `skills/persian-colloquial/references/word-pairs.md` | 195+ colloquial to formal word pairs, grouped by pattern |
| `skills/persian-colloquial/references/discourse-markers.md` | خب, دیگه, آخه, که, بابا, والا and more, with function and examples |
| `skills/persian-colloquial/references/chat-style.md` | Chat conventions: short sentences, Finglish, spelling variation |
| `skills/persian-colloquial/examples/before-after.md` | 8 worked conversions, plus a mixed-register bad example with fixes |
| `skills/persian-colloquial/scripts/check_register.py` | Stdlib-only register checker: scores any Persian text 0 to 100 |
| `skills/persian-colloquial/data/verbs.csv` | All verb stems (source: shekar) |
| `skills/persian-colloquial/data/informal_words.csv` | Informal word list (source: shekar) |
| `skills/persian-colloquial/data/verb_forms_formal.txt` | 20,241 generated formal verb forms |
| `skills/persian-colloquial/data/verb_forms_informal.txt` | 17,905 generated colloquial verb forms |

## Install

This repo follows the [Agent Skills open standard](https://agentskills.io): one skill at `skills/persian-colloquial/`, with manifests for the Claude Code, Cursor, and Codex plugin systems.

**Any agent (recommended):** the `skills` CLI installs it into the right folder for whichever agent you use.

```bash
npx skills add KalimIzy/persian-colloquial-skill
```

**GitHub CLI:**

```bash
gh skill install KalimIzy/persian-colloquial-skill
```

**Claude Code plugin:**

```
/plugin marketplace add KalimIzy/persian-colloquial-skill
/plugin install persian-colloquial@persian-colloquial
```

**Codex plugin:**

```bash
codex plugin marketplace add KalimIzy/persian-colloquial-skill
```

**Manual:** copy `skills/persian-colloquial/` into your agent's skills folder (e.g. `~/.claude/skills/`).

**Muse:** copy `skills/persian-colloquial/` to `~/workspace/custom-skills/persian_colloquial/`.

**Register checker only:** no install needed, Python 3.9+ and nothing else.

```bash
python skills/persian-colloquial/scripts/check_register.py --text "نمیدونم اونا میتونن این مشکلو حل کنن یا نه."
python skills/persian-colloquial/scripts/check_register.py message.txt
python skills/persian-colloquial/scripts/check_register.py --text "..." --json
```

## The register scale

| Score | Verdict | Typical text |
| --- | --- | --- |
| 0–20 | Formal | Essay, news, official message |
| 21–40 | Mostly formal | Careful email, lecture |
| 41–60 | Semi-formal | Polite work chat; a mid-range score can also mean mixed register, so check the spans |
| 61–80 | Colloquial | Friendly chat, voice message |
| 81–100 | Heavily colloquial | Close friends, slang-heavy chat |

The checker counts colloquial markers (informal verb forms, informal words, discourse markers, possessive endings) against formal markers (full verb forms, `را`, `است`, `زیرا`, `بسیار`) and reports the spans it found, so you can see exactly what pushed the score. Scores from fewer than 4 markers are shrunk toward 50 and labeled a weak signal. Pass `--register` with the target level (1–5) when checking against one: at levels 4–5 the missing-tanvin check is skipped, since colloquial writing does not use tanvin.

## Verb coverage

341 unique infinitives, from 352 stem pairs in the shekar verb data. The top 40 verbs carry full tables: present, past, subjunctive, and imperative, formal and colloquial side by side. The rest carry stems plus the full colloquial present tense. Generation used the shekar Conjugator 1.8.0; the top 40 were verified by hand.

## What this skill does not do

- It targets **Tehran-based colloquial Persian**, the variety heard in national media. Dari, Tajik, and regional Iranian varieties differ and are not covered.
- **Politeness is not formality.** Colloquial `شما` with plural verbs (`شما میخواین؟`) is polite. The skill keeps them separate.
- Colloquial Persian has **no single enforced spelling standard**. `میرم` and `می‌رم` are the same word; the skill accepts both and never calls one wrong. Output uses the attached form (`میرم`), the way people actually type: in real usage it outnumbers the ZWNJ form by roughly 30 to 1 (wordfreq data, November 2026).
- Register is a **continuum**, not a switch. Real speakers mix features; the skill teaches consistency, not purity.
- The checker is **token-based**: it cannot see multi-word verb forms (`رفته است`, `دارم می‌روم`), and its هکسره detection is heuristic — `possible-hekasre` means "check this", not "this is wrong".

## Sources and credits

- [shekar](https://github.com/amirivojdan/shekar) (MIT) — verb stems, informal word list, conjugator, and the rule-based informal classifier this checker builds on.
- [persian-writing](https://github.com/ali2000hos/persian-writing) (MIT) — هکسره rules and the است-test, AI-tell patterns, orthography rules, and the deliverable-type register rule, adapted from its references.
- [Persian-Informal-Text-Detector](https://github.com/MahtaFetrat/Persian-Informal-Text-Detector) — informal word list and verb-pattern regexes.
- [Degarbayan-SC](https://github.com/mut-deep/Degarbayan-SC) — 1.5M colloquial paraphrase pairs from movie subtitles.
- [LSCP](https://iasbs.ac.ir/~ansari/lscp/) — Large-Scale Colloquial Persian, 120M sentences from 27M casual tweets.
- [Settemila Lingue Persian grammar](https://www.settemilalingue.com/en/languages/fa/grammar/colloquial-vs-formal-register) — colloquial vs formal register reference.

## License

MIT. See [LICENSE](LICENSE).
