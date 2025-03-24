# core/code_editor/settings_manager.py
import json
import os
from PyQt6.QtCore import QFileSystemWatcher

class SettingsManager:
    def __init__(self, settings_path):
        self.settings_path = settings_path
        self.settings = self.load_settings()
        self.watcher = QFileSystemWatcher([settings_path])
        self.watcher.fileChanged.connect(self.load_settings)

    def load_settings(self):
        if os.path.exists(self.settings_path):
            with open(self.settings_path, "r") as f:
                self.settings = json.load(f)
        return self.settings
