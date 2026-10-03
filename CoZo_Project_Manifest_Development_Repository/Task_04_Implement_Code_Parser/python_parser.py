import argparse
import ast
import json
import re
from pathlib import Path


def py_params(node):
    args = []
    for a in getattr(node.args, 'posonlyargs', []): args.append(a.arg)
    for a in node.args.args: args.append(a.arg)
    if node.args.vararg: args.append('*' + node.args.vararg.arg)
    for a in node.args.kwonlyargs: args.append(a.arg)
    if node.args.kwarg: args.append('**' + node.args.kwarg.arg)
    return args


def py_signature(node):
    return f"{node.name}({','.join(py_params(node))})"


def parse_python(path: Path):
    src = path.read_text(encoding='utf-8', errors='replace')
    tree = ast.parse(src)
    classes, functions = [], []
    class_method_ids = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            methods = []
            for item in node.body:
                if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    class_method_ids.add(id(item))
                    methods.append({
                        'name': item.name,
                        'signature': py_signature(item),
                        'parameters': py_params(item),
                        'async': isinstance(item, ast.AsyncFunctionDef),
                        'line_start': getattr(item, 'lineno', None),
                        'line_end': getattr(item, 'end_lineno', None),
                    })
            classes.append({'name': node.name, 'line_start': getattr(node,'lineno',None), 'line_end': getattr(node,'end_lineno',None), 'methods': methods})
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and id(node) not in class_method_ids:
            functions.append({'name': node.name, 'signature': py_signature(node), 'parameters': py_params(node), 'async': isinstance(node, ast.AsyncFunctionDef), 'line_start': getattr(node,'lineno',None), 'line_end': getattr(node,'end_lineno',None)})
    return {'classes': classes, 'functions': functions}


def parse_generic(path: Path, language: str):
    """Best-effort symbol extraction without external parsers; Python uses AST above."""
    text = path.read_text(encoding='utf-8', errors='replace')
    classes, functions = [], []
    class_patterns = [r'\bclass\s+([A-Za-z_$][\w$]*)', r'\binterface\s+([A-Za-z_$][\w$]*)']
    function_patterns = {
        'JavaScript': [r'\bfunction\s+([A-Za-z_$][\w$]*)\s*\(([^)]*)\)', r'\b(?:const|let|var)\s+([A-Za-z_$][\w$]*)\s*=\s*(?:async\s*)?\(([^)]*)\)\s*=>'],
        'TypeScript': [r'\bfunction\s+([A-Za-z_$][\w$]*)\s*\(([^)]*)\)', r'\b(?:const|let|var)\s+([A-Za-z_$][\w$]*)\s*=\s*(?:async\s*)?\(([^)]*)\)\s*=>'],
        'Go': [r'\bfunc\s+(?:\([^)]*\)\s*)?([A-Za-z_]\w*)\s*\(([^)]*)\)'],
        'PHP': [r'\bfunction\s+([A-Za-z_]\w*)\s*\(([^)]*)\)'],
        'Ruby': [r'^\s*def\s+([A-Za-z_]\w*[!?=]?)\s*(?:\(([^)]*)\))?'],
        'Java': [r'\b(?:public|private|protected|static|final|synchronized|abstract|native|\s)+[\w<>,.?\[\]]+\s+([A-Za-z_]\w*)\s*\(([^)]*)\)\s*\{'],
        'CSharp': [r'\b(?:public|private|protected|internal|static|virtual|override|async|sealed|\s)+[\w<>,.?\[\]]+\s+([A-Za-z_]\w*)\s*\(([^)]*)\)'],
        'C++': [r'\b[A-Za-z_][\w:<>,*&\s]+\s+([A-Za-z_]\w*)\s*\(([^;{}]*)\)\s*\{'],
        'C': [r'\b[A-Za-z_][\w*\s]+\s+([A-Za-z_]\w*)\s*\(([^;{}]*)\)\s*\{'],
    }
    for pat in class_patterns:
        for m in re.finditer(pat, text, re.MULTILINE):
            line = text.count('\n', 0, m.start()) + 1
            classes.append({'name': m.group(1), 'line_start': line, 'line_end': None, 'methods': []})
    seen = set()
    for pat in function_patterns.get(language, []):
        for m in re.finditer(pat, text, re.MULTILINE):
            name, raw = m.group(1), (m.group(2) or '')
            if name in seen: continue
            seen.add(name)
            params = [p.strip() for p in raw.split(',') if p.strip()]
            line = text.count('\n', 0, m.start()) + 1
            functions.append({'name': name, 'signature': f"{name}({','.join(params)})", 'parameters': params, 'line_start': line, 'line_end': None})
    return {'classes': classes, 'functions': functions}


def main():
    ap = argparse.ArgumentParser(description='Parse every supported source file in repository inventory.')
    ap.add_argument('--repo', required=True)
    ap.add_argument('--inventory', required=True, help='Language-updated inventory JSON')
    ap.add_argument('--output', default=str(Path(__file__).parent / 'output' / 'code_structure.json'))
    args = ap.parse_args()
    repo = Path(args.repo).resolve()
    inv = json.loads(Path(args.inventory).read_text(encoding='utf-8'))
    results = []
    for item in inv.get('files', []):
        rel = item.get('path')
        lang = item.get('language', 'Unknown')
        path = repo / rel
        entry = {'path': rel, 'language': lang, 'classes': [], 'functions': []}
        try:
            if lang == 'Python': parsed = parse_python(path)
            elif lang in {'JavaScript','TypeScript','Java','CSharp','C++','C','Go','PHP','Ruby'}: parsed = parse_generic(path, lang)
            else: parsed = {'classes': [], 'functions': []}
            entry.update(parsed)
        except Exception as exc:
            entry['parse_error'] = str(exc)
        results.append(entry)
    out = {'repository_root': str(repo), 'files': results}
    p = Path(args.output); p.parent.mkdir(parents=True, exist_ok=True); p.write_text(json.dumps(out, indent=2), encoding='utf-8')
    print(f'✅ Code structure generated for {len(results)} files: {p}')

if __name__ == '__main__': main()
