import os

def count_lines_in_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            return sum(1 for _ in f)
    except:
        return 0

def count_lines_in_directory(directory, extensions=None):
    if extensions is None:
        extensions = {'.py', '.js', '.html', '.css', '.json', '.md', '.txt'}
    
    total_lines = 0
    file_count = 0
    
    for root, _, files in os.walk(directory):
        # Skip directories like __pycache__, .git, etc.
        if any(d in root for d in ['__pycache__', '.git', '.idea', 'venv', 'env', 'node_modules']):
            continue
            
        for file in files:
            if any(file.endswith(ext) for ext in extensions):
                file_path = os.path.join(root, file)
                lines = count_lines_in_file(file_path)
                total_lines += lines
                file_count += 1
                print(f"{file_path}: {lines} lines")
    
    return total_lines, file_count

if __name__ == "__main__":
    project_root = os.path.dirname(os.path.abspath(__file__))
    print("Counting lines of code in:", project_root)
    
    total_lines, file_count = count_lines_in_directory(project_root)
    
    print("\nSummary:")
    print(f"Total files: {file_count}")
    print(f"Total lines: {total_lines}")
