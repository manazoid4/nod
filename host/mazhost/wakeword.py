"""Local streaming wakeword detection for 16 kHz mono PCM16 device audio."""
from pathlib import Path

import numpy as np

RATE = 16000
MODEL_SUFFIX = "epoch-12-avg-2-chunk-16-left-64.int8.onnx"


class Wakeword:
    def __init__(self, model_dir: str | Path, keywords_file: str | Path | None = None):
        import sherpa_onnx

        model_dir = Path(model_dir)
        self.spotter = sherpa_onnx.KeywordSpotter(
            tokens=str(model_dir / "tokens.txt"),
            encoder=str(model_dir / f"encoder-{MODEL_SUFFIX}"),
            decoder=str(model_dir / f"decoder-{MODEL_SUFFIX}"),
            joiner=str(model_dir / f"joiner-{MODEL_SUFFIX}"),
            keywords_file=str(keywords_file or Path(__file__).with_name("hey_piblo_keywords.txt")),
            num_threads=1,
        )
        self.stream = self.spotter.create_stream()

    def reset(self):
        self.stream = self.spotter.create_stream()

    def feed(self, pcm: bytes, sample_rate: int = RATE) -> bool:
        """Feed little-endian PCM16 and return true once for each detection."""
        if sample_rate != RATE or len(pcm) % 2:
            raise ValueError("wakeword audio must be 16 kHz mono PCM16")
        if not pcm:
            return False
        samples = np.frombuffer(pcm, dtype="<i2").astype(np.float32) / 32768.0
        self.stream.accept_waveform(RATE, samples)
        detected = False
        while self.spotter.is_ready(self.stream):
            self.spotter.decode_stream(self.stream)
            if self.spotter.get_result(self.stream):
                detected = True
                self.spotter.reset_stream(self.stream)
        return detected
