import os
import sys
from typing import List

from PyQt6.QtCore import QEasingCurve, QPoint, QPropertyAnimation, QRect, Qt
from PyQt6.QtGui import QGuiApplication
from PyQt6.QtWidgets import (
    QApplication,
    QFrame,
    QGraphicsDropShadowEffect,
    QHBoxLayout,
    QLabel,
    QMainWindow,
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
        self._apply_glow(26)

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(2, 2, 2, 2)
        layout.setSpacing(0)

        self.header = QWidget(self)
        self.header.setObjectName("panelHeader")
        header_layout = QHBoxLayout(self.header)
        header_layout.setContentsMargins(12, 7, 12, 7)

        title_label = QLabel(self.panel_title)
        title_label.setObjectName("panelTitle")
        header_layout.addWidget(title_label)
        header_layout.addStretch()

        indicator = QLabel("◉")
        indicator.setStyleSheet("color: #00eaff;")
        header_layout.addWidget(indicator)

        layout.addWidget(self.header)
        layout.addWidget(self.content_widget)

    def _apply_glow(self, blur_radius: float) -> None:
        glow = QGraphicsDropShadowEffect(self)
        glow.setBlurRadius(blur_radius)
        glow.setColor(Qt.GlobalColor.cyan)
        glow.setOffset(0, 0)
        self.setGraphicsEffect(glow)

    def _animate_glow(self, target_radius: float) -> None:
        effect = self.graphicsEffect()
        if not isinstance(effect, QGraphicsDropShadowEffect):
            return
        self.glow_animation = QPropertyAnimation(effect, b"blurRadius", self)
        self.glow_animation.setDuration(160)
        self.glow_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        self.glow_animation.setStartValue(effect.blurRadius())
        self.glow_animation.setEndValue(target_radius)
        self.glow_animation.start()

    def _animate_scale_bump(self, up: bool) -> None:
        self.bump_anim = QPropertyAnimation(self, b"windowOpacity", self)
        self.bump_anim.setDuration(140)
        self.bump_anim.setStartValue(1.0)
        self.bump_anim.setEndValue(0.92 if up else 1.0)
        self.bump_anim.start()

    def _in_header(self, pos: QPoint) -> bool:
        return self.header.geometry().contains(pos)

    def toggle_maximize(self) -> None:
        parent = self.parentWidget()
        if parent is None:
            return

        if not self.is_maximized:
            self.restored_geometry = self.geometry()
            target = parent.rect().adjusted(30, 30, -30, -30)
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
            self._animate_glow(42)
            self._animate_scale_bump(True)
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
            self._animate_glow(26)
            self._animate_scale_bump(False)
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

        root = QWidget()
        self.setCentralWidget(root)
        self.setAttribute(Qt.WidgetAttribute.WA_AcceptTouchEvents, True)

        self._build_panels(root)

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
            else:
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
                                            stop:0 rgba(6, 12, 24, 210),
                                            stop:1 rgba(4, 26, 34, 185));
                border: 1px solid rgba(0, 234, 255, 190);
                border-radius: 12px;
            }
            QWidget#panelHeader {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                            stop:0 rgba(0, 234, 255, 34),
                                            stop:1 rgba(0, 130, 255, 20));
                border-bottom: 1px solid rgba(0, 234, 255, 120);
                border-top-left-radius: 11px;
                border-top-right-radius: 11px;
            }
            QLabel#panelTitle {
                color: #00eaff;
                font-size: 14px;
                font-weight: 700;
                letter-spacing: 1px;
            }
            QLabel#panelSubtle {
                color: rgba(165, 248, 255, 180);
                font-size: 12px;
            }
            QTextEdit, QListWidget {
                color: #c3f9ff;
                background: rgba(0, 20, 30, 80);
                border: 1px solid rgba(0, 234, 255, 55);
                border-radius: 8px;
                padding: 6px;
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
