# core/search_bar.py
from PyQt6.QtWidgets import QLineEdit

class SearchBar(QLineEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setPlaceholderText("Search across files...")
