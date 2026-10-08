from __future__ import annotations
import math
from PIL import Image, ImageDraw
from PySide6.QtCore import Qt, QPointF, QRectF, Signal
from PySide6.QtGui import QColor, QImage, QPainter, QPen, QTransform
from PySide6.QtWidgets import QWidget
from .model import Layer


def qimage(image):
    rgba = image.convert("RGBA")
    return QImage(
        rgba.tobytes(),
        rgba.width,
        rgba.height,
        rgba.width * 4,
        QImage.Format.Format_RGBA8888,
    ).copy()


class Canvas(QWidget):
    changed = Signal()
    selected = Signal()
    picked = Signal(str)
    text_requested = Signal(float, float)
    dropped = Signal(list)
    position = Signal(str)
    zoom_requested = Signal(int)

    def __init__(self, doc):
        super().__init__()
        self.doc = doc
        self.zoom = 1.0
        self.tool = "select"
        self.color = "#1847F1"
        self.secondary = "#ffffff"
        self.brush_size = 5
        self.shape = "Rectangle"
        self.brush_style = "Round brush"
        self.shape_fill = False
        self.selection = []
        self.aspect_lock = True
        self.drag = None
        self.marquee = None
        self._cache = {}
        self.setAcceptDrops(True)
        self.setMouseTracking(True)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.resize_canvas()

    def resize_canvas(self):
        self.setFixedSize(
            round(self.doc.width * self.zoom) + 40,
            round(self.doc.height * self.zoom) + 40,
        )
        self.update()

    def refresh(self):
        self._cache.clear()
        self.selection = [
            i for i in self.selection if any(l.id == i for l in self.doc.layers)
        ]
        self.resize_canvas()
        self.changed.emit()

    def layers(self):
        return [l for l in self.doc.layers if l.id in self.selection]

    def transform(self, layer):
        t = QTransform()
        t.translate(layer.x + layer.width / 2, layer.y + layer.height / 2)
        t.rotate(layer.angle)
        t.scale(
            (-1 if layer.flip_h else 1) * layer.width / layer.image.width,
            (-1 if layer.flip_v else 1) * layer.height / layer.image.height,
        )
        t.translate(-layer.image.width / 2, -layer.image.height / 2)
        return t

    def bounding(self):
        bounds = [l.bounds() for l in self.layers()]
        if not bounds:
            return None
        x = min(b[0] for b in bounds)
        y = min(b[1] for b in bounds)
        right = max(b[0] + b[2] for b in bounds)
        bottom = max(b[1] + b[3] for b in bounds)
        return QRectF(x, y, right - x, bottom - y)

    def handles(self):
        b = self.bounding()
        if b is None:
            return {}
        return {
            "nw": b.topLeft(),
            "n": QPointF(b.center().x(), b.top()),
            "ne": b.topRight(),
            "e": QPointF(b.right(), b.center().y()),
            "se": b.bottomRight(),
            "s": QPointF(b.center().x(), b.bottom()),
            "sw": b.bottomLeft(),
            "w": QPointF(b.left(), b.center().y()),
            "rotate": QPointF(b.center().x(), b.top() - 28 / self.zoom),
        }

    def paintEvent(self, event):
        p = QPainter(self)
        p.fillRect(self.rect(), QColor("#e8edf3"))
        p.setPen(QColor("#687c96"))
        for x in range(0, self.doc.width + 1, 100):
            px = 20 + x * self.zoom
            p.drawLine(round(px), 14, round(px), 19)
            p.drawText(round(px) + 2, 12, str(x))
        for y in range(0, self.doc.height + 1, 100):
            py = 20 + y * self.zoom
            p.drawLine(14, round(py), 19, round(py))
            p.save()
            p.translate(11, py + 4)
            p.rotate(-90)
            p.drawText(0, 0, str(y))
            p.restore()
        p.translate(20, 20)
        p.scale(self.zoom, self.zoom)
        p.setClipRect(QRectF(0, 0, self.doc.width, self.doc.height))
        p.fillRect(QRectF(0, 0, self.doc.width, self.doc.height), QColor("white"))
        step = 16
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QColor("#e9e9e9"))
        for y in range(0, self.doc.height, step):
            for x in range(0, self.doc.width, step):
                if (x // step + y // step) % 2:
                    p.drawRect(x, y, step, step)
        for l in self.doc.layers:
            if not l.visible:
                continue
            key = l.id
            if key not in self._cache:
                self._cache[key] = qimage(l.image)
            p.save()
            p.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, not l.nearest)
            p.setTransform(self.transform(l), True)
            p.drawImage(0, 0, self._cache[key])
            p.restore()
        p.setClipping(False)
        b = self.bounding()
        if b and self.tool in ("select", "move"):
            p.setPen(QPen(QColor("#0078d4"), 1 / self.zoom, Qt.PenStyle.DashLine))
            p.setBrush(Qt.BrushStyle.NoBrush)
            p.drawRect(b)
            hs = self.handles()
            p.drawLine(hs["n"], hs["rotate"])
            p.setBrush(QColor("white"))
            p.setPen(QPen(QColor("#0078d4"), 1 / self.zoom))
            radius = 4 / self.zoom
            for name, point in hs.items():
                if name == "rotate":
                    p.drawEllipse(point, 6 / self.zoom, 6 / self.zoom)
                else:
                    p.drawRect(
                        QRectF(
                            point.x() - radius,
                            point.y() - radius,
                            2 * radius,
                            2 * radius,
                        )
                    )
        if self.marquee:
            p.setPen(QPen(QColor("#0078d4"), 1 / self.zoom, Qt.PenStyle.DashLine))
            p.setBrush(QColor(0, 120, 212, 25))
            p.drawRect(self.marquee)
        p.end()

    def point(self, event):
        return QPointF(
            (event.position().x() - 20) / self.zoom,
            (event.position().y() - 20) / self.zoom,
        )

    def hit(self, point):
        for l in reversed(self.doc.layers):
            if l.locked or not l.visible:
                continue
            inverse, valid = self.transform(l).inverted()
            if not valid:
                continue
            pos = inverse.map(point)
            x, y = int(pos.x()), int(pos.y())
            if (
                0 <= pos.x() < l.image.width
                and 0 <= pos.y() < l.image.height
                and l.image.getpixel((x, y))[3] > 15
            ):
                return l
        return None

    def select_layer(self, layer, additive=False):
        if not additive:
            self.selection = []
        ids = (
            [l.id for l in self.doc.layers if l.group == layer.group]
            if layer.group
            else [layer.id]
        )
        if additive and layer.id in self.selection:
            self.selection = [i for i in self.selection if i not in ids]
        else:
            self.selection = list(dict.fromkeys(self.selection + ids))
        self.selected.emit()
        self.update()

    def mousePressEvent(self, event):
        if event.button() not in (
            Qt.MouseButton.LeftButton,
            Qt.MouseButton.RightButton,
        ):
            return
        pos = self.point(event)
        if not (0 <= pos.x() < self.doc.width and 0 <= pos.y() < self.doc.height):
            return
        color = (
            self.secondary
            if event.button() == Qt.MouseButton.RightButton
            else self.color
        )
        if self.tool == "eyedropper":
            pixel = self.doc.flatten().getpixel((int(pos.x()), int(pos.y())))
            self.picked.emit(QColor(*pixel[:3]).name())
            return
        if self.tool == "text":
            self.text_requested.emit(pos.x(), pos.y())
            return
        if self.tool in ("select", "move"):
            for name, h in self.handles().items():
                if (
                    math.hypot(h.x() - pos.x(), h.y() - pos.y()) < 9 / self.zoom
                    and self.layers()
                ):
                    if any(l.locked for l in self.layers()):
                        return
                    self.doc.checkpoint()
                    self.drag = {
                        "kind": name,
                        "start": pos,
                        "bounds": self.bounding(),
                        "originals": {
                            l.id: (l.x, l.y, l.width, l.height, l.angle)
                            for l in self.layers()
                        },
                    }
                    return
            layer = self.hit(pos)
            if layer:
                if (
                    layer.id not in self.selection
                    or event.modifiers() & Qt.KeyboardModifier.ControlModifier
                ):
                    self.select_layer(
                        layer,
                        bool(event.modifiers() & Qt.KeyboardModifier.ControlModifier),
                    )
                if self.layers() and not any(l.locked for l in self.layers()):
                    self.doc.checkpoint()
                    self.drag = {
                        "kind": "move",
                        "start": pos,
                        "originals": {
                            l.id: (l.x, l.y, l.width, l.height, l.angle)
                            for l in self.layers()
                        },
                    }
            else:
                self.selection = []
                self.selected.emit()
                self.drag = {"kind": "marquee", "start": pos}
                self.marquee = QRectF(pos, pos)
            self.update()
            return
        if self.tool in ("crop", "region"):
            self.drag = {"kind": self.tool, "start": pos}
            self.marquee = QRectF(pos, pos)
            return
        if self.tool in ("pencil", "brush", "eraser", "fill", "shape"):
            self.doc.checkpoint()
            layer = next((l for l in self.layers() if not l.locked), None)
            if self.tool == "eraser" and layer is None:
                layer = self.hit(pos)
                if layer is None:
                    return
            if self.tool not in ("eraser", "fill"):
                layer = Layer(
                    "Shape" if self.tool == "shape" else "Drawing",
                    Image.new("RGBA", (self.doc.width, self.doc.height)),
                )
                self.doc.layers.append(layer)
            elif layer is None:
                layer = self.hit(pos)
                if layer is None:
                    return
            self.selection = [layer.id]
            local = self.transform(layer).inverted()[0].map(pos)
            if self.tool == "fill":
                xy = (int(local.x()), int(local.y()))
                if 0 <= xy[0] < layer.image.width and 0 <= xy[1] < layer.image.height:
                    ImageDraw.floodfill(
                        layer.image, xy, QColor(color).getRgb(), thresh=10
                    )
                self.refresh()
                return
            self.drag = {
                "kind": self.tool,
                "start": pos,
                "last": pos,
                "layer": layer,
                "color": color,
            }
            self.stroke(pos, pos)
            self.selected.emit()
            self.update()

    def stroke(self, start, end):
        d = self.drag
        layer = d["layer"]
        inverse = self.transform(layer).inverted()[0]
        a = inverse.map(start)
        b = inverse.map(end)
        draw = ImageDraw.Draw(layer.image)
        width = 1 if d["kind"] == "pencil" else self.brush_size
        color = (0, 0, 0, 0) if d["kind"] == "eraser" else QColor(d["color"]).getRgb()
        if d["kind"] == "shape":
            return
        if d["kind"] == "brush" and self.brush_style == "Marker":
            color = (*color[:3], 110)
        if d["kind"] == "brush" and self.brush_style == "Airbrush":
            import random

            for _ in range(width * 2):
                radius = random.random() * width / 2
                angle = random.random() * math.tau
                x = b.x() + radius * math.cos(angle)
                y = b.y() + radius * math.sin(angle)
                draw.point((x, y), fill=color)
            self._cache.pop(layer.id, None)
            return
        if d["kind"] == "brush" and self.brush_style == "Calligraphy":
            for offset in range(-width // 2, width // 2 + 1):
                draw.line(
                    (a.x() + offset, a.y() + offset, b.x() + offset, b.y() + offset),
                    fill=color,
                    width=2,
                )
            self._cache.pop(layer.id, None)
            return
        draw.line((a.x(), a.y(), b.x(), b.y()), fill=color, width=width)
        r = width / 2
        draw.ellipse((b.x() - r, b.y() - r, b.x() + r, b.y() + r), fill=color)
        self._cache.pop(layer.id, None)

    def mouseMoveEvent(self, event):
        pos = self.point(event)
        self.position.emit(f"{round(pos.x())}, {round(pos.y())} px")
        if not self.drag:
            return
        d = self.drag
        start = d["start"]
        kind = d["kind"]
        if kind in ("marquee", "crop", "region", "shape"):
            self.marquee = QRectF(start, pos).normalized()
        elif kind in ("pencil", "brush", "eraser"):
            self.stroke(d["last"], pos)
            d["last"] = pos
        elif kind == "move":
            for l in self.layers():
                x, y, w, h, a = d["originals"][l.id]
                l.x = x + pos.x() - start.x()
                l.y = y + pos.y() - start.y()
        elif kind == "rotate":
            center = d["bounds"].center()
            delta = math.degrees(
                math.atan2(pos.y() - center.y(), pos.x() - center.x())
                - math.atan2(start.y() - center.y(), start.x() - center.x())
            )
            if event.modifiers() & Qt.KeyboardModifier.ShiftModifier:
                delta = round(delta / 15) * 15
            rad = math.radians(delta)
            for l in self.layers():
                x, y, w, h, a = d["originals"][l.id]
                cx = x + w / 2 - center.x()
                cy = y + h / 2 - center.y()
                l.x = center.x() + cx * math.cos(rad) - cy * math.sin(rad) - w / 2
                l.y = center.y() + cx * math.sin(rad) + cy * math.cos(rad) - h / 2
                l.angle = a + delta
        else:
            b = d["bounds"]
            left, top, right, bottom = b.left(), b.top(), b.right(), b.bottom()
            dx, dy = pos.x() - start.x(), pos.y() - start.y()
            if "w" in kind:
                left = min(right - 1, left + dx)
            if "e" in kind:
                right = max(left + 1, right + dx)
            if "n" in kind:
                top = min(bottom - 1, top + dy)
            if "s" in kind:
                bottom = max(top + 1, bottom + dy)
            sx = (right - left) / max(1, b.width())
            sy = (bottom - top) / max(1, b.height())
            if (
                self.aspect_lock
                or event.modifiers() & Qt.KeyboardModifier.ShiftModifier
            ):
                scale = sy if kind in ("n", "s") else sx
                sx = sy = scale
                if "w" in kind:
                    left = b.right() - b.width() * scale
                if "n" in kind:
                    top = b.bottom() - b.height() * scale
            if max(b.width() * sx, b.height() * sy) > 16000:
                return
            for l in self.layers():
                x, y, w, h, a = d["originals"][l.id]
                l.x = left + (x - b.left()) * sx
                l.y = top + (y - b.top()) * sy
                l.width = max(1, w * sx)
                l.height = max(1, h * sy)
        self.update()

    def mouseReleaseEvent(self, event):
        if not self.drag:
            return
        d = self.drag
        kind = d["kind"]
        if kind == "marquee" and self.marquee:
            self.selection = [
                l.id
                for l in self.doc.layers
                if not l.locked
                and l.visible
                and self.marquee.contains(QRectF(*l.bounds()))
            ]
            self.selected.emit()
        elif (
            kind == "region"
            and self.marquee
            and self.marquee.width() > 1
            and self.marquee.height() > 1
        ):
            self.extract_region(self.marquee)
        elif (
            kind == "crop"
            and self.marquee
            and self.marquee.width() > 1
            and self.marquee.height() > 1
        ):
            r = self.marquee.intersected(QRectF(0, 0, self.doc.width, self.doc.height))
            self.doc.crop((r.left(), r.top(), r.right(), r.bottom()))
        elif kind == "shape" and self.marquee:
            r = self.marquee
            draw = ImageDraw.Draw(d["layer"].image)
            color = QColor(d["color"]).getRgb()
            box = (r.left(), r.top(), r.right(), r.bottom())
            fill = color if self.shape_fill else None
            if self.shape == "Ellipse":
                draw.ellipse(box, fill=fill, outline=color, width=self.brush_size)
            elif self.shape == "Line":
                draw.line(
                    (
                        d["start"].x(),
                        d["start"].y(),
                        self.point(event).x(),
                        self.point(event).y(),
                    ),
                    fill=color,
                    width=self.brush_size,
                )
            elif self.shape == "Triangle":
                draw.polygon(
                    [
                        (r.center().x(), r.top()),
                        (r.right(), r.bottom()),
                        (r.left(), r.bottom()),
                    ],
                    fill=fill,
                    outline=color,
                    width=self.brush_size,
                )
            elif self.shape == "Rounded rectangle":
                draw.rounded_rectangle(
                    box,
                    radius=min(r.width(), r.height()) / 5,
                    fill=fill,
                    outline=color,
                    width=self.brush_size,
                )
            else:
                draw.rectangle(box, fill=fill, outline=color, width=self.brush_size)
        if kind in ("pencil", "brush", "shape"):
            layer = d["layer"]
            box = layer.image.getbbox()
            if box:
                layer.image = layer.image.crop(box)
                layer.x = box[0]
                layer.y = box[1]
                layer.width = layer.image.width
                layer.height = layer.image.height
        self.drag = None
        self.marquee = None
        self.refresh()

    def extract_region(self, rect):
        layer = next(
            (
                l
                for l in reversed(self.doc.layers)
                if l.id in self.selection and not l.locked
            ),
            None,
        )
        if layer is None:
            layer = self.hit(rect.center())
        if layer is None or layer.angle or layer.flip_h or layer.flip_v:
            return
        inverse = self.transform(layer).inverted()[0]
        a = inverse.map(rect.topLeft())
        b = inverse.map(rect.bottomRight())
        box = (
            max(0, int(a.x())),
            max(0, int(a.y())),
            min(layer.image.width, int(b.x())),
            min(layer.image.height, int(b.y())),
        )
        if box[2] <= box[0] or box[3] <= box[1]:
            return
        self.doc.checkpoint()
        image = layer.image.crop(box)
        ImageDraw.Draw(layer.image).rectangle(
            (box[0], box[1], box[2] - 1, box[3] - 1), fill=(0, 0, 0, 0)
        )
        sx = layer.width / layer.image.width
        sy = layer.height / layer.image.height
        selection = Layer(
            "Selection",
            image,
            layer.x + box[0] * sx,
            layer.y + box[1] * sy,
            image.width * sx,
            image.height * sy,
        )
        self.doc.layers.append(selection)
        self.selection = [selection.id]
        self.tool = "select"
        self.selected.emit()

    def wheelEvent(self, event):
        if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            self.zoom_requested.emit(10 if event.angleDelta().y() > 0 else -10)
            event.accept()
        else:
            super().wheelEvent(event)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self.selection = []
            self.selected.emit()
            self.update()
            event.accept()
            return
        offsets = {
            Qt.Key.Key_Left: (-1, 0),
            Qt.Key.Key_Right: (1, 0),
            Qt.Key.Key_Up: (0, -1),
            Qt.Key.Key_Down: (0, 1),
        }
        layers = self.layers()
        if event.key() in offsets and layers and not any(l.locked for l in layers):
            self.doc.checkpoint()
            dx, dy = offsets[event.key()]
            factor = 10 if event.modifiers() & Qt.KeyboardModifier.ShiftModifier else 1
            for layer in layers:
                layer.x += dx * factor
                layer.y += dy * factor
            self.refresh()
            event.accept()
            return
        super().keyPressEvent(event)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        self.dropped.emit(
            [u.toLocalFile() for u in event.mimeData().urls() if u.isLocalFile()]
        )
        event.acceptProposedAction()
