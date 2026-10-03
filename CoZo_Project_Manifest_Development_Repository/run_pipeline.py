import argparse
import json
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
BUILD = ROOT / 'build'


def run(*args):
    print('\n>', ' '.join(map(str,args)))
    subprocess.run([sys.executable, *map(str,args)], check=True)


def prepare_repo(repo: str | None, repo_zip: str | None) -> Path:
    if bool(repo) == bool(repo_zip):
        raise SystemExit('Provide exactly one of --repo or --repo-zip')
    if repo:
        p = Path(repo).resolve()
        if not p.is_dir(): raise SystemExit(f'Repository folder not found: {p}')
        return p
    z = Path(repo_zip).resolve()
    if not z.is_file(): raise SystemExit(f'Repository ZIP not found: {z}')
    target = BUILD / 'extracted_repo'
    if target.exists(): shutil.rmtree(target)
    target.mkdir(parents=True)
    with zipfile.ZipFile(z) as f: f.extractall(target)
    children=[p for p in target.iterdir() if p.is_dir()]
    return children[0] if len(children)==1 else target


def main():
    ap=argparse.ArgumentParser(description='Run the complete CoZo project-manifest pipeline against a real cloned repo or GitHub ZIP.')
    ap.add_argument('--repo', help='Path to cloned GitHub repository')
    ap.add_argument('--repo-zip', help='Path to GitHub/project ZIP; extracted automatically')
    ap.add_argument('--work-items', help='Optional neutral Requirement→Story→Task JSON contract for traceability')
    ap.add_argument('--repository-url', default='', help='Useful for ZIPs, which do not contain .git metadata')
    ap.add_argument('--branch', default='')
    ap.add_argument('--commit-sha', default='')
    args=ap.parse_args()

    BUILD.mkdir(exist_ok=True)
    repo=prepare_repo(args.repo,args.repo_zip)
    inventory=BUILD/'file_inventory.json'; languages=BUILD/'language_inventory.json'; structure=BUILD/'code_structure.json'; symbols=BUILD/'symbols.json'; deps=BUILD/'dependencies.json'; base=BUILD/'base-project-manifest.json'; gitmeta=BUILD/'git_metadata.json'; trace=BUILD/'traceability.json'; final=BUILD/'project-manifest.json'; report=BUILD/'validation_report.json'

    run(ROOT/'Task_02_Build_Repository_Scanner/repository_scanner.py','--repo',repo,'--output',inventory)
    run(ROOT/'Task_03_Implement_Language_Detection/update_inventory_language.py','--input',inventory,'--output',languages)
    run(ROOT/'Task_04_Implement_Code_Parser/python_parser.py','--repo',repo,'--inventory',languages,'--output',structure)
    run(ROOT/'Task_05_Extract_Code_Symbols/symbol_extractor.py','--input',structure,'--output',symbols)
    run(ROOT/'Task_06_Extract_Imports_Dependencies/dependency_extractor.py','--repo',repo,'--inventory',languages,'--output',deps)
    run(ROOT/'Task_07_Generate_Project_Manifest/manifest_generator.py','--inventory',inventory,'--languages',languages,'--structure',structure,'--symbols',symbols,'--dependencies',deps,'--output',base)
    git_args=[ROOT/'Task_08_Add_Git_Metadata/git_metadata.py','--repo',repo,'--output',gitmeta]
    if args.repository_url: git_args += ['--repository-url',args.repository_url]
    if args.branch: git_args += ['--branch',args.branch]
    if args.commit_sha: git_args += ['--commit-sha',args.commit_sha]
    run(*git_args)
    trace_args=[ROOT/'Task_09_Code_Traceability_Mapping/traceability_mapper.py','--symbols',symbols,'--output',trace]
    if args.work_items: trace_args += ['--work-items',Path(args.work_items).resolve()]
    run(*trace_args)
    run(ROOT/'Task_10_Manifest_Update_Code_Changes/final_manifest_generator.py','--base-manifest',base,'--git-metadata',gitmeta,'--traceability',trace,'--output',final)
    run(ROOT/'Task_11_Manifest_Validation_Tests/validate_manifest.py','--manifest',final,'--schema',ROOT/'Task_01_Define_Project_Manifest_Schema/manifest-schema.json','--output',report)
    print('\n✅ COMPLETE')
    print('Repository:', repo)
    print('Manifest:', final)
    print('Validation:', report)

if __name__=='__main__': main()
