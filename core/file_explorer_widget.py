# core/file_explorer_widget.py
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QToolBar, QLabel
from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtCore import Qt
from core.file_explorer import FileExplorer

class FileExplorerWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        
        self.toolbar = QToolBar()
        self.toolbar.setMovable(False)
        self.toolbar.setFloatable(False)
        
        self.header_label = QLabel("Files")
        self.toolbar.addWidget(self.header_label)
        self.toolbar.addSeparator()
        
        add_file_action = QAction(QIcon("assets/icons/file2.svg"), "Add File", self)
        add_file_action.triggered.connect(self.add_file)
        self.toolbar.addAction(add_file_action)
        
        add_folder_action = QAction(QIcon("assets/icons/folder.svg"), "Add Folder", self)
        add_folder_action.triggered.connect(self.add_folder)
        self.toolbar.addAction(add_folder_action)
        
        fold_all_action = QAction("Fold All", self)
        fold_all_action.triggered.connect(self.fold_all)
        self.toolbar.addAction(fold_all_action)
        
        self.layout.addWidget(self.toolbar)
        
        self.explorer = FileExplorer(self)
        self.layout.addWidget(self.explorer)
        self.set_header(self.explorer.file_model.root_path)
    
    def set_header(self, path):
        from PyQt6.QtCore import QDir
        folder_name = QDir(path).dirName() or path
        self.header_label.setText(folder_name)
    
    def add_file(self):
        print("Add File action triggered")
    
    def add_folder(self):
        print("Add Folder action triggered")
    
    def fold_all(self):
        self.explorer.collapseAll()
