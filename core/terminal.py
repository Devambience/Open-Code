import os
import sys
import shlex
from PyQt6.QtWidgets import QTextEdit, QApplication, QMainWindow, QVBoxLayout, QWidget
from PyQt6.QtGui import QTextCharFormat, QFont, QColor, QTextCursor, QFontDatabase
from PyQt6.QtCore import Qt, QProcess

class Terminal(QTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        # Initialize state variables
        self.current_directory = os.getcwd()
        self.username = os.getlogin()
        self.hostname = "localhost"
        self.command_history = []
        self.history_index = -1
        self.current_command = ""
        self.locked = False
        self.process = QProcess(self)
        self.pending_lines = []
        self.prompt_position = 0

        # Setup appearance and process
        self.setup_appearance()
        self.process.setProcessChannelMode(QProcess.ProcessChannelMode.MergedChannels)
        self.process.readyReadStandardOutput.connect(self.read_output)
        self.process.finished.connect(self.process_finished)

        # Define color palette
        self.colors = {
            "prompt": QColor("#50fa7b"),
            "command": QColor("#f8f8f2"),
            "output": QColor("#8be9fd"),
            "error": QColor("#ff5555"),
            "warning": QColor("#f1fa8c"),
            "success": QColor("#50fa7b")
        }

        # Display welcome message
        self.append_text("Welcome to Advanced IDE Terminal\n", color="success", parse_ansi=False)
        self.display_prompt()

    def setup_appearance(self):
        """Configure the terminal's modern styling."""
        font_name = next((f for f in ["Cascadia Code", "Fira Code", "Consolas"] 
                          if f in QFontDatabase.families()), "Monospace")
        font = QFont(font_name, 10)
        font.setStyleHint(QFont.StyleHint.Monospace)
        self.setFont(font)
        self.setStyleSheet("QTextEdit { background-color: #282a36; color: #50fa7b; border: none; padding: 8px; }")
        self.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)

    def display_prompt(self):
        """Display the command prompt and track its position."""
        dir_name = os.path.basename(self.current_directory) or self.current_directory
        prompt = f"{self.username}@{self.hostname}:{dir_name}$ "
        self.append_text(prompt, color="prompt", parse_ansi=False)
        self.prompt_position = self.textCursor().position()
        self.move_cursor_to_end()

    def append_text(self, text, color="output", parse_ansi=True):
        """Append text to the terminal with specified color, optionally parsing ANSI codes."""
        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        format_text = QTextCharFormat()
        format_text.setForeground(self.colors.get(color, QColor("#8be9fd")))

        if parse_ansi:
            text = text.replace('\r', '')  # Remove carriage returns
            parts = text.split('\033[')
            for part in parts:
                if not part:
                    continue
                if part[0].isdigit() and 'm' in part:
                    code_str, _, content = part.partition('m')
                    codes = code_str.split(';')
                    for code in codes:
                        if code == '0':
                            format_text = QTextCharFormat()
                            format_text.setForeground(self.colors["output"])
                        elif code in ['30', '31', '32', '33', '34', '35', '36', '37']:
                            color_index = int(code) - 30
                            colors = [Qt.GlobalColor.black, Qt.GlobalColor.red, Qt.GlobalColor.green, Qt.GlobalColor.yellow,
                                      Qt.GlobalColor.blue, Qt.GlobalColor.magenta, Qt.GlobalColor.cyan, Qt.GlobalColor.white]
                            format_text.setForeground(colors[color_index])
                    if content:
                        cursor.insertText(content, format_text)
                else:
                    cursor.insertText(part, format_text)
        else:
            cursor.insertText(text, format_text)
        self.setTextCursor(cursor)
        self.ensureCursorVisible()

    def keyPressEvent(self, event):
        """Handle key presses with proper process termination."""
        cursor = self.textCursor()
        if self.locked:
            if event.key() == Qt.Key.Key_C and event.modifiers() & Qt.KeyboardModifier.ControlModifier:
                self.process.kill()
                self.process.waitForFinished(1000)  # Wait for process to finish
                self.append_text("\n[Terminated]", color="error", parse_ansi=False)
                self.locked = False
                self.display_prompt()
            return

        if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            self.handle_command_entry()
        elif event.key() == Qt.Key.Key_Up:
            if self.history_index < len(self.command_history) - 1:
                self.history_index += 1
                self.set_current_command(self.command_history[self.history_index])
        elif event.key() == Qt.Key.Key_Down:
            if self.history_index > -1:
                self.history_index -= 1
                self.set_current_command("" if self.history_index == -1 else self.command_history[self.history_index])
        elif event.key() == Qt.Key.Key_Tab:
            self.handle_tab_completion()
        elif event.key() == Qt.Key.Key_Backspace:
            if cursor.position() > self.prompt_position:
                super().keyPressEvent(event)
                self.current_command = self.get_current_command_text()
        elif event.key() == Qt.Key.Key_Left:
            if cursor.position() > self.prompt_position:
                super().keyPressEvent(event)
        else:
            if cursor.position() < self.prompt_position:
                cursor.setPosition(self.prompt_position)
                self.setTextCursor(cursor)
            super().keyPressEvent(event)
            self.current_command = self.get_current_command_text()

    def get_current_command_text(self):
        """Extract the current command text after the prompt."""
        text = self.toPlainText()
        return text[self.prompt_position:].strip()

    def set_current_command(self, command):
        """Update the displayed command text."""
        cursor = self.textCursor()
        cursor.setPosition(self.prompt_position)
        cursor.movePosition(QTextCursor.MoveOperation.End, QTextCursor.MoveMode.KeepAnchor)
        cursor.removeSelectedText()
        self.append_text(command, color="command", parse_ansi=False)
        self.current_command = command
        self.move_cursor_to_end()

    def move_cursor_to_end(self):
        """Move the cursor to the end of the text."""
        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        self.setTextCursor(cursor)

    def handle_command_entry(self):
        """Process the entered command, supporting multi-line inputs."""
        command = self.current_command.strip()
        if not command:
            self.append_text("\n", parse_ansi=False)
            self.display_prompt()
            return

        if command.endswith('\\'):
            self.pending_lines.append(command.rstrip('\\'))
            self.append_text("\n> ", color="prompt", parse_ansi=False)
            self.current_command = ""
            self.prompt_position = self.textCursor().position()
            return

        if self.pending_lines:
            self.pending_lines.append(command)
            full_command = '\n'.join(self.pending_lines)
            self.pending_lines = []
            self.execute_command(full_command)
        else:
            self.execute_command(command)

    def execute_command(self, command):
        """Execute the command, either built-in or external."""
        self.command_history.insert(0, command)
        if len(self.command_history) > 100:
            self.command_history.pop()
        self.history_index = -1
        self.append_text("\n", parse_ansi=False)

        # Built-in commands
        if command == "clear":
            self.clear()
            self.display_prompt()
        elif command == "exit":
            QApplication.quit()
        elif command.startswith("cd "):
            try:
                new_dir = os.path.expanduser(command[3:].strip() or "~")
                new_dir = os.path.normpath(os.path.join(self.current_directory, new_dir))
                os.chdir(new_dir)
                self.current_directory = os.getcwd()
                self.display_prompt()
            except FileNotFoundError:
                self.append_text(f"cd: Directory '{new_dir}' not found", color="error", parse_ansi=False)
                self.append_text("\n", parse_ansi=False)
                self.display_prompt()
        elif command == "pwd":
            self.append_text(self.current_directory, color="output", parse_ansi=False)
            self.append_text("\n", parse_ansi=False)
            self.display_prompt()
        elif command.startswith("echo "):
            self.append_text(command[5:], color="output", parse_ansi=False)
            self.append_text("\n", parse_ansi=False)
            self.display_prompt()
        elif command == "help":
            self.append_text("""
Built-in commands:
  clear - Clear screen
  exit - Exit terminal
  cd <dir> - Change directory
  pwd - Print working directory
  echo <text> - Display text
  help - Show this message
Run any shell command, including sudo.""", color="output", parse_ansi=False)
            self.display_prompt()
        else:
            self.run_external_command(command)

    def run_external_command(self, command):
        """Run an external command, ensuring no process is already running."""
        self.locked = True
        self.process.setWorkingDirectory(self.current_directory)
        
        # Terminate any running process before starting a new one
        if self.process.state() != QProcess.ProcessState.NotRunning:
            self.process.kill()
            self.process.waitForFinished(1000)  # Wait up to 1 second for termination
        
        try:
            if sys.platform == "win32":
                self.process.start("cmd.exe", ["/c", command])
            else:
                shell_command = command
                if command.startswith("sudo "):
                    shell_command = f"pkexec /bin/bash -c '{command[5:]}'"
                self.process.start("/bin/bash", ["-c", shell_command])
            if not self.process.waitForStarted(2000):
                raise RuntimeError(self.process.errorString())
        except Exception as e:
            self.append_text(f"Error: {str(e)}", color="error", parse_ansi=False)
            self.locked = False
            self.display_prompt()

    def read_output(self):
        """Read and display output from the process with ANSI parsing."""
        data = self.process.readAllStandardOutput()
        text = bytes(data).decode('utf-8', errors='replace')
        if text:
            self.append_text(text, parse_ansi=True)

    def process_finished(self, exit_code, _):
        """Handle process completion and display exit status."""
        self.read_output()
        if exit_code != 0:
            self.append_text(f"\n[Exit code: {exit_code}]", color="warning", parse_ansi=False)
        self.append_text("\n", parse_ansi=False)
        self.locked = False
        self.display_prompt()

    def handle_tab_completion(self):
        """Provide tab completion for commands and file paths."""
        command = self.current_command.strip()
        if not command:
            return
        parts = shlex.split(command)
        completing = parts[-1]
        base_dir = self.current_directory if not os.path.isabs(completing) else os.path.dirname(completing)
        prefix = os.path.basename(completing)

        try:
            matches = [f for f in os.listdir(base_dir) if f.startswith(prefix)]
            if len(matches) == 1:
                new_part = matches[0] + ("/" if os.path.isdir(os.path.join(base_dir, matches[0])) else "")
                self.set_current_command(" ".join(parts[:-1] + [new_part]))
            elif len(matches) > 1:
                common = os.path.commonprefix(matches)
                if common != prefix:
                    self.set_current_command(" ".join(parts[:-1] + [common]))
                else:
                    self.append_text("\n" + "  ".join(matches), color="output", parse_ansi=False)
                    self.append_text("\n", parse_ansi=False)
                    self.display_prompt()
                    self.set_current_command(command)
        except:
            pass

class TerminalWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Advanced IDE Terminal")
        widget = QWidget()
        self.setCentralWidget(widget)
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        self.terminal = Terminal()
        layout.addWidget(self.terminal)
        self.resize(800, 500)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TerminalWindow()
    window.show()
    sys.exit(app.exec())