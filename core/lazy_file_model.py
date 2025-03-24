# core/lazy_file_model.py
import os
from PyQt6.QtGui import QIcon, QStandardItemModel, QStandardItem
from PyQt6.QtCore import QDir, Qt, QFileInfo  # Added QDir import

class LazyFileModel(QStandardItemModel):
    def __init__(self, root_path=""):
        super().__init__()
        self.root_path = root_path if root_path else QDir.homePath()
        self.loaded_folders = set()
        folder_name = QDir(self.root_path).dirName() or self.root_path
        self.setHorizontalHeaderLabels([folder_name])
        self.populate_top_level(self.root_path, self.invisibleRootItem())

    def populate_top_level(self, path, parent_item):
        # Add ".." entry if not at system root.
        if os.path.abspath(path) != os.path.abspath(QDir.rootPath()):
            parent_dir = os.path.dirname(os.path.abspath(path.rstrip("/")))
            parent_item_ = QStandardItem("..")
            parent_item_.setIcon(QIcon("assets/icons/folder.svg"))
            parent_item_.setData(parent_dir, Qt.ItemDataRole.UserRole)
            parent_item_.setData(True, Qt.ItemDataRole.UserRole + 1)  # isFolder
            self.appendRow(parent_item_)
        self.populate_folder(path, self.invisibleRootItem())

    def populate_folder(self, folder_path, parent_item):
        folder_path = os.path.abspath(folder_path)
        if folder_path in self.loaded_folders:
            return
        self.loaded_folders.add(folder_path)
        directory = QDir(folder_path)
        entries = directory.entryList(
            QDir.Filter(QDir.Filter.AllEntries | QDir.Filter.NoDotAndDotDot),
            QDir.SortFlag.Name
        )
        for entry in entries:
            full_path = directory.filePath(entry)
            fi = QFileInfo(full_path)
            item = QStandardItem(entry)
            if fi.isDir() and not fi.isSymLink():
                item.setIcon(QIcon("assets/icons/folder.svg"))
                item.setData(full_path, Qt.ItemDataRole.UserRole)
                item.setData(True, Qt.ItemDataRole.UserRole + 1)  # isFolder
                # Add a dummy child so the folder is expandable.
                dummy = QStandardItem("")
                item.appendRow(dummy)
            else:
                item.setData(full_path, Qt.ItemDataRole.UserRole)
                item.setData(False, Qt.ItemDataRole.UserRole + 1)  # isFolder
                lower = entry.lower()
                if lower.endswith(".py"):
                    item.setIcon(QIcon("assets/icons/python.svg"))
                elif lower.endswith(".js"):
                    item.setIcon(QIcon("assets/icons/javascriptX.svg"))
                elif lower.endswith(".java"):
                    item.setIcon(QIcon("assets/icons/java.svg"))
                elif lower.endswith(".css"):
                    item.setIcon(QIcon("assets/icons/css.svg"))
                elif lower.endswith(".html"):
                    item.setIcon(QIcon("assets/icons/html.svg"))
                elif lower.endswith(".ts"):
                    item.setIcon(QIcon("assets/icons/typescript.svg"))
                else:
                    item.setIcon(QIcon("assets/icons/file2.svg"))
            parent_item.appendRow(item)
