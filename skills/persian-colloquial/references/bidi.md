# Bidirectional Text: Persian + English Without the Jumble

Persian runs right-to-left, English runs left-to-right, and one
sentence can hold both. The Unicode bidirectional algorithm decides
the display order, and it gets it wrong in predictable ways. This
reference lists the breakages and the fixes. The checker flags the
mechanical ones; see its `latin-line-start`, `trailing-latin-punct`,
`url-punct`, and `latin-paren` issues.

## How it breaks

A paragraph's direction comes from its first strong character: a
Persian letter makes it right-to-left, a Latin letter makes it
left-to-right. Punctuation, spaces, and digits are neutral: they take
their direction from whatever surrounds them. A Latin word inside a
Persian sentence is a left-to-right island. Breakage happens at the
edges of those islands: at the start of a line, at the end of a
sentence, and around punctuation.

## The control characters

| Character | Code | What it does |
| --- | --- | --- |
| RLM | U+200F | Right-to-left mark: an invisible Persian-direction character |
| LRM | U+200E | Left-to-right mark: the mirror image |
| RLI … PDI | U+2067 … U+2069 | Right-to-left isolate: seals a run so its direction cannot leak out |
| LRI … PDI | U+2066 … U+2069 | Left-to-right isolate |

Rule of thumb: prefer restructuring the sentence over invisible
characters. RLM is the one you will actually use, and only where
restructuring is impossible (a URL at the end of a sentence, a
version number). Invisible characters confuse the next editor and
break search, so never sprinkle them by default.

## 1. Lead with a Persian word

Chat apps, GitHub, and most editors set a paragraph's direction from
its first letter, so a line starting with a Latin word renders
left-to-right: wrong alignment, the period on the wrong side. This
covers every sentence, bullet, heading, table cell, and caption.

- Wrong: «React یک کتابخانه است.»
- Right: «کتابخانه‌ی React برای ساخت رابط کاربری است.»
- Wrong: «Docker را نصب کنید.»
- Right: «ابزار Docker را نصب کنید.»

## 2. Do not end a sentence with a Latin word, a URL, or Latin digits

A Latin run at the end of a Persian sentence pulls the trailing
punctuation to the wrong side: the period appears to the left of the
word instead of the right.

- Wrong: «نسخه جدید React.»
- Right: «نسخه جدید React منتشر شد.»
- Wrong: «ساعت 5.»
- Right: «ساعت ۵ است.» (Persian digits take the paragraph direction)
- Wrong: «لینک اینه: https://example.com.»
- Right: «لینک اینه:» then the URL on its own line, with no period.

When restructuring is impossible, put an RLM (U+200F) right after the
Latin run, before the punctuation, or use Persian punctuation (۔ ؟).

## 3. URLs, emails, @mentions, and #hashtags

A URL is a long left-to-right run. Inside a Persian sentence it
usually survives, but punctuation right after it breaks, and a URL at
the start of a line flips the paragraph. Put URLs on their own line
whenever you can. Inline, wrap them in an isolate (RLI … PDI) or add
an RLM after them, and never put a period directly after one: the
period either jumps or becomes part of the link.

- Wrong: «مقاله رو اینجا بخونید: https://example.com/article.»
- Right: «مقاله رو اینجا بخونید:» then the URL alone on the next line.
- @mentions and #hashtags behave like short URLs: keep them at the
  end of a Persian sentence only with an RLM before the punctuation,
  or put them on their own line.

## 4. Numbers

Prefer Persian digits (۱۲۳) in Persian text: they are Arabic numbers
and take the paragraph direction, so punctuation around them stays
put. Latin digits (123) are European numbers and behave like a Latin
run: keep the whole number together, do not split it across a line
break, and do not end a sentence with one. Phone numbers, prices in
dollars, and version numbers stay in Latin digits; write them as one
unbroken run and end the sentence with a Persian word after them.

- Fine: «قیمت 120 دلار.» (the sentence ends with a Persian word)
- Wrong: «نسخه 2.»
- Right: «نسخه ۲ منتشر شد.» or «نسخه 2 منتشر شد.»

## 5. Parentheses and quotes around Latin

Parentheses are neutral, so in a right-to-left paragraph they mirror:
«(React)» displays with the opening paren on the right. Readers cope,
but nested or repeated parens get confusing fast. Use Persian quotes
instead, or put an RLM before the opening paren.

- Confusing: «این کتابخانه (React) معروف است.»
- Better: «این کتابخانه «React» معروف است.»
- Better: put an RLM (U+200F) between the Persian word and the
  opening paren, so the parens stop mirroring.

## 6. Lists

List markers sit on the right in RTL text. Each item leads with a
Persian word, exactly like a sentence. An item that is only a Latin
word or a URL gets its own line and no trailing punctuation.

## 7. Code

Code is left-to-right. In Markdown, use fenced code blocks: the fence
sets the direction and nothing leaks. Inline code inside a Persian
sentence usually renders fine on GitHub but breaks in chat apps, so
in chat put the code on its own line. In HTML, put `dir="ltr"` on
code blocks and `dir="rtl"` on the Persian container.

## 8. Emoji

Emoji are neutral. One emoji at the end of a Persian sentence stays
at the visual end (the left) and is fine. Do not put an emoji between
a Persian run and a Latin run: it takes the direction of whichever
side the renderer picks, and the order flips unpredictably.

## 9. HTML and documents

- Put `dir="rtl"` (and `lang="fa"`) on Persian containers.
- Wrap usernames, URLs, and file paths in `<bdi>` so their direction
  cannot leak into the surrounding text.
- Put `dir="ltr"` on code blocks, tables of Latin data, and terminal
  output.

## Checklist

- [ ] Every line, bullet, heading, and caption starts with a Persian word.
- [ ] No sentence ends with a Latin word, a URL, or Latin digits.
- [ ] No punctuation directly after a URL or @mention.
- [ ] Numbers use Persian digits, unless they are phone numbers, prices, or versions.
- [ ] Latin in parens uses «» quotes or an RLM.
- [ ] Code is in fenced blocks or on its own line.
- [ ] No invisible control characters except where restructuring was impossible.
