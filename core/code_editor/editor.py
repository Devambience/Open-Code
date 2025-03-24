import os
import json
from core.code_editor.completion import CodeCompleter
import re
from PyQt6.QtWidgets import QPlainTextEdit, QTextEdit
from PyQt6.QtGui import (
    QFont, QColor, QTextCursor, QTextFormat, QPainter,
    QTextCharFormat, QKeySequence, QPalette
)
from PyQt6.QtCore import QRect, Qt, pyqtSignal
from core.code_editor.syntax_highlighter import Highlighter
from core.code_editor.line_number_area import LineNumberArea
from core.code_editor.settings_manager import SettingsManager


class CodeEditor(QPlainTextEdit):
    contentChanged = pyqtSignal()
    cursorPositionUpdated = pyqtSignal(int, int)

    def __init__(self, settings_path="assets/settings.json", parent=None):
        super().__init__(parent)
        self.settings_manager = SettingsManager(settings_path)
        self.settings = self.settings_manager.settings
        self.completer = CodeCompleter(self)

        # Initialize editor features
        self.bracket_matching = True
        self.auto_indent = True
        self.bracket_pairs = {
            '(': ')', '[': ']', '{': '}', '"': '"', "'": "'"
        }

        self.setup_editor()
        self.highlighter = Highlighter(self.document(), self.settings.get("syntax"))

        # Connect signals
        self.textChanged.connect(self.on_text_changed)
        self.cursorPositionChanged.connect(self.on_cursor_position_changed)

    def setup_editor(self):
        # Font settings
        font_family = self.settings.get("font_family", "Fira Code")
        font_size = self.settings.get("font_size", 12)
        font = QFont(font_family, font_size)
        font.setStyleHint(QFont.StyleHint.Monospace)
        self.setFont(font)

        # Tab settings
        tab_width = self.fontMetrics().horizontalAdvance(' ') * self.settings.get("tab_width", 4)
        self.setTabStopDistance(tab_width)

        # Line number area
        self.lineNumberArea = LineNumberArea(self)
        self.blockCountChanged.connect(self.update_line_number_area_width)
        self.updateRequest.connect(self.update_line_number_area)
        self.cursorPositionChanged.connect(self.highlight_current_line)
        self.update_line_number_area_width(0)

        # Apply colors
        self.apply_color_scheme()

    def apply_color_scheme(self):
        palette = self.palette()
        bg_color = QColor(self.settings.get("editor_bg", "#282C34"))
        text_color = QColor(self.settings.get("editor_fg", "#ABB2BF"))
        selection_color = QColor(self.settings.get("selection_bg", "#3E4451"))
        
        palette.setColor(QPalette.ColorRole.Base, bg_color)
        palette.setColor(QPalette.ColorRole.Text, text_color)
        palette.setColor(QPalette.ColorRole.Highlight, selection_color)
        self.setPalette(palette)

    def on_text_changed(self):
        self.contentChanged.emit()
        if self.bracket_matching:
            self.handle_bracket_insertion()

    def on_cursor_position_changed(self):
        cursor = self.textCursor()
        line = cursor.blockNumber() + 1
        column = cursor.positionInBlock() + 1
        self.cursorPositionUpdated.emit(line, column)
        
        self.highlight_current_line()
        if self.bracket_matching:
            self.highlight_matching_bracket()

    def highlight_matching_bracket(self):
        if not self.bracket_matching:
            return

        # Clear previous bracket highlights while keeping current line highlight
        current_selections = [sel for sel in self.extraSelections() 
                            if not sel.format.background().color().name() == self.settings.get("bracket_highlight_bg", "#3E4451")]
        
        cursor = self.textCursor()
        block_text = cursor.block().text()
        pos_in_block = cursor.positionInBlock()

        # Check for brackets before and at cursor position
        check_positions = [pos_in_block - 1, pos_in_block] if pos_in_block > 0 else [pos_in_block]
        
        for pos in check_positions:
            if pos < 0 or pos >= len(block_text):
                continue

            char = block_text[pos]
            if char in '([{':
                self.highlight_bracket_pair(cursor.block(), pos, 1)
                break
            elif char in ')]}':
                self.highlight_bracket_pair(cursor.block(), pos, -1)
                break

    def highlight_bracket_pair(self, block, pos, direction):
        pairs = {'(': ')', '[': ']', '{': '}', ')': '(', ']': '[', '}': '{'}
        stack = []
        
        char = block.text()[pos]
        target = pairs.get(char)
        if not target:
            return

        # Create format for highlighting
        format = QTextCharFormat()
        format.setBackground(QColor(self.settings.get("bracket_highlight_bg", "#3E4451")))
        
        # Highlight the opening/closing bracket
        cursor = self.textCursor()
        cursor.setPosition(block.position() + pos)
        cursor.movePosition(QTextCursor.MoveOperation.Right, QTextCursor.MoveMode.KeepAnchor)
        
        selection = QTextEdit.ExtraSelection()
        selection.format = format
        selection.cursor = cursor
        
        current_selections = [sel for sel in self.extraSelections() 
                            if sel.format.background().color().name() != self.settings.get("bracket_highlight_bg", "#3E4451")]
        current_selections.append(selection)

        # Find and highlight matching bracket
        if direction > 0:  # Search forward
            current_block = block
            current_pos = pos + 1
            while current_block.isValid():
                text = current_block.text()
                while current_pos < len(text):
                    if text[current_pos] == char:
                        stack.append(current_pos)
                    elif text[current_pos] == target:
                        if not stack:
                            # Found matching bracket
                            cursor = self.textCursor()
                            cursor.setPosition(current_block.position() + current_pos)
                            cursor.movePosition(QTextCursor.MoveOperation.Right, QTextCursor.MoveMode.KeepAnchor)
                            selection = QTextEdit.ExtraSelection()
                            selection.format = format
                            selection.cursor = cursor
                            current_selections.append(selection)
                            self.setExtraSelections(current_selections)
                            return
                        stack.pop()
                    current_pos += 1
                current_block = current_block.next()
                current_pos = 0
        else:  # Search backward
            current_block = block
            current_pos = pos - 1
            while current_block.isValid():
                text = current_block.text()
                while current_pos >= 0:
                    if text[current_pos] == char:
                        stack.append(current_pos)
                    elif text[current_pos] == target:
                        if not stack:
                            # Found matching bracket
                            cursor = self.textCursor()
                            cursor.setPosition(current_block.position() + current_pos)
                            cursor.movePosition(QTextCursor.MoveOperation.Right, QTextCursor.MoveMode.KeepAnchor)
                            selection = QTextEdit.ExtraSelection()
                            selection.format = format
                            selection.cursor = cursor
                            current_selections.append(selection)
                            self.setExtraSelections(current_selections)
                            return
                        stack.pop()
                    current_pos -= 1
                current_block = current_block.previous()
                if current_block is not None:
                    current_pos = len(current_block.text()) - 1
                else:
                    break

        self.setExtraSelections(current_selections)

    def handle_bracket_insertion(self):
        cursor = self.textCursor()
        if cursor.hasSelection():
            return

        pos = cursor.position()
        if pos > 0:
            current_char = self.document().characterAt(pos - 1)
            if current_char in self.bracket_pairs:
                closing_char = self.bracket_pairs[current_char]
                cursor.insertText(closing_char)
                cursor.movePosition(QTextCursor.MoveOperation.Left)
                self.setTextCursor(cursor)

    def lineNumberAreaWidth(self) -> int:
        digits = len(str(max(1, self.blockCount())))
        num_width = 8 + self.fontMetrics().horizontalAdvance('9') * digits
        return num_width + 20

    def update_line_number_area_width(self, _):
        self.setViewportMargins(self.lineNumberAreaWidth(), 0, 0, 0)

    def update_line_number_area(self, rect, dy):
        if dy:
            self.lineNumberArea.scroll(0, dy)
        else:
            self.lineNumberArea.update(0, rect.y(), self.lineNumberArea.width(), rect.height())
        if rect.contains(self.viewport().rect()):
            self.update_line_number_area_width(0)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        cr = self.contentsRect()
        self.lineNumberArea.setGeometry(
            QRect(cr.left(), cr.top(), self.lineNumberAreaWidth(), cr.height())
        )

    def lineNumberAreaPaintEvent(self, event):
        painter = QPainter(self.lineNumberArea)
        painter.fillRect(event.rect(), QColor(self.settings.get("line_number_bg", "#21252B")))

        block = self.firstVisibleBlock()
        blockNumber = block.blockNumber()
        top = int(self.blockBoundingGeometry(block).translated(self.contentOffset()).top())
        bottom = top + int(self.blockBoundingRect(block).height())

        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                number = str(blockNumber + 1)
                painter.setPen(QColor(self.settings.get("line_number_color", "#636D83")))
                painter.drawText(
                    0, top, self.lineNumberArea.width()-4,
                    self.fontMetrics().height(),
                    Qt.AlignmentFlag.AlignRight,
                    number
                )
            block = block.next()
            top = bottom
            bottom = top + int(self.blockBoundingRect(block).height())
            blockNumber += 1

    def highlight_current_line(self):
        extraSelections = []
        if not self.isReadOnly():
            selection = QTextEdit.ExtraSelection()
            selection.format.setBackground(
                QColor(self.settings.get("current_line_bg", "#2C313C"))
            )
            selection.format.setProperty(QTextFormat.Property.FullWidthSelection, True)
            selection.cursor = self.textCursor()
            selection.cursor.clearSelection()
            extraSelections.append(selection)
        self.setExtraSelections(extraSelections)

    def reload_settings(self, path=None):
        if path:
            self.settings_manager.settings_path = path
        self.settings = self.load_settings()
        self.apply_settings()

    def apply_settings(self):
        font_family = self.settings.get("font_family", "Fira Code")
        font_size = self.settings.get("font_size", 12)
        font = QFont(font_family, font_size)
        self.setFont(font)
        
        tab_width = self.fontMetrics().horizontalAdvance(' ') * self.settings.get("tab_width", 4)
        self.setTabStopDistance(tab_width)
        
        if hasattr(self, 'highlighter'):
            self.highlighter.deleteLater()
        self.highlighter = Highlighter(self.document(), self.settings.get("syntax"))
        
        self.apply_color_scheme()
        self.update_line_number_area_width(0)
        self.viewport().update()

    def load_settings(self):
        if os.path.exists(self.settings_manager.settings_path):
            try:
                with open(self.settings_manager.settings_path, "r") as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading settings: {e}")
        return {}