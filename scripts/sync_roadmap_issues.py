#!/usr/bin/env python3
"""
Sync GitHub issues with Science Data Kit roadmaps.
Creates issues for 'To Do' tasks and updates existing issues with progress.
"""

import re
import subprocess
import json
from pathlib import Path
from typing import List, Dict, Tuple

def parse_roadmap_tasks(roadmap_file: Path) -> List[Dict]:
    """Extract tasks from roadmap markdown tables."""
    tasks = []
    
    with open(roadmap_file, 'r') as f:
        content = f.read()
    
    # Find task tables (look for | Task | Priority | Status | Notes |)
    table_pattern = r'\| Task \| Priority \| Status \| Notes \|.*?\n\|[^\n]+\|\n((?:\|[^\n]+\|\n)*)'
    tables = re.findall(table_pattern, content, re.DOTALL)
    
    for table in tables:
        # Parse individual task rows
        rows = table.strip().split('\n')
        for row in rows:
            if '|' in row and 'To Do' in row:
                parts = [p.strip() for p in row.split('|')[1:-1]]  # Remove empty first/last
                if len(parts) >= 4:
                    tasks.append({
                        'task': parts[0],
                        'priority': parts[1],
                        'status': parts[2],
                        'notes': parts[3],
                        'roadmap_file': roadmap_file.name
                    })
    
    return tasks

def create_github_issue(task: Dict) -> None:
    """Create a GitHub issue for a roadmap task."""
    title = f"Roadmap Task: {task['task']}"
    
    # Determine component from roadmap filename
    component = "general"
    if "kg" in task['roadmap_file'].lower():
        component = "knowledge-graph"
    elif "designux" in task['roadmap_file'].lower():
        component = "design-ux"
    elif "repo" in task['roadmap_file'].lower():
        component = "repository"
    
    body = f"""**Roadmap**: {task['roadmap_file']}
**Priority**: {task['priority']}
**Component**: {component}

**Task Description**: {task['task']}

**Notes**: {task['notes']}

**Implementation Checklist**:
- [ ] Analyze task requirements and dependencies
- [ ] Design solution approach
- [ ] Implement necessary changes
- [ ] Test implementation thoroughly
- [ ] Update roadmap status to 'Completed'
- [ ] Document implementation details

**Testing Requirements**:
- [ ] Use appropriate testing prompts from docs/roadmaps/prompts.md
- [ ] Validate integration with existing components
- [ ] Update testing status in docs/roadmaps/index.md

*Auto-created from roadmap task tracking*"""

    # Create the issue using GitHub CLI
    cmd = [
        'gh', 'issue', 'create',
        '--title', title,
        '--body', body,
        '--label', 'roadmap',
        '--label', f'roadmap-{component}',
        '--label', f'priority-{task["priority"].lower()}',
        '--assignee', '@me'
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        print(f"✅ Created issue for: {task['task']}")
        print(f"   Issue URL: {result.stdout.strip()}")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to create issue for: {task['task']}")
        print(f"   Error: {e.stderr}")

def main():
    """Main function to sync roadmap tasks with GitHub issues."""
    roadmap_dir = Path('docs/roadmaps/active')
    
    if not roadmap_dir.exists():
        print("❌ Roadmap directory not found: docs/roadmaps/active")
        return
    
    print("🔍 Scanning for roadmap files...")
    roadmap_files = list(roadmap_dir.glob('roadmap_*.md'))
    
    if not roadmap_files:
        print("❌ No roadmap files found")
        return
    
    print(f"📋 Found {len(roadmap_files)} roadmap files")
    
    all_tasks = []
    for roadmap_file in roadmap_files:
        print(f"   Parsing: {roadmap_file.name}")
        tasks = parse_roadmap_tasks(roadmap_file)
        all_tasks.extend(tasks)
    
    todo_tasks = [task for task in all_tasks if task['status'] == 'To Do']
    
    if not todo_tasks:
        print("✅ No 'To Do' tasks found - all roadmap tasks are completed or in progress!")
        return
    
    print(f"\n📝 Found {len(todo_tasks)} 'To Do' tasks")
    print("Creating GitHub issues...")
    
    for task in todo_tasks:
        create_github_issue(task)
    
    print(f"\n✅ Roadmap sync completed!")
    print(f"   Use 'gh issue list --label roadmap' to see all roadmap issues")

if __name__ == '__main__':
    main()