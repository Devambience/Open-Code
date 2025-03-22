import os
import json
import re
from PyQt6.QtWidgets import (QPlainTextEdit, QWidget, QTextEdit, QColorDialog)
from PyQt6.QtGui import (QPainter, QColor, QTextFormat, QFont, QSyntaxHighlighter,
                         QTextCharFormat, QKeyEvent, QMouseEvent)
from PyQt6.QtCore import QRect, QSize, Qt, QPoint, QFileSystemWatcher
from PyQt6.QtGui import QTextBlockUserData
from PyQt6.QtSvg import QSvgRenderer  # For SVG rendering

# --- Block user data for storing color code info (for highlighting only) ---
class ColorCodeBlockData(QTextBlockUserData):
    def __init__(self):
        super().__init__()
        self.colors = []  # each item: {'start': int, 'length': int, 'color': QColor}

# --- Gutter (LineNumberArea) widget ---
class LineNumberArea(QWidget):
    def __init__(self, editor):
        super().__init__(editor)
        self.codeEditor = editor

    def sizeHint(self) -> QSize:
        return QSize(self.codeEditor.lineNumberAreaWidth(), 0)

    def paintEvent(self, event):
        self.codeEditor.lineNumberAreaPaintEvent(event)

    def mousePressEvent(self, event: QMouseEvent):
        self.codeEditor.lineNumberAreaMouseEvent(event)

# --- Syntax Highlighter using settings ---
class Highlighter(QSyntaxHighlighter):
    def __init__(self, parent, syntax_settings):
        super().__init__(parent)
        self.rules = []
        # Keywords
        keyword_format = QTextCharFormat()
        keyword_format.setForeground(QColor(syntax_settings.get("keyword_color", "#61AFEF")))
        keywords = ["def", "class", "import", "from", "if", "else", "elif", "while",
                    "for", "return", "in", "try", "except", "with", "as", "self", "True", "False", "None"]
        for word in keywords:
            pattern = r'\b' + word + r'\b'
            self.rules.append((re.compile(pattern), keyword_format))
        # Function names (any word followed by an opening parenthesis)
        func_format = QTextCharFormat()
        func_format.setForeground(QColor("#E5C07B"))
        self.rules.append((re.compile(r'\b[A-Za-z_]\w*(?=\()'), func_format))
        # Strings
        string_format = QTextCharFormat()
        string_format.setForeground(QColor(syntax_settings.get("string_color", "#98C379")))
        self.rules.append((re.compile(r'".*?"'), string_format))
        self.rules.append((re.compile(r"'.*?'"), string_format))
        # Comments
        comment_format = QTextCharFormat()
        comment_format.setForeground(QColor(syntax_settings.get("comment_color", "#5C6370")))
        self.rules.append((re.compile(r'#.*'), comment_format))
        # Numbers
        number_format = QTextCharFormat()
        number_format.setForeground(QColor("#D19A66"))
        self.rules.append((re.compile(r'\b\d+(\.\d+)?\b'), number_format))
        # Color codes – underline them so they are noticeable.
        color_format = QTextCharFormat()
        color_format.setUnderlineStyle(QTextCharFormat.UnderlineStyle.SingleUnderline)
        color_format.setUnderlineColor(QColor("#E06C75"))
        self.color_pattern_hex = re.compile(r'#(?:[0-9a-fA-F]{3}){1,2}\b')
        self.color_pattern_rgb = re.compile(r'rgb\(\s*\d+\s*,\s*\d+\s*,\s*\d+\s*\)')
        self.color_format = color_format

    def highlightBlock(self, text):
        # Apply standard rules.
        for pattern, fmt in self.rules:
            for match in pattern.finditer(text):
                start = match.start()
                length = match.end() - start
                self.setFormat(start, length, fmt)
        # Process color codes and record decoration data (for underline only).
        block = self.currentBlock()
        data = ColorCodeBlockData()
        for pattern in [self.color_pattern_hex, self.color_pattern_rgb]:
            for match in pattern.finditer(text):
                start = match.start()
                length = match.end() - start
                self.setFormat(start, length, self.color_format)
                token = text[start:start+length]
                color = None
                if token.lower().startswith("#"):
                    try:
                        color = QColor(token)
                    except Exception:
                        pass
                elif token.lower().startswith("rgb"):
                    nums = re.findall(r'\d+', token)
                    if len(nums) == 3:
                        color = QColor(int(nums[0]), int(nums[1]), int(nums[2]))
                if color and color.isValid():
                    data.colors.append({'start': start, 'length': length, 'color': color})
        if data.colors:
            block.setUserData(data)

# --- Code Editor Widget with dynamic settings reload ---
class CodeEditor(QPlainTextEdit):
    def __init__(self, settings_path="settings.json", parent=None):
        super().__init__(parent)
        self.settings_path = settings_path
        self.settings = self.load_settings()
        # OneDark-inspired defaults (can be overridden via settings.json)
        self.settings.setdefault("font_family", "Consolas")
        self.settings.setdefault("font_size", 11)
        self.settings.setdefault("tab_width", 4)
        self.settings.setdefault("line_number_bg", "#21252B")
        self.settings.setdefault("line_number_color", "#636D83")
        self.settings.setdefault("current_line_bg", "#2C313C")
        self.settings.setdefault("bracket_match_bg", "#3E4451")
        self.settings.setdefault("selection_bg", "#3E4451")
        self.settings.setdefault("selection_fg", "#FFFFFF")

        self.settings.setdefault("syntax", {
            "keyword_color": "#61AFEF",
            "string_color": "#98C379",
            "comment_color": "#5C6370"
        })

        # Set up font and tab spacing.
        font = QFont(self.settings.get("font_family"), self.settings.get("font_size"))
        self.setFont(font)
        tab_width = self.fontMetrics().horizontalAdvance(' ') * self.settings.get("tab_width")
        self.setTabStopDistance(tab_width)

        # Set up line number area (gutter): shows only line numbers and fold markers.
        self.lineNumberArea = LineNumberArea(self)
        self.blockCountChanged.connect(self.update_line_number_area_width)
        self.updateRequest.connect(self.update_line_number_area)
        self.cursorPositionChanged.connect(self.highlight_current_line)
        self.update_line_number_area_width(0)

        # Set up syntax highlighter.
        self.highlighter = Highlighter(self.document(), self.settings.get("syntax"))

        # Watch settings.json for changes.
        self.settingsWatcher = QFileSystemWatcher([self.settings_path])
        self.settingsWatcher.fileChanged.connect(self.reload_settings)
    
    def update_selection_color(self):
        """Applies the selection color from settings.json"""
        palette = self.palette()
        palette.setColor(self.backgroundRole(), QColor(self.settings.get("background", "#282C34")))
        palette.setColor(QPalette.ColorRole.Highlight, QColor(self.settings.get("selection_bg", "#3E4451")))
        palette.setColor(QPalette.ColorRole.HighlightedText, QColor(self.settings.get("selection_fg", "#FFFFFF")))
        self.setPalette(palette)

    def load_settings(self):
        if os.path.exists(self.settings_path):
            try:
                with open(self.settings_path, "r") as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading settings: {e}")
        return {}

    def reload_settings(self, path):
        # Reload settings from file.
        new_settings = self.load_settings()
        self.settings = new_settings
        # Update font and tab stop.
        font = QFont(self.settings.get("font_family"), self.settings.get("font_size"))
        self.setFont(font)
        tab_width = self.fontMetrics().horizontalAdvance(' ') * self.settings.get("tab_width")
        self.setTabStopDistance(tab_width)
        # Update highlighter.
        self.highlighter.deleteLater()
        self.highlighter = Highlighter(self.document(), self.settings.get("syntax"))
        # Update gutter colors.
        self.update_line_number_area_width(0)
        self.viewport().update()

    def lineNumberAreaWidth(self) -> int:
        # Reserve space for line numbers plus fold marker area.
        digits = len(str(max(1, self.blockCount())))
        num_width = 8 + self.fontMetrics().horizontalAdvance('9') * digits
        return num_width + 16

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
        self.lineNumberArea.setGeometry(QRect(cr.left(), cr.top(), self.lineNumberAreaWidth(), cr.height()))

    def lineNumberAreaPaintEvent(self, event):
        painter = QPainter(self.lineNumberArea)
        painter.fillRect(event.rect(), QColor(self.settings.get("line_number_bg")))
        total_width = self.lineNumberArea.width()
        fold_marker_area = 16  # rightmost area for fold marker
        line_number_width = total_width - fold_marker_area

        block = self.firstVisibleBlock()
        blockNumber = block.blockNumber()
        top = int(self.blockBoundingGeometry(block).translated(self.contentOffset()).top())
        bottom = top + int(self.blockBoundingRect(block).height())

        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                number = str(blockNumber + 1)
                painter.setPen(QColor(self.settings.get("line_number_color")))
                painter.drawText(0, top, line_number_width - 4, self.fontMetrics().height(),
                                 Qt.AlignmentFlag.AlignRight, number)
                text = block.text().strip()
                if "{" in text:
                    marker_rect = QRect(line_number_width, top, fold_marker_area - 4, 12)
                    renderer = QSvgRenderer("icons/arrowdown.svg")
                    from PyQt6.QtCore import QRectF
                    renderer.render(painter, QRectF(marker_rect))
            block = block.next()
            top = bottom
            bottom = top + int(self.blockBoundingRect(block).height())
            blockNumber += 1

    def lineNumberAreaMouseEvent(self, event: QMouseEvent):
        click_y = event.pos().y()
        block = self.firstVisibleBlock()
        top = int(self.blockBoundingGeometry(block).translated(self.contentOffset()).top())
        bottom = top + int(self.blockBoundingRect(block).height())
        while block.isValid() and top <= click_y:
            if block.isVisible() and bottom >= click_y:
                break
            block = block.next()
            top = bottom
            bottom = top + int(self.blockBoundingRect(block).height())
        if not block.isValid():
            return
        total_width = self.lineNumberArea.width()
        fold_marker_area = 16
        line_number_width = total_width - fold_marker_area
        marker_rect = QRect(line_number_width, top, fold_marker_area - 4, 12)
        if marker_rect.contains(event.pos()):
            self.toggle_fold(block)
        else:
            cursor = self.textCursor()
            cursor.setPosition(block.position())
            self.setTextCursor(cursor)

    def toggle_fold(self, block):
        if "{" not in block.text():
            return
        doc = self.document()
        start_block = block
        count = 0
        end_block = start_block
        while end_block.isValid():
            t = end_block.text()
            count += t.count("{")
            count -= t.count("}")
            if count == 0:
                break
            end_block = end_block.next()
        if not end_block.isValid():
            return
        b = start_block.next()
        toggle = not b.isVisible()
        while b.isValid() and b.position() < end_block.position():
            b.setVisible(toggle)
            b = b.next()
        self.viewport().update()

    def highlight_current_line(self):
        extraSelections = []
        if not self.isReadOnly():
            selection = QTextEdit.ExtraSelection()
            lineColor = QColor(self.settings.get("current_line_bg"))
            selection.format.setBackground(lineColor)
            selection.format.setProperty(QTextFormat.Property.FullWidthSelection, True)
            selection.cursor = self.textCursor()
            selection.cursor.clearSelection()
            extraSelections.append(selection)
        self.setExtraSelections(extraSelections)
        self.highlight_matching_brackets()

    def highlight_matching_brackets(self):
        cursor = self.textCursor()
        pos = cursor.position()
        doc = self.document()
        charLeft = doc.characterAt(pos - 1) if pos > 0 else ''
        charRight = doc.characterAt(pos) if pos < doc.characterCount() else ''
        match_char = ''
        direction = 0
        if charLeft and charLeft in "([{":
            match_char = { "(":")", "[":"]", "{":"}" }[charLeft]
            direction = 1
            start_pos = pos - 1
        elif charRight and charRight in ")]}":
            match_char = { ")":"(", "]":"[", "}":"{" }[charRight]
            direction = -1
            start_pos = pos
        else:
            return

        count = 0
        match_pos = -1
        if direction == 1:
            for i in range(start_pos, doc.characterCount()):
                c = doc.characterAt(i)
                if c == charLeft:
                    count += 1
                elif c == match_char:
                    count -= 1
                if count == 0:
                    match_pos = i
                    break
        else:
            for i in range(start_pos, -1, -1):
                c = doc.characterAt(i)
                if c == charRight:
                    count += 1
                elif c == match_char:
                    count -= 1
                if count == 0:
                    match_pos = i
                    break

        if match_pos != -1:
            extraSelections = self.extraSelections()
            selection = QTextEdit.ExtraSelection()
            selection.format.setBackground(QColor(self.settings.get("bracket_match_bg")))
            temp_cursor = self.textCursor()
            temp_cursor.setPosition(match_pos)
            temp_cursor.movePosition(temp_cursor.MoveOperation.NextCharacter, temp_cursor.MoveMode.KeepAnchor)
            selection.cursor = temp_cursor
            extraSelections.append(selection)
            self.setExtraSelections(extraSelections)

    def keyPressEvent(self, event: QKeyEvent):
        # Ctrl+Shift+I triggers code formatting.
        if event.modifiers() == (Qt.KeyboardModifier.ControlModifier | Qt.KeyboardModifier.ShiftModifier) and event.key() == Qt.Key.Key_I:
            self.format_code()
            return
        # Auto-indent after '{'
        if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            cursor = self.textCursor()
            block_text = cursor.block().text()
            indent = re.match(r'\s*', block_text).group()
            extra_indent = ""
            if block_text.rstrip().endswith("{"):
                extra_indent = " " * self.settings.get("tab_width")
                super().keyPressEvent(event)
                self.insertPlainText("\n" + indent + extra_indent)
                cursor = self.textCursor()
                cursor.movePosition(cursor.MoveOperation.End)
                self.setTextCursor(cursor)
                self.insertPlainText("\n" + indent + "}")
                cursor.movePosition(cursor.MoveOperation.Up)
                cursor.movePosition(cursor.MoveOperation.End)
                self.setTextCursor(cursor)
                return
        # Auto bracket completion.
        brackets = {"(":")", "[":"]", "{":"}", "\"":"\"", "'":"'"}
        if event.text() in brackets:
            closing = brackets[event.text()]
            super().keyPressEvent(event)
            self.insertPlainText(closing)
            cursor = self.textCursor()
            cursor.movePosition(cursor.MoveOperation.PreviousCharacter)
            self.setTextCursor(cursor)
            return
        super().keyPressEvent(event)

    def format_code(self):
        code = self.toPlainText()
        lines = code.splitlines()
        formatted_lines = []
        indent_level = 0
        indent_str = " " * self.settings.get("tab_width")
        for line in lines:
            stripped = line.strip()
            if stripped.startswith("}"):
                indent_level = max(indent_level - 1, 0)
            formatted_lines.append((indent_str * indent_level) + stripped)
            if stripped.endswith("{"):
                indent_level += 1
        new_code = "\n".join(formatted_lines)
        self.setPlainText(new_code)

    def mousePressEvent(self, event: QMouseEvent):
        # Check for clicks on inline color codes.
        pos = event.pos()
        cursor = self.cursorForPosition(pos)
        cursor.select(cursor.SelectionType.WordUnderCursor)
        word = cursor.selectedText()
        if re.fullmatch(r'#[0-9a-fA-F]{3,6}', word) or re.fullmatch(r'rgb\(\s*\d+\s*,\s*\d+\s*,\s*\d+\s*\)', word):
            try:
                old_color = QColor(word)
            except Exception:
                old_color = QColor("#ffffff")
            new_color = QColorDialog.getColor(old_color, self, "Pick Color")
            if new_color.isValid():
                cursor.insertText(new_color.name().upper())
            return
        super().mousePressEvent(event)

