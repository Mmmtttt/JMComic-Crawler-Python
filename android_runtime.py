from __future__ import annotations

import gc
import os
import platform
import time
from io import BytesIO
from typing import Any, Dict

from PIL import Image, UnidentifiedImageError


_FALLBACK_INSTALLED = False
_FALLBACK_INSTALL_ERROR = ""
_ORIGINAL_OPEN_IMAGE = None


def is_android_runtime() -> bool:
    runtime_profile = str(os.environ.get("BACKEND_RUNTIME_PROFILE") or "").strip().lower()
    platform_text = f"{platform.system()} {platform.platform()} {os.environ.get('ANDROID_ARGUMENT', '')}".lower()
    return runtime_profile in {"android", "apk"} or "android" in platform_text


def android_download_overrides() -> Dict[str, Any]:
    if not is_android_runtime():
        return {}
    image_workers = _safe_positive_int(os.environ.get("JMCOMIC_ANDROID_IMAGE_WORKERS"), 1)
    photo_workers = _safe_positive_int(os.environ.get("JMCOMIC_ANDROID_PHOTO_WORKERS"), 1)
    suffix = str(os.environ.get("JMCOMIC_ANDROID_IMAGE_SUFFIX") or ".png").strip() or ".png"
    if not suffix.startswith("."):
        suffix = f".{suffix}"
    return {
        "threading": {
            "image": image_workers,
            "photo": photo_workers,
        },
        "image": {
            "suffix": suffix,
        },
    }


def install_android_webp_fallback() -> bool:
    global _FALLBACK_INSTALLED, _FALLBACK_INSTALL_ERROR, _ORIGINAL_OPEN_IMAGE
    if _FALLBACK_INSTALLED:
        return True
    if not is_android_runtime():
        return False

    try:
        from jmcomic.jm_toolkit import JmImageTool
    except Exception as exc:
        _FALLBACK_INSTALL_ERROR = str(exc)
        return False

    original_open_image = getattr(JmImageTool, "open_image", None)
    if original_open_image is None:
        _FALLBACK_INSTALL_ERROR = "jmcomic.JmImageTool.open_image not found"
        return False

    def open_image_with_android_webp(cls, fp):
        try:
            return original_open_image(fp)
        except UnidentifiedImageError as original_exc:
            if not isinstance(fp, (bytes, bytearray, memoryview)):
                raise
            payload = bytes(fp)
            if not _is_webp(payload):
                raise
            try:
                png_bytes = _decode_webp_to_png_bytes(payload)
                return Image.open(BytesIO(png_bytes))
            except Exception as fallback_exc:
                raise original_exc from fallback_exc

    _ORIGINAL_OPEN_IMAGE = original_open_image
    JmImageTool.open_image = classmethod(open_image_with_android_webp)
    _FALLBACK_INSTALLED = True
    _FALLBACK_INSTALL_ERROR = ""
    return True


def append_download_log(path_or_dir: str, message: str) -> None:
    if not is_android_runtime():
        return
    try:
        target_dir = path_or_dir
        if os.path.splitext(path_or_dir)[1]:
            target_dir = os.path.dirname(path_or_dir)
        if not target_dir:
            target_dir = os.environ.get("HOME") or "."
        os.makedirs(target_dir, exist_ok=True)
        log_path = os.path.join(target_dir, "jmcomic_android.log")
        timestamp = time.strftime("%Y-%m-%dT%H:%M:%S%z")
        with open(log_path, "a", encoding="utf-8") as fp:
            fp.write(f"{timestamp} {message} {diagnostic_memory_text()}\n")
            fp.flush()
            try:
                os.fsync(fp.fileno())
            except OSError:
                pass
    except Exception:
        pass


def open_pillow_image_from_bytes(payload: bytes):
    try:
        return Image.open(BytesIO(payload))
    except UnidentifiedImageError as original_exc:
        if not is_android_runtime() or not _is_webp(bytes(payload)):
            raise
        try:
            return Image.open(BytesIO(_decode_webp_to_png_bytes(bytes(payload))))
        except Exception as fallback_exc:
            raise original_exc from fallback_exc


def diagnostics() -> Dict[str, Any]:
    pillow_features: Dict[str, Any] = {}
    try:
        from PIL import features

        pillow_features["webp"] = bool(features.check("webp"))
    except Exception as exc:
        pillow_features["webp_error"] = str(exc)

    return {
        "android_runtime": is_android_runtime(),
        "android_webp_fallback_installed": bool(_FALLBACK_INSTALLED),
        "android_webp_fallback_error": _FALLBACK_INSTALL_ERROR,
        "android_download_overrides": android_download_overrides(),
        "pillow_features": pillow_features,
    }


def diagnostic_memory_text() -> str:
    parts = []
    try:
        status_path = "/proc/self/status"
        if os.path.exists(status_path):
            values = {}
            with open(status_path, "r", encoding="utf-8", errors="ignore") as fp:
                for line in fp:
                    key, _, value = line.partition(":")
                    if key in {"VmRSS", "VmHWM", "VmSwap", "Threads"}:
                        values[key] = value.strip()
            if values:
                parts.append(" ".join([f"{key}={value}" for key, value in sorted(values.items())]))
    except Exception:
        pass
    return f"[{' '.join(parts)}]" if parts else ""


def collect_after_large_image() -> None:
    if is_android_runtime():
        gc.collect()


def _safe_positive_int(raw: object, fallback: int) -> int:
    try:
        value = int(str(raw or "").strip())
        return value if value > 0 else fallback
    except Exception:
        return fallback


def _is_webp(payload: bytes) -> bool:
    return len(payload) >= 12 and payload[:4] == b"RIFF" and payload[8:12] == b"WEBP"


def _decode_webp_to_png_bytes(payload: bytes) -> bytes:
    from java import jclass

    BitmapFactory = jclass("android.graphics.BitmapFactory")
    ByteArrayOutputStream = jclass("java.io.ByteArrayOutputStream")
    CompressFormat = jclass("android.graphics.Bitmap$CompressFormat")

    bitmap = BitmapFactory.decodeByteArray(payload, 0, len(payload))
    if bitmap is None:
        raise RuntimeError("Android BitmapFactory failed to decode WebP bytes")

    stream = ByteArrayOutputStream()
    try:
        ok = bitmap.compress(CompressFormat.PNG, 100, stream)
        if not ok:
            raise RuntimeError("Android Bitmap.compress(PNG) returned false")
        return bytes(stream.toByteArray())
    finally:
        try:
            bitmap.recycle()
        except Exception:
            pass
        try:
            stream.close()
        except Exception:
            pass
