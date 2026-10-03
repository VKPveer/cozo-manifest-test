"""Compatibility/demo adapter.
Production code should export Requirement→Story→Task records from the real CoZo API/Mongo models
into the neutral work-items contract accepted by traceability_mapper.py. No collection names are assumed here.
"""
import json
from pathlib import Path

EXAMPLE={"items":[{"tenant_id":"TENANT-001","project_id":"PROJ-001","requirement_ids":["REQ-001"],"story_id":"STORY-001","task_id":"TASK-001","task_run_id":"RUN-001","code_reference":{"file":"src/user_service.py","class_name":"UserService","symbol":"create_user"}}]}
if __name__=='__main__':
    p=Path('input/work_items.example.json'); p.parent.mkdir(parents=True,exist_ok=True); p.write_text(json.dumps(EXAMPLE,indent=2),encoding='utf-8'); print(f'Example neutral work-item contract written to {p}')
