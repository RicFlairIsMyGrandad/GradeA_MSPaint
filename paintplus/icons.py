"""Small original tool illustrations; no proprietary image resources."""

from PySide6.QtCore import Qt, QPointF, QRectF
from PySide6.QtGui import QIcon, QPixmap, QPainter, QPen, QColor, QPolygonF, QFont


def tool_icon(name):
    pix = QPixmap(64, 64)
    pix.fill(Qt.GlobalColor.transparent)
    p = QPainter(pix)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)
    p.scale(2, 2)
    p.setPen(QPen(QColor("#46627e"), 1.4))
    p.setBrush(Qt.BrushStyle.NoBrush)
    if name in ("select", "region"):
        p.setPen(QPen(QColor("#0078d4"), 1.4, Qt.PenStyle.DashLine))
        p.setBrush(QColor("#d9edff"))
        p.drawRect(QRectF(5, 5, 22, 22))
    elif name == "pencil":
        p.setBrush(QColor("#f5c35d"))
        p.drawPolygon(
            QPolygonF(
                [QPointF(6, 22), QPointF(21, 6), QPointF(26, 11), QPointF(11, 27)]
            )
        )
        p.setBrush(QColor("#f5e5c9"))
        p.drawPolygon(QPolygonF([QPointF(6, 22), QPointF(11, 27), QPointF(4, 29)]))
    elif name == "brush":
        p.setBrush(QColor("#e49b43"))
        p.drawPolygon(
            QPolygonF(
                [QPointF(15, 18), QPointF(25, 3), QPointF(29, 7), QPointF(20, 22)]
            )
        )
        p.setBrush(QColor("#0078d4"))
        p.drawEllipse(QRectF(6, 17, 14, 11))
        p.setPen(QPen(QColor("#0078d4"), 3))
        p.drawLine(5, 27, 22, 27)
    elif name == "eraser":
        p.setBrush(QColor("#ef939c"))
        p.drawPolygon(
            QPolygonF(
                [
                    QPointF(5, 22),
                    QPointF(19, 7),
                    QPointF(28, 15),
                    QPointF(15, 28),
                    QPointF(10, 28),
                ]
            )
        )
        p.setBrush(QColor("#fafafa"))
        p.drawPolygon(
            QPolygonF(
                [
                    QPointF(5, 22),
                    QPointF(10, 17),
                    QPointF(20, 23),
                    QPointF(15, 28),
                    QPointF(10, 28),
                ]
            )
        )
    elif name == "fill":
        p.setBrush(QColor("#d5e8fa"))
        p.drawPolygon(
            QPolygonF(
                [QPointF(4, 15), QPointF(14, 5), QPointF(24, 15), QPointF(14, 25)]
            )
        )
        p.drawArc(QRectF(10, 2, 13, 13), 0, 180 * 16)
        p.setBrush(QColor("#0078d4"))
        p.drawEllipse(QRectF(24, 19, 5, 8))
    elif name == "text":
        p.setFont(QFont("DejaVu Serif", 23))
        p.setPen(QColor("#274a78"))
        p.drawText(5, 27, "A")
    elif name == "shape":
        p.setPen(QPen(QColor("#0078d4"), 1.5))
        p.drawRect(QRectF(3, 4, 18, 17))
        p.setBrush(QColor("#f8fbff"))
        p.drawEllipse(QRectF(12, 13, 17, 16))
    elif name == "eyedropper":
        p.setPen(QPen(QColor("#46627e"), 4))
        p.drawLine(7, 25, 22, 10)
        p.setPen(QPen(QColor("#46627e"), 2))
        p.drawLine(16, 8, 25, 17)
        p.setBrush(QColor("#0078d4"))
        p.drawEllipse(QRectF(3, 25, 5, 5))
    elif name == "crop":
        p.setPen(QPen(QColor("#0078d4"), 2))
        p.drawLine(8, 3, 8, 24)
        p.drawLine(8, 24, 29, 24)
        p.drawLine(3, 8, 24, 8)
        p.drawLine(24, 8, 24, 29)
    elif name == "move":
        p.setPen(QPen(QColor("#0078d4"), 1.8))
        p.drawLine(16, 3, 16, 29)
        p.drawLine(3, 16, 29, 16)
        for points in [
            [(12, 7), (16, 3), (20, 7)],
            [(12, 25), (16, 29), (20, 25)],
            [(7, 12), (3, 16), (7, 20)],
            [(25, 12), (29, 16), (25, 20)],
        ]:
            p.drawPolyline(QPolygonF([QPointF(*v) for v in points]))
    else:
        p.setBrush(QColor("#d9edff"))
        p.drawRoundedRect(QRectF(5, 4, 22, 25), 2, 2)
        p.drawLine(10, 10, 22, 10)
        p.drawLine(10, 15, 22, 15)
        p.drawLine(10, 20, 22, 20)
    p.end()
    return QIcon(pix)
