# Changelog

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
