# Piblo: 50 feature ideas (9 Nov 2026)

Fit to the Cardputer ADV hardware: keyboard, mic, speaker, IR transmitter, motion sensor, microSD, Wi-Fi, Bluetooth, USB (can act as a keyboard), Grove port.
Effort: **S** = days, **M** = 1-3 weeks, **L** = month+. ⭐ = top-10 pick for the campaign.

## 1. Never forget (memory and reminders)
1. ⭐ **Snooze that learns** (S): "later" picks a smart time (after your meeting, when you get home) instead of a fixed 10 min.
2. ⭐ **"Where did I put it?"** (S): say "keys in the blue drawer"; ask later "where are my keys?".
3. **Leaving-the-house check** (M): when your phone/laptop goes off Wi-Fi, Piblo runs your list: keys, wallet, charger.
4. **Medication tracker** (S): one-press "taken", nags only if missed, weekly streak. (Not a medical device.)
5. **Bin day, bills, birthdays** (S): recurring life admin from a simple text list, with yes/no/later.

## 2. Focus and getting started (ADHD-friendly, all sorts of people)
6. ⭐ **Body-double mode** (M): Buddy "works" next to you, checks in every 25 min by voice, celebrates when you finish.
7. ⭐ **"Just the next step"** (S): say a scary task, Piblo breaks it down and only shows step 1.
8. **Visual countdown timer** (S): time shrinking on screen, not just numbers (time blindness).
9. **Transition warnings** (S): "10 minutes until you need to leave" with chime escalation.
10. **Distraction parking** (S): press a key, say the stray thought, it's saved for later and you're back in focus.

## 3. Voice and capture
11. ⭐ **Meeting mode, press-to-mark** (M): records locally, press a key when something matters; Core gives a summary + actions at those marks.
12. **Voice-to-anywhere** (M): spoken note lands in Notion, Obsidian, Todoist, Google Tasks or email, chosen by saying "to Notion".
13. **Read it back** (S): "read me my notes from today" while you walk.
14. **Idea threads** (M): Piblo links new voice notes to earlier ones on the same idea.
15. **Offline capture** (S): notes save to microSD when Wi-Fi is down, sync later with a "saved to PC" tick.

## 4. AI agent control (the developer hook)
16. ⭐ **Approve any agent** (S, partly built): Claude Code, Codex, n8n, Zapier, GitHub Actions via webhooks; yes/no from the keys.
17. **Claude Desktop Buddy protocol** (M): Piblo also speaks Anthropic's open Bluetooth protocol, so it works with Claude's own app.
18. **Agent status board** (S): see what each agent is doing; "3 running, 1 waiting on you".
19. **Spending guard** (M): any agent action that costs money shows the amount and needs a long-press to approve.
20. **Daily agent report** (S): "today your agents did 14 things" with undo links on the PC.

## 5. Computer control (Stream Deck in your pocket)
21. ⭐ **Macro keys** (M): one key = open apps, join a meeting, mute mic, start a focus playlist.
22. **Plug in as a keyboard** (M): USB text expander: type your address, email templates, code snippets.
23. **Remote presenter** (S): next/back slides, a timer and your speaker notes on screen.
24. **Mute indicator** (S): shows if you're muted on Teams/Zoom/Meet; one press to toggle.
25. **Clipboard to pocket** (S): copy on PC, read or paste it from Piblo later.

## 6. Home and real world
26. ⭐ **TV/aircon remote via IR** (M): "TV off", learned buttons, works without smart devices.
27. **Home Assistant buttons** (M): lights, heating, doorbell alerts with yes/no.
28. **Parcel and doorbell alerts** (S): webhook in, "Parcel at door" with the Buddy waving.
29. **Plant/pet care rota** (S): who fed the cat, shared via Core.
30. **Kitchen timers by voice** (S): several named timers at once ("pasta 9 minutes").

## 7. Work and small business
31. **Missed-call and lead alerts** (M): from a receptionist bot, CRM or website form; reply "call back at 3" by voice.
32. **Daily brief** (S): calendar, top 3 tasks, weather, first meeting, spoken at a press.
33. **End-of-day wrap** (S): "what did you get done?" voice log becomes a timesheet or standup.
34. **Invoice and payment pings** (S): Stripe/PayPal webhook: "£79 received from ...".
35. **Customer reply drafts** (M): AI drafts a reply to a new email, you approve with a key press.

## 8. Learning and students
36. **Flashcards with spaced repetition** (M): keys for "got it / again", Anki import.
37. **Language buddy** (M): short spoken practice sessions with the AI, scored streaks.
38. **Lecture capture with timestamps** (M): same press-to-mark as meetings.
39. **Pomodoro with streaks** (S): ties into XP and ranks.
40. **Homework helper that won't give answers** (M): hints-only mode for kids and parents.

## 9. Health, calm and wellbeing
41. **Breathing coach** (S): animated Buddy breathing, 1-minute calm.
42. **Water and stand-up nudges** (S): uses the motion sensor so it doesn't nag while you're walking.
43. **Mood check-in** (S): one key a day, weekly pattern shown privately on your PC.
44. **Wind-down mode** (S): screen dims, no alerts after a set time, morning summary instead.
45. **Gentle wake-up** (S): rising chime plus your first reminder of the day.

## 10. Fun, sharing and trust
46. ⭐ **Buddy that grows** (M): Buddy changes with your streaks; unlock outfits by finishing tasks (Flipper's dolphin effect).
47. **Two Piblos talking** (M): send a quick voice note or "on my way" to a partner's Piblo, no phone.
48. **Family shared lists** (M): shopping list anyone in the house can add to by voice.
49. ⭐ **Privacy light + local-only mode** (S): visible recording light; switch to "nothing leaves my PC" with local models.
50. **Plugin store on GitHub** (L): community adds features as small add-ons (like Flipper apps), installed from Core.

## Top 10 to show on the campaign (one per audience)
Busy people: 1, 2. ADHD/focus: 6, 7. Meetings: 11. Developers: 16. Everyone at a desk: 21. Home: 26. Fun: 46. Trust: 49.

Sources for inspiration: ADHD tool round-ups (deepwrk.io/blog/adhd-products, zangy.io/blog/best-productivity-tools-adhd-2026, adhdcareconnect.com body-doubling guide), Flipper Zero app catalogue (lab.flipper.net/apps), plus the competitor and complaints research in `research/`.
