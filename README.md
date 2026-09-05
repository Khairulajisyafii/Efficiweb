# Efficiweb

**Efficiweb** is a modern, lightweight, and blazingly fast companion tool designed specifically for Frontend Developers. Built with Python and `customtkinter`, it runs as a sleek, resizable floating window alongside your code editor, giving you instant access to your project's essential assets.

![Efficiweb](https://img.shields.io/badge/UI-CustomTkinter-blue?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.x-yellow?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

---

## Features

- ** Smart Color Palette Manager**
  - Store your project's colors (Background, Text, Accent, etc.).
  - **Auto-detects format**: Just paste `#FFF`, `rgb(255,255,255)`, or `hsl(0,0%,100%)` and Efficiweb will automatically convert and store all three formats.
  - 1-click copy for HEX, RGBA, and HSL.
- **🔗 Universal Shortlink Manager**
  - Keep track of documentation, Figma files, API endpoints, and staging URLs.
  - Assign custom emojis to links.
  - 1-click open in your default browser.
- **📋 CSS Snippet Vault**
  - Store reusable CSS rules, complex flexbox/grid layouts, or keyframe animations.
  - 1-click copy to clipboard.
- **🌍 Global vs Project-Specific Assets**
  - Assets can be scoped to a specific project or saved globally (accessible across all your projects).
- **💨 Minimalist & Unobtrusive UI**
  - **Glassmorphism** effect with a sleek monochrome dark theme.
  - **Zero-Flicker Resizable Sidebar**: Shrink the app down to a tiny vertical strip (auto-collapsing text into icons) so it takes up minimal screen space while you code.

## Installation & Usage

1.  **Clone the repository:**

    ```bash
    git clone https://github.com/Khairulajisyafii/Efficiweb-utilities-frontend-developer.git
    cd Efficiweb-utilities-frontend-developer
    ```

2.  **Install requirements:**
    Ensure you have Python installed, then install the required dependencies:

    ```bash
    pip install customtkinter
    ```

3.  **Run the app:**
    ```bash
    python main.py
    ```

## Building to Executable (.exe)

You can compile Efficiweb into a standalone Windows executable using PyInstaller.

1. Install PyInstaller:
   ```bash
   pip install pyinstaller
   ```
2. Build using the provided spec file:
   ```bash
   pyinstaller --clean Efficiweb.spec
   ```
3. The executable will be located in the `dist` folder. _(Note: If you update the icon, you may need to rename the `.exe` or move it to a different folder to bypass the Windows Icon Cache)._

## Project Structure

- `main.py`: Entry point of the application.
- `views.py`: UI components and layout logic (Home, Dashboard, Dialogs).
- `models.py`: Data classes and database interaction (JSON storage).
- `config.py`: App configuration, theme colors, and font settings.
- `utils.py`: Helper utilities (e.g., Color parsing).
- `database/`: Local directory where project JSON files are stored.

## License

This project is open-source and available under the MIT License.
