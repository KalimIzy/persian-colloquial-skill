# How the register is decided

`suggest_register.py` picks one of the five levels in
[register-levels.md](register-levels.md). It combines five signals in a
fixed order, so the decision is a rule, not a guess.

## Precedence

1. **Explicit `--level`** — the user overrides everything.
2. **Deliverable type (`--deliverable`)** — when the user asks for an
   artifact, the artifact decides, not the tone of the request. A
   casual «یه پروپوزال واسه مشتری بنویس» still needs a formal
   proposal. Mirroring applies to replies, not artifacts.
3. **Mirroring** — the register of the incoming message (`--incoming`),
   scored by `check_register.py`. A live message beats a stored
   default: if someone who usually writes casually sends a formal
   message, answer formally this time. The user's own request
   (`--prompt`) is never mirrored: the user may ask casually for a
   formal text, and that must not drag the reply colloquial.
4. **Contact profile** — the stored level for that contact
   (`contacts.yaml`, see `examples/contacts.example.yaml`). Used when
   there is no incoming message, e.g. when starting a conversation.
5. **Audience × channel matrix**, adjusted by topic — the generic prior
   when nothing specific is known.
6. **Default level 3** (semi-formal) when nothing at all is known. It
   is the safest choice: polite, and never wrong by much.

Mirroring only counts when the incoming message has at least three
register markers. A message with fewer markers (e.g. «باشه») carries
no signal and the decision falls through to the profile or the matrix.
Two formal words like را and است are not enough to call a message
very formal.

## Deliverable types

| Deliverable | Level | Why |
| --- | --- | --- |
| admin-letter, thesis, contract | 1 | Official, academic, and legal writing |
| proposal, letter, email, report, essay, cv, cover-letter | 2 | Formal documents |
| announcement, newsletter | 3 | Public writing that stays polite and plain |
| caption, post, ad, tweet | 4 | Social writing is colloquial and warm |
| story, dialogue, script | 5 | Stories and spoken lines are spoken-style |

A deliverable outranks mirroring even when they disagree by two levels
or more; the script reports the disagreement.

## Score to level (mirroring)

| Colloquial score | Level |
| --- | --- |
| 0–20 | 2 (formal), or 1 when the message carries a level-1 marker (احتراماً، اینجانب، بدین‌وسیله، خواهشمند، مستدعی) |
| 21–40 | 2 (formal) |
| 41–60 | 3 (semi-formal) |
| 61–80 | 4 (mild colloquial) |
| 81–100 | 5 (full colloquial) |

A merely formal score is level 2. Level 1 needs admin or legal
wording, not just the absence of colloquial words: را and است in a
short message mean formal, not a legal letter.

## Audience baseline

| Audience | Baseline |
| --- | --- |
| close-friend | 5 |
| friend, family, family-elder | 4 |
| colleague, client, stranger, public | 3 |
| boss, teacher | 2 |

Family sits at 4, not 5: in Persian culture family spans elders and
peers, and polite colloquial (شما with colloquial verbs) is the safe
default. Close friends stay at 5.

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
- Deliverable: 85.
- Mirroring: 60–90, starting at 60 for 3 markers and rising 5 per
  extra marker, capped at 90. Drops by 10 when the live message
  disagrees with the stored profile by two levels or more (the script
  still follows the live message and says so). A thin mirror that
  disagrees with the profile lands below 60, which is when the
  low-confidence rule fires.
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
`--incoming "سلام چطوری؟ خوبی؟ کجایی؟"` scores 88 (3 markers), so the
mirror says level 5 with confidence 60. Reply in full colloquial.

**2. No incoming message; email to a teacher about paperwork.**
Audience teacher starts at 2, email adjusts −1, topic admin adjusts −1,
clamped to level 1 with confidence 70. Reply very formally.

**3. Mom usually gets level 5, but her message is formal.**
`--contact مامان --profile contacts.yaml --incoming "سلام پسرم، می‌خواستم بگویم که فردا به دانشگاه می‌روم و گزارش را می‌خوانم."`
The profile says 5, the mirror says 2 (score 12, 3 markers). The mirror
wins (live signal), confidence drops from 60 to 50, and the script
reports the disagreement and flags low confidence. Reply formally this
time, and do not change the stored profile — one formal message does
not rewrite the relationship.

**4. Nothing known.**
No text, no audience, no contact. Level 3, confidence 50, with a note
to confirm when it matters.

**5. Casual request for a proposal.**
`--prompt "یه پروپوزال واسه مشتری بنویس" --deliverable proposal`
The request tone is colloquial (level 5), but the deliverable is a
proposal, so the answer is level 2 with confidence 85. The script
reports that the deliverable outranked the tone. Note that `--prompt`
is never mirrored: without the deliverable, this request would fall
through to the default, not to level 5.

**6. Colloquial message plus an admin letter.**
`--incoming "سلام چطوری؟ خوبی؟ کجایی؟" --deliverable admin-letter`
The mirror says 5, the deliverable says 1. The deliverable wins with
confidence 85, and the disagreement is reported.
