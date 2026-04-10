---
paths:
  - "**/tasks*"
  - "**/gws-tasks*"
---

# Google Tasks Workflow

## When to Use

Decide autonomously. Register only meaningful work. Do NOT ask user — proceed automatically.

### Auto-register criteria (ALL must be met)

1. **5+ steps** required
2. **30+ minutes** estimated
3. **Clear deliverable** (code, docs, config, etc.)

Examples: project init, feature implementation, large refactoring, full PDCA cycle

### Do NOT register

- Q&A, search, file cleanup, skill install, config changes
- One-off commands (mark as read, create label, etc.)
- Tasks that finish within 10 minutes

## Workflow

### 1. Task start — create task list

```bash
gws tasks tasklists insert --json '{"title": "[Claude] {task_name}"}'

# Insert tasks in reverse order for correct display
gws tasks tasks insert --params '{"tasklist": "{list_id}"}' \
  --json '{"title": "Step 1: {description}", "notes": "{details}"}'
```

### 2. Step start — update notes

```bash
gws tasks tasks update --params '{"tasklist": "{list_id}", "task": "{task_id}"}' \
  --json '{"notes": "In progress - {current status}"}'
```

### 3. Step complete — mark done

```bash
gws tasks tasks update --params '{"tasklist": "{list_id}", "task": "{task_id}"}' \
  --json '{"status": "completed"}'
```

### 4. All complete — keep task list (as record)

Keep completed task lists in Google Tasks. Only delete when user requests.

## Naming Convention

- Task list: `[Claude] {task_name} ({date})`
- Task: `{number}. {step_name}`
- Notes: details, progress status, results

## Google Tasks vs Claude TodoWrite

| | Google Tasks | Claude TodoWrite |
|---|---|---|
| Persistence | Survives session end | Current session only |
| Purpose | Progress record, resume in next session | Current task tracking |
| Visibility | Google Tasks app | Claude conversation |
