from PyQt6.QtWidgets import QMenuBar, QMenu
from PyQt6.QtGui import QAction, QIcon

def create_menu_bar(window):
    menu_bar = QMenuBar()
    
    # File menu
    file_menu = QMenu("&File", window)
    menu_bar.addMenu(file_menu)
    
    new_action = QAction("&New File", window)
    new_action.setShortcut("Ctrl+N")
    new_action.setIcon(QIcon("icons/file2.svg"))
    new_action.setIconVisibleInMenu(False)
    new_action.triggered.connect(window.new_file)
    file_menu.addAction(new_action)
    
    open_action = QAction("&Open File", window)
    open_action.setShortcut("Ctrl+O")
    open_action.setIcon(QIcon("icons/openfolder.svg"))
    open_action.setIconVisibleInMenu(False)
    open_action.triggered.connect(window.open_file)
    file_menu.addAction(open_action)
    
    save_action = QAction("&Save", window)
    save_action.setShortcut("Ctrl+S")
    save_action.setIcon(QIcon("icons/arrowdown.svg"))
    save_action.setIconVisibleInMenu(False)
    save_action.triggered.connect(window.save_file)
    file_menu.addAction(save_action)
    
    save_as_action = QAction("Save &As", window)
    save_as_action.setShortcut("Ctrl+Shift+S")
    save_as_action.setIconVisibleInMenu(False)
    save_as_action.triggered.connect(window.save_as_file)
    file_menu.addAction(save_as_action)
    
    # Add Auto Save action to File menu
    auto_save_action = QAction("Toggle &Auto Save", window)
    auto_save_action.setShortcut("Ctrl+Alt+S")
    auto_save_action.setIconVisibleInMenu(False)
    auto_save_action.triggered.connect(window.toggle_auto_save)
    file_menu.addAction(auto_save_action)
    
    file_menu.addSeparator()
    
    exit_action = QAction("E&xit", window)
    exit_action.setShortcut("Alt+F4")
    exit_action.setIconVisibleInMenu(False)
    exit_action.triggered.connect(window.close)
    file_menu.addAction(exit_action)
    
    # Edit menu
    edit_menu = QMenu("&Edit", window)
    menu_bar.addMenu(edit_menu)
    
    undo_action = QAction("&Undo", window)
    undo_action.setShortcut("Ctrl+Z")
    undo_action.setIconVisibleInMenu(False)
    undo_action.triggered.connect(lambda: window.code_tabs.currentWidget().undo() if window.code_tabs.currentWidget() else None)
    edit_menu.addAction(undo_action)
    
    redo_action = QAction("&Redo", window)
    redo_action.setShortcut("Ctrl+Y")
    redo_action.setIconVisibleInMenu(False)
    redo_action.triggered.connect(lambda: window.code_tabs.currentWidget().redo() if window.code_tabs.currentWidget() else None)
    edit_menu.addAction(redo_action)
    
    edit_menu.addSeparator()
    
    cut_action = QAction("Cu&t", window)
    cut_action.setShortcut("Ctrl+X")
    cut_action.setIconVisibleInMenu(False)
    cut_action.triggered.connect(lambda: window.code_tabs.currentWidget().cut() if window.code_tabs.currentWidget() else None)
    edit_menu.addAction(cut_action)
    
    copy_action = QAction("&Copy", window)
    copy_action.setShortcut("Ctrl+C")
    copy_action.setIconVisibleInMenu(False)
    copy_action.triggered.connect(lambda: window.code_tabs.currentWidget().copy() if window.code_tabs.currentWidget() else None)
    edit_menu.addAction(copy_action)
    
    paste_action = QAction("&Paste", window)
    paste_action.setShortcut("Ctrl+V")
    paste_action.setIconVisibleInMenu(False)
    paste_action.triggered.connect(lambda: window.code_tabs.currentWidget().paste() if window.code_tabs.currentWidget() else None)
    edit_menu.addAction(paste_action)
    
    # View menu
    view_menu = QMenu("&View", window)
    menu_bar.addMenu(view_menu)
    
    explorer_action = QAction("Toggle &File Explorer", window)
    explorer_action.setShortcut("Ctrl+E")
    explorer_action.setIconVisibleInMenu(False)
    explorer_action.triggered.connect(window.toggle_file_explorer)
    view_menu.addAction(explorer_action)
    
    terminal_action = QAction("Toggle &Terminal", window)
    terminal_action.setShortcut("Ctrl+`")
    terminal_action.setIconVisibleInMenu(False)
    terminal_action.triggered.connect(window.toggle_terminal)
    view_menu.addAction(terminal_action)
    
    view_menu.addSeparator()
    
    theme_action = QAction("Toggle &Dark/Light Theme", window)
    theme_action.setIconVisibleInMenu(False)
    theme_action.triggered.connect(window.change_theme)
    view_menu.addAction(theme_action)
    
    font_action = QAction("Increase &Font Size", window)
    font_action.setShortcut("Ctrl++")
    font_action.setIconVisibleInMenu(False)
    font_action.triggered.connect(window.change_font_size)
    view_menu.addAction(font_action)
    
    # Terminal menu
    terminal_menu = QMenu("&Terminal", window)
    menu_bar.addMenu(terminal_menu)
    
    new_term_action = QAction("&New Terminal", window)
    new_term_action.setIconVisibleInMenu(False)
    new_term_action.triggered.connect(window.new_terminal)
    terminal_menu.addAction(new_term_action)
    
    clear_term_action = QAction("&Clear Terminal", window)
    clear_term_action.setIconVisibleInMenu(False)
    clear_term_action.triggered.connect(window.clear_terminal)
    terminal_menu.addAction(clear_term_action)
    
    settings_action = QAction("&Settings", window)
    settings_action.setIconVisibleInMenu(False)
    settings_action.triggered.connect(window.open_settings)
    menu_bar.addAction(settings_action)
    
    return menu_bar

