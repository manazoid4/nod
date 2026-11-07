> Drafted by Claude Opus 5.5 via OpenRouter ($0.124, 6 Nov 2026), reviewed in-session. FFmpeg normalise, caption burn-in and concat commands tested on a synthetic clip; the caption file was finished by hand after the model hit its token limit.

# Nod: Prelaunch Film Plan

**Goal:** Honest, uncut-feeling prototype footage for the Kickstarter prelaunch page.
**Kit:** One phone, the Nod prototype (M5Stack Cardputer ADV), your Windows PC running Nod Core, and one desk lamp.
**Budget:** £0.

> **Note:** The case is still being designed. Film the device as it is today, and say so on screen ("prototype hardware").

---

## General night-time setup (do this once)

1. Turn off the overhead light. It causes glare on the 1.14in screen.
2. Use one desk lamp, bounced off a white wall or ceiling, not pointed at the device.
3. Set the device screen to maximum brightness.
4. On the phone, use the 1x lens. Do not use digital zoom. Move closer instead.
5. Tap the device screen on your phone and hold to lock focus and exposure. Then drag exposure down until the screen text is readable rather than glowing.
6. Shoot at 30fps.
7. Choose orientation before you film:
   - Vertical for 9:16 clips.
   - Horizontal for 16:9 clips.
8. Tilt the device 10–15° away from the lamp to kill reflections.
9. Clean the screen. Dust shows at macro distance.

---

## 1. Tonight: 6 shots

### Shot 1: In the hand (6s)
- **Framing:** Medium close-up. The device sits in your palm and the keyboard is visible.
- **Lighting:** Bounce the lamp from the side so the hand is lit but the screen isn't washed out.
- **Action:** Wake the device. The current home or mode screen appears. Slowly tilt it towards the lens.
- **Proves:** It's real, pocket-sized hardware that you can hold.

### Shot 2: CAPTURE to MEMORY (10s)
- **Framing:** Tight on the screen and keyboard, top-down.
- **Lighting:** Keep the lamp behind the phone, high, at about 45°.
- **Action:**
  1. Open CAPTURE.
  2. Speak a short note: "Buy printer filament."
  3. Open MEMORY.
  4. The note is in the inbox.
- **Proves:** Voice notes are saved and retrievable.

### Shot 3: AGENTS approval (8s)
- **Framing:** Over the shoulder. The device is in the foreground and the PC monitor is softly in the background.
- **Lighting:** Turn the monitor brightness down to about 40% so it doesn't blow out.
- **Action:**
  1. A pending approval shows on the device.
  2. Press approve.
  3. The PC (Nod Core) reacts.
- **Proves:** The device approves real agent actions on the PC.

### Shot 4: CONTROL (8s)
- **Framing:** Wide enough to see both the device and the PC.
- **Lighting:** Keep the same setup as Shot 3.
- **Action:** Trigger one PC control you already have set up. The PC visibly responds.
- **Proves:** Physical control of your PC from the device.

### Shot 5: FOCUS timer (6s)
- **Framing:** Close-up on the screen, with the device on the desk next to a notebook.
- **Lighting:** Use warm lamp light, bounced.
- **Action:** Start a focus timer. The countdown visibly ticks.
- **Proves:** Timers and tasks work on-device.

### Shot 6: Charging mode (8s)
- **Framing:** Top-down on the device with the cable plugged in.
- **Lighting:** Lower the lamp so the cable doesn't cast hard shadows.
- **Action:** Plug in. The Charging screen shows the big %, "Charging" and the time-to-full.
  - If you have a fully charged unit, also film the "Fully charged / Safe to unplug" screen.
- **Proves:** The new charging screen exists and works.

**Before filming, blur or hide** Wi-Fi names, IP addresses, tokens and email or notification pop-ups. Enable Windows Focus Assist.

---

## 2. One uncut proof take (CALL, 30–60s)

**Framing**
- Horizontal and static. Prop the phone on books.
- You are visible from the chest up, holding the device.
- The PC is in frame with Nod Core open.

**Audio**
- Keep the phone within 1m of you.
- Turn off fans and the TV.

**Script**
1. **(0s)** Look at the camera: "This is the Nod prototype. One take, no cuts, real speed."
2. **(5s)** Show the screen to the lens. Open CALL.
3. **(10s)** Hold the talk key and say clearly: *"What's a good ten-minute break idea for tonight?"*
4. Release the key. **Say nothing.** Let the real wait play out.
5. The spoken reply plays from the device speaker. Let it finish.
6. **(~40s)** Say: "That's it. Hold, speak, it answers. Still a prototype."
7. Hold for 2s, then stop recording.

**Rules**
- If it fails, film again from the start. Never splice takes.
- Post the full take on the page, labelled "Uncut, real time".

---

## 3. Edit pipeline

### Step 1: Copy footage
1. Copy the phone clips to a folder: `C:\nod\raw\`.
2. Work in `C:\nod\`.

### Step 2: Normalise with FFmpeg
This step fixes the variable frame rate, sets the size and evens out loudness.

**9:16 (1080x1920):**
```
ffmpeg -i raw\shot1.mp4 -vf "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2,fps=30,format=yuv420p" -af "loudnorm=I=-16:TP=-1.5:LRA=11" -c:v libx264 -crf 18 -preset medium -c:a aac -b:a 192k -ar 48000 v_shot1.mp4
```

**16:9 (1920x1080):**
```
ffmpeg -i raw\shot1.mp4 -vf "scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2,fps=30,format=yuv420p" -af "loudnorm=I=-16:TP=-1.5:LRA=11" -c:v libx264 -crf 18 -preset medium -c:a aac -b:a 192k -ar 48000 h_shot1.mp4
```

Repeat for each clip. Footage filmed in the wrong orientation will get black bars. That's honest, but reshooting is better.

### Step 3: Title cards and lower-thirds in Friction
1. Create a new scene at 1080x1920 (or 1920x1080), 30fps.
2. Title cards:
   - Use white text on black, 2s each.
   - Render them as MP4 clips.
3. Lower-thirds (for example "Prototype hardware"):
   - Use a transparent background.
   - Render as a PNG sequence (`lt_0001.png`…).
4. Overlay a lower-third on a shot:
```
ffmpeg -i v_shot1.mp4 -framerate 30 -i lt_%04d.png -filter_complex "[0][1]overlay=0:0:eof_action=pass" -c:v libx264 -crf 18 -c:a copy v_shot1_lt.mp4
```
5. Give title cards a silent audio track so the clips join cleanly:
```
ffmpeg -i title1.mp4 -f lavfi -i anullsrc=r=48000:cl=stereo -shortest -c:v libx264 -crf 18 -pix_fmt yuv420p -r 30 -c:a aac -b:a 192k title1_a.mp4
```

### Step 4: Natron (only if the screen is glary or soft)
Use a 5-node graph:
1. **Read:** loads the clip.
2. **Roto:** draw a shape around the device screen and track or keyframe it if the device moves.
3. **Grade:** connect the Roto to its mask input and lower the gain or whitepoint to tame glare on the screen only.
4. **SharpenCImg:** also masked by the Roto. Use a light amount, because too much creates halos.
5. **Write:** output a PNG sequence.

Rebuild the clip with its original audio:
```
ffmpeg -framerate 30 -i fix_%04d.png -i v_shot2.mp4 -map 0:v -map 1:a -c:v libx264 -crf 18 -pix_fmt yuv420p -c:a copy v_shot2_fix.mp4
```

**Rule:** you may only clean up the screen. Never replace or redraw it.

### Step 5: Assemble and export
1. Make `list.txt`:
```
file 'title1_a.mp4'
file 'v_shot1_lt.mp4'
file 'v_shot2_fix.mp4'
```
2. Join the clips:
```
ffmpeg -f concat -safe 0 -i list.txt -c copy teaser.mp4
```
   This works because every clip was normalised identically.
3. If the join glitches, re-encode instead:
```
ffmpeg -f concat -safe 0 -i list.txt -c:v libx264 -crf 18 -c:a aac -b:a 192k teaser.mp4
```

**Optional:** latent-spaces/brag is a promo-video toolkit. Check its README for anything useful, but don't depend on it tonight.

---

## 4. 15–25s teaser cut (about 21s)

| Time | Shot | On-screen text |
|---|---|---|
| 0–2s | Title card | **Nod** |
| 2–5s | Shot 1 (in hand) | A small device for your desk and pocket |
| 5–10s | CALL take excerpt (real speed) | Hold a key. Ask. Hear the answer. |
| 10–13s | Shot 2 (CAPTURE→MEMORY) | Say a note. Find it later. |
| 13–16s | Shot 3 (AGENTS) | Approve your PC's AI tasks |
| 16–18s | Shot 6 (Charging) | Works with Nod Core on Windows |
| 18–21s | Title card | Prototype. Coming to Kickstarter. |

If the CALL reply takes longer than 5s, trim to show the question and the reply with an on-screen **"Wait trimmed. Full take on our page."** Or extend the teaser up to 25s.

---

## 5. Honesty checklist

- **Label anything planned as "coming".** That covers SUBTITLES, ROUTINES, SAVE THIS, the 3.5in screen and the final case. Never show them as working.
- **Don't hide cuts in response times.** If a wait is trimmed, say so on screen. Link the uncut take.
- **No fake screens.** No mock-ups or CGI composited onto the device. Natron is for glare and sharpening only.
- **Blur private information.** Hide Wi-Fi names, IPs, tokens, API keys, emails and notifications.
- **Say "prototype hardware".** It's an M5Stack Cardputer ADV in a work-in-progress case.
- **Keep claims factual.** No "does everything" lines, and no implying the device works without the PC and Nod Core.

---

## 6. Captions

### Burn in captions with FFmpeg
1. Save the SRT as `teaser.srt` in the same folder as the video. This avoids Windows path issues.
2. Run:
```
ffmpeg -i teaser.mp4 -vf "subtitles=teaser.srt:force_style='FontName=Arial,FontSize=14,PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,BorderStyle=1,Outline=2,Alignment=2,MarginV=60'" -c:v libx264 -crf 18 -c:a copy teaser_captioned.mp4
```
3. If you get an error, your FFmpeg build needs libass. The standard Windows "full" builds include it.
4. For 9:16, raise `MarginV` to about 160 to clear the app interface.

### Sample `teaser.srt`
```
1
00:00:02,000 --> 00:00:05,000
A small device for your desk and pocket.

2
00:00:05,500 --> 00:00:09,000
Hold a key. Ask out loud. Hear the answer.

3
00:00:09,500 --> 00:00:13,000
Save an idea before it disappears.

4
00:00:13,500 --> 00:00:17,000
Prototype. Real footage. Coming to Kickstarter.
```
