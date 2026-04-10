# /oms-pro-max — Autonomous Full-Cycle Development Pipeline

You are the orchestrator of a 9-phase development pipeline.
Phases 0-3 are interactive (user reviews and approves).
Phases 4-8 are fully autonomous with Ralph loop (verify-improve cycle up to 10 times).

## Input

Feature description from `$ARGUMENTS`.
Example: `/oms-pro-max "OAuth 기반 사용자 인증 시스템"`

---

## PHASE 0: INITIALIZATION

### 0.1 Generate Slug
Convert the feature description to a kebab-case slug.
Example: "OAuth 기반 사용자 인증 시스템" → `oauth-user-auth`

### 0.2 Create Pipeline Directory
```
mkdir -p .pipeline/{interviews,prd,plans,design,reports,memory,logs}
```

### 0.3 Initialize State
Write `.pipeline/state.json`:
```json
{
  "slug": "{slug}",
  "feature": "{original description}",
  "currentPhase": 0,
  "ralph": { "iteration": 0, "maxIterations": 10 },
  "startedAt": "{ISO timestamp}",
  "phases": {
    "0": { "status": "in_progress", "artifacts": [] },
    "1": { "status": "pending", "artifacts": [] },
    "2": { "status": "pending", "artifacts": [] },
    "3": { "status": "pending", "artifacts": [] },
    "4": { "status": "pending", "artifacts": [] },
    "5": { "status": "pending", "artifacts": [] },
    "6": { "status": "pending", "artifacts": [] },
    "7": { "status": "pending", "artifacts": [] },
    "8": { "status": "pending", "artifacts": [] }
  }
}
```

### 0.4 Load Learnings
If `.pipeline/memory/learnings.json` exists, read it.
Display to user: "이전 실행에서 {count}개의 학습 패턴을 로드했습니다."

---

## PHASE 0: DEEP INTERVIEW (Interactive)

Use the `deep-interview` skill (global, from oh-my-stalab Harness).

1. Invoke `/deep-interview` with the feature description
2. Conduct the full interview (one question at a time)
3. Save result to `.pipeline/interviews/interview-{slug}.md`
4. Update state: phase 0 → completed

**Checkpoint**: User must confirm interview is complete before proceeding.

---

## PHASE 1: PRD CORE (Interactive)

Invoke the `pm-agent` (project agent, opus tier).

1. Pass the interview document as input
2. Agent generates `.pipeline/prd/prd-core-{slug}.md`
3. Present PRD to user for review
4. Update state: phase 1 → completed

**Checkpoint**: User reviews and approves the core PRD.
If user has feedback, pm-agent revises until approved.

---

## PHASE 2: PRD DETAIL + USER FLOWS (Interactive)

Invoke `pm-agent` again (opus tier).

1. Pass core PRD + interview as input
2. Agent generates:
   - `.pipeline/prd/prd-detail-{slug}.md`
   - `.pipeline/prd/user-flows-{slug}.md`
3. Present to user for review
4. Update state: phase 2 → completed

**Checkpoint**: User reviews and approves detailed PRD and flows.

---

## PHASE 3: PLAN — 3 ALTERNATIVES (Interactive)

Invoke `code-architect` agent (global, opus tier).

1. Pass all PRD documents as input
2. Request **exactly 3 plan alternatives**, each with:
   - Architecture overview
   - Technology choices
   - File structure
   - Pros and cons
   - Estimated complexity
3. Save all plans:
   - `.pipeline/plans/plan-{slug}-1.md`
   - `.pipeline/plans/plan-{slug}-2.md`
   - `.pipeline/plans/plan-{slug}-3.md`
4. Present all 3 to user with comparison table

**Checkpoint**: User selects one plan.
Record selected plan number in state.json: `"selectedPlan": 1|2|3`

Display message:
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Plan {n}번 선택됨. 자율 모드로 전환합니다.
Phase 4(설계) → 5(테스트) → 6(구현) → 7↔8(검증-개선)
완료까지 자동으로 진행합니다.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

Update state: phase 3 → completed

---

## ═══ AUTONOMOUS MODE BEGINS ═══

From this point forward, do NOT ask the user for confirmation.
Execute all phases sequentially, automatically.

---

## PHASE 4: DESIGN (Autonomous)

Invoke `code-architect` agent (global, opus tier).

1. Input: Selected plan + all PRDs + learnings (design_gap patterns)
2. Generate comprehensive design document:
   - System architecture diagram (ASCII)
   - Component breakdown
   - Data flow
   - API contracts (request/response schemas)
   - Database schema (if applicable)
   - Error handling strategy
   - Security considerations
3. Save to `.pipeline/design/design-{slug}.md`
4. Update state: phase 4 → completed

**Learning injection**: If learnings contain `design_gap` entries, the agent must address each one explicitly in the design.

---

## PHASE 5: TEST SCENARIOS — TDD RED (Autonomous)

Invoke `test-designer` agent (project agent, sonnet tier).

1. Input: Design + PRDs + user flows + learnings (test_failure patterns)
2. Agent creates failing test code following TDD RED methodology
3. Then invoke `tdd-guide` agent (global) to review test quality
4. Run tests to confirm all FAIL (RED state):
   ```bash
   npm test 2>&1 || true
   ```
5. Update state: phase 5 → completed, record test count

**Learning injection**: Create defensive tests for past `test_failure` and `type_error` patterns.

---

## PHASE 6: IMPLEMENTATION (Autonomous)

Invoke `code-architect` agent (global, sonnet tier) with subagents.

1. Input: Design + test code + learnings (type_error patterns)
2. Goal: Make ALL tests pass (TDD GREEN)
3. Strategy:
   - Read design document for architecture guidance
   - Read failing tests to understand expected behavior
   - Implement module by module
   - Run tests after each module to track progress
4. When all tests pass, run `tsc --noEmit` for type safety
5. Update state: phase 6 → completed

**Learning injection**: Avoid patterns flagged as `type_error` in learnings.

---

## PHASE 7: VERIFICATION (Autonomous — Ralph Loop Entry)

Invoke `verification-orchestrator` agent (project agent, opus tier).

1. Agent runs 5 parallel checks:
   - Test suite execution
   - Linter check
   - Type check (tsc --noEmit)
   - Code review (code-reviewer agent, global)
   - Gap analysis (bkit:gap-detector agent)
2. Agent generates `.pipeline/reports/verification-{slug}-{iteration}.md`
3. Update state with results

### If ALL PASS:
→ Jump to COMPLETION (skip Phase 8)

### If ANY FAIL:
→ Proceed to Phase 8

---

## PHASE 8: IMPROVEMENT (Autonomous — Ralph Loop Fix)

Based on verification failures, auto-fix:

### Fix Priority Order:
1. **Type errors** → Read error messages, fix type annotations
2. **Test failures** → Read failing test, fix implementation
3. **Linter errors** → Auto-fix where possible (`eslint --fix`), manual for rest
4. **Code review CRITICAL** → Address each issue
5. **Design gaps** → Invoke `bkit:pdca-iterator` for auto-improvement

### Fix Execution:
1. For each failure in priority order:
   - Read the error/issue
   - Identify the root cause
   - Apply the fix
   - If learnings contain a matching `how_fixed` pattern, apply that first
2. After all fixes applied → return to Phase 7

### Record Fix Patterns:
For each fix, record to learnings:
```json
{
  "type": "fix_pattern",
  "category": "{test_failure|type_error|lint_violation|design_gap}",
  "what_failed": "{description}",
  "why_failed": "{root cause}",
  "how_fixed": "{fix applied}",
  "iteration": {n}
}
```

Update state: phase 8 → completed, increment ralph.iteration

---

## RALPH LOOP (Phase 7 ↔ 8)

```
iteration = 0
while iteration < 10:
    result = run_phase_7()
    if result == PASS:
        break
    run_phase_8(result.fixList)
    iteration += 1

if iteration >= 10:
    generate_failure_report()
else:
    generate_success_report()
```

### Escalation Rules:
- **Same failure 3+ times**: Mark as "architectural issue", try different approach
- **Iteration 5+**: Reduce scope — focus on critical paths only
- **Iteration 8+**: Suggest scope reduction in report
- **Iteration 10**: Stop and generate failure report with recommendations

---

## COMPLETION

### Auto-Retro (Learning)

After Ralph loop completes (success or failure):

1. Analyze all verification reports in `.pipeline/reports/`
2. Extract patterns:
   - Most common failure types
   - Average iterations to fix each type
   - Persistent issues
3. Update `.pipeline/memory/learnings.json`:
   ```json
   {
     "learnings": [
       {
         "id": "L{next_id}",
         "type": "failure_pattern",
         "category": "{category}",
         "description": "{what went wrong}",
         "solution": "{what fixed it}",
         "frequency": {count},
         "lastSeen": "{date}",
         "applicablePhases": [5, 6]
       }
     ]
   }
   ```

### Final Report

Generate `.pipeline/reports/final-{slug}.md`:

```markdown
# Final Report — {feature}

## Result: SUCCESS / FAILURE

## Timeline
- Started: {timestamp}
- Completed: {timestamp}
- Duration: {duration}
- Ralph iterations: {count}

## Artifacts
- Interview: .pipeline/interviews/interview-{slug}.md
- PRD Core: .pipeline/prd/prd-core-{slug}.md
- PRD Detail: .pipeline/prd/prd-detail-{slug}.md
- User Flows: .pipeline/prd/user-flows-{slug}.md
- Plans: .pipeline/plans/plan-{slug}-{1,2,3}.md (selected: {n})
- Design: .pipeline/design/design-{slug}.md
- Verification Reports: .pipeline/reports/verification-{slug}-*.md

## Verification Summary
| Check | Final Status |
|-------|-------------|
| Tests | {status} ({pass}/{total}) |
| Linter | {status} |
| Types | {status} |
| Code Review | {status} |
| Gap Analysis | {status} ({match_rate}%) |

## Learnings Captured
{count} new patterns recorded to learnings.json

## Files Changed
{list of all files created or modified during implementation}
```

### Invoke bkit Report Generator
If bkit is available, also invoke `bkit:report-generator` for PDCA-format report.

### Display Completion
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
/oms-pro-max 완료
기능: {feature}
결과: {SUCCESS/FAILURE}
소요: {duration} | Ralph 반복: {iterations}회
학습: {learnings_count}개 패턴 기록
리포트: .pipeline/reports/final-{slug}.md
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

Update state: pipeline complete.

---

## STATE MANAGEMENT

After every phase transition, update `.pipeline/state.json`:
- Set completed phase status to `"completed"`
- Set next phase status to `"in_progress"`
- Add artifact paths to the phase's `artifacts` array
- Update `currentPhase` number
- On Ralph iterations, update `ralph.iteration`

If the session is interrupted, the state file allows resuming from the last completed phase.

---

## ERROR HANDLING

### Session Interruption
If Claude session ends mid-pipeline:
- State is preserved in `.pipeline/state.json`
- User can resume: `/oms-pro-max --resume`
- Resume reads state.json and continues from `currentPhase`

### Agent Failure
If any agent fails to produce output:
- Retry once with the same input
- If still fails, log the error and skip to next phase with a warning
- Record the failure in `.pipeline/logs/`

### No Test Framework
If the project has no test framework:
- Phase 5: Install appropriate framework (jest/vitest based on project)
- Record installation in state.json
