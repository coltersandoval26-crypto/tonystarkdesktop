from PyQt6.QtCore import QEasingCurve, QPropertyAnimation, Qt, QTimer
from PyQt6.QtGui import QColor, QConicalGradient, QPainter, QPen
from PyQt6.QtWidgets import QLabel, QVBoxLayout, QWidget


class ArcReactorWidget(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.setMinimumSize(180, 180)
        self.glow_level = 0.35
        self.rotation = 0

        self.spin_timer = QTimer(self)
        self.spin_timer.timeout.connect(self._tick)
        self.spin_timer.start(40)

    def _tick(self) -> None:
        self.rotation = (self.rotation + 2) % 360
        self.update()

    def pulse(self) -> None:
        self.pulse_anim = QPropertyAnimation(self, b"glowLevel", self)
        self.pulse_anim.setDuration(600)
        self.pulse_anim.setEasingCurve(QEasingCurve.Type.InOutSine)
        self.pulse_anim.setStartValue(0.35)
        self.pulse_anim.setKeyValueAt(0.45, 1.0)
        self.pulse_anim.setEndValue(0.45)
        self.pulse_anim.start()

    def get_glow_level(self) -> float:
        return self.glow_level

    def set_glow_level(self, value: float) -> None:
        self.glow_level = max(0.2, min(1.0, value))
        self.update()

    glowLevel = property(get_glow_level, set_glow_level)

    def paintEvent(self, event) -> None:  # type: ignore[override]
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        center = self.rect().center()
        radius = min(self.width(), self.height()) // 2 - 10

        gradient = QConicalGradient(center, self.rotation)
        gradient.setColorAt(0.0, QColor(0, 234, 255, int(255 * self.glow_level)))
        gradient.setColorAt(0.5, QColor(0, 90, 140, 90))
        gradient.setColorAt(1.0, QColor(0, 234, 255, int(255 * self.glow_level)))

        pen_outer = QPen(gradient, 5)
        painter.setPen(pen_outer)
        painter.drawEllipse(center, radius, radius)

        pen_inner = QPen(QColor(180, 255, 255, int(220 * self.glow_level)), 3)
        painter.setPen(pen_inner)
        painter.drawEllipse(center, radius - 18, radius - 18)

        pen_core = QPen(QColor(0, 234, 255, int(240 * self.glow_level)), 2)
        painter.setPen(pen_core)
        painter.drawEllipse(center, radius - 42, radius - 42)


class ArcReactorPanel(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.setAttribute(Qt.WidgetAttribute.WA_AcceptTouchEvents, True)

        self.reactor = ArcReactorWidget()
        self.status = QLabel("Five-finger touch to ignite core")
        self.status.setObjectName("panelSubtle")
        self.status.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)
        layout.addWidget(self.reactor, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status)

    def event(self, event) -> bool:  # type: ignore[override]
        if event.type() == event.Type.TouchBegin or event.type() == event.Type.TouchUpdate:
            if len(event.points()) >= 5:
                self.reactor.pulse()
                self.status.setText("ARC REACTOR ONLINE")
                return True
        return super().event(event)
