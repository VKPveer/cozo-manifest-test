import argparse
import ast
import json
import re
import sys
from pathlib import Path

STDLIB = set(getattr(sys, 'stdlib_module_names', set()))

def internal_module_index(repo: Path):
    idx=set()
    for p in repo.rglob('*.py'):
        if '.git' in p.parts or '__pycache__' in p.parts: continue
        rel=p.relative_to(repo).with_suffix('')
        parts=list(rel.parts)
        if parts and parts[-1]=='__init__': parts=parts[:-1]
        if parts:
            idx.add('.'.join(parts)); idx.add(parts[0]); idx.add(parts[-1])
    return idx

def classify_python(name, internal):
    root=(name or '').split('.')[0]
    if root in STDLIB: return 'standard_library'
    if name in internal or root in internal or any(m == name or m.startswith(name+'.') or name.startswith(m+'.') for m in internal): return 'internal'
    return 'external'

def python_deps(path: Path, internal):
    tree=ast.parse(path.read_text(encoding='utf-8',errors='replace')); out=[]
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for a in node.names: out.append({'name':a.name,'type':'import','category':classify_python(a.name,internal)})
        elif isinstance(node, ast.ImportFrom):
            module=node.module or ''
            for a in node.names:
                full=f'{module}.{a.name}'.strip('.')
                out.append({'name':full,'type':'from_import','category':classify_python(module or a.name,internal)})
    return out

def js_deps(path: Path, repo: Path):
    text=path.read_text(encoding='utf-8',errors='replace'); out=[]
    patterns=[(r'\bimport\s+(?:[^;]*?\s+from\s+)?[\'\"]([^\'\"]+)[\'\"]','import'),(r'\brequire\(\s*[\'\"]([^\'\"]+)[\'\"]\s*\)','require'),(r'\bimport\(\s*[\'\"]([^\'\"]+)[\'\"]\s*\)','dynamic_import')]
    for pat, typ in patterns:
        for m in re.finditer(pat,text):
            name=m.group(1); cat='internal' if name.startswith('.') else 'external'; out.append({'name':name,'type':typ,'category':cat})
    return out

def main():
    ap=argparse.ArgumentParser(description='Extract dependencies for every inventory file.')
    ap.add_argument('--repo',required=True); ap.add_argument('--inventory',required=True); ap.add_argument('--output',default=str(Path(__file__).parent/'output'/'dependencies.json')); args=ap.parse_args()
    repo=Path(args.repo).resolve(); inv=json.loads(Path(args.inventory).read_text(encoding='utf-8')); internal=internal_module_index(repo); results=[]
    for item in inv.get('files',[]):
        rel=item.get('path'); lang=item.get('language'); p=repo/rel; deps=[]; err=None
        try:
            if lang=='Python': deps=python_deps(p,internal)
            elif lang in {'JavaScript','TypeScript'}: deps=js_deps(p,repo)
        except Exception as exc: err=str(exc)
        record={'file':rel,'dependencies':deps}
        if err: record['parse_error']=err
        results.append(record)
    payload={'files':results}
    out=Path(args.output); out.parent.mkdir(parents=True,exist_ok=True); out.write_text(json.dumps(payload,indent=2),encoding='utf-8')
    print(f'✅ Dependency extraction completed for {len(results)} files: {out}')
if __name__=='__main__': main()
