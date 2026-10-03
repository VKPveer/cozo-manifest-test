from pathlib import Path
LANGUAGE_MAP = {'.py':'Python','.js':'JavaScript','.jsx':'JavaScript','.ts':'TypeScript','.tsx':'TypeScript','.java':'Java','.cs':'CSharp','.cpp':'C++','.c':'C','.h':'C/C++ Header','.hpp':'C++ Header','.go':'Go','.rs':'Rust','.php':'PHP','.rb':'Ruby','.sql':'SQL','.json':'JSON','.yaml':'YAML','.yml':'YAML'}
def detect_language(file_path):
    return LANGUAGE_MAP.get(Path(file_path).suffix.lower(), 'Unknown')
