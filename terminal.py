import os
import subprocess
import platform
import glob
from PyQt6.QtWidgets import QTextEdit, QApplication
from PyQt6.QtCore import Qt, QProcess, pyqtSignal
from PyQt6.QtGui import QTextCursor, QColor, QKeyEvent, QFont

class Terminal(QTextEdit):
    commandEntered = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Appearance and styling
        self.setReadOnly(False)
        self.setMinimumHeight(200)
        self.setStyleSheet("""
            QTextEdit {
                background-color: #1E1E1E;
                color: #CCCCCC;
                border: none;
                font-family: 'Consolas', 'Courier New', monospace;
                padding: 5px;
            }
        """)
        
        font = QFont("Consolas", 11)
        font.setStyleHint(QFont.StyleHint.Monospace)
        self.setFont(font)
        
        # Process initialization for command execution
        self.process = QProcess(self)
        self.process.readyReadStandardOutput.connect(self.handle_stdout)
        self.process.readyReadStandardError.connect(self.handle_stderr)
        self.process.finished.connect(self.handle_finished)
        
        # Determine shell settings based on OS
        if platform.system() == "Windows":
            self.shell = "cmd.exe"
            self.shell_args = ["/c"]
            self.path_separator = "\\"
            self.list_dir_cmd = "dir /b"
            self.get_commands_cmd = "help"
        else:
            self.shell = "/bin/bash"
            self.shell_args = ["-c"]
            self.path_separator = "/"
            self.list_dir_cmd = "ls -1"
            self.get_commands_cmd = "compgen -c"
        
        # Initialize command history and tab completion variables
        self.command_history = []
        self.history_index = 0
        self.current_command = ""
        self.completion_options = []
        self.completion_index = 0
        self.last_tab_text = ""
        self.command_cache = None
        
        # Terminal prompt initialization
        self.clear_terminal()
    
    def update_prompt(self) -> str:
        current_dir = os.path.basename(os.getcwd()) or os.path.abspath(os.getcwd())
        self.prompt = f"{current_dir} $ "
        return self.prompt
    
    def clear_terminal(self):
        self.clear()
        self.append_text(self.update_prompt())
        self.command_start_position = self.textCursor().position()
    
    def append_text(self, text: str, color: str = None):
        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        if color:
            original_format = cursor.charFormat()
            fmt = original_format
            fmt.setForeground(QColor(color))
            cursor.setCharFormat(fmt)
            cursor.insertText(text)
            cursor.setCharFormat(original_format)
        else:
            cursor.insertText(text)
        self.setTextCursor(cursor)
        self.ensureCursorVisible()
    
    def keyPressEvent(self, event: QKeyEvent) -> None:
        cursor = self.textCursor()
        if cursor.position() < self.command_start_position:
            cursor.setPosition(self.document().characterCount())
            self.setTextCursor(cursor)
        if cursor.hasSelection():
            if cursor.selectionStart() < self.command_start_position:
                return
        if event.key() in (Qt.Key.Key_Backspace, Qt.Key.Key_Delete):
            if cursor.position() <= self.command_start_position:
                return
        if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            self.handle_enter()
            return
        elif event.key() == Qt.Key.Key_Up:
            self.navigate_history(-1)
            return
        elif event.key() == Qt.Key.Key_Down:
            self.navigate_history(1)
            return
        elif event.key() == Qt.Key.Key_Tab:
            self.handle_tab_completion()
            return
        elif event.key() == Qt.Key.Key_C and event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            if self.process.state() == QProcess.ProcessState.Running:
                self.process.kill()
                self.append_text("\n^C\n" + self.update_prompt())
                self.command_start_position = self.textCursor().position()
                return
        else:
            self.completion_options = []
            self.completion_index = 0
        super().keyPressEvent(event)
    
    def handle_enter(self):
        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        self.setTextCursor(cursor)
        command = self.toPlainText()[self.command_start_position:]
        self.append_text("\n")
        if command.strip():
            self.command_history.append(command)
            self.history_index = len(self.command_history)
        self.commandEntered.emit(command)
        self.execute_command(command)
    
    def execute_command(self, command: str):
        command = command.strip()
        if not command:
            self.append_text(self.update_prompt())
            self.command_start_position = self.textCursor().position()
            return
        if command in ("clear", "cls"):
            self.clear_terminal()
            return
        if command.startswith("cd "):
            try:
                directory = command[3:].strip()
                if directory.startswith("~"):
                    directory = os.path.expanduser(directory)
                os.chdir(directory)
                self.append_text(self.update_prompt())
                self.command_start_position = self.textCursor().position()
                return
            except Exception as e:
                self.append_text(f"Error changing directory: {e}\n", "red")
                self.append_text(self.update_prompt())
                self.command_start_position = self.textCursor().position()
                return
        try:
            full_command = self.shell_args + [command]
            self.process.start(self.shell, full_command)
        except Exception as e:
            self.append_text(f"Error executing command: {e}\n", "red")
            self.append_text(self.update_prompt())
            self.command_start_position = self.textCursor().position()
    
    def handle_stdout(self):
        data = self.process.readAllStandardOutput().data().decode(errors='replace')
        self.append_text(data)
    
    def handle_stderr(self):
        data = self.process.readAllStandardError().data().decode(errors='replace')
        self.append_text(data, "red")
    
    def handle_finished(self, exit_code, exit_status):
        if exit_code != 0:
            self.append_text(f"\nProcess exited with code {exit_code}\n", "yellow")
        self.append_text(self.update_prompt())
        self.command_start_position = self.textCursor().position()
    
    def navigate_history(self, direction: int):
        if self.history_index == len(self.command_history):
            cursor = self.textCursor()
            cursor.setPosition(self.command_start_position)
            cursor.movePosition(QTextCursor.MoveOperation.End, QTextCursor.MoveMode.KeepAnchor)
            self.current_command = cursor.selectedText()
        new_index = self.history_index + direction
        if 0 <= new_index <= len(self.command_history):
            self.history_index = new_index
            cursor = self.textCursor()
            cursor.setPosition(self.command_start_position)
            cursor.movePosition(QTextCursor.MoveOperation.End, QTextCursor.MoveMode.KeepAnchor)
            cursor.removeSelectedText()
            if self.history_index == len(self.command_history):
                cursor.insertText(self.current_command)
            else:
                cursor.insertText(self.command_history[self.history_index])
    
    def get_current_command_text(self) -> str:
        cursor = self.textCursor()
        cursor.setPosition(self.command_start_position)
        cursor.movePosition(QTextCursor.MoveOperation.End, QTextCursor.MoveMode.KeepAnchor)
        return cursor.selectedText()
    
    def get_command_prefix(self) -> str:
        current_cmd = self.get_current_command_text()
        cursor_pos = self.textCursor().position() - self.command_start_position
        return current_cmd[:cursor_pos]
    
    def get_completion_candidates(self, prefix: str) -> list:
        parts = prefix.split()
        if len(parts) == 0 or (len(parts) == 1 and not prefix.endswith(" ")):
            if self.command_cache is None:
                try:
                    process = subprocess.Popen(
                        [self.shell, "-c", self.get_commands_cmd],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE
                    )
                    output, _ = process.communicate()
                    commands = output.decode('utf-8', errors='replace').splitlines()
                    common_commands = ["cd", "ls", "dir", "pwd", "echo", "clear", "mkdir", "rm", "cp", "mv"]
                    self.command_cache = sorted(set(commands + common_commands))
                except Exception:
                    self.command_cache = ["cd", "ls", "dir", "pwd", "echo", "clear", "mkdir", "rm", "cp", "mv"]
            cmd_prefix = parts[0] if parts else ""
            return [cmd for cmd in self.command_cache if cmd.startswith(cmd_prefix)]
        else:
            last_part = parts[-1]
            if last_part.startswith("~"):
                last_part = os.path.expanduser(last_part)
            if os.path.isabs(last_part) or last_part.startswith("~"):
                search_dir = os.path.dirname(last_part) or "/"
                filename_prefix = os.path.basename(last_part)
            else:
                search_dir = os.path.dirname(last_part) if os.path.dirname(last_part) else "."
                filename_prefix = os.path.basename(last_part)
            try:
                matches = []
                search_pattern = os.path.join(search_dir, f"{filename_prefix}*")
                for path in glob.glob(search_pattern):
                    base_name = os.path.basename(path)
                    if os.path.isdir(path):
                        matches.append(f"{base_name}{self.path_separator}")
                    else:
                        matches.append(base_name)
                return sorted(matches)
            except Exception:
                return []
    
    def handle_tab_completion(self):
        current_prefix = self.get_command_prefix()
        if not self.completion_options or current_prefix != self.last_tab_text:
            self.completion_options = self.get_completion_candidates(current_prefix)
            self.completion_index = 0
            self.last_tab_text = current_prefix
        else:
            self.completion_index = (self.completion_index + 1) % max(1, len(self.completion_options))
        if not self.completion_options:
            return
        parts = current_prefix.split()
        if len(parts) <= 1 and not current_prefix.endswith(" "):
            completed_text = self.completion_options[self.completion_index]
        else:
            base_parts = current_prefix.rsplit(" ", 1)
            prefix_part = base_parts[0] + " " if len(base_parts) > 1 else ""
            completed_text = prefix_part + self.completion_options[self.completion_index]
        cursor = self.textCursor()
        cursor.setPosition(self.command_start_position)
        cursor.movePosition(QTextCursor.MoveOperation.End, QTextCursor.MoveMode.KeepAnchor)
        cursor.removeSelectedText()
        cursor.insertText(completed_text)

