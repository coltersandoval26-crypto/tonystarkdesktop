from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import QLabel, QVBoxLayout, QWidget
import psutil


class SystemPanel(QWidget):
    def __init__(self) -> None:
        super().__init__()

        self.cpu_label = QLabel()
        self.ram_label = QLabel()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(8)
        layout.addWidget(self.cpu_label)
        layout.addWidget(self.ram_label)
        layout.addStretch()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.refresh_metrics)
        self.timer.start(1000)
        self.refresh_metrics()

    def refresh_metrics(self) -> None:
        cpu_usage = psutil.cpu_percent(interval=None)
        ram_usage = psutil.virtual_memory().percent

        self.cpu_label.setText(f"CPU Usage: {cpu_usage:.1f}%")
        self.ram_label.setText(f"RAM Usage: {ram_usage:.1f}%")
