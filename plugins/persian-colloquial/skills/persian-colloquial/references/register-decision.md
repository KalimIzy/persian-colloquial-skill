# How the register is decided

`suggest_register.py` picks one of the five levels in
[register-levels.md](register-levels.md). It combines four signals in a
fixed order, so the decision is a rule, not a guess.

## Precedence

1. **Explicit `--level`** — the user overrides everything.
2. **Mirroring** — the register of the incoming message, scored by
   `check_register.py`. A live message beats a stored default: if
   someone who usually writes casually sends a formal message, answer
   formally this time.
3. **Contact profile** — the stored level for that contact
   (`contacts.yaml`, see `examples/contacts.example.yaml`). Used when
   there is no incoming message, e.g. when starting a conversation.
4. **Audience × channel matrix**, adjusted by topic — the generic prior
   when nothing specific is known.
5. **Default level 3** (semi-formal) when nothing at all is known. It
   is the safest choice: polite, and never wrong by much.

Mirroring only counts when the incoming message has at least two
register markers. A message with no markers (e.g. «باشه») carries no
signal and the decision falls through to the profile or the matrix.

## Score to level (mirroring)

| Colloquial score | Level |
| --- | --- |
| 0–20 | 1 (very formal) |
| 21–40 | 2 (formal) |
| 41–60 | 3 (semi-formal) |
| 61–80 | 4 (mild colloquial) |
| 81–100 | 5 (full colloquial) |

## Audience baseline

| Audience | Baseline |
| --- | --- |
| close-friend, family | 5 |
| friend, family-elder | 4 |
| colleague, client, stranger, public | 3 |
| boss, teacher | 2 |

## Channel adjustment

| Channel | Adjustment |
| --- | --- |
| email, document, letter | −1 |
| work-chat, private-chat, group-chat, sms, call, comment | 0 |
| voice-message, caption | +1 |

## Topic adjustment

| Topic | Adjustment |
| --- | --- |
| admin, academic, legal, complaint, condolence | −1 |
| work, planning, favor | 0 |
| casual, joke, catch-up | +1 |

Levels are clamped to 1–5 after all adjustments.

## Confidence

- Explicit level: 100.
- Mirroring: 75–90, higher with more markers. Drops by 10 when the
  live message disagrees with the stored profile by two levels or more
  (the script still follows the live message and says so).
- Profile: 80.
- Matrix: 60–70, higher when audience and channel are both known.
- Default: 50.

Below 60 the script says confidence is low. In that case confirm the
register with the user when it matters, and otherwise write at level 3.

## Feedback

When the user corrects the register («با مامان محاوره‌ای‌تر حرف بزن»),
store the correction so it is not repeated:

```bash
python scripts/suggest_register.py --set "مامان:5" --profile contacts.yaml
```

The profile file is the user's own data: it lives outside the repo
(copy `examples/contacts.example.yaml` to `contacts.yaml`) and is
gitignored, so a correction is never published.

## Worked examples

**1. Friend sends a colloquial message.**
`--text "سلام چطوری؟ خوبی؟ کجایی؟"` scores 100, so the mirror says
level 5 with confidence 75. Reply in full colloquial.

**2. No incoming message; email to a teacher about paperwork.**
Audience teacher starts at 2, email adjusts −1, topic admin adjusts −1,
clamped to level 1 with confidence 70. Reply very formally.

**3. Mom usually gets level 5, but her message is formal.**
`--contact مامان --profile contacts.yaml --text "سلام پسرم، می‌خواستم بگویم که فردا به دانشگاه می‌روم و با استاد صحبت خواهم کرد."`
The profile says 5, the mirror says 1 (score 0, 2 markers). The mirror
wins (live signal), confidence drops from 75 to 65, and the script
reports the disagreement. Reply formally this time, and do not change
the stored profile — one formal message does not rewrite the
relationship.

**4. Nothing known.**
No text, no audience, no contact. Level 3, confidence 50, with a note
to confirm when it matters.
