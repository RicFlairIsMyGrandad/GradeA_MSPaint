"""Local U²-Net small-model inference. Never downloads anything at runtime."""

import hashlib
import os
import sys
from pathlib import Path
import numpy as np
from PIL import Image, ImageFilter
from PySide6.QtCore import QThread, Signal

MODEL_SHA256 = "309c8469258dda742793dce0ebea8e6dd393174f89934733ecc8b14c76f4ddd8"


def model_path():
    override = os.environ.get("PAINTPLUS_MODEL_PATH")
    if override:
        return Path(override)
    root = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent.parent))
    return root / "models" / "u2netp.onnx"


def remove_background(image, path=None, feather=0):
    import onnxruntime as ort

    path = Path(path or model_path())
    if hashlib.sha256(path.read_bytes()).hexdigest() != MODEL_SHA256:
        raise ValueError(
            "AI model checksum does not match the verified U²-Net small model."
        )
    source = image.convert("RGBA")
    rgb = source.convert("RGB").resize((320, 320), Image.Resampling.LANCZOS)
    array = np.asarray(rgb, dtype=np.float32)
    array /= max(float(array.max()), 1.0)
    array = (array - np.array([0.485, 0.456, 0.406], dtype=np.float32)) / np.array(
        [0.229, 0.224, 0.225], dtype=np.float32
    )
    tensor = np.transpose(array, (2, 0, 1))[None].astype(np.float32)
    options = ort.SessionOptions()
    options.intra_op_num_threads = min(4, os.cpu_count() or 1)
    session = ort.InferenceSession(
        str(path), sess_options=options, providers=["CPUExecutionProvider"]
    )
    prediction = session.run(None, {session.get_inputs()[0].name: tensor})[0][0, 0]
    minimum, maximum = float(prediction.min()), float(prediction.max())
    mask = np.clip((prediction - minimum) / max(maximum - minimum, 1e-8), 0, 1)
    alpha = Image.fromarray((mask * 255).astype(np.uint8)).resize(
        source.size, Image.Resampling.LANCZOS
    )
    if feather:
        alpha = alpha.filter(ImageFilter.GaussianBlur(feather))
    original = np.asarray(source.getchannel("A"), dtype=np.float32)
    alpha = Image.fromarray(
        (np.asarray(alpha, dtype=np.float32) * original / 255).astype(np.uint8)
    )
    source.putalpha(alpha)
    return source


class BackgroundWorker(QThread):
    result = Signal(str, object)
    failed = Signal(str)

    def __init__(self, image, id, parent=None, feather=0):
        super().__init__(parent)
        self.image = image
        self.id = id
        self.feather = feather

    def run(self):
        try:
            self.result.emit(
                self.id, remove_background(self.image, feather=self.feather)
            )
        except Exception as e:
            self.failed.emit("Local background removal failed: " + str(e))
