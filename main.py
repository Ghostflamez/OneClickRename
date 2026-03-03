"""
Main entry point and UI for the batch file renamer.
"""

import ctypes
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path

import engine
import history

# DPI awareness for Windows 10/11
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except Exception:
    pass


class App(tk.Tk):
    """Main application window."""

    def __init__(self):
        super().__init__()

        self.title("Batch File Renamer")
        self.geometry("900x650")
        self.minsize(700, 500)

        # Configure default font
        self.option_add("*Font", "Segoe\\ UI 10")

        # Apply vista theme
        self.style = ttk.Style()
        self.style.theme_use('vista')

        # Configure treeview tag colors
        self.style.configure("Treeview", rowheight=25)

        # State
        self.current_folder: Path | None = None
        self.files: list[Path] = []
        self.history = history.History()
        self._preview_job: str | None = None

        # Build UI
        self._create_toolbar()
        self._create_filter_bar()
        self._create_preview_pane()
        self._create_rules_panel()

        # Update button states
        self._update_button_states()

    def _create_toolbar(self):
        """Create the top toolbar with action buttons."""
        toolbar = ttk.Frame(self)
        toolbar.pack(fill=tk.X, padx=5, pady=5)

        self.btn_open = ttk.Button(toolbar, text="Open Folder", command=self._on_open_folder)
        self.btn_open.pack(side=tk.LEFT, padx=2)

        self.btn_undo = ttk.Button(toolbar, text="Undo", command=self._on_undo)
        self.btn_undo.pack(side=tk.LEFT, padx=2)

        self.btn_redo = ttk.Button(toolbar, text="Redo", command=self._on_redo)
        self.btn_redo.pack(side=tk.LEFT, padx=2)

        self.btn_apply = ttk.Button(toolbar, text="Apply", command=self._on_apply)
        self.btn_apply.pack(side=tk.LEFT, padx=2)

        self.btn_clear = ttk.Button(toolbar, text="Clear", command=self._on_clear)
        self.btn_clear.pack(side=tk.LEFT, padx=2)

    def _create_filter_bar(self):
        """Create the file type filter bar."""
        filter_frame = ttk.Frame(self)
        filter_frame.pack(fill=tk.X, padx=5, pady=2)

        ttk.Label(filter_frame, text="Filter:").pack(side=tk.LEFT, padx=2)

        self.filter_var = tk.StringVar()
        self.filter_var.trace_add("write", lambda *_: self._schedule_preview())
        self.filter_entry = ttk.Entry(filter_frame, textvariable=self.filter_var, width=20)
        self.filter_entry.pack(side=tk.LEFT, padx=2)

        ttk.Label(
            filter_frame,
            text="(e.g., *.txt, *.jpg) | Multi-select: Ctrl+Click, Shift+Click",
            foreground="gray"
        ).pack(side=tk.LEFT, padx=10)

    def _create_preview_pane(self):
        """Create the file preview treeview."""
        preview_frame = ttk.Frame(self)
        preview_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Treeview with scrollbar
        self.tree = ttk.Treeview(
            preview_frame,
            columns=("check", "original", "new"),
            show="headings",
            selectmode="extended"
        )

        self.tree.heading("check", text="✓")
        self.tree.heading("original", text="Original Name")
        self.tree.heading("new", text="New Name")

        self.tree.column("check", width=30, anchor=tk.CENTER, stretch=False)
        self.tree.column("original", width=300, anchor=tk.W)
        self.tree.column("new", width=300, anchor=tk.W)

        # Configure tags for highlighting
        self.tree.tag_configure("changed", foreground="green")
        self.tree.tag_configure("invalid", foreground="red")
        self.tree.tag_configure("unchanged", foreground="black")

        scrollbar = ttk.Scrollbar(preview_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Checkbox toggle on click
        self.tree.bind("<Button-1>", self._on_tree_click)

        # Track checked items
        self.checked_items: set[str] = set()

    def _create_rules_panel(self):
        """Create the bottom rules notebook."""
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.X, padx=5, pady=5)

        # Prefix/Suffix tab
        prefix_frame = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(prefix_frame, text="Prefix/Suffix")
        self._create_prefix_suffix_tab(prefix_frame)

        # Case tab
        case_frame = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(case_frame, text="Case")
        self._create_case_tab(case_frame)

        # Numbering tab
        number_frame = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(number_frame, text="Numbering")
        self._create_numbering_tab(number_frame)

        # Regex tab
        regex_frame = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(regex_frame, text="Regex")
        self._create_regex_tab(regex_frame)

    def _create_prefix_suffix_tab(self, parent):
        """Create prefix/suffix controls."""
        # Add prefix
        row1 = ttk.Frame(parent)
        row1.pack(fill=tk.X, pady=2)
        ttk.Label(row1, text="Add Prefix:", width=15).pack(side=tk.LEFT)
        self.prefix_add_var = tk.StringVar()
        self.prefix_add_var.trace_add("write", lambda *_: self._schedule_preview())
        ttk.Entry(row1, textvariable=self.prefix_add_var, width=30).pack(side=tk.LEFT, padx=5)

        # Remove prefix
        row2 = ttk.Frame(parent)
        row2.pack(fill=tk.X, pady=2)
        ttk.Label(row2, text="Remove Prefix:", width=15).pack(side=tk.LEFT)
        self.prefix_remove_var = tk.StringVar()
        self.prefix_remove_var.trace_add("write", lambda *_: self._schedule_preview())
        ttk.Entry(row2, textvariable=self.prefix_remove_var, width=30).pack(side=tk.LEFT, padx=5)

        # Add suffix
        row3 = ttk.Frame(parent)
        row3.pack(fill=tk.X, pady=2)
        ttk.Label(row3, text="Add Suffix:", width=15).pack(side=tk.LEFT)
        self.suffix_add_var = tk.StringVar()
        self.suffix_add_var.trace_add("write", lambda *_: self._schedule_preview())
        ttk.Entry(row3, textvariable=self.suffix_add_var, width=30).pack(side=tk.LEFT, padx=5)

        # Remove suffix
        row4 = ttk.Frame(parent)
        row4.pack(fill=tk.X, pady=2)
        ttk.Label(row4, text="Remove Suffix:", width=15).pack(side=tk.LEFT)
        self.suffix_remove_var = tk.StringVar()
        self.suffix_remove_var.trace_add("write", lambda *_: self._schedule_preview())
        ttk.Entry(row4, textvariable=self.suffix_remove_var, width=30).pack(side=tk.LEFT, padx=5)

        # Folder name options
        row5 = ttk.Frame(parent)
        row5.pack(fill=tk.X, pady=5)
        self.folder_prefix_var = tk.BooleanVar()
        self.folder_prefix_var.trace_add("write", lambda *_: self._schedule_preview())
        ttk.Checkbutton(
            row5, text="Add folder name as prefix", variable=self.folder_prefix_var
        ).pack(side=tk.LEFT, padx=5)

        self.folder_suffix_var = tk.BooleanVar()
        self.folder_suffix_var.trace_add("write", lambda *_: self._schedule_preview())
        ttk.Checkbutton(
            row5, text="Add folder name as suffix", variable=self.folder_suffix_var
        ).pack(side=tk.LEFT, padx=5)

    def _create_case_tab(self, parent):
        """Create case transformation controls."""
        self.case_var = tk.StringVar(value="")

        btn_frame = ttk.Frame(parent)
        btn_frame.pack(fill=tk.X, pady=5)

        cases = [
            ("UPPER", "upper"),
            ("lower", "lower"),
            ("Title", "title"),
            ("camelCase", "camel"),
            ("PascalCase", "pascal"),
            ("None", ""),
        ]

        for text, value in cases:
            ttk.Radiobutton(
                btn_frame, text=text, value=value, variable=self.case_var,
                command=self._schedule_preview
            ).pack(side=tk.LEFT, padx=10)

    def _create_numbering_tab(self, parent):
        """Create numbering controls."""
        row1 = ttk.Frame(parent)
        row1.pack(fill=tk.X, pady=5)

        ttk.Label(row1, text="Pattern:").pack(side=tk.LEFT, padx=5)
        self.number_pattern_var = tk.StringVar(value="file_{:02d}")
        self.number_pattern_var.trace_add("write", lambda *_: self._schedule_preview())
        ttk.Entry(row1, textvariable=self.number_pattern_var, width=25).pack(side=tk.LEFT, padx=5)

        ttk.Label(row1, text="Start:").pack(side=tk.LEFT, padx=5)
        self.number_start_var = tk.IntVar(value=1)
        self.number_start_var.trace_add("write", lambda *_: self._schedule_preview())
        ttk.Spinbox(
            row1, textvariable=self.number_start_var, from_=0, to=9999, width=8
        ).pack(side=tk.LEFT, padx=5)

        self.use_numbering_var = tk.BooleanVar(value=False)
        self.use_numbering_var.trace_add("write", lambda *_: self._schedule_preview())
        ttk.Checkbutton(
            row1, text="Enable numbering", variable=self.use_numbering_var
        ).pack(side=tk.LEFT, padx=20)

    def _create_regex_tab(self, parent):
        """Create regex controls."""
        row1 = ttk.Frame(parent)
        row1.pack(fill=tk.X, pady=5)

        ttk.Label(row1, text="Find (regex):").pack(side=tk.LEFT, padx=5)
        self.regex_find_var = tk.StringVar()
        self.regex_find_var.trace_add("write", lambda *_: self._schedule_preview())
        ttk.Entry(row1, textvariable=self.regex_find_var, width=30).pack(side=tk.LEFT, padx=5)

        ttk.Label(row1, text="Replace:").pack(side=tk.LEFT, padx=5)
        self.regex_replace_var = tk.StringVar()
        self.regex_replace_var.trace_add("write", lambda *_: self._schedule_preview())
        ttk.Entry(row1, textvariable=self.regex_replace_var, width=30).pack(side=tk.LEFT, padx=5)

    def _get_rules(self) -> dict:
        """Collect current rules from UI."""
        return {
            'prefix_add': self.prefix_add_var.get(),
            'prefix_remove': self.prefix_remove_var.get(),
            'suffix_add': self.suffix_add_var.get(),
            'suffix_remove': self.suffix_remove_var.get(),
            'case': self.case_var.get() or None,
            'regex_find': self.regex_find_var.get(),
            'regex_replace': self.regex_replace_var.get(),
            'folder_prefix': self.folder_prefix_var.get(),
            'folder_suffix': self.folder_suffix_var.get(),
            'folder_name': self.current_folder.name if self.current_folder else '',
        }

    def _schedule_preview(self):
        """Schedule a debounced preview update (300ms)."""
        if self._preview_job:
            self.after_cancel(self._preview_job)
        self._preview_job = self.after(300, self._update_preview)

    def _update_preview(self):
        """Update the preview treeview with current rules."""
        self._preview_job = None

        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)

        if not self.files:
            return

        # Filter files
        filter_pattern = self.filter_var.get().strip()
        filtered_files = self._filter_files(filter_pattern)

        # Handle numbering mode
        if self.use_numbering_var.get():
            pattern = self.number_pattern_var.get()
            start = self.number_start_var.get()
            new_names = engine.auto_number(
                [str(f) for f in filtered_files], pattern, start
            )
            for file_path, new_name in zip(filtered_files, new_names):
                old_name = file_path.name
                is_valid = engine.validate_filename(new_name)
                tag = "invalid" if not is_valid else ("changed" if old_name != new_name else "unchanged")
                check = "✓" if str(file_path) in self.checked_items else ""
                self.tree.insert("", tk.END, iid=str(file_path), values=(check, old_name, new_name), tags=(tag,))
        else:
            # Regular rules mode
            rules = self._get_rules()
            previews = engine.preview_rename([str(f) for f in filtered_files], rules)

            for file_path, (old_name, new_name) in zip(filtered_files, previews):
                is_valid = engine.validate_filename(new_name)
                tag = "invalid" if not is_valid else ("changed" if old_name != new_name else "unchanged")
                check = "✓" if str(file_path) in self.checked_items else ""
                self.tree.insert("", tk.END, iid=str(file_path), values=(check, old_name, new_name), tags=(tag,))

    def _filter_files(self, pattern: str) -> list[Path]:
        """Filter files based on pattern."""
        if not pattern:
            return self.files

        # Support glob-like patterns
        if pattern.startswith("*."):
            ext = pattern[1:].lower()  # e.g., ".txt"
            return [f for f in self.files if f.suffix.lower() == ext]
        elif "*" in pattern:
            import fnmatch
            return [f for f in self.files if fnmatch.fnmatch(f.name.lower(), pattern.lower())]
        else:
            # Simple substring match
            return [f for f in self.files if pattern.lower() in f.name.lower()]

    def _on_tree_click(self, event):
        """Handle clicks on treeview for checkbox toggle."""
        region = self.tree.identify_region(event.x, event.y)
        if region == "cell":
            column = self.tree.identify_column(event.x)
            if column == "#1":  # Check column
                item = self.tree.identify_row(event.y)
                if item:
                    if item in self.checked_items:
                        self.checked_items.discard(item)
                    else:
                        self.checked_items.add(item)
                    # Update display
                    values = self.tree.item(item, "values")
                    new_check = "✓" if item in self.checked_items else ""
                    self.tree.item(item, values=(new_check, values[1], values[2]))

    def _on_open_folder(self):
        """Open folder dialog and load files."""
        folder = filedialog.askdirectory(title="Select Folder")
        if folder:
            self.current_folder = Path(folder)
            self.files = [
                f for f in self.current_folder.iterdir()
                if f.is_file()
            ]
            self.files.sort(key=lambda f: f.name.lower())
            self.checked_items.clear()
            self._update_preview()
            self.title(f"Batch File Renamer - {self.current_folder}")

    def _on_undo(self):
        """Undo last rename operation."""
        action = self.history.undo()
        if action:
            # Reverse the renames
            for after_path, before_path in zip(action['after'], action['before']):
                try:
                    after_path.rename(before_path)
                except OSError as e:
                    messagebox.showerror("Undo Error", f"Failed to restore {after_path}: {e}")
            # Refresh file list
            self._refresh_files()
        self._update_button_states()

    def _on_redo(self):
        """Redo last undone operation."""
        action = self.history.redo()
        if action:
            # Re-apply the renames
            for before_path, after_path in zip(action['before'], action['after']):
                try:
                    before_path.rename(after_path)
                except OSError as e:
                    messagebox.showerror("Redo Error", f"Failed to rename {before_path}: {e}")
            # Refresh file list
            self._refresh_files()
        self._update_button_states()

    def _on_apply(self):
        """Apply rename operations to selected/all files."""
        if not self.files:
            return

        # Get files to rename (checked or all visible)
        items = self.tree.get_children()
        files_to_rename = []
        invalid_names = []

        for item in items:
            values = self.tree.item(item, "values")
            old_name, new_name = values[1], values[2]

            # Skip if no change
            if old_name == new_name:
                continue

            file_path = Path(item)

            # Check validity
            if not engine.validate_filename(new_name):
                invalid_names.append(new_name)
            else:
                new_path = file_path.parent / new_name
                files_to_rename.append((file_path, new_path))

        if not files_to_rename and not invalid_names:
            messagebox.showinfo("No Changes", "No files to rename.")
            return

        # Show warning for invalid names
        if invalid_names:
            msg = f"The following {len(invalid_names)} name(s) are invalid and will be skipped:\n\n"
            msg += "\n".join(invalid_names[:10])
            if len(invalid_names) > 10:
                msg += f"\n... and {len(invalid_names) - 10} more"
            messagebox.showwarning("Invalid Names", msg)

        if not files_to_rename:
            return

        # Confirm
        if not messagebox.askyesno(
            "Confirm Rename",
            f"Rename {len(files_to_rename)} file(s)?"
        ):
            return

        # Perform renames
        before_paths = []
        after_paths = []
        errors = []

        for old_path, new_path in files_to_rename:
            try:
                old_path.rename(new_path)
                before_paths.append(old_path)
                after_paths.append(new_path)
            except OSError as e:
                errors.append(f"{old_path.name}: {e}")

        # Record in history
        if before_paths:
            self.history.push({
                'before': before_paths,
                'after': after_paths
            })

        # Show errors if any
        if errors:
            messagebox.showerror(
                "Rename Errors",
                f"Failed to rename {len(errors)} file(s):\n\n" + "\n".join(errors[:10])
            )

        # Refresh
        self._refresh_files()
        self._update_button_states()

    def _refresh_files(self):
        """Reload files from current folder."""
        if self.current_folder:
            self.files = [
                f for f in self.current_folder.iterdir()
                if f.is_file()
            ]
            self.files.sort(key=lambda f: f.name.lower())
            self.checked_items.clear()
            self._update_preview()

    def _update_button_states(self):
        """Update undo/redo button enabled states."""
        self.btn_undo.config(state=tk.NORMAL if self.history.can_undo() else tk.DISABLED)
        self.btn_redo.config(state=tk.NORMAL if self.history.can_redo() else tk.DISABLED)

    def _has_edits(self) -> bool:
        """Check if any rule inputs have non-default values."""
        if self.prefix_add_var.get():
            return True
        if self.prefix_remove_var.get():
            return True
        if self.suffix_add_var.get():
            return True
        if self.suffix_remove_var.get():
            return True
        if self.case_var.get():
            return True
        if self.regex_find_var.get():
            return True
        if self.regex_replace_var.get():
            return True
        if self.folder_prefix_var.get():
            return True
        if self.folder_suffix_var.get():
            return True
        if self.use_numbering_var.get():
            return True
        if self.number_pattern_var.get() != "file_{:02d}":
            return True
        if self.number_start_var.get() != 1:
            return True
        if self.filter_var.get():
            return True
        return False

    def _on_clear(self):
        """Clear all rule inputs. Show confirmation if there are edits."""
        if self._has_edits():
            if not messagebox.askyesno(
                "Clear Rules",
                "You have unsaved rule inputs. Clear all?"
            ):
                return

        # Clear all inputs
        self.prefix_add_var.set("")
        self.prefix_remove_var.set("")
        self.suffix_add_var.set("")
        self.suffix_remove_var.set("")
        self.case_var.set("")
        self.regex_find_var.set("")
        self.regex_replace_var.set("")
        self.folder_prefix_var.set(False)
        self.folder_suffix_var.set(False)
        self.use_numbering_var.set(False)
        self.number_pattern_var.set("file_{:02d}")
        self.number_start_var.set(1)
        self.filter_var.set("")

        # Refresh preview
        self._update_preview()


def main():
    app = App()
    app.mainloop()


if __name__ == "__main__":
    main()
