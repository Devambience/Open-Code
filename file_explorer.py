from PyQt6.QtWidgets import QTreeView, QMainWindow
from PyQt6.QtGui import QIcon, QStandardItemModel, QStandardItem
from PyQt6.QtCore import QDir, Qt, QFileInfo

class CustomFileModel(QStandardItemModel):
    def __init__(self, root_path=""):
        super().__init__()
        # Use a default shallow path (e.g., your home directory)
        self.root_path = root_path if root_path else QDir.homePath()
        self.setHorizontalHeaderLabels(["Name"])
        # Limit recursion depth (e.g., 2 levels)
        self.populate(self.root_path, self.invisibleRootItem(), depth=0, max_depth=2)

    def populate(self, path, parent_item, depth=0, max_depth=2):
        """
        Recursively populate the model with files and directories.
        Recursion is limited to max_depth.
        """
        directory = QDir(path)
        # List all entries except '.' and '..'
        entry_list = directory.entryList(
            QDir.Filter(QDir.Filter.AllEntries | QDir.Filter.NoDotAndDotDot),
            QDir.SortFlag.Name
        )
        for entry in entry_list:
            full_path = directory.filePath(entry)
            item = QStandardItem(entry)
            fi = QFileInfo(full_path)
            # Avoid recursing into symlinked directories
            if fi.isDir() and not fi.isSymLink():
                item.setIcon(QIcon("icons/folder.svg"))
                # Only recurse if we haven't reached max_depth
                if depth < max_depth:
                    self.populate(full_path, item, depth + 1, max_depth)
            else:
                lower = entry.lower()
                if lower.endswith(".py"):
                    item.setIcon(QIcon("icons/python.svg"))
                elif lower.endswith(".js"):
                    item.setIcon(QIcon("icons/javascriptX.svg"))
                elif lower.endswith(".java"):
                    item.setIcon(QIcon("icons/java.svg"))
                elif lower.endswith(".css"):
                    item.setIcon(QIcon("icons/css.svg"))
                elif lower.endswith(".html"):
                    item.setIcon(QIcon("icons/html.svg"))
                elif lower.endswith(".ts"):
                    item.setIcon(QIcon("icons/typescript.svg"))
                else:
                    item.setIcon(QIcon("icons/file2.svg"))
            # Store the full path for later use
            item.setData(full_path, Qt.ItemDataRole.UserRole)
            parent_item.appendRow(item)

class FileExplorer(QTreeView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.file_model = CustomFileModel()
        self.setModel(self.file_model)
        self.setHeaderHidden(False)
        # Remove expandAll() to avoid scanning too many nodes on startup.
        # self.expandAll()
        self.clicked.connect(self.open_file)

    def open_file(self, index):
        """Open the file and pass its content to the main window's editor."""
        full_path = index.data(Qt.ItemDataRole.UserRole)
        if full_path:
            try:
                with open(full_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                main_window = self.window()
                if isinstance(main_window, QMainWindow) and hasattr(main_window, "open_file_in_editor"):
                    filename = full_path.split("/")[-1]
                    main_window.open_file_in_editor(filename, content)
                else:
                    print("Error: Unable to find main window reference.")
            except Exception as e:
                print(f"Error opening file: {str(e)}")

