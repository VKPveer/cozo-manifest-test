import argparse
import json
from datetime import datetime, timezone
from pathlib import Path


def load(path): return json.loads(Path(path).read_text(encoding='utf-8'))
def norm(p): return str(p or '').replace('\\','/')


def main():
    ap=argparse.ArgumentParser(description='Generate base project manifest from repository-wide analysis outputs.')
    ap.add_argument('--inventory',required=True); ap.add_argument('--languages',required=True); ap.add_argument('--structure',required=True); ap.add_argument('--symbols',required=True); ap.add_argument('--dependencies',required=True); ap.add_argument('--output',default=str(Path(__file__).parent/'output'/'project-manifest.json')); args=ap.parse_args()
    inv=load(args.inventory); langs=load(args.languages); struct=load(args.structure); symbols=load(args.symbols); deps=load(args.dependencies)
    lang_map={norm(x.get('path')):x.get('language','Unknown') for x in langs.get('files',[])}
    struct_map={norm(x.get('path')):x for x in struct.get('files',[])}
    dep_map={norm(x.get('file')):x.get('dependencies',[]) for x in deps.get('files',[])}
    sym_map={}
    for s in symbols:
        sym_map.setdefault(norm(s.get('file')),[]).append(s)
    files=[]
    for item in inv.get('files',[]):
        p=norm(item.get('path')); parsed=struct_map.get(p,{})
        files.append({
            'path':p,'name':item.get('name'),'extension':item.get('extension'),'type':item.get('type','source'),
            'language':lang_map.get(p,'Unknown'),'size':item.get('size'),'hash':item.get('hash'),'last_modified':item.get('last_modified'),
            'classes':parsed.get('classes',[]),'functions':parsed.get('functions',[]),'symbols':sym_map.get(p,[]),'dependencies':dep_map.get(p,[]),
            **({'parse_error': parsed.get('parse_error')} if parsed.get('parse_error') else {})
        })
    manifest={'manifest_version':'1.0','generated_at':datetime.now(timezone.utc).isoformat(),'repository':{'name':'','url':'','branch':'','commit_sha':''},'files':files,'traceability':[]}
    out=Path(args.output); out.parent.mkdir(parents=True,exist_ok=True); out.write_text(json.dumps(manifest,indent=2),encoding='utf-8')
    print(f'✅ Base project manifest generated: {out} ({len(files)} files)')
if __name__=='__main__': main()
