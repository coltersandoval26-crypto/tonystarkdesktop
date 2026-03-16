import os

from PyQt6.QtCore import QFileSystemWatcher
from PyQt6.QtWidgets import QLabel, QListWidget, QVBoxLayout, QWidget


class ProjectsPanel(QWidget):
    def __init__(self, projects_dir: str) -> None:
        super().__init__()
        self.projects_dir = projects_dir

        self.path_label = QLabel(f"Folder: {projects_dir}")
        self.path_label.setWordWrap(True)
        self.files_list = QListWidget()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(6)
        layout.addWidget(self.path_label)
        layout.addWidget(self.files_list)

        self.watcher = QFileSystemWatcher(self)
        self.watcher.addPath(self.projects_dir)
        self.watcher.directoryChanged.connect(self.refresh_files)

        self.refresh_files()

    def refresh_files(self) -> None:
        self.files_list.clear()
        entries = sorted(os.listdir(self.projects_dir))

        if not entries:
            self.files_list.addItem("No project files found.")
            return

        for entry in entries:
            full_path = os.path.join(self.projects_dir, entry)
            prefix = "📁" if os.path.isdir(full_path) else "📄"
            self.files_list.addItem(f"{prefix} {entry}")
