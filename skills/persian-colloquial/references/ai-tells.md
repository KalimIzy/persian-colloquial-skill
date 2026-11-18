# AI tells in Persian

Patterns that make Persian text read machine-written. They survive
register conversion: a colloquial text with these tells still looks
like AI, only a chatty one. Check the output against this list before
delivering, at every register level.

Adapted from [persian-writing](https://github.com/ali2000hos/persian-writing)
(MIT), which catalogues 18 tells (T1–T18); this is the subset that
matters for converted and generated Persian.

## Bureaucratic tells

Stiff, official-sounding words that no one uses in speech and that
even formal writing should avoid:

| Tell | Use instead |
| --- | --- |
| می‌باشد | است |
| می‌گردد / گردید | می‌شود / شد |
| لازم به ذکر است | (delete it; just say the thing) |
| در راستای | برای |
| از اهمیت ویژه‌ای برخوردار است | مهم است، چون… |
| نقش بسزایی ایفا می‌کند | (say what it actually does) |

## AI tells

| Tell | Example | Fix |
| --- | --- | --- |
| Em/en dash | رفتم — ولی دیر شد | رفتم، ولی دیر شد |
| Rule-of-three triad | سریع، آسان و مطمئن | pick the one claim that matters |
| نه تنها ... بلکه | نه تنها سریع است، بلکه ارزان است | two short sentences |
| Tacked-on analysis | ...که نشان‌دهنده‌ی اهمیت آن است | cut the clause, end on the fact |
| Vague authority | کارشناسان معتقدند | name the source or drop it |
| Generic opener | در دنیای امروز | start with the actual subject |
| Generic closer | در نهایت می‌توان گفت | end on a fact or a next step |
| همچنین pileup | همچنین ... همچنین ... | vary the connector or cut it |
| Chatbot sign-off | امیدوارم مفید بوده باشد | end on the content, not a bow |
| Fake ranges | ۷۰ تا ۸۰ درصد | a real number or no number |

## What NOT to flag

- Genuine Persian idioms and proverbs are not tells; overusing them is.
- Repetition for emphasis («خیلی خیلی») is colloquial, not a flaw.
- A long sentence is fine when it carries one clear thought; the flaw
  is uniform length, every sentence 15–20 words. Vary the rhythm:
  a short sentence after two long ones reads human.
- Persian has no detector-proof style. The goal is prose that is
  genuinely better, not prose tuned to fool a detector.
