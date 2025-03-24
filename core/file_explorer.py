# core/file_explorer.py
import os
from PyQt6.QtWidgets import QTreeView, QApplication, QMainWindow
from PyQt6.QtCore import Qt
from core.lazy_file_model import LazyFileModel

def get_main_window(widget):
    from PyQt6.QtWidgets import QMainWindow
    while widget is not None:
        if isinstance(widget, QMainWindow) and hasattr(widget, "open_file_in_editor"):
            return widget
        widget = widget.parentWidget()
    return QApplication.instance().activeWindow()

class FileExplorer(QTreeView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        # Set the drag-drop mode to accept drops from external sources.
        self.setDragDropMode(QTreeView.DragDropMode.DropOnly)
        self.setExpandsOnDoubleClick(True)
        self.setHeaderHidden(False)
        self.file_model = LazyFileModel()
        self.setModel(self.file_model)
        self.expanded.connect(self.on_item_expanded)
        self.clicked.connect(self.on_item_clicked)

    def on_item_expanded(self, index):
        is_folder = index.data(Qt.ItemDataRole.UserRole + 1)
        if is_folder:
            model = index.model()
            item = model.itemFromIndex(index)
            if item.hasChildren() and item.rowCount() == 1 and not item.child(0).data(Qt.ItemDataRole.UserRole):
                item.removeRow(0)
                folder_path = item.data(Qt.ItemDataRole.UserRole)
                model.populate_folder(folder_path, item)

    def on_item_clicked(self, index):
        is_folder = index.data(Qt.ItemDataRole.UserRole + 1)
        path = index.data(Qt.ItemDataRole.UserRole)
        if not path:
            return
        # If the user clicks the ".." item, change root to its parent.
        if index.data() == "..":
            new_root = path
            self.file_model = LazyFileModel(new_root)
            self.setModel(self.file_model)
            print(f"Moved to parent directory: {new_root}")
            return
        if is_folder:
            # Let double-click handle folder expansion.
            return
        try:
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            main_window = get_main_window(self)
            if main_window:
                filename = os.path.basename(path)
                main_window.open_file_in_editor(filename, content)
            else:
                print("Error: Unable to find main window reference.")
        except Exception as e:
            print(f"Error opening file: {str(e)}")

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        event.acceptProposedAction()

    def dropEvent(self, event):
        urls = event.mimeData().urls()
        if urls:
            local_path = urls[0].toLocalFile()
            if os.path.isdir(local_path):
                self.file_model = LazyFileModel(local_path)
                self.setModel(self.file_model)
                print(f"File explorer updated to directory: {local_path}")
            else:
                try:
                    with open(local_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    main_window = get_main_window(self)
                    if main_window:
                        filename = os.path.basename(local_path)
                        main_window.open_file_in_editor(filename, content)
                    else:
                        print("Error: Unable to find main window reference.")
                except Exception as e:
                    print(f"Error opening dropped file: {str(e)}")
            event.acceptProposedAction()
