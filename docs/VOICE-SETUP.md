# Live voice setup (as found 11 Nov 2026)

## Model server (MazPC)

- Model: `LFM3-Omni-2B-Q4_K_M.gguf` plus projector `mmproj-LFM3-Omni-2B-Q8_0.gguf` (folder `models\LFM3-Omni-2B-GGUF` in the MazPC user profile).
- Server: llama.cpp `llama-server.exe` (folder `tools\llama-cpp` in the MazPC user profile).
- Command:

```
llama-server.exe -m <models>\LFM3-Omni-2B-GGUF\LFM3-Omni-2B-Q4_K_M.gguf ^
  -mm <models>\LFM3-Omni-2B-GGUF\mmproj-LFM3-Omni-2B-Q8_0.gguf ^
  --host 127.0.0.1 --port 8080 --reasoning off --temp 0 -ngl 99 -c 4096
```

It listens on MazPC's localhost only.

## Using it from the laptop

Core on the laptop expects the model at `http://127.0.0.1:8080` (setting `llamacpp_url`, the default). Forward the port over SSH (nothing changes on MazPC):

```
ssh -N -L 127.0.0.1:8080:127.0.0.1:8080 <user>@mazpc
curl http://127.0.0.1:8080/health   # {"status":"ok"}
```

## On the device

Open the **Live** app from the device menu (the remote `open live` command is not supported in firmware v1.5.1). **Call Piblo** (`open talk`) is the older hold-SPACE-to-talk path.

## Known issues found on 11 Nov

1. **Answers "what's on today?" with its model name.** Core's live brain defaults to `live_brain = "cloud"`: the omni model only hears and speaks, and OpenRouter thinks. The laptop Core has no OpenRouter key (`cloud:AUTH_FAILED` in the log) and the local fallbacks are unavailable, so the omni model ends up answering while its session only has the TTS instruction ("Perform TTS in English...") and no Piblo persona. Fix: give the fallback the Piblo persona and memory context, and configure a working free brain.
2. **Keyboard taps count as speech.** `live_voice.Vad` is an energy-only detector (`MIN_RMS = 700` after a 10x mic gain), so key clicks right next to the mic look like speech. Fix: a real speech detector (e.g. Silero VAD, MIT) and/or ignore audio around key events.
3. **Installed Core differs from the repo.** `%LOCALAPPDATA%\Piblo\Core\mazhost\live_voice.py` is not the same as `host/mazhost/live_voice.py` on main. Test against what is actually installed, or reinstall from main first.
4. Battery reads 0% while charging (reading bug or flat battery).
