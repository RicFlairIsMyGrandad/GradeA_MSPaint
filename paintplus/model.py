"""UI-independent scene model. Original RGBA pixels are never resized in place."""

from __future__ import annotations
import copy
import io
import json
import math
import os
import tempfile
import uuid
import zipfile
from dataclasses import dataclass, field
from pathlib import Path
from PIL import Image

SPECIAL_BLUE = "#1847F1"
MAX_PIXELS = 64_000_000


@dataclass
class Layer:
    name: str
    image: Image.Image
    x: float = 0
    y: float = 0
    width: float = 0
    height: float = 0
    angle: float = 0
    visible: bool = True
    locked: bool = False
    flip_h: bool = False
    flip_v: bool = False
    group: str | None = None
    text: dict | None = None
    id: str = field(default_factory=lambda: uuid.uuid4().hex)
    nearest: bool = False

    def __post_init__(self):
        self.image = self.image.convert("RGBA")
        self.width = self.width or self.image.width
        self.height = self.height or self.image.height

    def rendered(self):
        size = (max(1, round(self.width)), max(1, round(self.height)))
        if size[0] * size[1] > MAX_PIXELS:
            raise ValueError("Object is too large (maximum 64 million pixels).")
        image = self.image.resize(
            size, Image.Resampling.NEAREST if self.nearest else Image.Resampling.LANCZOS
        )
        if self.flip_h:
            image = image.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
        if self.flip_v:
            image = image.transpose(Image.Transpose.FLIP_TOP_BOTTOM)
        if self.angle:
            image = image.rotate(
                -self.angle,
                Image.Resampling.NEAREST if self.nearest else Image.Resampling.BICUBIC,
                expand=True,
            )
        return image

    def bounds(self):
        r = math.radians(self.angle)
        w = abs(self.width * math.cos(r)) + abs(self.height * math.sin(r))
        h = abs(self.height * math.cos(r)) + abs(self.width * math.sin(r))
        return self.x + (self.width - w) / 2, self.y + (self.height - h) / 2, w, h


class Document:
    def __init__(self, width=1200, height=800):
        self.width, self.height = width, height
        self.layers = [Layer("Background", Image.new("RGBA", (width, height), "white"))]
        self.undo_stack = []
        self.redo_stack = []
        self.dirty = False

    def snapshot(self):
        return self.width, self.height, copy.deepcopy(self.layers)

    def checkpoint(self):
        self.undo_stack.append(self.snapshot())
        self.undo_stack = self.undo_stack[-30:]
        self.redo_stack.clear()
        self.dirty = True

    def undo(self):
        if not self.undo_stack:
            return False
        self.redo_stack.append(self.snapshot())
        self.width, self.height, self.layers = self.undo_stack.pop()
        self.dirty = True
        return True

    def redo(self):
        if not self.redo_stack:
            return False
        self.undo_stack.append(self.snapshot())
        self.width, self.height, self.layers = self.redo_stack.pop()
        self.dirty = True
        return True

    def flatten(self):
        output = Image.new("RGBA", (self.width, self.height))
        for layer in self.layers:
            if not layer.visible:
                continue
            image = layer.rendered()
            x = round(layer.x + (layer.width - image.width) / 2)
            y = round(layer.y + (layer.height - image.height) / 2)
            output.alpha_composite(image, (x, y))
        return output

    def add_image(self, image, name="Image", x=40, y=40):
        self.checkpoint()
        layer = Layer(name, image, x, y)
        self.layers.append(layer)
        return layer

    def crop(self, box):
        left, top, right, bottom = map(round, box)
        if right <= left or bottom <= top:
            raise ValueError("Select a nonempty crop area.")
        self.checkpoint()
        self.width, self.height = right - left, bottom - top
        for layer in self.layers:
            layer.x -= left
            layer.y -= top

    def merge(self, ids):
        selected = [l for l in self.layers if l.id in ids]
        if len(selected) < 2:
            return
        if any(l.locked for l in selected):
            raise ValueError("Unlock the selected layers first.")
        self.checkpoint()
        sub = Document(self.width, self.height)
        sub.layers = selected
        image = sub.flatten()
        position = max(self.layers.index(l) for l in selected)
        merged = Layer("Merged layers", image)
        self.layers.insert(position + 1, merged)
        self.layers = [l for l in self.layers if l.id not in ids]
        return merged

    def save(self, path):
        path = Path(path)
        metadata = {
            "version": 1,
            "width": self.width,
            "height": self.height,
            "layers": [],
        }
        with tempfile.NamedTemporaryFile(dir=path.parent, delete=False) as f:
            temp = Path(f.name)
        try:
            with zipfile.ZipFile(temp, "w", zipfile.ZIP_DEFLATED) as archive:
                for i, layer in enumerate(self.layers):
                    data = {k: v for k, v in vars(layer).items() if k != "image"}
                    data["file"] = f"images/{i}.png"
                    metadata["layers"].append(data)
                    buf = io.BytesIO()
                    layer.image.save(buf, "PNG")
                    archive.writestr(data["file"], buf.getvalue())
                archive.writestr("document.json", json.dumps(metadata))
            os.replace(temp, path)
            self.dirty = False
        finally:
            temp.unlink(missing_ok=True)

    @classmethod
    def load(cls, path):
        with zipfile.ZipFile(path) as archive:
            if sum(i.file_size for i in archive.infolist()) > 512_000_000:
                raise ValueError("Project exceeds the 512 MB safety limit.")
            data = json.loads(archive.read("document.json"))
            if data.get("version") != 1:
                raise ValueError("Unsupported project version.")
            w, h = int(data["width"]), int(data["height"])
            if min(w, h) < 1 or w * h > MAX_PIXELS:
                raise ValueError("Invalid canvas size.")
            doc = cls(w, h)
            doc.layers = []
            for entry in data["layers"]:
                entry = dict(entry)
                image = Image.open(io.BytesIO(archive.read(entry.pop("file"))))
                image.load()
                doc.layers.append(Layer(image=image, **entry))
            return doc

    def export(self, path):
        image = self.flatten()
        suffix = Path(path).suffix.lower()
        if suffix in (".jpg", ".jpeg", ".bmp"):
            background = Image.new("RGB", image.size, "white")
            background.paste(image, mask=image.getchannel("A"))
            image = background
        image.save(path, quality=95)


def unique_path(folder, filename, extension):
    name = filename.strip()
    if not name or name in (".", "..") or any(c in name for c in '<>:"/\\|?*'):
        raise ValueError("Enter a filename without Windows reserved characters.")
    if name.split(".")[0].upper() in {
        "CON",
        "PRN",
        "AUX",
        "NUL",
        *[f"COM{i}" for i in range(1, 10)],
        *[f"LPT{i}" for i in range(1, 10)],
    }:
        raise ValueError("That filename is reserved by Windows.")
    name = name.rstrip(". ")
    if name.lower().endswith(extension.lower()):
        name = name[: -len(extension)]
    if not name:
        raise ValueError("Enter a filename.")
    path = Path(folder) / (name + extension)
    counter = 2
    while path.exists():
        path = Path(folder) / f"{name} ({counter}){extension}"
        counter += 1
    return path
