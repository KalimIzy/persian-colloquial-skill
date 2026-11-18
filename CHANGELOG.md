# Changelog

## 1.0.0

- Initial release: the Colloquial Persian skill for AI agents.
- Converts formal Persian to widely understood Tehran-based colloquial Persian: verb contraction, attached copula, object marker رو, vowel shifts, word replacements, discourse markers, and chat conventions.
- 341 unique infinitives with stems and colloquial present tense (top 40 verbs hand-checked with full tables); 195+ word pairs; 20,241 formal and 17,905 colloquial generated verb forms.
- Stdlib-only register checker (`scripts/check_register.py`) scoring any Persian text 0 to 100, with the spans it found; it also reports mechanical issues (dash, Arabic characters, Latin punctuation, tanvin, probable هکسره, bureaucratic verbs, missing ZWNJ) and has a `--rhythm` flag.
- Smart register choice: five levels (very formal to full colloquial) and a decision engine (`scripts/suggest_register.py`) that mirrors the incoming message, falls back to a stored contact profile, then to an audience × channel matrix adjusted by topic, and reports a level, a confidence, and its reasons; `--deliverable` lets the artifact decide, not the request tone.
- Orthography layer (`references/orthography.md`) and AI-tell reference (`references/ai-tells.md`), adapted from persian-writing (MIT).
- Runnable evals (`evals/evals.json`): register tripwire, mirror-vs-deliverable, هکسره, tanvin, dash, and Arabic-character cases, all run by the package validator.
- Fixed after an external review (Gemini, 18 November 2026):
  possessive-suffix false positives (پروتون، زیتون), single-letter
  strip collisions (چیت، نهش), هکسره false positives (درباره من)
  and misses (ماشینه سفید), the neutral word نه counted as
  colloquial, Latin punctuation in bilingual text, the ها emphasis
  particle, length-blind scoring, decimal/domain sentence splits,
  prompt/incoming confusion in the suggester, the 2-marker mirror
  threshold, the dead sub-60 confidence rule, the hand-rolled YAML
  parser, missing deliverable types, and the ین grammar error
  (second person plural, not third). The checker now reports
  AI-tell phrases, accepts a --register target, and labels scores
  from fewer than 4 markers as weak signals; the suggester takes
  --incoming and --prompt separately and needs admin markers for
  level 1. Evals grew from 8 to 30 cases, including negative tests.
- Default colloquial spelling is attached (میرم، میخوام، میشه),
  matching real usage: wordfreq data (November 2026) shows میرم
  outnumbers می‌رم by about 30 to 1. The ZWNJ form remains the
  careful variant for edited text; the checker accepts both.
- Bidirectional-text guidance (`references/bidi.md`) with wrong/right
  examples for mixed Persian and English: line-leading Latin words,
  trailing punctuation, URLs, numbers, parentheses, lists, code, and
  emoji. The checker flags the mechanical breakages
  (latin-line-start, trailing-latin-punct, url-punct, latin-paren),
  and evals grew to 38 cases.
- Packaged to the Agent Skills open standard: YAML frontmatter, `skills/persian-colloquial/` layout, Claude Code and Cursor plugin manifests, Codex marketplace copy, and a CI validation workflow.
