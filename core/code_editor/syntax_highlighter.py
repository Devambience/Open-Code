from PyQt6.QtGui import QTextCharFormat, QColor, QFont, QSyntaxHighlighter
from PyQt6.QtCore import QRegularExpression, Qt

class Highlighter(QSyntaxHighlighter):
    def __init__(self, document, syntax_settings=None):
        super().__init__(document)
        # One Dark Pro theme colors
        self.colors = {
            "chalky": "#e5c07b",
            "coral": "#e06c75",
            "dark": "#5c6370",
            "error": "#f44747",
            "fountainBlue": "#56b6c2",
            "green": "#98c379",
            "invalid": "#ffffff",
            "lightDark": "#7f848e",
            "lightWhite": "#abb2bf",
            "malibu": "#61afef",
            "purple": "#c678dd",
            "whiskey": "#d19a66",
            "deepRed": "#be5046"
        }

        self.settings = syntax_settings or {}
        self.highlighting_rules = []
        self.setup_formats()
        self.setup_rules()

    def setup_formats(self):
        """Initialize text formats for different syntax elements"""
        self.formats = {
            # Variables and identifiers
            "variable": self.create_format(self.colors["lightWhite"]),
            "property": self.create_format(self.colors["coral"]),
            "special_var": self.create_format(self.colors["whiskey"]),
            
            # Functions and methods
            "function": self.create_format(self.colors["malibu"]),
            "method": self.create_format(self.colors["malibu"]),
            "decorator": self.create_format(self.colors["coral"], italic=True),
            
            # Keywords and control
            "keyword": self.create_format(self.colors["purple"], bold=True),
            "control": self.create_format(self.colors["purple"]),
            "conditional": self.create_format(self.colors["purple"]),
            
            # Types and classes
            "class": self.create_format(self.colors["chalky"], bold=True),
            "type": self.create_format(self.colors["chalky"]),
            "interface": self.create_format(self.colors["chalky"]),
            
            # Constants and values
            "constant": self.create_format(self.colors["whiskey"]),
            "number": self.create_format(self.colors["whiskey"]),
            "boolean": self.create_format(self.colors["whiskey"]),
            "null": self.create_format(self.colors["whiskey"]),
            
            # Strings
            "string": self.create_format(self.colors["green"]),
            "string_escape": self.create_format(self.colors["fountainBlue"]),
            "char": self.create_format(self.colors["green"]),
            
            # Comments
            "comment": self.create_format(self.colors["lightDark"], italic=True),
            "docstring": self.create_format(self.colors["lightDark"], italic=True),
            
            # Operators and symbols
            "operator": self.create_format(self.colors["fountainBlue"]),
            "bracket": self.create_format(self.colors["lightWhite"]),
            
            # Special
            "regex": self.create_format(self.colors["green"]),
            "annotation": self.create_format(self.colors["coral"]),
            "preprocessor": self.create_format(self.colors["purple"]),
            "url": self.create_format(self.colors["malibu"], underline=True),
            "error": self.create_format(self.colors["error"], underline=True)
        }

    def setup_rules(self):
        """Define syntax highlighting rules"""
        # Keywords
        keywords = [
            # Python keywords
            "and", "as", "assert", "async", "await", "break", "class", "continue",
            "def", "del", "elif", "else", "except", "finally", "for", "from",
            "global", "if", "import", "in", "is", "lambda", "nonlocal", "not",
            "or", "pass", "raise", "return", "try", "while", "with", "yield",
            # Additional keywords for other languages
            "function", "var", "let", "const", "static", "public", "private",
            "protected", "void", "int", "string", "bool", "float", "double"
        ]

        self.add_keywords(keywords)
        
        # Built-in types
        types = [
            "bool", "int", "float", "str", "list", "dict", "set", "tuple",
            "object", "None", "True", "False"
        ]
        
        self.add_types(types)

        # Regular expressions for various patterns
        rules = [
            # Docstrings
            (r'"""(?:.|\n)*?"""', "docstring"),
            (r"'''(?:.|\n)*?'''", "docstring"),
            
            # Single-line comments
            (r"#[^\n]*", "comment"),
            
            # Function definitions
            (r"\bdef\s+(\w+)", "function"),
            
            # Class definitions
            (r"\bclass\s+(\w+)", "class"),
            
            # Decorators
            (r"@\w+", "decorator"),
            
            # String literals
            (r'"[^"\\]*(\\.[^"\\]*)*"', "string"),
            (r"'[^'\\]*(\\.[^'\\]*)*'", "string"),
            
            # Numbers
            (r"\b\d+\b", "number"),
            (r"\b0x[0-9A-Fa-f]+\b", "number"),
            (r"\b\d+\.\d*\b", "number"),
            
            # Special variables
            (r"\bself\b", "special_var"),
            (r"\bcls\b", "special_var"),
            
            # Function calls
            (r"\b\w+(?=\s*\()", "function"),
            
            # Operators
            (r"[+\-*/=<>!&|^~]", "operator"),
            
            # Brackets
            (r"[\[\]{}()]", "bracket"),
            
            # Regular expressions
            (r"r'[^'\\]*(\\.[^'\\]*)*'", "regex"),
            (r'r"[^"\\]*(\\.[^"\\]*)*"', "regex"),
            
            # URLs
            (r"https?://\S+", "url"),
            
            # String escape sequences
            (r"\\[abfnrtv'\"\\]", "string_escape"),
            
            # Property access
            (r"\.\w+", "property")
        ]

        for pattern, format_name in rules:
            self.add_rule(pattern, format_name)

    def add_keywords(self, keywords):
        """Add keyword highlighting rules"""
        for keyword in keywords:
            pattern = f"\\b{keyword}\\b"
            self.add_rule(pattern, "keyword")

    def add_types(self, types):
        """Add type highlighting rules"""
        for type_name in types:
            pattern = f"\\b{type_name}\\b"
            self.add_rule(pattern, "type")

    def add_rule(self, pattern, format_name):
        """Add a highlighting rule"""
        expression = QRegularExpression(pattern)
        self.highlighting_rules.append((expression, self.formats[format_name]))

    def create_format(self, color, bold=False, italic=False, underline=False):
        """Create a text format with specified properties"""
        text_format = QTextCharFormat()
        text_format.setForeground(QColor(color))
        
        if bold:
            text_format.setFontWeight(QFont.Weight.Bold)
        if italic:
            text_format.setFontItalic(True)
        if underline:
            text_format.setFontUnderline(True)
            
        return text_format

    def highlightBlock(self, text):
        """Apply highlighting to the given block of text"""
        # Apply normal rules
        for pattern, text_format in self.highlighting_rules:
            match_iterator = pattern.globalMatch(text)
            while match_iterator.hasNext():
                match = match_iterator.next()
                self.setFormat(match.capturedStart(), match.capturedLength(), text_format)

        # Handle multi-line comments
        self.setCurrentBlockState(0)
        self.handle_multiline_strings(text)

    def handle_multiline_strings(self, text):
        """Handle multi-line strings and docstrings"""
        triple_quotes = ['"""', "'''"]
        
        for quote in triple_quotes:
            if self.handle_multiline_block(text, quote):
                break

    def handle_multiline_block(self, text, delimiter):
        """Process a multi-line block with the given delimiter"""
        if self.previousBlockState() == 1:
            start_index = 0
            add_length = 0
        else:
            start_index = text.find(delimiter)
            if start_index == -1:
                return False
            add_length = len(delimiter)

        end_index = text.find(delimiter, start_index + add_length)
        
        while start_index >= 0:
            if end_index == -1:
                self.setCurrentBlockState(1)
                length = len(text) - start_index
            else:
                length = end_index - start_index + add_length
                
            self.setFormat(start_index, length, self.formats["docstring"])
            
            start_index = text.find(delimiter, start_index + length)
            if start_index == -1:
                break
                
            end_index = text.find(delimiter, start_index + add_length)

        return True