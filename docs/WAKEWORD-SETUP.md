# Local wakeword setup

From the repository root, using the same Python environment as Core:

```powershell
python -m pip install sherpa-onnx
python scripts/setup-wakeword.py "$env:LOCALAPPDATA\Piblo\wakeword-model"
```

Set Core's `wakeword_model_dir` to the printed model directory. An empty setting disables the gate. Restart Core and open the live voice app on the device. Say “Hey Piblo”, pause briefly, then speak the command. The device currently displays the normal listening state and has no wake acknowledgment. This is not always-on from the home screen.

The script downloads the pinned [English GigaSpeech KWS model](https://github.com/k2-fsa/sherpa-onnx/releases/download/kws-models/sherpa-onnx-kws-zipformer-gigaspeech-3.3M-2024-01-01.tar.bz2) from the [Sherpa-ONNX project](https://k2-fsa.github.io/sherpa/onnx/kws/pretrained_models/index.html), checks its SHA-256, and copies only the four required files. The archive is about 17 MB; installed int8 files are about 5.3 MB. No model weights are included in this repository. **The model weights' license and redistribution terms remain unconfirmed; resolve them before shipping.**

On 13 Nov 2026, the detector processed the upstream model's `test_wavs/1.wav` as 20 ms 16 kHz mono PCM16 chunks and detected two upstream keywords. A Windows System.Speech synthetic sample saying “Hey peeblo” produced one target detection; a synthetic sample of the literal spelling “Hey Piblo” produced none. These are smoke tests, not accuracy measurements. Real-device microphone performance, false activations, and reliability across speakers remain untested.
