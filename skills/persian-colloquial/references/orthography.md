# Orthography: the mechanical layer

These rules apply at every register level. Register lives in grammar
and word choice; spelling, characters, and punctuation are the same
whether the text is formal or colloquial. A colloquial text with
Arabic letters or Latin punctuation still looks wrong.

Adapted from [persian-writing](https://github.com/ali2000hos/persian-writing)
(MIT); see its `references/orthography.md` for the full treatment.

## ZWNJ (نیم‌فاصله, U+200C)

Join the prefix to the verb, the suffix to the word, and the parts of
a compound:

- می‌روم, نمی‌خواهم, می‌شود (never می روم, می شود)
- کتاب‌ها, بزرگ‌تر, خانه‌ام, به‌عنوان
- فراگرفتن, بازنویسی (compounds join; فرا گرفتن splits them)

In colloquial output (levels 4–5), the می/نمی prefix attaches to the
verb (میرم، میخوام، میشه): that is the default, the way people type.
The ZWNJ form (می‌رم) is the careful variant for edited text. The
checker accepts both and never flags either. A standalone می/نمی
followed by a space is still a missing ZWNJ at any level.

## Persian characters only

- ی (U+06CC), never Arabic ي (U+064A)
- ک (U+06A9), never Arabic ك (U+0643)

Arabic codepoints break search, sorting, and the verb tables, and
readers notice them. The checker flags them.

## Persian digits and punctuation

- Digits inside Persian prose are Persian: ۰۱۲۳۴۵۶۷۸۹, with ٬ as the
  thousands separator and ٪ for percent. Latin digits stay in URLs,
  emails, codes, and version numbers. Never Arabic-Indic ٤٥٦ forms.
- Punctuation is Persian: ، ؛ ؟ and «گیومه» for quotes, … for ellipsis.
  No space before a punctuation mark, one space after it.

## هکسره: ezafe is not ـه

The colloquial clitic ـه means است («این کتابه» = این کتاب است).
The ezafe kasre is a different thing and is never written ـه:

| Wrong | Right | Why |
| --- | --- | --- |
| کتابه من رو ندیدی؟ | کتابِ من رو ندیدی؟ | ezafe, not است |
| خونه‌ی من بزرگه | خونه‌ی من بزرگه | بزرگه = بزرگ است, correct |
| هوا خیلی خوبِ | هوا خیلی خوبه | خوبه = خوب است, correct |

**The است-test:** substitute است for the ـه. If the sentence stays
grammatical («این کتاب است»), ـه is right. If it breaks («کتاب است من»),
the word needs a kasre (usually unwritten: کتاب من) or an explicit
ـِ in careful writing. Iranians treat this error as a mark of
carelessness. The checker flags the pattern «word+ه + possessive
pronoun» as probable هکسره, and «known stem+ه + adjective or noun»
(ماشینه سفید، کتابه خوب) as possible هکسره. The second pattern is
heuristic: words that genuinely end in ه (خانه، دسته، دانشگاه) are
excluded, but a false positive is still possible, so
possible-hekasre means "check this", not "this is wrong".

## Tanvin

Tanvin (اً) is Arabic morphology. It is required on Arabic loans and
wrong on Persian words:

- Required: لطفاً, حتماً, واقعاً, قطعاً, اصلاً, کاملاً, دقیقاً, کلاً,
  قبلاً, بعداً, فعلاً, مثلاً, احتمالاً, معمولاً
- Wrong: گاهاً → گاهی, دوماً → دوم اینکه, سوماً → سوم اینکه,
  ناچاراً → به‌ناچار

The formal forms of the adverbs are کلاً and دقیقاً, not کلا and دقیقا.
The colloquial shortenings کلن and دقیقن drop the tanvin entirely,
which is why they are colloquial.

## No em or en dashes

Never use — or – in Persian prose at any level. Use ، or ؛, or start
a new sentence:

- «رفتم — ولی دیر شد» → «رفتم، ولی دیر شد»

The dash is one of the strongest AI tells in Persian text. The checker
flags it.

## Do not start a line with a Latin word

Chat apps, GitHub, and most editors set a paragraph's direction from
its first letter, so a line starting with a Latin word renders
left-to-right: wrong alignment, the period on the wrong side. Lead
with a Persian word instead:

- «React یک کتابخانه است.» → «کتابخانه‌ی React برای ساخت رابط کاربری است.»
- «Docker را نصب کنید.» → «ابزار Docker را نصب کنید.»

This covers every sentence, bullet, heading, table cell, and caption,
and matters most in captions and posts that name brands or apps.
