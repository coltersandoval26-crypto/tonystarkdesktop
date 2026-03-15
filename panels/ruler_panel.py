from PyQt6.QtCore import QPoint, QRect, Qt
from PyQt6.QtGui import QColor, QPainter, QPen
from PyQt6.QtWidgets import QLabel, QSlider, QVBoxLayout, QWidget


class RulerWidget(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.length_px = 260
        self.setMinimumHeight(80)

    def set_length(self, px: int) -> None:
        self.length_px = max(160, min(520, px))
        self.update()

    def paintEvent(self, event) -> None:  # type: ignore[override]
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        ruler_rect = QRect(16, 20, self.length_px, 36)
        painter.fillRect(ruler_rect, QColor(8, 26, 36, 180))

        painter.setPen(QPen(QColor(0, 234, 255, 220), 2))
        painter.drawRoundedRect(ruler_rect, 6, 6)

        for i in range(0, self.length_px + 1, 10):
            x = ruler_rect.left() + i
            if i % 50 == 0:
                tick_h = 18
            elif i % 20 == 0:
                tick_h = 12
            else:
                tick_h = 8
            painter.drawLine(QPoint(x, ruler_rect.top()), QPoint(x, ruler_rect.top() + tick_h))


class RulerPanel(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.label = QLabel("Length: 260 px")
        self.label.setObjectName("panelSubtle")

        self.ruler = RulerWidget()
        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setRange(160, 520)
        self.slider.setValue(260)
        self.slider.valueChanged.connect(self._change_length)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.addWidget(self.label)
        layout.addWidget(self.ruler)
        layout.addWidget(self.slider)

    def _change_length(self, value: int) -> None:
        self.ruler.set_length(value)
        self.label.setText(f"Length: {value} px")
