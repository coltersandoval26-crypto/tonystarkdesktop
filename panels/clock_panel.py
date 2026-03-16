from datetime import datetime

from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtWidgets import QLabel, QVBoxLayout, QWidget


class ClockPanel(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.time_label = QLabel()
        self.date_label = QLabel()

        self.time_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.date_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.time_label.setStyleSheet("font-size: 34px; font-weight: 700; color: #d6fdff;")
        self.date_label.setObjectName("panelSubtle")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 12, 10, 12)
        layout.addWidget(self.time_label)
        layout.addWidget(self.date_label)
        layout.addStretch()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self._update_time)
        self.timer.start(1000)
        self._update_time()

    def _update_time(self) -> None:
        now = datetime.now()
        self.time_label.setText(now.strftime("%H:%M:%S"))
        self.date_label.setText(now.strftime("%A • %d %B %Y"))
