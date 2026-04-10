# TeleHub Orchestrator 설계

## Context

현재 TeleHub은 "라우터"일 뿐 "오케스트레이터"가 아니다. `;얘들아 서로 인사나눠` 같은 요청 시 4봇이 동시 응답 + 핸드오프 폭발 → 16+개 메시지 카오스. 봇 간 협업(턴 관리, 응답 릴레이, 의존성)이 불가능. 이를 해결하기 위해 Hub에 Claude 기반 Orchestrator 레이어를 추가한다.

## 핵심 결정: Fast Path / AI Path 분리

```
메시지 수신
├─ ;이름 task     → Fast Path (파서, 0ms)    ← 기존 그대로
├─ Reply to bot  → Fast Path
├─ /system       → Fast Path
└─ ;얘들아 / multi → AI Path (Orchestrator, ~1초 Haiku)
```

- 단순 1:1 호출은 기존 파서 유지 (속도)
- 브로드캐스트/멀티봇은 Orchestrator가 판단

## 구현 계획

### 1. 신규: `src/core/orchestrator.ts` (~200줄)

```typescript
interface ExecutionStep {
  id: string;              // "step-1"
  bot: string;             // "김제헌"
  task: string;            // 봇에게 전달할 메시지
  dependsOn?: string[];    // 선행 step (없으면 즉시 실행)
  relayFrom?: string;      // 이전 step 응답을 컨텍스트에 포함
}

interface ExecutionPlan {
  type: 'sequential' | 'parallel' | 'mixed';
  steps: ExecutionStep[];
}
```

**핵심 함수:**
- `createPlan(message, bots)` — Haiku CLI로 ExecutionPlan JSON 생성
- `executePlan(plan, context)` — step별 실행 엔진
  - `dependsOn` 없는 step → 동시 실행
  - `dependsOn` 있는 step → 선행 완료 후 실행
  - `relayFrom` 있는 step → 선행 응답을 task에 주입
- `buildOrchestratorPrompt(bots, message)` — 봇 목록 + 판단 규칙 + JSON 형식

**Orchestrator Prompt 핵심:**
```
봇 목록: [이름(역할)] ...
사용자 요청: "{message}"

판단 기준:
- "서로 인사해" → sequential (한 명씩 차례로, 이전 응답 릴레이)
- "각자 의견" → parallel (동시 실행)
- "A가 조사하고 B가 구현" → mixed (A 먼저, 결과를 B에게)
- 단순 질문 → parallel (기존 broadcast 동일)

JSON만 출력:
```

**CLI 호출:** `claude --model haiku -p --output-format text --dangerously-skip-permissions`

### 2. 수정: `src/bot/manager.ts` — dispatchAndWait 추가

```typescript
async dispatchAndWait(route: RouteResult): Promise<{ output: string; sessionId: string }>
```
- EventBus의 `bot:complete` / `bot:error`를 Promise로 래핑
- Orchestrator가 봇 응답을 기다린 후 다음 step 실행
- 타임아웃: `healthTimeoutMs` 재활용

### 3. 수정: `src/app.ts` — broadcast/multi 분기 변경

**Before:**
```typescript
if (parsed.type === 'broadcast') {
  router.routeBroadcast(parsed).then(...)
}
if (parsed.type === 'multi') {
  for (const botName of parsed.botNames) dispatch(...)
}
```

**After:**
```typescript
if (parsed.type === 'broadcast' || parsed.type === 'multi') {
  orchestrator.handle(parsed).catch(...)
}
```

- "계획 중..." thinking 메시지 표시 (Haiku 응답 1초 대기)
- Plan 생성 후 step-by-step 실행

### 4. 수정: `src/core/router.ts` — 축소

- `routeBroadcast()` 제거 (orchestrator로 이관)
- `runClaudeOnce()` 제거 (orchestrator가 자체 CLI 호출)
- `isGeneralMessage()` 제거 (orchestrator가 판단)
- Router는 순수 1:1 매핑만 담당

### 5. 수정: `src/core/queue.ts` — RouteResult.source 확장

- `source` 타입에 `'orchestrated'` 추가

### 6. 수정: `src/core/event-bus.ts` — 이벤트 추가

```typescript
| { type: 'orchestrator:plan'; steps: number }
| { type: 'orchestrator:step'; bot: string; status: 'start' | 'complete' }
```

### 7. 핸드오프 변경

- **Orchestrated 모드** (AI Path): handoff 감지 비활성화. Orchestrator가 turnOrder/relayFrom으로 통제
- **Fast Path**: 기존 handoff 로직 유지 (`;이름` regex + depth 제한)
- `manager.ts`의 `onComplete`에서: `route.source === 'orchestrated'`이면 handoff 감지 스킵

### 8. 설정: `src/config/schema.ts` + `hub-config.json`

```typescript
settings: {
  orchestratorModel: z.string().default('haiku'),
}
```

## 실행 흐름 예시

### `;얘들아 서로 인사나눠`

```
1. Parser: broadcast, text="서로 인사나눠"
2. Orchestrator: Haiku 호출 (~1초)
   → Plan: sequential, steps:
     [제헌→"팀원들에게 인사해", 용훈→"제헌이 인사했어, 너도 해", ...]
3. "계획 중..." 메시지 삭제
4. Step 1: 제헌 dispatch + wait → "안녕하세요! 리서처 김제헌입니다."
5. Step 2: 용훈 dispatch("제헌이 '안녕하세요!...'라고 함. 너도 인사해") + wait
6. Step 3, 4: 이전 대화 누적하며 진행
→ 텔레그램에서 자연스러운 순차 대화처럼 보임
```

### `;얘들아 각자 이번주 할일 보고해`

```
1. Orchestrator → Plan: parallel, all 4 bots
2. 4봇 동시 dispatch (기존 broadcast 동일)
→ 핸드오프 감지 꺼져있으므로 각자 응답만 하고 끝
```

## 파일 변경 요약

| 파일 | 변경 | 줄 수 |
|------|------|-------|
| `src/core/orchestrator.ts` | **신규** | ~200 |
| `src/bot/manager.ts` | `dispatchAndWait()` 추가 | +30 |
| `src/app.ts` | broadcast/multi → orchestrator | ~±15 |
| `src/core/router.ts` | routeBroadcast/runClaudeOnce 제거 | -60 |
| `src/core/queue.ts` | source에 'orchestrated' 추가 | +1 |
| `src/core/event-bus.ts` | 이벤트 타입 추가 | +3 |
| `src/config/schema.ts` | orchestratorModel 필드 | +1 |

## 검증

1. **빌드**: `tsc --noEmit`
2. **테스트**: `vitest run` (기존 108개 + orchestrator 신규 테스트)
3. **수동 테스트 (맥)**:
   - `;제헌아 안녕` → Fast Path, 기존 동작 확인
   - `;얘들아 서로 인사나눠` → sequential 실행, 자연스러운 턴
   - `;얘들아 각자 할일 보고` → parallel 실행
   - `;제헌 ;용훈 협업해서 분석해` → mixed plan
