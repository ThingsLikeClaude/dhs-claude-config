# Orchestration Enhancement + Research Phase

## Context

noyeah-harness has 12 agents but only 7 are actively used. 5 agents (security-reviewer, verifier, debugger, explorer, writer) sit at 0-5% utilization. Additionally, when building something with known competitors (e.g., "팀 협업앱 만들어줘"), no external research happens — the system relies solely on LLM training data.

**Goals:**
1. Activate all 12 agents with automatic dispatch triggers
2. Add a 13th agent (`researcher`) for competitive intelligence via MCP tools
3. Maximize parallelism where sequential execution is unnecessary

---

## Files to Modify (17 total)

### New Files (3)
| File | Purpose |
|------|---------|
| `agents/researcher.md` | New research agent definition |
| `docs/research-phase.md` | Research phase documentation |
| `docs/contracts/research-contract.md` | Research I/O schema |

### Modified Files (14)
| File | Changes |
|------|---------|
| `skills/noyeah-ralph/SKILL.md` | +security gate, +debugger escalation, +build-fixer auto, +verifier agent, +4-agent panel, +writer auto |
| `skills/noyeah-autopilot/SKILL.md` | +research phase, +agent-based QA, +critic in validation |
| `skills/noyeah-ralplan/SKILL.md` | +parallel planner+architect, +research context injection |
| `skills/noyeah-deep-interview/SKILL.md` | +parallel explorer during Q&A |
| `skills/noyeah-team/SKILL.md` | +mixed team composition syntax |
| `skills/noyeah-ultrawork/SKILL.md` | +semantic conflict detection in integrator |
| `docs/contracts/dispatch-templates.md` | +researcher dispatch template |
| `docs/contracts/core-contracts.md` | +research_path in planner input |
| `docs/contracts/noyeah-ralph-state-contract.md` | +failure_tracking field |
| `docs/architecture.md` | Updated composition diagram |
| `docs/agent-tiers.md` | +researcher row, +security-reviewer/build-fixer/writer rows |
| `rules/keyword-detection.md` | +research auto-detection rules |
| `rules/delegation-rules.md` | +researcher dispatch rule |
| `CLAUDE.md` | +researcher in agent table (13 agents), updated composition model |

---

## Implementation Order

### Group A (parallel, no dependencies)
1. `agents/researcher.md` — New agent definition
2. `rules/keyword-detection.md` — Research auto-detection
3. `skills/noyeah-deep-interview/SKILL.md` — Explorer parallel dispatch
4. `skills/noyeah-team/SKILL.md` — Mixed team syntax
5. `skills/noyeah-ultrawork/SKILL.md` — Semantic integrator

### Group B (depends on Group A)
6. `skills/noyeah-ralph/SKILL.md` — 6 major changes
7. `skills/noyeah-autopilot/SKILL.md` — Research phase + QA + validation
8. `skills/noyeah-ralplan/SKILL.md` — Parallel planning + research injection

### Group C (depends on Group B)
9-17. All docs, contracts, CLAUDE.md updates

---

## Detailed Changes

### 1. New Agent: `agents/researcher.md`

- **Tier**: STANDARD (sonnet) — web search doesn't need opus, but synthesis needs more than haiku
- **Posture**: deep-worker
- **Tools**: Read, Write, Glob, Grep, Bash (needs Write for saving reports)
- **Protocol**:
  1. Parse task → extract domain keywords
  2. `mcp__exa__web_search_exa` → competitor discovery (max 4 searches)
  3. `mcp__exa__web_search_exa` → architecture patterns (max 2 searches)
  4. `mcp__jina-reader__jina_reader` → deep-read top 3 competitor pages
  5. `mcp__exa__get_code_context_exa` → implementation patterns (max 2 searches)
  6. Synthesize → structured report
- **Output**: `.harness/context/research-{slug}-{ts}.md`
- **Cost control**: Max 8 web searches, max 3 Jina reads per run
- **Output format**:
  ```
  # Research: {task}
  ## Competitors ({N} found)
  ## Architecture Patterns
  ## Feature Matrix
  ## UX Patterns
  ## Technical Recommendations
  ## Summary (500 tokens, for prompt injection)
  ```

### 2. Research Auto-Detection (`rules/keyword-detection.md`)

Add section:
```
## Research Auto-Detection

Trigger when ALL conditions met:
1. Creation verb: "만들어줘", "build", "create", "make", "develop", "구현"
2. Domain noun: "app", "platform", "system", "tool", "service", "site", "dashboard"
3. Task is NOT referencing an existing file/path (greenfield)

Domain mapping for search queries:
| Keywords | Category | Example Searches |
|----------|----------|-----------------|
| collaboration, team, project | PM/Collab | "team collaboration app features 2026" |
| e-commerce, shop, store | E-commerce | "e-commerce platform architecture" |
| social, feed, follow | Social | "social media app architecture patterns" |
| chat, messaging, real-time | Communication | "real-time chat architecture" |
| analytics, dashboard | Analytics | "analytics dashboard patterns" |

Skip research: /noyeah-autopilot --no-research "task"
Force research: /noyeah-autopilot --research "task"
```

### 3. Ralph 6 Changes (`skills/noyeah-ralph/SKILL.md`)

**3a. Security Gate (Step 2, after GREEN)**
```
After GREEN phase, if task involves auth/user-input/API/DB:
  Dispatch security-reviewer(opus) IN PARALLEL with next iteration prep
  Verdict: BLOCK → pause, surface to user
           FIX_BEFORE_MERGE → add to next iteration TODO
           ACCEPTABLE → log and continue
  Non-blocking: does not slow the loop
```

**3b. Debugger Auto-Escalation (Step 2)**
```
Track error_signature → count in ralph-state.json
Same error 2x → dispatch debugger(sonnet) INSTEAD of executor
  debugger uses 5-step protocol: REPRODUCE → GATHER → HYPOTHESIZE → FIX → VERIFY
Reset count after successful fix
```

**3c. Build-Fixer Auto-Dispatch (Step 2)**
```
Build FAIL → dispatch build-fixer(sonnet) IN PARALLEL
  executor continues non-build tasks
  build failure does NOT count toward debugger escalation
```

**3d. Verifier Agent (Step 3)**
```
Replace inline verification with:
  Dispatch verifier(sonnet) → structured evidence output
  PASS → Step 4
  FAIL/INCOMPLETE → add to next iteration TODO → loop to Step 2
Benefit: executor can prep next iteration while verifier checks
```

**3e. 4-Agent Validation Panel (Step 4)**
```
Replace single architect with 4 parallel agents:
  architect(sonnet/opus) — correctness
  critic(opus) — plan adherence + tradeoffs + ADR
  security-reviewer(opus) — final security scan
  writer(haiku) — doc update check (advisory)
Approval: architect + critic + security must approve
  writer findings noted for Step 5.5
```

**3f. Auto Writer (new Step 5.5)**
```
If writer-check found doc updates needed:
  Dispatch writer(haiku) → update docs
  Non-blocking: proceed to completion regardless
```

### 4. Autopilot 3 Changes (`skills/noyeah-autopilot/SKILL.md`)

**4a. Research Phase (new Phase 0.5)**
```
After intake, if research auto-detection triggers:
  Dispatch researcher(sonnet) → wait for report
  Extract research_summary (500 tokens)
  Store research_path in autopilot-state.json
  Pass both to Phase 1 (planning)
```

**4b. Agent-Based QA (Phase 3)**
```
Replace inline QA with per-cycle agents:
  verifier(sonnet) → check
  If FAIL: debugger(sonnet) → diagnose, executor(sonnet) → fix
  Same failure 3x → escalate to user
```

**4c. 4-Agent Validation (Phase 4)**
```
Add critic(opus) as 4th parallel reviewer
  Now: correctness + security + maintainability + critic
```

### 5. Ralplan 2 Changes (`skills/noyeah-ralplan/SKILL.md`)

**5a. Parallel Planner + Architect**
```
Instead of: Planner → Architect → Critic (sequential)
Now: Planner + Architect (parallel) → Architect reconciles → Critic validates

Planner produces plan. Architect independently produces analysis.
Then Architect reviews planner's plan WITH its own prior analysis.
Critic validates the reconciled result.
~40% planning time reduction.
```

**5b. Research Context Injection**
```
If .harness/context/research-{slug}-*.md exists:
  Inject research_summary into both planner and architect prompts
  Full report path available for on-demand reading
```

### 6. Deep-Interview 1 Change

**Parallel Explorer**
```
While waiting for user answer:
  If previous answer mentioned a concept/module:
    Dispatch explorer(haiku) IN BACKGROUND
    Use results to inform next question
  Fire-and-forget: natural "free time" during user input wait
```

### 7. Team 1 Change

**Mixed Composition**
```
New syntax: /noyeah-team executor+test-engineer+security-reviewer "task"
Parse: "+" delimiter → one worker per role
Each worker uses its own agent file and default tier
Leader decomposes task into role-appropriate subtasks
```

### 8. Ultrawork 1 Change

**Semantic Integrator**
```
After agents complete, integrator checks:
  File overlaps (existing) + semantic conflicts (new):
  - Compatible assumptions about shared state?
  - APIs match at module boundaries?
  - Naming/typing conflicts?
  TRIVIAL → auto-resolve
  COMPLEX → escalate to architect
```

---

## Agent Utilization: Before vs After

| Agent | Before | After | Trigger |
|-------|--------|-------|---------|
| security-reviewer | 0% | Medium | Auto after GREEN + final panel |
| verifier | 0% | High | Replaces inline verification |
| debugger | ~5% | Medium | Auto-escalation on 2x failure |
| explorer | 0% | Low-Med | Parallel during deep-interview |
| writer | ~2% | Low-Med | Auto after Ralph completion |
| researcher | N/A | Medium | New: research phase |
| build-fixer | ~5% | Medium | Auto on build failure |
| critic | Medium | High | Added to Ralph final panel |

**Active agents per full autopilot run: 7 → 13**

---

## Research Context Flow

```
"팀 협업앱 만들어줘"
  → Auto-detect: creation verb + domain noun
  → researcher(sonnet): Exa search competitors, Jina deep-read top 3
  → .harness/context/research-team-collab-{ts}.md
  → research_summary (500 tokens) injected into:
    → planner prompt (informed plan)
    → architect prompt (informed review)
    → executor (report path available on demand)
```

---

## Verification Plan

1. **Syntax check**: All SKILL.md files parse correctly as markdown
2. **Cross-reference**: Every agent mentioned in skills has a corresponding `agents/*.md` file
3. **State schema**: ralph-state.json updated schema is backward-compatible (new fields optional)
4. **Keyword detection**: New rules don't conflict with existing trigger keywords
5. **CLAUDE.md consistency**: Agent count, composition diagram, skill descriptions all match
6. **Dry run**: Walk through "팀 협업앱 만들어줘" mentally through the full autopilot flow to verify all phases connect
