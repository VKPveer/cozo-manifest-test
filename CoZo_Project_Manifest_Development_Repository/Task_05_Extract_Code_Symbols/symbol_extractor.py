import argparse
import json
from pathlib import Path


def extract_symbols(data):
    symbols = []
    for file_data in data.get('files', []):
        path = file_data.get('path')
        language = file_data.get('language')
        for cls in file_data.get('classes', []):
            symbols.append({'symbol_type':'class','name':cls.get('name'),'file':path,'language':language,'line_start':cls.get('line_start'),'line_end':cls.get('line_end')})
            for method in cls.get('methods', []):
                symbols.append({'symbol_type':'method','class_name':cls.get('name'),'name':method.get('name'),'signature':method.get('signature'),'parameters':method.get('parameters',[]),'file':path,'language':language,'line_start':method.get('line_start'),'line_end':method.get('line_end')})
        for func in file_data.get('functions', []):
            symbols.append({'symbol_type':'function','name':func.get('name'),'signature':func.get('signature'),'parameters':func.get('parameters',[]),'file':path,'language':language,'line_start':func.get('line_start'),'line_end':func.get('line_end')})
    return symbols


def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--input', required=True); ap.add_argument('--output', default=str(Path(__file__).parent/'output'/'symbols.json')); args=ap.parse_args()
    data=json.loads(Path(args.input).read_text(encoding='utf-8')); symbols=extract_symbols(data)
    p=Path(args.output); p.parent.mkdir(parents=True,exist_ok=True); p.write_text(json.dumps(symbols,indent=2),encoding='utf-8')
    print(f'✅ Symbol extraction completed: {len(symbols)} symbols -> {p}')
if __name__=='__main__': main()
