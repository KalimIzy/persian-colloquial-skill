# Changelog

## 1.0.0

- Initial release: the Colloquial Persian skill for AI agents.
- Converts formal Persian to widely understood Tehran-based colloquial Persian: verb contraction, attached copula, object marker رو, vowel shifts, word replacements, discourse markers, and chat conventions.
- 341 unique infinitives with stems and colloquial present tense (top 40 verbs hand-checked with full tables); 195+ word pairs; 20,241 formal and 17,905 colloquial generated verb forms.
- Stdlib-only register checker (`scripts/check_register.py`) scoring any Persian text 0 to 100, with the spans it found; it also reports mechanical issues (dash, Arabic characters, Latin punctuation, tanvin, probable هکسره, bureaucratic verbs, missing ZWNJ) and has a `--rhythm` flag.
- Smart register choice: five levels (very formal to full colloquial) and a decision engine (`scripts/suggest_register.py`) that mirrors the incoming message, falls back to a stored contact profile, then to an audience × channel matrix adjusted by topic, and reports a level, a confidence, and its reasons; `--deliverable` lets the artifact decide, not the request tone.
- Orthography layer (`references/orthography.md`) and AI-tell reference (`references/ai-tells.md`), adapted from persian-writing (MIT).
- Runnable evals (`evals/evals.json`): register tripwire, mirror-vs-deliverable, هکسره, tanvin, dash, and Arabic-character cases, all run by the package validator.
- Packaged to the Agent Skills open standard: YAML frontmatter, `skills/persian-colloquial/` layout, Claude Code and Cursor plugin manifests, Codex marketplace copy, and a CI validation workflow.
