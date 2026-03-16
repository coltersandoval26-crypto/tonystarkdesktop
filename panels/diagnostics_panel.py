import platform

import psutil
from PyQt6.QtWidgets import QLabel, QVBoxLayout, QWidget


class DiagnosticsPanel(QWidget):
    def __init__(self) -> None:
        super().__init__()

        os_name = platform.platform()
        cpu_name = platform.processor() or "Unknown CPU"
        ram_total_gb = psutil.virtual_memory().total / (1024**3)

        details = [
            f"OS: {os_name}",
            f"CPU: {cpu_name}",
            f"RAM: {ram_total_gb:.2f} GB",
        ]

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(8)

        for line in details:
            layout.addWidget(QLabel(line))

        layout.addStretch()
