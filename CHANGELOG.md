# Changelog

## 1.2.0

- New orthography layer (`references/orthography.md`): ZWNJ, Persian
  characters, digits and punctuation, tanvin rules, the هکسره rule with
  the است-test, the em-dash ban, and the bidi rule. Adapted from
  persian-writing (MIT), with credit in the README.
- New AI-tell reference (`references/ai-tells.md`): bureaucratic tells
  (می‌باشد, می‌گردد) and AI tells (dashes, rule-of-three, نه تنها ...
  بلکه, generic openers and closers) with fixes.
- `suggest_register.py` gains `--deliverable`: the artifact decides
  the register, not the tone of the request. A casual request for a
  proposal now returns level 2, not level 5.
- `check_register.py` now reports mechanical issues (dash, Arabic
  characters, Latin punctuation, missing and fake tanvin, probable
  هکسره, bureaucratic verbs, missing ZWNJ) and gains a `--rhythm`
  flag for flat sentence rhythm.
- New runnable evals (`evals/evals.json`): register tripwire,
  mirror-vs-deliverable, هکسره, tanvin, dash, and Arabic-character
  cases, all run by the package validator.
- Fixes: the level-1 example no longer uses «موکول گردد» (now
  «موکول شود»); the formal adverb forms are کلاً and دقیقاً, not
  کلا and دقیقا; level 5 allows only the fixed pair خب دیگه, not
  marker stacking in general; level 1 gains نامه اداری conventions
  and the rule that formal is not bureaucratic.

## 1.1.0

- The skill now chooses the register, not only converts it: five levels
  (very formal to full colloquial) in `references/register-levels.md`,
  with one message written at all five levels.
- New decision engine `scripts/suggest_register.py`: mirrors the
  incoming message, falls back to a stored contact profile, then to an
  audience × channel matrix adjusted by topic, and reports a level,
  a confidence, and its reasons. Precedence and confidence rules live
  in `references/register-decision.md`.
- Contact profiles (`examples/contacts.example.yaml`, gitignored):
  store a level per contact and update it with `--set` when the user
  corrects the register.

## 1.0.0

- Initial release: the Colloquial Persian skill for AI agents.
- Converts formal Persian to widely understood Tehran-based colloquial Persian: verb contraction, attached copula, object marker رو, vowel shifts, word replacements, discourse markers, and chat conventions.
- 341 unique infinitives with stems and colloquial present tense (top 40 verbs hand-checked with full tables); 195+ word pairs; 20,241 formal and 17,905 colloquial generated verb forms.
- Stdlib-only register checker (`scripts/check_register.py`) scoring any Persian text 0 to 100, with the spans it found.
- Packaged to the Agent Skills open standard: YAML frontmatter, `skills/persian-colloquial/` layout, Claude Code and Cursor plugin manifests, Codex marketplace copy, and a CI validation workflow.
