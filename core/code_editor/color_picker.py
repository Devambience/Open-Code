# core/code_editor/color_picker.py
import re
from PyQt6.QtWidgets import QColorDialog
from PyQt6.QtGui import QColor

class ColorPicker:
    @staticmethod
    def pick_color(parent, word):
        if re.fullmatch(r'#[0-9a-fA-F]{3,6}', word) or re.fullmatch(r'rgb\(\s*\d+\s*,\s*\d+\s*,\s*\d+\s*\)', word):
            old_color = QColor(word) if QColor(word).isValid() else QColor("#FFFFFF")
            new_color = QColorDialog.getColor(old_color, parent, "Pick Color")
            if new_color.isValid():
                return new_color.name().upper()
        return None
