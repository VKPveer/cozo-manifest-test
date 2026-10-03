import argparse
import json
import os
from pathlib import Path

def load_json(p): return json.loads(Path(p).read_text(encoding='utf-8'))
def load_manifest(manifest_path, validation_path=None):
    if validation_path:
        report=load_json(validation_path)
        if report.get('status')!='VALID': raise ValueError('Manifest is not validated.')
    return load_json(manifest_path)

def files_by_symbol(m,name):
    return [f.get('path') for f in m.get('files',[]) if any(s.get('name')==name or s.get('class_name')==name for s in f.get('symbols',[]))]
def task_by_symbol(m,name):
    return [t.get('task_id') for t in m.get('traceability',[]) if (t.get('code_reference') or {}).get('symbol')==name]
def requirements_by_task(m,task):
    return [r for t in m.get('traceability',[]) if t.get('task_id')==task for r in t.get('requirement_ids',[])]
def commits_by_task(m,task):
    return [(t.get('git') or {}).get('commit_sha') for t in m.get('traceability',[]) if t.get('task_id')==task and (t.get('git') or {}).get('commit_sha')]
def deps_by_file(m,name):
    for f in m.get('files',[]):
        if f.get('path')==name or f.get('name')==name or os.path.basename(f.get('path',''))==name: return f.get('dependencies',[])
    return []

def interactive(m):
    while True:
        print('\n1 File(s) by symbol\n2 Task(s) by symbol\n3 Requirements by task\n4 Commits by task\n5 Dependencies by file\n6 Manifest version\n0 Exit')
        c=input('Choose option: ').strip()
        if c=='0': break
        if c=='1': print(files_by_symbol(m,input('Symbol/class: ').strip()))
        elif c=='2': print(task_by_symbol(m,input('Symbol: ').strip()))
        elif c=='3': print(requirements_by_task(m,input('Task ID: ').strip()))
        elif c=='4': print(commits_by_task(m,input('Task ID: ').strip()))
        elif c=='5': print(json.dumps(deps_by_file(m,input('File: ').strip()),indent=2))
        elif c=='6': print(m.get('manifest_version'))
        else: print('Invalid option')

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--manifest',default='input/project-manifest.json'); ap.add_argument('--validation-report'); ap.add_argument('--query',choices=['symbol-file','symbol-task','task-requirements','task-commits','file-dependencies']); ap.add_argument('--value'); args=ap.parse_args()
    m=load_manifest(args.manifest,args.validation_report)
    if not args.query: print('✅ Project manifest loaded'); interactive(m); return
    fn={'symbol-file':files_by_symbol,'symbol-task':task_by_symbol,'task-requirements':requirements_by_task,'task-commits':commits_by_task,'file-dependencies':deps_by_file}[args.query]
    print(json.dumps(fn(m,args.value or ''),indent=2))
if __name__=='__main__': main()
