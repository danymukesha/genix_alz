import ast
import os

PROJECT_ROOT = ""  # should maybe adjust if running from inside genix-alz already
REQUIREMENTS_FILE = os.path.join(PROJECT_ROOT, "requirements.txt")

BUILTINS = {
    "os", "sys", "json", "datetime", "tempfile", "shutil", "subprocess",
    "logging", "math", "re", "io", "abc", "collections", "threading",
    "multiprocessing", "functools", "itertools", "typing", "pathlib",
    "email", "unittest", "http", "argparse"
}

def find_python_files(root_dir):
    py_files = []
    for dirpath, _, filenames in os.walk(root_dir):
        for f in filenames:
            if f.endswith(".py"):
                py_files.append(os.path.join(dirpath, f))
    return py_files

def get_imported_modules(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        try:
            tree = ast.parse(f.read(), filename=file_path)
        except Exception as e:
            print(f"⚠️  Failed to parse {file_path}: {e}")
            return set()
    imports = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for n in node.names:
                imports.add(n.name.split('.')[0])
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imports.add(node.module.split('.')[0])
    return imports

def get_requirements(file_path):
    reqs = set()
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                # Remove version specifiers for matching
                pkg = line.split("==")[0].split(">=")[0].split("<=")[0].split(">")[0].split("<")[0]
                reqs.add(pkg.lower())
    return reqs

def main():
    py_files = find_python_files(PROJECT_ROOT)
    all_imports = set()
    for py_file in py_files:
        all_imports.update(get_imported_modules(py_file))

    requirements = get_requirements(REQUIREMENTS_FILE)
    # Filter out builtins and project local modules (src)
    missing = []
    for imp in sorted(all_imports):
        imp_lower = imp.lower()
        if imp_lower not in requirements and imp not in BUILTINS and not imp.startswith("src") and imp != "":
            missing.append(imp)

    if missing:
        print("🔍 Missing libraries in requirements.txt:")
        for lib in missing:
            print(f" - {lib}")
    else:
        print("✅ All imported libraries are listed in requirements.txt")

if __name__ == "__main__":
    main()
