# OneClickRename

A lightweight Windows 10/11 desktop GUI app for batch renaming files using regex patterns.

## Download

**Latest Release: v1.0.1**

- [OneClickRename.exe](dist/OneClickRename.exe) (11 MB) - Standalone executable, no installation required

## Features

### Rename Rules
- **Prefix/Suffix**: Add or remove text at the start or end of filenames
- **Case Conversion**: UPPER, lower, Title, camelCase, PascalCase
- **Numbering**: Sequential numbering with custom patterns (e.g., `file_{:02d}`)
- **Regex**: Find and replace using regular expressions
- **Folder Name**: Option to add parent folder name as prefix/suffix

### File Management
- **Live Preview**: See changes before applying (300ms debounce)
- **Undo/Redo**: Full history support (up to 50 operations)
- **Clear**: Reset all rule inputs with confirmation dialog
- **Filter**: Dropdown menu with checkboxes for file type filtering
  - Categorized presets: Documents, Images, Media, Archives, Code
  - Custom extension support with validation

### UI Layout
```
┌─────────────────────────────────────────────────┐
│ [Open Folder] [Undo] [Redo] [Clear]             │  <- Toolbar
├─────────────────────────────────────────────────┤
│ Filter: [All Files    ] [Select... ▼]           │  <- Filter Bar
├─────────────────────────────────────────────────┤
│ ✓ │ Original Name        │ New Name             │
│───┼──────────────────────┼──────────────────────│  <- Preview
│   │ file1.txt            │ FILE1.txt (green)    │
│   │ file2.txt            │ FILE2.txt (green)    │
├─────────────────────────────────────────────────┤
│ [Prefix/Suffix] [Case] [Numbering] [Regex]      │  <- Rules Tabs
│ ┌─────────────────────────────────────────────┐ │
│ │ Add Prefix: [________]                      │ │
│ │ Remove Prefix: [________]                   │ │
│ └─────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────┤
│                               [Apply Rename]    │  <- Action Bar
└─────────────────────────────────────────────────┘
```

## Requirements

### For Users
- Windows 10/11
- No installation required (portable executable)

### For Developers
- Python 3.10+
- No third-party runtime dependencies (stdlib only)

## Usage

### Run Executable
Double-click `OneClickRename.exe` to launch.

### Run from Source
```bash
python main.py
```

## Building Executable

```bash
pip install pyinstaller
pyinstaller --onefile --windowed --name "OneClickRename" main.py
```

The `.exe` will be created in the `dist/` folder.

## Project Structure

```
OneClickRename/
├── main.py          # Entry point + UI (tkinter + ttk)
├── engine.py        # Rename logic (pure functions)
├── history.py       # Undo/redo stack (Command Pattern)
├── requirements.txt # Dependencies
└── dist/
    └── OneClickRename.exe  # Standalone executable
```

## Changelog

### v1.0.1 (2025-03-03)

**Bug Fix**

- Fix checkbox selection: only rename checked files when checkboxes are used
- Fall back to renaming all files if none are checked

### v1.0.0 (2025-03-03)

**Initial Release**

- Core rename rules: Prefix/Suffix, Case conversion, Numbering, Regex
- Live preview with color-coded feedback (green=changed, red=invalid)
- Undo/Redo support with 50-operation history
- File type filter with categorized dropdown menu
- Clear button to reset all inputs
- DPI-aware UI with Windows Vista theme
- Single-file portable executable (no installation required)

## License

MIT License

Copyright (c) 2025 OneClickRename

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
