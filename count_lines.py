import os
from collections import defaultdict

# --- Configure your project root and folders to count ---
PROJECT_ROOT = r"."  # or full path like r"C:\OpenLingu"
FOLDERS_TO_COUNT = {"client", "lectioncreator", "server", "docs"}

# --- File extensions to language mapping ---
EXT_TO_LANG = {
    ".py": "Python",
    ".js": "JavaScript",
    ".ts": "TypeScript",
    ".html": "HTML",
    ".css": "CSS",
    ".json": "JSON",
    ".md": "Markdown",
    ".yml": "YAML",
    ".yaml": "YAML",
    ".cpp": "C++",
    ".c": "C",
    ".h": "C Header",
    ".java": "Java",
    ".cs": "C#",
}

def count_lines_in_file(filepath):
    try:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            return sum(1 for _ in f)
    except Exception:
        return 0

def main():
    folder_counts = defaultdict(int)
    lang_counts = defaultdict(int)
    total_lines = 0

    for root, _, files in os.walk(PROJECT_ROOT):
        rel_root = os.path.relpath(root, PROJECT_ROOT)
        top_folder = rel_root.split(os.sep)[0]  # get first-level folder
        if top_folder not in FOLDERS_TO_COUNT:
            continue  # skip anything outside the three folders

        folder_total = 0
        for file in files:
            ext = os.path.splitext(file)[1].lower()
            lang = EXT_TO_LANG.get(ext)
            if not lang:
                continue  # skip unknown file types

            path = os.path.join(root, file)
            lines = count_lines_in_file(path)
            folder_total += lines
            lang_counts[lang] += lines
            total_lines += lines

        folder_counts[top_folder] += folder_total

    # --- Print results ---
    print("\n📂 Line count by folder:")
    print("-" * 40)
    for folder, lines in folder_counts.items():
        print(f"{folder:<20} {lines:>8} lines")

    print("\n🈯 Line count by language:")
    print("-" * 40)
    for lang, lines in sorted(lang_counts.items(), key=lambda x: -x[1]):
        print(f"{lang:<15} {lines:>8} lines")

    print("\n📊 TOTAL LINES:", total_lines)

if __name__ == "__main__":
    main()