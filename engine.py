"""
Pure functions for file rename operations.
No UI imports, no side effects on import.
"""

import re
from pathlib import Path

# Characters forbidden in Windows filenames
INVALID_CHARS = frozenset('\\/:*?"<>|')


def preview_rename(files: list[str], rules: dict) -> list[tuple[str, str]]:
    """
    Generate preview of rename operations.

    Args:
        files: List of file paths as strings
        rules: Dict containing active rename rules

    Returns:
        List of (old_name, new_name) tuples
    """
    results = []
    for file_path in files:
        path = Path(file_path)
        old_name = path.name
        new_name = apply_rules(old_name, rules)
        results.append((old_name, new_name))
    return results


def apply_rules(name: str, rules: dict) -> str:
    """
    Apply all active rename rules to a filename.

    Args:
        name: Original filename (stem + suffix)
        rules: Dict with rule configurations:
            - prefix_add: str to prepend
            - prefix_remove: str to remove from start
            - suffix_add: str to append before extension
            - suffix_remove: str to remove from end (before extension)
            - case: 'upper' | 'lower' | 'title' | 'camel' | 'pascal' | None
            - regex_find: regex pattern to find
            - regex_replace: replacement string
            - folder_prefix: bool to add parent folder as prefix
            - folder_suffix: bool to add parent folder as suffix
            - folder_name: str parent folder name (when folder_prefix/suffix is True)

    Returns:
        Modified filename
    """
    path = Path(name)
    stem = path.stem
    suffix = path.suffix

    # Apply prefix removal
    if rules.get('prefix_remove') and stem.startswith(rules['prefix_remove']):
        stem = stem[len(rules['prefix_remove']):]

    # Apply suffix removal (from stem, before extension)
    if rules.get('suffix_remove') and stem.endswith(rules['suffix_remove']):
        stem = stem[:-len(rules['suffix_remove'])]

    # Apply regex replacement
    if rules.get('regex_find'):
        try:
            stem = re.sub(rules['regex_find'], rules.get('regex_replace', ''), stem)
        except re.error:
            pass  # Invalid regex, skip

    # Apply case transformation
    case = rules.get('case')
    if case == 'upper':
        stem = stem.upper()
    elif case == 'lower':
        stem = stem.lower()
    elif case == 'title':
        stem = stem.title()
    elif case == 'camel':
        stem = _to_camel_case(stem)
    elif case == 'pascal':
        stem = _to_pascal_case(stem)

    # Apply folder name as prefix
    if rules.get('folder_prefix') and rules.get('folder_name'):
        stem = rules['folder_name'] + '_' + stem

    # Apply folder name as suffix
    if rules.get('folder_suffix') and rules.get('folder_name'):
        stem = stem + '_' + rules['folder_name']

    # Apply prefix addition
    if rules.get('prefix_add'):
        stem = rules['prefix_add'] + stem

    # Apply suffix addition (before extension)
    if rules.get('suffix_add'):
        stem = stem + rules['suffix_add']

    return stem + suffix


def _to_camel_case(text: str) -> str:
    """Convert text to camelCase."""
    # Split on non-alphanumeric characters
    words = re.split(r'[^a-zA-Z0-9]+', text)
    words = [w for w in words if w]
    if not words:
        return text
    result = words[0].lower()
    for word in words[1:]:
        result += word.capitalize()
    return result


def _to_pascal_case(text: str) -> str:
    """Convert text to PascalCase."""
    words = re.split(r'[^a-zA-Z0-9]+', text)
    words = [w for w in words if w]
    if not words:
        return text
    return ''.join(word.capitalize() for word in words)


def validate_filename(name: str) -> bool:
    """
    Check if filename is valid for Windows.

    Args:
        name: Filename to validate

    Returns:
        False if name contains any of \\ / : * ? " < > |
    """
    if not name or name.isspace():
        return False
    return not any(char in INVALID_CHARS for char in name)


def auto_number(files: list[str], pattern: str, start: int = 1) -> list[str]:
    """
    Generate numbered filenames.

    Args:
        files: List of original file paths
        pattern: Format pattern with {} placeholder, e.g., "file_{:02d}"
        start: Starting number (default 1)

    Returns:
        List of new filenames with numbering applied
    """
    results = []
    for i, file_path in enumerate(files, start=start):
        path = Path(file_path)
        suffix = path.suffix
        try:
            new_stem = pattern.format(i)
        except (IndexError, KeyError, ValueError):
            # Invalid pattern, use as literal with number appended
            new_stem = f"{pattern}{i}"
        results.append(new_stem + suffix)
    return results
