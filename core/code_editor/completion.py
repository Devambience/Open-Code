from PyQt6.QtWidgets import QCompleter
from PyQt6.QtCore import Qt, QStringListModel

class CodeCompleter(QCompleter):
    def __init__(self, editor):
        super().__init__(editor)
        self.editor = editor
        self.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.setCompletionMode(QCompleter.CompletionMode.PopupCompletion)
        
        # Initial keywords list - can be expanded based on language
        self.keywords = [
            # Python keywords
            'False', 'None', 'True', 'and', 'as', 'assert', 'async', 'await',
            'break', 'class', 'continue', 'def', 'del', 'elif', 'else', 'except',
            'finally', 'for', 'from', 'global', 'if', 'import', 'in', 'is', 'lambda',
            'nonlocal', 'not', 'or', 'pass', 'raise', 'return', 'try', 'while',
            'with', 'yield',
            
            # Common built-in functions
            'print', 'len', 'str', 'int', 'float', 'list', 'dict', 'set', 'tuple',
            'range', 'enumerate', 'zip', 'map', 'filter', 'sorted', 'sum', 'max',
            'min', 'abs', 'round', 'open', 'isinstance', 'type'
        ]
        
        self.setModel(QStringListModel(self.keywords))
        
        # Connect signals
        self.activated.connect(self.insert_completion)

    def insert_completion(self, completion):
        # Get the current text cursor
        tc = self.editor.textCursor()
        
        # Get the number of characters to the left of cursor that need to be replaced
        extra = len(self.completionPrefix())
        tc.movePosition(tc.Left, tc.KeepAnchor, extra)
        tc.insertText(completion)
        self.editor.setTextCursor(tc)

    def update_completions(self, new_words):
        """Update the completion list with new words"""
        current_words = set(self.keywords)
        current_words.update(new_words)
        self.setModel(QStringListModel(sorted(list(current_words))))

    def get_word_under_cursor(self):
        """Get the word under the cursor for completion"""
        tc = self.editor.textCursor()
        tc.select(tc.WordUnderCursor)
        return tc.selectedText()