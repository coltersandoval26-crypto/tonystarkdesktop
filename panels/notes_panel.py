import os

from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import QTextEdit, QVBoxLayout, QWidget


class NotesPanel(QWidget):
    def __init__(self, notes_path: str) -> None:
        super().__init__()
        self.notes_path = notes_path

        self.editor = QTextEdit()
        self.editor.setPlaceholderText("Write notes here...")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.addWidget(self.editor)

        self._load_notes()

        self.save_timer = QTimer(self)
        self.save_timer.setSingleShot(True)
        self.save_timer.setInterval(500)
        self.save_timer.timeout.connect(self.save_notes)
        self.editor.textChanged.connect(self._queue_save)

    def _load_notes(self) -> None:
        if os.path.exists(self.notes_path):
            with open(self.notes_path, "r", encoding="utf-8") as note_file:
                self.editor.setPlainText(note_file.read())

    def _queue_save(self) -> None:
        self.save_timer.start()

    def save_notes(self) -> None:
        with open(self.notes_path, "w", encoding="utf-8") as note_file:
            note_file.write(self.editor.toPlainText())
