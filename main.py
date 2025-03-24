# main.py
import sys
import os
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QWidget, QSplitter,
    QTabWidget, QLineEdit, QFileDialog, QMessageBox, QToolBar, QHBoxLayout
)
from PyQt6.QtCore import Qt

def load_stylesheet(app, stylesheet_path="ui/styles.qss"):
    if os.path.exists(stylesheet_path):
        with open(stylesheet_path, "r") as f:
            app.setStyleSheet(f.read())

class CodeIDE(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Open Code IDE")
        self.resize(1200, 800)
        self.open_files = {}
        self.auto_save_enabled = False

        # Set up the menu bar.
        from core.menu import create_menu_bar
        self.setMenuBar(create_menu_bar(self))
        
        # Create a search toolbar with a centered search bar.
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search across files...")
        self.init_search_toolbar()

        # Set up the central widget and layout.
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(5, 5, 5, 5)

        # Splitter: Left = FileExplorerWidget; Right = Code Editor Tabs + Terminal.
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        from core.file_explorer_widget import FileExplorerWidget
        self.file_explorer_widget = FileExplorerWidget(self)
        self.splitter.addWidget(self.file_explorer_widget)

        self.code_tabs = QTabWidget()
        self.code_tabs.setTabsClosable(True)
        self.code_tabs.tabCloseRequested.connect(self.close_tab)
        from core.terminal import Terminal
        self.terminal = Terminal()
        self.code_splitter = QSplitter(Qt.Orientation.Vertical)
        self.code_splitter.addWidget(self.code_tabs)
        self.code_splitter.addWidget(self.terminal)
        self.splitter.addWidget(self.code_splitter)

        self.splitter.setSizes([240, 960])
        self.code_splitter.setSizes([600, 200])
        self.main_layout.addWidget(self.splitter)

    def init_search_toolbar(self):
        search_toolbar = QToolBar("Search", self)
        search_toolbar.setMovable(False)
        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addStretch()
        layout.addWidget(self.search_bar)
        layout.addStretch()
        search_toolbar.addWidget(container)
        self.addToolBar(search_toolbar)

    # Methods required by menu and file explorer:
    def open_file_in_editor(self, filename, content):
        for i in range(self.code_tabs.count()):
            if self.code_tabs.tabText(i) == filename:
                self.code_tabs.setCurrentIndex(i)
                return
        from core.code_editor.editor import CodeEditor
        editor = CodeEditor("assets/settings.json", self)
        editor.setPlainText(content)
        index = self.code_tabs.addTab(editor, filename)
        self.code_tabs.setCurrentIndex(index)
        self.open_files[index] = filename

    def toggle_auto_save(self, enabled):
        self.auto_save_enabled = enabled
        print("Auto Save enabled" if enabled else "Auto Save disabled")

    def new_file(self):
        from core.code_editor.editor import CodeEditor
        editor = CodeEditor("assets/settings.json", self)
        editor.setPlainText("")
        index = self.code_tabs.addTab(editor, "untitled")
        self.code_tabs.setCurrentIndex(index)
        self.log_to_terminal("Created new file")

    def open_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open File", "", "All Files (*)")
        if file_path:
            self.open_file_with_path(file_path)

    def open_file_with_path(self, file_path):
        for i in range(self.code_tabs.count()):
            if file_path == self.open_files.get(i):
                self.code_tabs.setCurrentIndex(i)
                return
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except UnicodeDecodeError:
            self.log_to_terminal(f"Error: Cannot open file {file_path} as text (binary file?)")
            return
        except Exception as e:
            self.log_to_terminal(f"Error opening file: {str(e)}")
            return
        from core.code_editor.editor import CodeEditor
        editor = CodeEditor("assets/settings.json", self)
        editor.setPlainText(content)
        tab_name = os.path.basename(file_path)
        index = self.code_tabs.addTab(editor, tab_name)
        self.open_files[index] = file_path
        self.code_tabs.setCurrentIndex(index)
        self.log_to_terminal(f"Opened file: {file_path}")

    def save_file(self):
        current_index = self.code_tabs.currentIndex()
        if current_index >= 0:
            file_path = self.open_files.get(current_index)
            editor = self.code_tabs.widget(current_index)
            try:
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

    def open_settings(self):
        settings_path = "assets/settings.json"
        try:
            with open(settings_path, "r", encoding="utf-8") as f:
                content = f.read()
            from core.code_editor.editor import CodeEditor
            editor = CodeEditor(settings_path, self)
            editor.setPlainText(content)
            index = self.code_tabs.addTab(editor, "settings.json")
            self.open_files[index] = settings_path
        except Exception as e:
            self.log_to_terminal(f"Error opening settings: {str(e)}")

    def new_terminal(self):
        self.terminal.clear()
        self.log_to_terminal("Terminal reset")

    def clear_terminal(self):
        self.terminal.clear()

    def toggle_file_explorer(self):
        if self.file_explorer_widget.isVisible():
            self.file_explorer_widget.hide()
        else:
            self.file_explorer_widget.show()
        self.log_to_terminal("Toggled file explorer")

    def toggle_terminal(self):
        if self.terminal.isVisible():
            self.terminal.hide()
        else:
            self.terminal.show()
        self.log_to_terminal("Toggled terminal")

    def change_theme(self):
        self.log_to_terminal("Theme change requested")

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

    def log_to_terminal(self, message):
        import datetime
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        self.terminal.append_text(f"[{timestamp}] {message}\n")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    load_stylesheet(app, "ui/styles.qss")
    ide = CodeIDE()
    ide.show()
    sys.exit(app.exec())
