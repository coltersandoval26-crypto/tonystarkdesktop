import os
import sys
from typing import List, Optional

from PyQt6.QtCore import QEasingCurve, QPoint, QPropertyAnimation, QRect, Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QColor, QGuiApplication, QPainter, QPen
from PyQt6.QtWidgets import (
    QApplication,
    QFrame,
    QGraphicsDropShadowEffect,
    QGraphicsOpacityEffect,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QProgressBar,
    QVBoxLayout,
    QWidget,
)

from panels.ambient_panel import AmbientPanel
from panels.arc_reactor_panel import ArcReactorPanel
from panels.clock_panel import ClockPanel
from panels.diagnostics_panel import DiagnosticsPanel
from panels.notes_panel import NotesPanel
from panels.projects_panel import ProjectsPanel
from panels.ruler_panel import RulerPanel
from panels.system_panel import SystemPanel

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
WORKSPACE_DIR = os.path.join(BASE_DIR, "workspace")
PROJECTS_DIR = os.path.join(WORKSPACE_DIR, "projects")
RUNTIME_DIR = os.path.join(WORKSPACE_DIR, "runtime")
NOTES_FILE = os.path.join(RUNTIME_DIR, "notes.txt")


def ensure_directories() -> None:
    os.makedirs(PROJECTS_DIR, exist_ok=True)
    os.makedirs(RUNTIME_DIR, exist_ok=True)


class WorkspaceCanvas(QWidget):
    def paintEvent(self, event) -> None:  # type: ignore[override]
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.fillRect(self.rect(), QColor("#05060a"))

        grid_pen = QPen(QColor(0, 234, 255, 18), 1)
        painter.setPen(grid_pen)
        step = 34
        for x in range(0, self.width(), step):
            painter.drawLine(x, 0, x, self.height())
        for y in range(0, self.height(), step):
            painter.drawLine(0, y, self.width(), y)

        painter.setPen(QPen(QColor(0, 234, 255, 40), 2))
        painter.drawRect(self.rect().adjusted(9, 9, -9, -9))




class BiometricHandWidget(QWidget):
    finger_pressed = pyqtSignal(int)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("biometricHand")
        self.setFixedSize(320, 360)

        self.palm_core = QLabel("PALM")
        self.palm_core.setObjectName("palmCore")
        self.palm_core.setParent(self)
        self.palm_core.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.finger_buttons: list[QPushButton] = []
        for index in range(5):
            button = QPushButton(str(index + 1), self)
            button.setObjectName("fingerTarget")
            button.setCursor(Qt.CursorShape.PointingHandCursor)
            button.clicked.connect(lambda _checked=False, i=index: self.finger_pressed.emit(i))
            self.finger_buttons.append(button)

        self._layout_targets()

    def resizeEvent(self, event) -> None:  # type: ignore[override]
        super().resizeEvent(event)
        self._layout_targets()

    def _layout_targets(self) -> None:
        points = [
            (38, 66),   # thumb
            (96, 24),   # index
            (146, 14),  # middle
            (196, 24),  # ring
            (246, 52),  # pinky
        ]
        for button, (x, y) in zip(self.finger_buttons, points):
            button.setGeometry(x, y, 38, 38)

        self.palm_core.setGeometry(90, 120, 140, 176)

    def paintEvent(self, event) -> None:  # type: ignore[override]
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        painter.setBrush(QColor(0, 234, 255, 24))
        painter.setPen(QPen(QColor(0, 234, 255, 120), 2))

        painter.drawRoundedRect(92, 116, 136, 180, 58, 58)
        painter.drawRoundedRect(38, 90, 38, 118, 16, 16)
        painter.drawRoundedRect(102, 42, 30, 88, 15, 15)
        painter.drawRoundedRect(144, 32, 30, 96, 15, 15)
        painter.drawRoundedRect(186, 42, 30, 88, 15, 15)
        painter.drawRoundedRect(228, 74, 30, 74, 15, 15)

class HandprintUnlockOverlay(QWidget):
    unlocked = pyqtSignal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("unlockOverlay")
        self.setAttribute(Qt.WidgetAttribute.WA_AcceptTouchEvents, True)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

        self.armed = False
        self.progress = 0
        self.unlocked_once = False
        self.finger_hits: set[int] = set()

        self.title = QLabel("BIOMETRIC START")
        self.title.setObjectName("unlockTitle")

        self.subtitle = QLabel("Tap each finger target (1–5) or place hand (4+ touch points) to initialize")
        self.subtitle.setObjectName("unlockSubtle")
        self.subtitle.setWordWrap(True)
        self.subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.hand_widget = BiometricHandWidget()
        self.hand_widget.finger_pressed.connect(self._on_finger_pressed)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(False)

        self.hint = QLabel("Quick start: tap all 5 finger targets")
        self.hint.setObjectName("unlockHint")
        self.hint.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.demo_button = QPushButton("Skip Scan (Instant Unlock)")
        self.demo_button.setObjectName("unlockButton")
        self.demo_button.clicked.connect(self._trigger_demo_unlock)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        container = QWidget()
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(14)
        container_layout.addStretch()
        container_layout.addWidget(self.title, alignment=Qt.AlignmentFlag.AlignCenter)
        container_layout.addWidget(self.subtitle, alignment=Qt.AlignmentFlag.AlignCenter)
        container_layout.addWidget(self.hand_widget, alignment=Qt.AlignmentFlag.AlignCenter)
        container_layout.addWidget(self.progress_bar, alignment=Qt.AlignmentFlag.AlignCenter)
        container_layout.addWidget(self.hint, alignment=Qt.AlignmentFlag.AlignCenter)
        container_layout.addWidget(self.demo_button, alignment=Qt.AlignmentFlag.AlignCenter)
        container_layout.addStretch()
        container.setMaximumWidth(720)

        layout.addWidget(container, alignment=Qt.AlignmentFlag.AlignCenter)

        self.hold_timer = QTimer(self)
        self.hold_timer.timeout.connect(self._tick_progress)
        self.hold_timer.setInterval(55)

        self.decay_timer = QTimer(self)
        self.decay_timer.setInterval(50)
        self.decay_timer.timeout.connect(self._decay_progress)

    def _unlock_once(self, message: str) -> None:
        if self.unlocked_once:
            return
        self.unlocked_once = True
        self.hold_timer.stop()
        self.decay_timer.stop()
        self.progress = 100
        self.progress_bar.setValue(100)
        self.subtitle.setText(message)
        self.unlocked.emit()

    def _tick_progress(self) -> None:
        self.progress = min(100, self.progress + 10)
        self.progress_bar.setValue(self.progress)
        if self.progress >= 100:
            self._unlock_once("Identity confirmed. Loading tactical workspace...")


    def _decay_progress(self) -> None:
        if self.armed:
            return
        if self.progress <= 0:
            self.decay_timer.stop()
            return
        self.progress = max(0, self.progress - 3)
        self.progress_bar.setValue(self.progress)

    def _on_finger_pressed(self, finger_index: int) -> None:
        self.finger_hits.add(finger_index)
        self.hint.setText(f"Finger targets touched: {len(self.finger_hits)}/5")
        if len(self.finger_hits) >= 5:
            self._unlock_once("Finger map confirmed. Loading tactical workspace...")

    def _trigger_demo_unlock(self) -> None:
        self._unlock_once("Demo unlock initiated. Loading tactical workspace...")

    def _start_arming(self) -> None:
        if self.armed:
            return
        self.armed = True
        self.decay_timer.stop()
        self.hold_timer.start()
        self.hint.setText("Scanning... keep your hand steady")

    def _stop_arming(self) -> None:
        if not self.armed:
            return
        self.armed = False
        self.hold_timer.stop()
        self.hint.setText("Release detected. Progress will slowly fade — continue holding to unlock")
        self.decay_timer.start()

    def mousePressEvent(self, event) -> None:  # type: ignore[override]
        if event.button() == Qt.MouseButton.LeftButton and self.hand_widget.geometry().contains(event.position().toPoint()):
            self.hint.setText("Tap the numbered finger targets for guided unlock")
            event.accept()
            return
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event) -> None:  # type: ignore[override]
        super().mouseReleaseEvent(event)

    def event(self, event) -> bool:  # type: ignore[override]
        if event.type() in (event.Type.TouchBegin, event.Type.TouchUpdate):
            touches = len(event.points())
            if touches >= 4:
                self.subtitle.setText("Hand contact detected. Scanning...")
                self._start_arming()
                return True
            self._stop_arming()

        if event.type() in (event.Type.TouchEnd, event.Type.TouchCancel):
            self._stop_arming()

        return super().event(event)


class HudPanel(QFrame):
    def __init__(self, title: str, content_widget: QWidget, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.panel_title = title
        self.content_widget = content_widget
        self.dragging = False
        self.drag_offset = QPoint()
        self.restored_geometry = QRect()
        self.is_maximized = False
        self.scale_factor = 1.0

        self.setObjectName("hudPanel")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setMinimumSize(260, 200)
        self.resize(360, 260)
        self.setMouseTracking(True)
        self.grabGesture(Qt.GestureType.PinchGesture)

        self._build_ui()
        self._apply_glow(28)

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(2, 2, 2, 2)
        layout.setSpacing(0)

        self.header = QWidget(self)
        self.header.setObjectName("panelHeader")
        header_layout = QHBoxLayout(self.header)
        header_layout.setContentsMargins(12, 7, 12, 7)

        left_tag = QLabel("▣")
        left_tag.setObjectName("panelSubtle")
        title_label = QLabel(self.panel_title)
        title_label.setObjectName("panelTitle")
        right_tag = QLabel("◉")
        right_tag.setObjectName("panelLiveDot")

        header_layout.addWidget(left_tag)
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        header_layout.addWidget(right_tag)

        layout.addWidget(self.header)
        layout.addWidget(self.content_widget)

    def _apply_glow(self, blur_radius: float) -> None:
        glow = QGraphicsDropShadowEffect(self)
        glow.setBlurRadius(blur_radius)
        glow.setColor(QColor(0, 234, 255, 170))
        glow.setOffset(0, 0)
        self.setGraphicsEffect(glow)

    def _animate_glow(self, target_radius: float) -> None:
        effect = self.graphicsEffect()
        if not isinstance(effect, QGraphicsDropShadowEffect):
            return
        self.glow_animation = QPropertyAnimation(effect, b"blurRadius", self)
        self.glow_animation.setDuration(170)
        self.glow_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        self.glow_animation.setStartValue(effect.blurRadius())
        self.glow_animation.setEndValue(target_radius)
        self.glow_animation.start()

    def _in_header(self, pos: QPoint) -> bool:
        return self.header.geometry().contains(pos)

    def toggle_maximize(self) -> None:
        parent = self.parentWidget()
        if parent is None:
            return

        if not self.is_maximized:
            self.restored_geometry = self.geometry()
            target = parent.rect().adjusted(24, 24, -24, -24)
            self.is_maximized = True
        else:
            target = self.restored_geometry
            self.is_maximized = False

        self.anim = QPropertyAnimation(self, b"geometry", self)
        self.anim.setDuration(220)
        self.anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        self.anim.setStartValue(self.geometry())
        self.anim.setEndValue(target)
        self.anim.start()

    def scale_panel(self, factor_delta: float) -> None:
        new_factor = max(0.85, min(1.3, self.scale_factor * factor_delta))
        factor = new_factor / self.scale_factor
        self.scale_factor = new_factor

        geo = self.geometry()
        new_w = int(geo.width() * factor)
        new_h = int(geo.height() * factor)
        center = geo.center()
        self.setGeometry(QRect(center.x() - new_w // 2, center.y() - new_h // 2, new_w, new_h))

    def mousePressEvent(self, event) -> None:  # type: ignore[override]
        if event.button() == Qt.MouseButton.LeftButton and self._in_header(event.position().toPoint()):
            self.dragging = True
            self.drag_offset = event.position().toPoint()
            self.raise_()
            self._animate_glow(44)
            event.accept()
            return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event) -> None:  # type: ignore[override]
        if self.dragging:
            parent_pos = self.mapToParent(event.position().toPoint() - self.drag_offset)
            self.move(parent_pos)
            event.accept()
            return
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event) -> None:  # type: ignore[override]
        if event.button() == Qt.MouseButton.LeftButton and self.dragging:
            self.dragging = False
            self._animate_glow(28)
            event.accept()
            return
        super().mouseReleaseEvent(event)

    def mouseDoubleClickEvent(self, event) -> None:  # type: ignore[override]
        if event.button() == Qt.MouseButton.LeftButton and self._in_header(event.position().toPoint()):
            self.toggle_maximize()
            event.accept()
            return
        super().mouseDoubleClickEvent(event)

    def event(self, event) -> bool:  # type: ignore[override]
        if event.type() == event.Type.Gesture:
            pinch = event.gesture(Qt.GestureType.PinchGesture)
            if pinch:
                self.scale_panel(1.02 if pinch.scaleFactor() > 1.0 else 0.98)
                return True
        return super().event(event)


class StarkDesktop(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        ensure_directories()

        self.setWindowTitle("Tony Stark Desktop")
        self.setStyleSheet(self._stylesheet())
        self.workspace_dragging = False
        self.touch_last_center: QPoint | None = None
        self.panels: List[HudPanel] = []

        root = WorkspaceCanvas()
        self.setCentralWidget(root)
        self.setAttribute(Qt.WidgetAttribute.WA_AcceptTouchEvents, True)

        self._build_panels(root)
        for panel in self.panels:
            panel.hide()

        self.unlock_overlay: Optional[HandprintUnlockOverlay] = HandprintUnlockOverlay(root)
        self.unlock_overlay.unlocked.connect(self._unlock_workspace)
        self.unlock_overlay.setGeometry(root.rect())
        self.unlock_overlay.show()

    def resizeEvent(self, event) -> None:  # type: ignore[override]
        super().resizeEvent(event)
        if self.unlock_overlay is not None:
            try:
                self.unlock_overlay.setGeometry(self.centralWidget().rect())
            except RuntimeError:
                self.unlock_overlay = None

    def _unlock_workspace(self) -> None:
        for panel in self.panels:
            panel.show()

        if self.unlock_overlay is None:
            return

        self.unlock_fx = QGraphicsOpacityEffect(self.unlock_overlay)
        self.unlock_overlay.setGraphicsEffect(self.unlock_fx)
        self.unlock_anim = QPropertyAnimation(self.unlock_fx, b"opacity", self)
        self.unlock_anim.setDuration(420)
        self.unlock_anim.setStartValue(1.0)
        self.unlock_anim.setEndValue(0.0)
        self.unlock_anim.finished.connect(self._finalize_unlock_overlay)
        self.unlock_anim.start()

    def _finalize_unlock_overlay(self) -> None:
        if self.unlock_overlay is None:
            return
        self.unlock_overlay.hide()
        self.unlock_overlay.deleteLater()
        self.unlock_overlay = None

    def _build_panels(self, parent: QWidget) -> None:
        panel_specs = [
            ("System Panel", SystemPanel(), QPoint(40, 50)),
            ("Notes Panel", NotesPanel(NOTES_FILE), QPoint(430, 50)),
            ("Project Panel", ProjectsPanel(PROJECTS_DIR), QPoint(820, 50)),
            ("Diagnostics Panel", DiagnosticsPanel(), QPoint(1210, 50)),
            ("Clock Panel", ClockPanel(), QPoint(40, 360)),
            ("Arc Reactor", ArcReactorPanel(), QPoint(430, 360)),
            ("Field Visualizer", AmbientPanel(), QPoint(820, 360)),
            ("Ruler Panel", RulerPanel(), QPoint(1210, 360)),
        ]

        for title, content, position in panel_specs:
            panel = HudPanel(title, content, parent)
            panel.move(position)
            panel.show()
            self.panels.append(panel)

    def keyPressEvent(self, event) -> None:  # type: ignore[override]
        if event.key() == Qt.Key.Key_Escape:
            if self.isFullScreen():
                self.showNormal()
            return

        if event.modifiers() == Qt.KeyboardModifier.ControlModifier and event.key() == Qt.Key.Key_Q:
            self.close()
            return

        super().keyPressEvent(event)

    def event(self, event) -> bool:  # type: ignore[override]
        if event.type() == event.Type.TouchBegin:
            points = event.points()
            if len(points) >= 2:
                self.workspace_dragging = True
                p1, p2 = points[0].position(), points[1].position()
                self.touch_last_center = QPoint(int((p1.x() + p2.x()) / 2), int((p1.y() + p2.y()) / 2))
                return True

        if event.type() == event.Type.TouchUpdate and self.workspace_dragging:
            points = event.points()
            if len(points) >= 2 and self.touch_last_center is not None:
                p1, p2 = points[0].position(), points[1].position()
                center = QPoint(int((p1.x() + p2.x()) / 2), int((p1.y() + p2.y()) / 2))
                delta = center - self.touch_last_center
                for panel in self.panels:
                    panel.move(panel.pos() + delta)
                self.touch_last_center = center
                return True

        if event.type() in (event.Type.TouchEnd, event.Type.TouchCancel):
            self.workspace_dragging = False
            self.touch_last_center = None

        return super().event(event)

    @staticmethod
    def _stylesheet() -> str:
        return """
            QMainWindow, QWidget {
                background-color: #05060a;
                color: #dcfaff;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QFrame#hudPanel {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                            stop:0 rgba(8, 16, 30, 216),
                                            stop:1 rgba(3, 27, 35, 192));
                border: 1px solid rgba(0, 234, 255, 175);
                border-radius: 12px;
            }
            QWidget#panelHeader {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                            stop:0 rgba(0, 234, 255, 38),
                                            stop:1 rgba(0, 132, 255, 19));
                border-bottom: 1px solid rgba(0, 234, 255, 130);
                border-top-left-radius: 11px;
                border-top-right-radius: 11px;
            }
            QLabel#panelTitle {
                color: #00eaff;
                font-size: 14px;
                font-weight: 700;
                letter-spacing: 1px;
            }
            QLabel#panelLiveDot {
                color: rgba(0, 234, 255, 210);
                font-size: 12px;
            }
            QLabel#panelSubtle {
                color: rgba(168, 250, 255, 190);
                font-size: 12px;
            }
            QTextEdit, QListWidget {
                color: #c3f9ff;
                background: rgba(0, 20, 30, 90);
                border: 1px solid rgba(0, 234, 255, 65);
                border-radius: 8px;
                padding: 6px;
            }
            QProgressBar {
                border: 1px solid rgba(0, 234, 255, 120);
                border-radius: 6px;
                background: rgba(0, 15, 22, 180);
                min-width: 320px;
                max-width: 320px;
                min-height: 12px;
            }
            QProgressBar::chunk {
                border-radius: 5px;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                            stop:0 #00eaff,
                                            stop:1 #7fffff);
            }
            QSlider::groove:horizontal {
                height: 6px;
                background: rgba(0, 234, 255, 45);
                border-radius: 3px;
            }
            QSlider::handle:horizontal {
                width: 14px;
                margin: -4px 0;
                background: #00eaff;
                border-radius: 7px;
            }
            QWidget#unlockOverlay {
                background: qradialgradient(cx:0.5, cy:0.5, radius:0.9,
                                            fx:0.5, fy:0.5,
                                            stop:0 rgba(3, 24, 32, 225),
                                            stop:1 rgba(0, 0, 0, 238));
            }
            QLabel#unlockTitle {
                color: #00eaff;
                font-size: 30px;
                font-weight: 700;
                letter-spacing: 3px;
            }
            QLabel#unlockSubtle {
                color: rgba(179, 250, 255, 200);
                font-size: 13px;
            }
            QLabel#unlockHint {
                color: rgba(220, 255, 255, 180);
                font-size: 12px;
            }
            QPushButton#unlockButton {
                color: #ccfbff;
                background: rgba(0, 234, 255, 30);
                border: 1px solid rgba(0, 234, 255, 120);
                border-radius: 8px;
                padding: 8px 16px;
                font-weight: 600;
            }
            QPushButton#unlockButton:hover {
                background: rgba(0, 234, 255, 55);
            }
            QWidget#biometricHand {
                background: rgba(0, 0, 0, 0);
            }
            QLabel#palmCore {
                border: 1px solid rgba(0, 234, 255, 120);
                background: rgba(0, 234, 255, 16);
                border-radius: 42px;
                color: rgba(193, 252, 255, 170);
                font-size: 12px;
                font-weight: 600;
                letter-spacing: 1px;
            }
            QPushButton#fingerTarget {
                border: 1px solid rgba(0, 234, 255, 180);
                background: rgba(0, 234, 255, 30);
                color: #dcfeff;
                border-radius: 19px;
                font-weight: 700;
            }
            QPushButton#fingerTarget:hover {
                background: rgba(0, 234, 255, 58);
            }
            QPushButton#fingerTarget:pressed {
                background: rgba(120, 255, 255, 120);
            }
        """


def main() -> None:
    app = QApplication(sys.argv)
    app.setAttribute(Qt.ApplicationAttribute.AA_SynthesizeTouchForUnhandledMouseEvents, True)
    app.setAttribute(Qt.ApplicationAttribute.AA_SynthesizeMouseForUnhandledTouchEvents, True)

    window = StarkDesktop()
    screen_geo = QGuiApplication.primaryScreen().availableGeometry()
    window.resize(screen_geo.width(), screen_geo.height())
    window.showFullScreen()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
