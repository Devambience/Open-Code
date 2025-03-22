# Open Code IDE

**Open Code IDE** is a lightweight code editor built using PyQt6. It offers a modern user interface with a customizable dark theme, draggable tabs with custom SVG close buttons, an integrated file explorer, and an embedded terminal. The project is designed to be extendable and customizable, making it a great starting point for building a more advanced development environment.

## Features

- **Modern UI with QSS Styling:**  
  A sleek, dark-themed interface with a custom stylesheet for a modern look.

- **Draggable Tabs:**  
  Easily reorder open file tabs with drag-and-drop functionality.

- **Custom Close Buttons:**  
  Each tab has a round, SVG-based close button instead of the default emoji.

- **Integrated File Explorer:**  
  Browse files and directories using a custom file explorer with icons representing different file types.

- **Embedded Terminal:**  
  Execute shell commands directly within the IDE.

- **Auto Save Toggle:**  
  Toggle an auto-save feature to periodically save your work.

- **Settings Editor:**  
  Open and edit the settings file (`settings.json`) with an integrated cut button in the toolbar.

## Installation

1. **Clone the repository:**

   ```bash
   git clone https://github.com/Devambience/Open-Code.git
   cd Open-Code
   ```

2. **Create a virtual environment (recommended):**

   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install the dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

   > **Note:** Ensure you have PyQt6 installed. If you experience issues with certain classes (e.g., `QFileSystemModel`), verify your PyQt6 version and adjust imports accordingly.

## Usage

Run the application with:

```bash
python3 main.py
```

- Use the **File Explorer** to navigate and open files.
- Edit files in the **Code Editor** with draggable tabs.
- Use the **Terminal** to run shell commands.
- Toggle features such as **Auto Save** and switch between **Dark/Light Themes** using the menu bar.
- Open settings via the menu to edit `settings.json`, which includes a custom toolbar with a cut button.

## Directory Structure

```
open-code-ide/
├── icons/                # SVG icons for UI elements (e.g., cross.svg, cut.svg, etc.)
├── code_editor.py        # Custom code editor widget with syntax highlighting and gutter
├── file_explorer.py      # Custom file explorer widget
├── main.py               # Main application file
├── menu.py               # Menu bar and actions
├── terminal.py           # Integrated terminal widget
├── settings.json         # Editor settings and customization file
└── README.md             # Project documentation
```

## Customization

- **UI Styling:**  
  Edit the QSS stylesheet in the `get_stylesheet` method in `main.py` to change the look and feel of the application.

- **Settings:**  
  Modify `settings.json` to adjust font settings, colors, and syntax highlighting preferences.

- **Icons:**  
  Place your SVG icon files in the `icons/` folder. Ensure the paths in your code (e.g., `"icons/cross.svg"`) match your file names.

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests to improve the project.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
