---
name: deep-interview
description: Relentless 1-on-1 interview that walks down every branch of the decision tree until shared understanding is reached
---
# Deep Interview - Relentless Requirements Discovery

## Purpose

Interview the user **one question at a time**, like a real conversation.
Walk down every branch of the decision tree. When an answer opens a new branch,
follow it before moving on. Don't stop until every assumption is surfaced,
every ambiguity resolved, and shared understanding is reached.

This is not a questionnaire. This is a **conversation**.

## Use When

- Vague or ambiguous task description
- User says "interview", "clarify", "what do I need?", "grill me"
- Before planning or implementation for complex features
- When multiple valid interpretations exist
- User wants to stress-test a plan or design

## Do Not Use When

- Requirements are already clear and specific
- Simple bug fix with obvious solution
- User has already provided detailed spec

## Modes

### Full Mode (Default) — up to 30 questions

Relentless exploration of every decision branch. Keeps going until all branches
are resolved or 30 questions are reached.

```
/deep-interview "build a notification system"
/deep-interview "redesign the authentication flow"
```

### Quick Mode — up to 10 questions

Focused pass on core areas only. Use when requirements are mostly clear.

```
/deep-interview --quick "add caching"
```

## Interview Protocol

### Phase 0: Explore the Codebase First

Before asking ANY questions, silently explore:
- Glob for related files
- Grep for related patterns
- Read key files to understand current state

If a question can be answered by exploring the codebase, **explore the codebase
instead of asking the user**. Never waste the user's time on questions the code
already answers.

### Phase 1: Open with Context

Start the interview by:
1. Stating what you already know from the codebase (2-3 sentences)
2. Stating your initial understanding of the task
3. Asking your **first question** — one question only

Example:
```
"I explored the project. It's Express + PostgreSQL with JWT auth.

You want a notification system — what triggers a notification?
For example, new comments, likes, follows, or system announcements?"
```

### Phase 2: One Question at a Time (Core Loop)

**Rules:**
1. **One question per turn.** Never ask multiple questions at once.
2. **Follow up on answers.** When an answer reveals a new branch, dig into it immediately.
3. **Resolve branches before moving on.** Never leave an unresolved branch behind.
4. **Check code instead of asking.** If the codebase can answer a question, look it up yourself.
5. **State assumptions and confirm.** "I'm assuming X — does that sound right?"
6. **Parallel explorer dispatch.** While waiting for the user's answer, if their previous answer
   mentioned a concept, module, or integration point, dispatch an explorer agent in the background
   to gather codebase context. Use this "free time" to inform your next question.

**Decision Tree Walking:**

```
Q1: "What triggers a notification?"
A1: "Comments, likes, follows"
  -> Branch found: 3 event types
Q2: "Are all three real-time, or are some batched via email?"
A2: "Comments are real-time, the rest are batched email"
  -> Branch found: real-time vs batch
Q3: "For real-time — WebSocket or SSE?"
A3: "WebSocket"
  -> Branch resolved -> move to next topic
Q4: "What's the batch interval for emails?"
...
```

**Coverage Areas** (cover only what's relevant — not all required):

| Area | What to Explore |
|------|----------------|
| **Problem** | Why is this needed? How is it currently handled? |
| **Users** | Who uses this? What's their skill level? |
| **Scope** | What's in and what's out? |
| **Data** | What data flows in/out? Where is it stored? |
| **Behavior** | Happy path? Edge cases? |
| **Integration** | Which existing systems does this touch? |
| **Performance** | Expected load, latency tolerance? |
| **Security** | Sensitive data? Auth/authz requirements? |
| **Error handling** | How should failures be communicated? |
| **Testing** | What level of test coverage is expected? |
| **Deployment** | Environment-specific considerations? |
| **Future** | What extensions might be needed later? |
| **Constraints** | Technical limits, timeline, dependencies? |
| **Validation** | How to determine completion? |

### Phase 3: Closing

When all branches are resolved:

1. **Present summary**: Show confirmed decisions in a structured format
2. **Check for gaps**: "Anything I missed?"
3. **Final confirmation**: "Ready to proceed with this?"

### Phase 4: Record & Transition

Save interview results to `docs/interviews/interview-{slug}-{YYYYMMDD-HHmm}.md`:

```markdown
---
title: "Interview: {task description}"
date: {YYYY-MM-DD}
tags: [interview, {topic-tag-1}, {topic-tag-2}]
type: interview
mode: full | quick
questions_asked: {count}
status: completed
---

# Interview: {task description}

## Summary
{2-3 sentence overview of what was discussed and key decisions}

## Q&A Transcript

| # | Question | Answer | Branch |
|---|----------|--------|--------|
| 1 | {question text} | {answer text} | {topic area} |
| 2 | {follow-up question} | {answer text} | {same or new topic} |
| ... | ... | ... | ... |

> **Note**: Branch column tracks which decision tree branch each Q&A belongs to.
> Long answers should be preserved in full, not summarized.

## Decisions Made
1. {decision}: {rationale}
2. ...

## Scope
- In scope: {list}
- Out of scope: {list}

## Technical Decisions
- {topic}: {choice} (because {reason})

## Constraints
- {constraint}: {impact}

## Assumptions Confirmed
- {assumption}: confirmed by user

## Open Questions
- {any remaining unknowns}
```

After saving the interview file, execute the **Plan Prompt Generation** sequence:

#### Step 1: Scan Available Tools

Silently scan the user's global harness to discover available capabilities:
- `~/.claude/skills/` — list all skill directories and read their SKILL.md descriptions
- `~/.claude/commands/` — list all command files and read their descriptions
- `~/.claude/agents/` — list all agent definitions if present

Build an internal catalog of available tools with their names and one-line descriptions.

#### Step 2: Match Tools to Interview Findings

From the interview decisions and scope, identify which skills/commands/agents
are relevant to the implementation. For example:
- Interview decided on "Next.js + Tailwind" → match `shadcn-ui`, `tailwind-theme-builder`, `frontend-design`
- Interview decided on "authentication needed" → match `bkit:bkend-auth`, `nextjs-supabase-auth`
- Interview decided on "mobile app" → match `bkit:mobile-app`
- Interview decided on "E2E testing" → match `playwright-e2e-testing`, `e2e`

#### Step 3: Generate & Output the Plan Prompt

Compose a detailed planning prompt and **output it directly in the chat** inside a copyable code block.
The prompt must incorporate all interview findings and matched tools:

```
══════════════════════════════════════════════════
📋 Interview Complete — {count} questions resolved

인터뷰 결과가 저장되었습니다:
  docs/interviews/interview-{slug}-{YYYYMMDD-HHmm}.md

──────────────────────────────────────────────────
📝 생성된 플랜 프롬프트 (복사해서 바로 사용 가능):
──────────────────────────────────────────────────
```

Then read `~/.claude/skills/deep-interview/plan-prompt-template.md`, fill in all `{placeholders}`
with actual interview results and matched tools, and output the filled prompt in a fenced code block.

## Anti-Patterns

| Don't | Why | Do Instead |
|-------|-----|-----------|
| Ask 5 questions at once | User gives shallow answers | One question per turn |
| "Is it A, B, or C?" | Forces premature choices | Open question first, then narrow |
| Ask what the code already answers | Wastes user time | Explore codebase first |
| Skip a branch to move on | Leaves unresolved assumptions | Resolve every branch fully |
| Repeat "What would you like?" | User may not know | Propose an assumption, then confirm |
| Always fill 30 questions | Unnecessary questions | End early when branches are resolved |

## Interview Style

- **Conversational**: Natural dialogue, not a rigid survey
- **Contextual linking**: "Following up on what you said about X..."
- **Assumption-first**: "Typically this is done with Y — does that work here?"
- **Adaptive depth**: Short answers = dig deeper. Detailed answers = move on faster.
- **Progress indicator**: Every 5 questions, state: "We've covered {N} questions so far, currently on {topic}"

## Constraints

- Full mode: max 30 questions (may end early when all branches are resolved)
- Quick mode: max 10 questions
- One question per turn (multiple questions per turn is strictly forbidden)
- If the codebase can answer a question, do not ask the user
- Show progress indicator every 5 questions

## Original Task

$ARGUMENTS
