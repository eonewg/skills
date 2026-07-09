# CUDA faster-whisper ASR route

Use this when the machine has an NVIDIA GPU and a downloaded MP4 needs a higher-quality transcript.

## WSL GPU check

In this WSL setup, `nvidia-smi` may not be on PATH. Check both:

```bash
command -v nvidia-smi || true
/usr/lib/wsl/lib/nvidia-smi || true
ldconfig -p | grep -E 'libcuda|libcudnn|libcublas' | head
```

A working WSL CUDA bridge may expose only `libcuda.so` under `/usr/lib/wsl/lib`. That is enough for the driver side, but faster-whisper / CTranslate2 also needs cuBLAS and cuDNN user-space libraries.

## Run with pip-provided CUDA libraries

Use `uv run` with NVIDIA CUDA wheels instead of modifying the system:

```bash
uv run \
  --with faster-whisper \
  --with nvidia-cublas-cu12 \
  --with nvidia-cudnn-cu12 \
  python transcribe_faster_whisper_large_cuda.py
```

`faster-whisper` can read MP4 directly through PyAV, so system `ffmpeg` is not required for this route.

## Recommended model tiers

- Fast draft: `base`, `device='cpu'`, `compute_type='int8'`.
- Better CUDA transcript: `large-v3`, `device='cuda'`, `compute_type='float16'`.
- If VRAM is tight, try `large-v3`, `compute_type='int8_float16'` or `distil-large-v3`.

## Proven case

On NVIDIA GeForce RTX 4060 Laptop GPU, WSL, CUDA driver visible at `/usr/lib/wsl/lib/nvidia-smi`:

- Video: Douyin `7648892907285417268`, 19m44s, 48 MB MP4.
- CPU draft: `faster-whisper base`, CPU int8, 129.43s, 674 segments.
- CUDA upgrade: `faster-whisper large-v3`, CUDA float16, 512.97s, 589 segments.
- Quality improvement: technical English terms improved significantly (`Tools`, `Skills`, `Memory`, `Context`, `Permission`, `Subagent`, `Sessions`, `Command`, `Hook`, `Query Engine`).

## Minimal script shape

```python
from pathlib import Path
from faster_whisper import WhisperModel

media = Path('media/video.mp4')
model = WhisperModel('large-v3', device='cuda', compute_type='float16')
segments, info = model.transcribe(
    str(media),
    language='zh',
    vad_filter=True,
    beam_size=5,
    condition_on_previous_text=True,
)
for seg in segments:
    print(seg.start, seg.end, seg.text)
```

## Pitfalls

- If `nvidia-smi` is missing, check `/usr/lib/wsl/lib/nvidia-smi` before concluding CUDA is unavailable.
- CTranslate2 CUDA may fail if cuBLAS/cuDNN are missing; add `nvidia-cublas-cu12` and `nvidia-cudnn-cu12` to the `uv run` environment.
- `large-v3` is not always faster than CPU `base`; it is higher quality. Use it for final transcripts, not quick triage.
- ASR still makes domain errors. Correct technical terms against chapter structure and visible context before writing the final note.
