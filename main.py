import sys
import os
import json
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QLineEdit, QTabWidget,
    QSplitter, QWidget, QFileDialog, QMessageBox, QPushButton, QHBoxLayout, QTabBar
)
from PyQt6.QtGui import QPalette, QColor, QAction, QIcon
from PyQt6.QtCore import QDir, Qt
from menu import create_menu_bar
from terminal import Terminal
from code_editor import CodeEditor
from file_explorer import FileExplorer

class CodeIDE(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Open Code")
        self.resize(1200, 800)
        
        # Track open files and their paths
        self.open_files = {}
        
        # Set a global style (if you have one in your menu or elsewhere)
        self.setStyleSheet(self.get_stylesheet())
        
        # Set the menu bar from menu.py
        self.setMenuBar(create_menu_bar(self))

        # Enable drag-and-drop
        self.setAcceptDrops(True)

        # Main layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(10, 10, 10, 10)

        # Search bar
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search across files...")
        self.search_bar.returnPressed.connect(self.search_in_files)
        self.search_bar.setStyleSheet("""
            QLineEdit {
                padding: 6px;
                border: 1px solid #444;
                border-radius: 4px;
                background-color: #333;
                color: #EEE;
            }
            QLineEdit:focus {
                border: 1px solid #66afe9;
            }
        """)
        self.main_layout.addWidget(self.search_bar)

        # Splitter for layout (Horizontal: file explorer | editor/terminal)
        self.splitter = QSplitter(Qt.Orientation.Horizontal)

        # File explorer (using custom FileExplorer widget)
        self.file_tree = FileExplorer()  # No parent needed; added to splitter
        self.splitter.addWidget(self.file_tree)

        # Code editor with tabs (using CodeEditor widget)
        self.code_tabs = QTabWidget()
        self.code_tabs.setMovable(True)  # Make tabs draggable/reorderable
        # Disable default close buttons since we add custom ones in open_file_in_editor
        self.code_tabs.setTabsClosable(False)

        # Terminal widget
        self.terminal = Terminal()
        self.terminal.commandEntered.connect(self.on_terminal_command)

        # Vertical splitter for editor and terminal
        self.code_splitter = QSplitter(Qt.Orientation.Vertical)
        self.code_splitter.addWidget(self.code_tabs)
        self.code_splitter.addWidget(self.terminal)
        self.splitter.addWidget(self.code_splitter)

        # Set splitter sizes (240px for file explorer, rest for code area)
        self.splitter.setSizes([240, 960])
        self.main_layout.addWidget(self.splitter)

        # Apply dark mode palette (or use your stylesheet)
        self.set_dark_mode()
        
        self.log_to_terminal("IDE initialized and ready!")
    
    def get_stylesheet(self):
        """Return a basic QSS for a modern look."""
        return """
        QWidget {
            background-color: #2E2E2E;
            color: #EEE;
            font-family: "Segoe UI", sans-serif;
            font-size: 12pt;
        }
        QTabBar::tab {
            background: #3C3F41;
            border: 1px solid #555;
            border-bottom-color: #2E2E2E;
            border-top-left-radius: 4px;
            border-top-right-radius: 4px;
            padding: 5px 10px;
            margin-right: 2px;
        }
        QTabBar::tab:selected {
            background: #2E2E2E;
            border-bottom-color: #2E2E2E;
        }
        QTabBar::tab:hover {
            background: #353A40;
        }
        QPushButton {
            background-color: transparent;
            border: none;
        }
        QPushButton:hover {
            background-color: rgba(255, 0, 0, 80);
        }
        QSplitter::handle {
            background: #444;
        }
        QTextEdit {
            background-color: #1E1E1E;
            color: #CCCCCC;
            font-family: "Consolas", "Courier New", monospace;
        }
        """

    def open_file_in_editor(self, filename, content):
        """Open the file content in a new tab with a custom close button."""
        # If the file is already open, switch to that tab
        for i in range(self.code_tabs.count()):
            if self.code_tabs.tabText(i) == filename:
                self.code_tabs.setCurrentIndex(i)
                return
        
        # Create a new CodeEditor instance for the file
        editor = CodeEditor("settings.json", self)
        editor.setPlainText(content)
        
        # Add the editor to the tabs and get the new tab index
        index = self.code_tabs.addTab(editor, filename)
        
        # Create a custom close button using a round QPushButton with an SVG icon
        close_button = QPushButton()
        close_button.setIcon(QIcon("icons/cross.svg"))  # Ensure the SVG exists
        close_button.setFixedSize(18, 18)
        close_button.setStyleSheet(
            """
            QPushButton {
                border: none;
                background-color: transparent;
                border-radius: 9px;
            }
            QPushButton:hover {
                background-color: rgba(255, 0, 0, 100);
            }
            """
        )
        close_button.clicked.connect(lambda: self.close_tab(index))
        
        # Use the QTabBar to set the custom close button on the right side of the tab
        self.code_tabs.tabBar().setTabButton(index, QTabBar.ButtonPosition.RightSide, close_button)
        
        self.code_tabs.setCurrentIndex(index)
        self.open_files[index] = filename

    def toggle_auto_save(self):
        """Toggle auto-save functionality."""
        self.auto_save_enabled = not getattr(self, 'auto_save_enabled', False)
        if self.auto_save_enabled:
            self.log_to_terminal("Auto Save enabled.")
            # Optionally, start a timer for periodic saves.
        else:
            self.log_to_terminal("Auto Save disabled.")
            # Stop the auto-save timer if running.

    def set_dark_mode(self):
        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window, QColor(30, 30, 30))
        palette.setColor(QPalette.ColorRole.WindowText, Qt.GlobalColor.white)
        palette.setColor(QPalette.ColorRole.Base, QColor(45, 45, 45))
        palette.setColor(QPalette.ColorRole.Text, Qt.GlobalColor.white)
        palette.setColor(QPalette.ColorRole.Button, QColor(53, 53, 53))
        palette.setColor(QPalette.ColorRole.ButtonText, Qt.GlobalColor.white)
        palette.setColor(QPalette.ColorRole.Highlight, QColor(42, 130, 218))
        palette.setColor(QPalette.ColorRole.HighlightedText, Qt.GlobalColor.black)
        self.setPalette(palette)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def open_settings(self):
        settings_path = "settings.json"
        if not os.path.exists(settings_path):
            default_settings = {
                "font_family": "Consolas",
                "font_size": 10,
                "tab_width": 4,
                "line_number_bg": "#2B2B2B",
                "line_number_color": "#858585",
                "current_line_bg": "#323232",
                "bracket_match_bg": "#404040",
                "syntax": {
                    "keyword_color": "#0000FF",
                    "string_color": "#008000",
                    "comment_color": "#808080"
                }
            }
            with open(settings_path, "w") as f:
                json.dump(default_settings, f, indent=4)
        with open(settings_path, "r") as f:
            content = f.read()
        
        # Create a custom container for settings.json that includes a Cut button
        editor = CodeEditor(settings_path, self)
        editor.setPlainText(content)
        
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Create a simple toolbar with a Cut button
        toolbar = QWidget()
        toolbar_layout = QHBoxLayout(toolbar)
        toolbar_layout.setContentsMargins(0, 0, 0, 0)
        cut_button = QPushButton("Cut")
        cut_button.setIcon(QIcon("icons/cross.svg"))  # Provide an appropriate icon
        cut_button.clicked.connect(editor.cut)
        toolbar_layout.addWidget(cut_button)
        toolbar_layout.addStretch()
        layout.addWidget(toolbar)
        layout.addWidget(editor)
        
        self.code_tabs.addTab(container, "settings.json")
        self.open_files[self.code_tabs.indexOf(container)] = settings_path

    def dropEvent(self, event):
        for url in event.mimeData().urls():
            path = url.toLocalFile()
            if QDir(path).exists():
                from file_explorer import CustomFileModel  # Import if needed
                self.file_tree.file_model = CustomFileModel(path)
                self.file_tree.setModel(self.file_tree.file_model)
                self.log_to_terminal(f"Opened directory: {path}")
            else:
                self.open_file_with_path(path)

    def open_file_from_tree(self, index):
        file_path = self.file_tree.file_model.filePath(index)
        if not self.file_tree.file_model.isDir(index):
            self.open_file_with_path(file_path)

    def open_file_with_path(self, file_path):
        for i in range(self.code_tabs.count()):
            if file_path == self.open_files.get(i):
                self.code_tabs.setCurrentIndex(i)
                return
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            editor = CodeEditor("settings.json", self)
            editor.setPlainText(content)
            tab_name = os.path.basename(file_path)
            index = self.code_tabs.addTab(editor, tab_name)
            self.open_files[index] = file_path
            self.code_tabs.setCurrentIndex(index)
            self.log_to_terminal(f"Opened file: {file_path}")
        except Exception as e:
            self.log_to_terminal(f"Error opening file: {str(e)}")
            QMessageBox.critical(self, "Error", f"Could not open file: {str(e)}")

    def close_tab(self, index):
        editor = self.code_tabs.widget(index)
        if hasattr(editor, "document") and editor.document().isModified():
            result = QMessageBox.question(
                self, "Unsaved Changes",
                "This file has unsaved changes. Save before closing?",
                QMessageBox.StandardButton.Save | QMessageBox.StandardButton.Discard | QMessageBox.StandardButton.Cancel
            )
            if result == QMessageBox.StandardButton.Save:
                self.save_file()
            elif result == QMessageBox.StandardButton.Cancel:
                return
        if index in self.open_files:
            del self.open_files[index]
        new_open_files = {}
        for i, path in self.open_files.items():
            new_open_files[i - 1 if i > index else i] = path
        self.open_files = new_open_files
        self.code_tabs.removeTab(index)

    def log_to_terminal(self, message):
        import datetime
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        self.terminal.append_text(f"[{timestamp}] {message}\n", "green")

    def on_terminal_command(self, command):
        if command.strip().startswith("ide:"):
            parts = command.strip()[4:].split()
            if parts and parts[0] == "open" and len(parts) > 1:
                self.open_file_with_path(parts[1])
                return True
            elif parts and parts[0] == "save":
                self.save_file()
                return True
        return False

    def new_file(self):
        editor = CodeEditor("settings.json", self)
        editor.setPlainText("")
        index = self.code_tabs.addTab(editor, "untitled")
        self.code_tabs.setCurrentIndex(index)
        self.log_to_terminal("Created new file")

    def open_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open File", "", "All Files (*)")
        if file_path:
            self.open_file_with_path(file_path)

    def save_file(self):
        current_index = self.code_tabs.currentIndex()
        if current_index >= 0:
            file_path = self.open_files.get(current_index)
            editor = self.code_tabs.widget(current_index)
            try:
                if file_path == "settings.json":
                    with open("settings.json", 'w', encoding='utf-8') as f:
                        f.write(editor.toPlainText())
                    editor.document().setModified(False)
                    self.log_to_terminal("Settings saved automatically.")
                    return True
                if not file_path:
                    return self.save_as_file()
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(editor.toPlainText())
                editor.document().setModified(False)
                self.log_to_terminal(f"Saved file: {file_path}")
                return True
            except Exception as e:
                self.log_to_terminal(f"Error saving file: {str(e)}")
                QMessageBox.critical(self, "Error", f"Could not save file: {str(e)}")
                return False
        return False

    def save_as_file(self):
        current_index = self.code_tabs.currentIndex()
        if current_index >= 0:
            file_path, _ = QFileDialog.getSaveFileName(self, "Save File As", "", "All Files (*)")
            if file_path:
                editor = self.code_tabs.widget(current_index)
                try:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(editor.toPlainText())
                    tab_name = os.path.basename(file_path)
                    self.code_tabs.setTabText(current_index, tab_name)
                    self.open_files[current_index] = file_path
                    editor.document().setModified(False)
                    self.log_to_terminal(f"Saved file as: {file_path}")
                    return True
                except Exception as e:
                    self.log_to_terminal(f"Error saving file: {str(e)}")
                    QMessageBox.critical(self, "Error", f"Could not save file: {str(e)}")
                    return False
        return False

    def new_terminal(self):
        self.terminal.clear()
        self.log_to_terminal("Terminal reset")

    def clear_terminal(self):
        self.terminal.clear()

    def toggle_file_explorer(self):
        if self.file_tree.isVisible():
            self.file_tree.hide()
        else:
            self.file_tree.show()
        self.log_to_terminal("Toggled file explorer")

    def toggle_terminal(self):
        if self.terminal.isVisible():
            self.terminal.hide()
        else:
            self.terminal.show()
        self.log_to_terminal("Toggled terminal")

    def change_theme(self):
        from PyQt6.QtGui import QPalette
        if self.palette().color(QPalette.ColorRole.Window).lightness() < 128:
            palette = QPalette()
            palette.setColor(QPalette.ColorRole.Window, QColor(240, 240, 240))
            palette.setColor(QPalette.ColorRole.WindowText, Qt.GlobalColor.black)
            palette.setColor(QPalette.ColorRole.Base, Qt.GlobalColor.white)
            palette.setColor(QPalette.ColorRole.Text, Qt.GlobalColor.black)
            palette.setColor(QPalette.ColorRole.Button, QColor(240, 240, 240))
            palette.setColor(QPalette.ColorRole.ButtonText, Qt.GlobalColor.black)
            self.setPalette(palette)
            self.log_to_terminal("Switched to light theme")
        else:
            self.set_dark_mode()
            self.log_to_terminal("Switched to dark theme")

    def change_font_size(self):
        for i in range(self.code_tabs.count()):
            editor = self.code_tabs.widget(i)
            if hasattr(editor, "font"):
                font = editor.font()
                font.setPointSize(font.pointSize() + 1)
                editor.setFont(font)
        self.log_to_terminal("Increased font size")

    def search_in_files(self):
        search_term = self.search_bar.text()
        if not search_term:
            return
        self.log_to_terminal(f"Searching for: {search_term}")
        for i in range(self.code_tabs.count()):
            editor = self.code_tabs.widget(i)
            file_path = self.open_files.get(i, f"Tab {i+1}")
            if hasattr(editor, "find"):
                cursor = editor.textCursor()
                cursor.movePosition(cursor.MoveOperation.Start)
                editor.setTextCursor(cursor)
                count = 0
                while editor.find(search_term):
                    count += 1
                if count > 0:
                    self.log_to_terminal(f"Found {count} matches in {file_path}")
                cursor.movePosition(cursor.MoveOperation.Start)
                editor.setTextCursor(cursor)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ide = CodeIDE()
    ide.show()
    sys.exit(app.exec())

