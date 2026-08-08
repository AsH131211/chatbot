import queue
import tempfile
import threading
from pathlib import Path

from pykokoro import KokoroPipeline, PipelineConfig, GenerationConfig

from .config import VOICE_ENABLED, VOICE_NAME, MODEL_QUALITY, LANGUAGE, SPEECH_SPEED
from .player import play

_pipeline: KokoroPipeline | None = None
_pipeline_lock = threading.Lock()
_STOP = object()
_speech_queue: queue.Queue = queue.Queue()
_worker: threading.Thread | None = None


def _get_pipeline() -> KokoroPipeline:
    global _pipeline
    with _pipeline_lock:
        if _pipeline is None:
            _pipeline = KokoroPipeline(
                PipelineConfig(
                    voice=VOICE_NAME,
                    model_quality=MODEL_QUALITY,
                    provider="cpu",
                    generation=GenerationConfig(lang=LANGUAGE, speed=SPEECH_SPEED),
                )
            )
    return _pipeline


def _generate_and_play(text: str) -> None:
    result = _get_pipeline().run(text)
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        path = Path(tmp.name)
    try:
        result.save_wav(str(path))
        play(path)
    finally:
        path.unlink(missing_ok=True)


def _worker_loop() -> None:
    while True:
        item = _speech_queue.get()
        try:
            if item is _STOP:
                return
            if item.strip():
                _generate_and_play(item)
        except Exception as exc:
            print(f"[voice] {exc}")
        finally:
            _speech_queue.task_done()


def _ensure_worker() -> None:
    global _worker
    if _worker is None or not _worker.is_alive():
        _worker = threading.Thread(target=_worker_loop, daemon=True, name="jarvis-tts")
        _worker.start()


def speak(text: str) -> None:
    if not VOICE_ENABLED or not text.strip():
        return
    _ensure_worker()
    _speech_queue.put(text.strip())


def wait() -> None:
    _speech_queue.join()


def preload() -> None:
    if not VOICE_ENABLED:
        return
    _ensure_worker()
    def _load() -> None:
        try:
            _get_pipeline()
        except Exception as exc:
            print(f"[voice preload] {exc}")
    threading.Thread(target=_load, daemon=True, name="jarvis-tts-preload").start()