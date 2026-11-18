---
name: persian-colloquial
description: Convert formal Persian to widely understood Tehran-based colloquial Persian and check the register of Persian text. Use when writing or rewriting Persian chat messages, captions, dialogue, or voice message transcripts in a natural spoken style, or when checking whether Persian text reads formal or colloquial.
license: MIT
metadata:
  version: "1.0.0"
---

# Colloquial Persian

Convert formal Persian to widely understood Tehran-based colloquial Persian, and check the register of Persian text.

## Convert verbs and the copula

- Convert present tense verbs with the colloquial stems and endings in [verb-tables.md](references/verb-tables.md), using می‌رم for می‌روم and می‌خوام for می‌خواهم.

- Use the ن ending for the third person plural, as in می‌رن and رفتن, and keep the ین variant only when the user already uses it.

- Attach the copula to the previous word, turning است into ـه, as in خوبه for خوب است and سرده for سرد است.

- Drop the می‌ prefix from داشتن in the present tense, using دارم and داره, and use داشته باشم for its subjunctive.

- Use the colloquial past stems where they exist, such as خوندم for خواندم and اومدم for آمدم.

- Keep the subjunctive ب prefix off prefixed verbs, writing برگردم and never بربگردم.

- Leave the infinitive unchanged, since رفتن and کردن are the same in both registers.

## Convert pronouns and markers

- Replace آن with اون and آن‌ها with اونا, and use ایشون for ایشان in polite speech.

- Replace the object marker را with رو, writing کتاب رو خریدم for کتاب را خریدم.

- Attach the object marker to pronouns, using اینو for این را and اونو for آن را.

- Shorten the plural ending ـها to ـا on nouns, as in کتابا for کتاب‌ها.

- Use the colloquial possessive endings مون, تون, and شون for our, your, and their, as in کتابمون for کتاب ما.

## Convert vocabulary and vowel shifts

- Replace formal words with their colloquial partners in [word-pairs.md](references/word-pairs.md), using اگه for اگر and واسه for برای.

- Apply the ā to u vowel shift only to the frequent words that actually show it, such as خونه for خانه and نون for نان, and never change every ا to و.

- Shorten adverbs ending in اً by replacing the ending with ن, as in کلن for کلا and دقیقن for دقیقا.

- Use آره for yes and نه for no in speech, and keep بله for polite or formal address.

- Use خیلی instead of بسیار for very, and use چون instead of زیرا for because.

- Keep technical terms, proper names, and numbers unchanged, since register lives in grammar and common words, not in terminology.

## Use discourse markers and chat style

- Add one discourse marker per thought where a speaker would use one, choosing from [discourse-markers.md](references/discourse-markers.md), and never stack two markers in one short sentence.

- Open a turn with خب to start or resume a topic, and use دیگه to close a topic or mark something as settled.

- Use آخه to explain a reason the listener should already see, and use مگه to ask a surprised question.

- Break long sentences into short ones, drop subjects the listener can recover, and let one thought run across two short messages in chat.

- Write contractions the way people type them in chat, such as میرم for می‌رم, and accept that informal spelling has no single standard.

- Match the script the user writes in, using Finglish only when they do, and use Persian script otherwise.

## Keep register and politeness consistent

- Pick one level of formality for the whole text and keep it, since mixing اگه with دارید in one sentence sounds uncertain.

- Keep شما and plural verb endings for polite address, and use colloquial verbs with them, as in شما می‌خواین, since politeness is not the same as formality.

- Use تو and singular verbs only with friends, family, and peers, and switch to شما with strangers, older people, and customers.

- Keep formal forms in essays, reports, official messages, and academic writing, and use colloquial forms in chat, voice messages, social posts, and dialogue.

- Avoid heavy slang with people you do not know, since a moderately colloquial sentence is polite and a forced slang sentence is risky.

- Leave quoted speech, titles, and proper names in their original register.

## Check the result with the script

- Run `scripts/check_register.py` on the converted text before sending it, passing the text with `--text` or a file path.

- Read the colloquial score and the verdict, and expect a friendly chat message to score above 55 and a formal text to score below 35.

- Fix the flagged formal spans the script lists, then run the script again until the score matches the target register.

- Treat the score as a guide, not a verdict on quality, since a text can be fully colloquial and still sound wrong when its register is mixed.

- Report the score and the verdict to the user when they ask for a check, along with the two or three strongest markers found.

## Available connectors

- Use `muse.connector_search` to find other connectors and `muse.skill_search` to find related skills.

- If nothing here fits, look on the web for a maintained API or MCP server and set it up with [Custom Connectors and MCPs](/opt/muse/skills/custom-connector-setup/SKILL.md), or build a custom connector.

## Alternatives for better results

- Ask the user for a sample of their own writing and match its register with the voice_match_writing skill instead of a generic colloquial voice.

- Generate the text in formal Persian first and convert it in a second pass when the content is complex, since drafting and converting at once invites mixed register.

- Keep a short list of the user's own frequent phrases and reuse them, since a personal stock of phrases reads as more natural than textbook colloquial forms.

- Use the humanize_text skill on English passages in the same text, and convert the Persian parts with this skill, when a message mixes both languages.
