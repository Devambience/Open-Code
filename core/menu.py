# core/menu.py
from PyQt6.QtWidgets import QMenuBar, QMenu
from PyQt6.QtGui import QAction, QIcon

def create_menu_bar(parent):
    menu_bar = QMenuBar(parent)

    # File Menu
    file_menu = QMenu("&File", parent)
    new_action = QAction("&New File", parent)
    new_action.setShortcut("Ctrl+N")
    new_action.setIcon(QIcon("assets/icons/file2.svg"))
    new_action.triggered.connect(parent.new_file)
    file_menu.addAction(new_action)

    open_action = QAction("&Open File", parent)
    open_action.setShortcut("Ctrl+O")
    open_action.setIcon(QIcon("assets/icons/openfolder.svg"))
    open_action.triggered.connect(parent.open_file)
    file_menu.addAction(open_action)

    save_action = QAction("&Save", parent)
    save_action.setShortcut("Ctrl+S")
    save_action.setIcon(QIcon("assets/icons/arrowdown.svg"))
    save_action.triggered.connect(parent.save_file)
    file_menu.addAction(save_action)

    save_as_action = QAction("Save &As", parent)
    save_as_action.setShortcut("Ctrl+Shift+S")
    save_as_action.triggered.connect(parent.save_as_file)
    file_menu.addAction(save_as_action)

    auto_save_action = QAction("Toggle &Auto Save", parent)
    auto_save_action.setCheckable(True)
    auto_save_action.setShortcut("Ctrl+Alt+S")
    auto_save_action.toggled.connect(parent.toggle_auto_save)
    file_menu.addAction(auto_save_action)

    file_menu.addSeparator()
    exit_action = QAction("E&xit", parent)
    exit_action.setShortcut("Alt+F4")
    exit_action.triggered.connect(parent.close)
    file_menu.addAction(exit_action)
    menu_bar.addMenu(file_menu)

    # Edit Menu
    edit_menu = QMenu("&Edit", parent)
    undo_action = QAction("&Undo", parent)
    undo_action.setShortcut("Ctrl+Z")
    undo_action.triggered.connect(lambda: parent.code_tabs.currentWidget().undo() if parent.code_tabs.currentWidget() else None)
    edit_menu.addAction(undo_action)

    redo_action = QAction("&Redo", parent)
    redo_action.setShortcut("Ctrl+Y")
    redo_action.triggered.connect(lambda: parent.code_tabs.currentWidget().redo() if parent.code_tabs.currentWidget() else None)
    edit_menu.addAction(redo_action)
    edit_menu.addSeparator()

    cut_action = QAction("Cu&t", parent)
    cut_action.setShortcut("Ctrl+X")
    cut_action.triggered.connect(lambda: parent.code_tabs.currentWidget().cut() if parent.code_tabs.currentWidget() else None)
    edit_menu.addAction(cut_action)

    copy_action = QAction("&Copy", parent)
    copy_action.setShortcut("Ctrl+C")
    copy_action.triggered.connect(lambda: parent.code_tabs.currentWidget().copy() if parent.code_tabs.currentWidget() else None)
    edit_menu.addAction(copy_action)

    paste_action = QAction("&Paste", parent)
    paste_action.setShortcut("Ctrl+V")
    paste_action.triggered.connect(lambda: parent.code_tabs.currentWidget().paste() if parent.code_tabs.currentWidget() else None)
    edit_menu.addAction(paste_action)
    menu_bar.addMenu(edit_menu)

    # View Menu
    view_menu = QMenu("&View", parent)
    explorer_action = QAction("Toggle &File Explorer", parent)
    explorer_action.setShortcut("Ctrl+E")
    explorer_action.triggered.connect(parent.toggle_file_explorer)
    view_menu.addAction(explorer_action)

    terminal_action = QAction("Toggle &Terminal", parent)
    terminal_action.setShortcut("Ctrl+`")
    terminal_action.triggered.connect(parent.toggle_terminal)
    view_menu.addAction(terminal_action)
    view_menu.addSeparator()

    theme_action = QAction("Toggle &Dark/Light Theme", parent)
    theme_action.triggered.connect(parent.change_theme)
    view_menu.addAction(theme_action)

    font_action = QAction("Increase &Font Size", parent)
    font_action.setShortcut("Ctrl++")
    font_action.triggered.connect(parent.change_font_size)
    view_menu.addAction(font_action)
    menu_bar.addMenu(view_menu)

    # Terminal Menu
    terminal_menu = QMenu("&Terminal", parent)
    new_term_action = QAction("&New Terminal", parent)
    new_term_action.triggered.connect(parent.new_terminal)
    terminal_menu.addAction(new_term_action)
    clear_term_action = QAction("&Clear Terminal", parent)
    clear_term_action.triggered.connect(parent.clear_terminal)
    terminal_menu.addAction(clear_term_action)
    menu_bar.addMenu(terminal_menu)

    # Settings as a standalone action in the menu bar
    settings_action = QAction("&Settings", parent)
    settings_action.setIcon(QIcon("assets/icons/bracket.svg"))
    settings_action.triggered.connect(parent.open_settings)
    menu_bar.addAction(settings_action)

    return menu_bar
