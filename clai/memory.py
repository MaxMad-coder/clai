import os
import json
import ast
import re
from datetime import datetime

SKIP_FOLDERS = {
    '.git', '__pycache__', 'node_modules', 'venv',
    '.venv', 'env', 'dist', 'build', '.idea', '.vscode'
}

SKIP_EXTENSIONS = {
    '.pyc', '.pyo', '.pyd', '.so', '.dll', '.class',
    '.jpg', '.jpeg', '.png', '.gif', '.svg', '.ico',
    '.mp3', '.mp4', '.zip', '.tar', '.gz', '.pdf'
}

CODE_EXTENSIONS = {
    '.py', '.js', '.ts', '.html', '.css', '.java',
    '.c', '.cpp', '.go', '.rs', '.rb', '.php',
    '.sh', '.bash', '.json', '.yaml', '.yml', '.toml'
}

MEMORY_FILE = ".clai_memory.json"

#Language specific extractors

#1)Python
def extract_python_symbols(filepath: str):
    functions,classes = [],[]
    try:
        with open(filepath,"r",encoding="utf-8",errors = "ignore") as f:
            source = f.read()
        tree = ast.parse(source)
        for node in ast.walk(tree):
            if isinstance(node,ast.ClassDef):
                classes.append(node.name)
            elif isinstance(node,ast.FunctionDef):
                functions.append(node.name)
            elif isinstance(node,ast.AsyncFunctionDef):
                functions.append(node.name)
    except Exception:
        pass
    return functions,classes

#2)Javascript
def extract_javascript_symbols(filepath: str):
    functions,classes = [],[]
    try:
        with open(filepath,"r",encoding="utf-8",errors = "ignore") as f:
            source = f.read()

        # Remove single-line and multi-line comments to avoid false matches
        source = re.sub(r'//.*?$', '', source, flags=re.MULTILINE)
        source = re.sub(r'/\*.*?\*/', '', source, flags=re.DOTALL)
        # Regular functions: function myFunc(
        functions += re.findall(r'\bfunction\s+(\w+)\s*\(', source)

        # Arrow functions assigned to const/let/var: const myFunc = () =>
        functions += re.findall(
            r'\b(?:const|let|var)\s+(\w+)\s*=\s*(?:async\s*)?\(.*?\)\s*=>', source
        )

        # Class methods: myMethod( inside a class
        functions += re.findall(r'^\s{2,}(\w+)\s*\(', source, re.MULTILINE)

        # Async functions: async function myFunc(
        functions += re.findall(r'\basync\s+function\s+(\w+)\s*\(', source)

        # Class declarations: class MyClass
        classes += re.findall(r'\bclass\s+(\w+)', source)
    except Exception:
        pass

    # Remove duplicates and common false positives
    false_positives = {'if', 'for', 'while', 'switch', 'catch', 'constructor'}
    functions = list(set(f for f in functions if f not in false_positives))
    classes = list(set(classes))

    return functions,classes

#3)Java
def extract_java_symbols(filepath: str):
    """
    Extract functions and classes from Java using regex.
    Covers: class declarations, method definitions.
    """
    functions, classes = [], []
    try:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            source = f.read()

        # Remove comments
        source = re.sub(r'//.*?$', '', source, flags=re.MULTILINE)
        source = re.sub(r'/\*.*?\*/', '', source, flags=re.DOTALL)

        # Class declarations: public class MyClass / class MyClass
        classes += re.findall(
            r'\b(?:public|private|protected|abstract|final)?\s*class\s+(\w+)', source
        )

        # Method declarations:
        # public void myMethod( / private int calculate( / static String getName(
        functions += re.findall(
            r'\b(?:public|private|protected|static|final|synchronized|abstract|native)'
            r'(?:\s+(?:static|final|synchronized|abstract|native))*'
            r'\s+\w[\w<>\[\]]*\s+(\w+)\s*\(',
            source
        )

    except Exception:
        pass

    functions = list(set(functions))
    classes   = list(set(classes))
    return functions, classes

#4)C and C++
def extract_c_cpp_symbols(filepath: str):
    """
    Extract functions and classes/structs from C and C++ using regex.
    Covers: function definitions, class declarations, struct declarations.
    """
    functions, classes = [], []
    try:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            source = f.read()

        # Remove comments
        source = re.sub(r'//.*?$', '', source, flags=re.MULTILINE)
        source = re.sub(r'/\*.*?\*/', '', source, flags=re.DOTALL)

        # Function definitions: return_type functionName(
        # Matches things like: int main( / void calculateSum( / std::string getName(
        functions += re.findall(
            r'\b(?:int|void|char|float|double|bool|long|short|unsigned|auto|string'
            r'|std::\w+|\w+_t)\s+(\w+)\s*\(',
            source
        )

        # C++ class declarations: class MyClass / struct MyStruct
        classes += re.findall(r'\b(?:class|struct)\s+(\w+)', source)

    except Exception:
        pass

    # Filter out common false positives like control keywords
    false_positives = {'if', 'for', 'while', 'switch', 'return', 'sizeof', 'main'}
    functions = list(set(f for f in functions if f not in false_positives))
    classes   = list(set(classes))

    return functions, classes

#5)HTML
def extract_html_symbols(filepath: str):
    """
    Extract meaningful info from HTML files.
    Collects: page title, all IDs, all CSS classes used, form actions.
    These are stored as 'functions' and 'classes' for consistency.
    """
    functions, classes = [], []
    try:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            source = f.read()

        # Page title
        titles = re.findall(r'<title[^>]*>(.*?)</title>', source, re.IGNORECASE)
        if titles:
            functions.append(f"title: {titles[0].strip()}")

        # All element IDs: id="myId"
        ids = re.findall(r'\bid=["\'](\w[\w-]*)["\']', source, re.IGNORECASE)
        functions += [f"#{i}" for i in ids]

        # All CSS classes used: class="btn primary"
        raw_classes = re.findall(r'\bclass=["\']([^"\']+)["\']', source, re.IGNORECASE)
        for raw in raw_classes:
            classes += raw.strip().split()

        # Form actions: action="/submit"
        actions = re.findall(r'\baction=["\']([^"\']+)["\']', source, re.IGNORECASE)
        functions += [f"form-action: {a}" for a in actions]

        # Script src references
        scripts = re.findall(r'<script[^>]+src=["\']([^"\']+)["\']', source, re.IGNORECASE)
        functions += [f"script: {s}" for s in scripts]

    except Exception:
        pass

    functions = list(set(functions))
    classes   = list(set(classes))[:30]  # cap at 30

    return functions, classes

#6)CSS
def extract_css_symbols(filepath: str):
    """
    Extract meaningful info from CSS files.
    Collects: all class selectors, ID selectors, and keyframe names.
    """
    functions, classes = [], []
    try:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            source = f.read()

        # Remove comments
        source = re.sub(r'/\*.*?\*/', '', source, flags=re.DOTALL)

        # CSS class selectors: .myClass
        classes += re.findall(r'\.([a-zA-Z][\w-]*)\s*[{,:]', source)

        # CSS ID selectors: #myId
        functions += re.findall(r'#([a-zA-Z][\w-]*)\s*[{,:]', source)

        # Keyframe animation names: @keyframes fadeIn
        functions += re.findall(r'@keyframes\s+(\w[\w-]*)', source)

        # CSS variables: --my-variable
        functions += re.findall(r'--([\w-]+)\s*:', source)

    except Exception:
        pass

    functions = list(set(functions))[:30]
    classes   = list(set(classes))[:30]

    return functions, classes

#Symbol Router
def extract_symbols(filepath: str,extension: str):
    if extension == ".py":
        return extract_python_symbols(filepath)
    elif extension == ".css":
        return extract_css_symbols(filepath)
    elif extension == ".java":
        return extract_java_symbols(filepath)
    elif extension in {".js",".ts"}:
        return extract_javascript_symbols(filepath)
    elif extension in {".c",".cpp",".cc",".cxx",".h","hpp"}:
        return extract_c_cpp_symbols(filepath)
    else:
        return [],[]

#Core Scanner
def scan_project(project_path: str) -> dict:
    project_path = os.path.abspath(project_path)
    memory = {
        "project_path": project_path,
        "project_name": os.path.basename(project_path),
        "last_updated": datetime.now().isoformat(),
        "project_type": "unknown",
        "files": [],
        "python_functions": [],
        "python_classes": [],
        "js_functions": [],
        "js_classes": [],
        "java_functions": [],
        "java_classes": [],
        "c_functions": [],
        "c_classes": [],
        "html_elements": [],
        "css_selectors": [],
        "summary": ""
    }

    all_file = []
    for root,dirs,files in os.walk(project_path):
        dirs[:] = [d for d in dirs if d not in SKIP_FOLDERS]
        for filename in files:
            ext = os.path.splitext(filename)[1].lower()
            if ext in SKIP_EXTENSIONS:
                continue
            filepath = os.path.join(root, filename)
            relative_filepath = os.path.relpath(filepath, project_path)
            file_info = {
                "path": relative_filepath,
                "extension": ext,
                "size_lines": count_lines(filepath),
                "functions": [],
                "classes": []
            }

            if ext in CODE_EXTENSIONS:
                functions, classes = extract_symbols(filepath, ext)
                file_info["functions"] = functions
                file_info["classes"] = classes

                # Store in language-specific master lists
                entry_f = [{"name": f, "file": relative_filepath} for f in functions]
                entry_c = [{"name": c, "file": relative_filepath} for c in classes]

                if ext==".py":
                    memory["python_functions"] += entry_f
                    memory["python_classes"] += entry_c

                elif ext in {".js",".ts"}:
                    memory["js_functions"] += entry_f
                    memory["js_classes"] += entry_c

                elif ext == ".java":
                    memory["java_functions"] += entry_f
                    memory["java_classes"] += entry_c

                elif ext in {".c",".cpp",".cc",".cxx",".h","hpp"}:
                    memory["c_selectors"] += entry_f
                    memory["c_classes"] += entry_c

                elif ext in {".html",".htm"}:
                    memory["html_elements"] += entry_f+entry_c
                elif ext == ".css":
                    memory["css_selectors"] += entry_f+entry_c

            all_file.append(file_info)
    memory["files"] = all_file
    memory["project_type"] = detect_project_type(all_file)
    memory["summary"] = build_summary(memory)

    return memory

#Helpers
def count_lines(filepath: str) -> int:
    try:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            return sum(1 for _ in f)
    except Exception:
        return 0


def detect_project_type(files: list) -> str:
    filenames = {f["path"].lower() for f in files}
    extensions = {f["extension"] for f in files}
    if "manage.py" in filenames:
        return "Django Web App"
    elif "app.py" in filenames and ".py" in extensions:
        return "Flask Web App"
    elif "package.json" in filenames and ".js" in extensions:
        return "Node.js App"
    elif "index.html" in filenames and ".css" in extensions:
        return "Static Website"
    elif "pom.xml" in filenames or ".java" in extensions:
        return "Java Project"
    elif ".cpp" in extensions or ".cc" in extensions:
        return "C++ Project"
    elif ".c" in extensions and ".cpp" not in extensions:
        return "C Project"
    elif "requirements.txt" in filenames and ".py" in extensions:
        return "Python Project"
    elif ".py" in extensions:
        return "Python Script"
    else:
        return "General Project"


def build_summary(memory: dict) -> str:
    name = memory["project_name"]
    project_type = memory["project_type"]
    total_files = len(memory["files"])

    # Count all symbols across all languages
    total_functions = (
            len(memory["python_functions"]) +
            len(memory["js_functions"]) +
            len(memory["java_functions"]) +
            len(memory["c_functions"])
    )
    total_classes = (
            len(memory["python_classes"]) +
            len(memory["js_classes"]) +
            len(memory["java_classes"]) +
            len(memory["c_classes"])
    )
    html_count = len(memory["html_elements"])
    css_count = len(memory["css_selectors"])

    parts = [
        f"{name} is a {project_type} with {total_files} files,",
        f"{total_functions} functions, and {total_classes} classes."
    ]

    if html_count:
        parts.append(f"HTML: {html_count} elements/IDs found.")
    if css_count:
        parts.append(f"CSS: {css_count} selectors found.")

    return " ".join(parts)

#Save and Load
def save_memory(memory: dict,project_path: str):
    memory_file = os.path.join(project_path,MEMORY_FILE)
    with open(memory_file, "w", encoding="utf-8") as f:
        json.dump(memory, f, ensure_ascii=False, indent=2)

def load_memory(project_path: str = ".") -> dict:
    memory_file = os.path.join(project_path,MEMORY_FILE)
    if not os.path.isfile(memory_file):
        return {}
    try:
        with open(memory_file, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

def memory_exists(project_path: str=".") -> bool:
    memory_file = os.path.join(os.path.abspath(project_path),MEMORY_FILE)
    return os.path.isfile(memory_file)

def format_memory_for_prompt(memory: dict) -> str:
    """
    Convert memory into a string injected into every AI prompt.
    Kept short to avoid overloading the model's context window.
    """
    if not memory:
        return "No project memory available."

    lines = [
        f"Project: {memory.get('project_name', 'unknown')}",
        f"Type:    {memory.get('project_type', 'unknown')}",
        f"Summary: {memory.get('summary', '')}",
        "",
        "Files:"
    ]

    code_files = [
        f for f in memory.get("files", [])
        if f.get("extension") in CODE_EXTENSIONS
    ]
    for f in code_files[:20]:
        lines.append(f"  - {f['path']} ({f.get('size_lines', 0)} lines)")

    # Python
    if memory.get("python_functions"):
        lines += ["", "Python Functions:"]
        for fn in memory["python_functions"][:20]:
            lines.append(f"  - {fn['name']}() in {fn['file']}")

    if memory.get("python_classes"):
        lines += ["", "Python Classes:"]
        for cls in memory["python_classes"][:10]:
            lines.append(f"  - {cls['name']} in {cls['file']}")

    # JavaScript
    if memory.get("js_functions"):
        lines += ["", "JavaScript Functions:"]
        for fn in memory["js_functions"][:20]:
            lines.append(f"  - {fn['name']}() in {fn['file']}")

    if memory.get("js_classes"):
        lines += ["", "JavaScript Classes:"]
        for cls in memory["js_classes"][:10]:
            lines.append(f"  - {cls['name']} in {cls['file']}")

    # Java
    if memory.get("java_functions"):
        lines += ["", "Java Methods:"]
        for fn in memory["java_functions"][:20]:
            lines.append(f"  - {fn['name']}() in {fn['file']}")

    if memory.get("java_classes"):
        lines += ["", "Java Classes:"]
        for cls in memory["java_classes"][:10]:
            lines.append(f"  - {cls['name']} in {cls['file']}")

    # C / C++
    if memory.get("c_functions"):
        lines += ["", "C/C++ Functions:"]
        for fn in memory["c_functions"][:20]:
            lines.append(f"  - {fn['name']}() in {fn['file']}")

    if memory.get("c_classes"):
        lines += ["", "C/C++ Classes/Structs:"]
        for cls in memory["c_classes"][:10]:
            lines.append(f"  - {cls['name']} in {cls['file']}")

    # HTML
    if memory.get("html_elements"):
        lines += ["", "HTML Elements/IDs:"]
        for el in memory["html_elements"][:15]:
            lines.append(f"  - {el['name']} in {el['file']}")

    # CSS
    if memory.get("css_selectors"):
        lines += ["", "CSS Selectors:"]
        for sel in memory["css_selectors"][:15]:
            lines.append(f"  - {sel['name']} in {sel['file']}")

    return "\n".join(lines)