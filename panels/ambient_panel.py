from PyQt6.QtCore import QTimer
from PyQt6.QtGui import QColor, QPainter, QPainterPath, QPen
from PyQt6.QtWidgets import QLabel, QVBoxLayout, QWidget
import math


class WaveformWidget(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.phase = 0.0
        self.setMinimumHeight(120)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self._animate)
        self.timer.start(35)

    def _animate(self) -> None:
        self.phase += 0.12
        self.update()

    def paintEvent(self, event) -> None:  # type: ignore[override]
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w = self.width()
        h = self.height()
        mid = h / 2

        for band, amp, alpha in [(1.0, 18, 170), (1.8, 10, 110), (2.8, 6, 80)]:
            path = QPainterPath()
            path.moveTo(0, mid)
            for x in range(w + 1):
                y = mid + math.sin((x / 45.0) * band + self.phase) * amp
                path.lineTo(x, y)
            painter.setPen(QPen(QColor(0, 234, 255, alpha), 2))
            painter.drawPath(path)


class AmbientPanel(QWidget):
    def __init__(self) -> None:
        super().__init__()
        label = QLabel("Aesthetic Signal Field")
        label.setObjectName("panelSubtle")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.addWidget(label)
        layout.addWidget(WaveformWidget())
