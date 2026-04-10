# Plan: Thinking UX 개선 + 세션 관리

## Context

현재 AI 에이전트 응답 시 **DELETE(생각중) → INSERT(응답)** 2단계 패턴 사용 중.
두 DB 트랜잭션 사이 시간차로 메시지가 깜빡이며 사라졌다 나타나는 어색한 UX 발생.
또한 매 호출이 완전 독립적이라 AI가 이전 대화를 전혀 기억하지 못함.

**목표:**
1. Thinking → 응답이 **같은 메시지 UPDATE**로 부드럽게 전환
2. 채널 내 최근 대화를 컨텍스트로 전달하여 **대화 연속성** 확보

---

## Part 1: Thinking → Response UPDATE 패턴

### 1-1. DB 마이그레이션 (새 파일)
**파일:** `supabase/migrations/20260401000001_add_thinking_type_and_update_rls.sql`

```sql
-- 1) message type에 'thinking' 추가
ALTER TABLE channel_messages DROP CONSTRAINT channel_messages_type_check;
ALTER TABLE channel_messages ADD CONSTRAINT channel_messages_type_check 
  CHECK (type IN ('text', 'buttons', 'card', 'table', 'status', 'thinking'));

-- 2) agent가 자기 메시지를 UPDATE할 수 있는 RLS 정책 (향후 확장용)
-- 현재 listener는 service_role로 RLS 우회하므로 당장 필수는 아님
CREATE POLICY "messages_update_own" ON channel_messages
  FOR UPDATE USING (author_id = auth.uid())
  WITH CHECK (author_id = auth.uid());
```

> **참고:** listener는 service_role key 사용 → RLS 우회. UPDATE 정책은 향후 클라이언트 직접 수정 대비용.

### 1-2. TypeScript 타입 업데이트
**파일:** `frontend/src/types/channel.types.ts`

- `MessageType`에 `'thinking'` 추가
- `ThinkingMetadata` 인터페이스 추가: `{ type: 'thinking' }`
- `MessageMetadata` 유니온에 `ThinkingMetadata` 추가
- Zod 스키마에 `z.object({ type: z.literal('thinking') })` 추가

### 1-3. ThinkingBlock 컴포넌트 생성
**파일:** `frontend/src/components/channel/message/blocks/ThinkingBlock.tsx` (새 파일)

- 3개 pulsing dots + shimmer 그라데이션 효과
- "생각하는 중..." 텍스트와 함께 애니메이션
- 에이전트 느낌의 보라색 테마

### 1-4. MessageBubble renderBlock 업데이트
**파일:** `frontend/src/components/channel/message/MessageBubble.tsx`

- `renderBlock` switch에 `case 'thinking': return <ThinkingBlock />;` 추가

### 1-5. useMessageCache에 updateMessage 추가
**파일:** `frontend/src/hooks/useMessageCache.ts`

```typescript
export function updateMessage(
  queryClient: QueryClient,
  channelId: string,
  updatedMsg: ChannelMessage
) {
  queryClient.setQueryData<ChannelMessage[]>(
    queryKeys.messages.byChannel(channelId),
    (old) => {
      if (!old) return [updatedMsg];
      return old.map((m) => m.id === updatedMsg.id ? updatedMsg : m);
    }
  );
}
```

### 1-6. useChannelRealtime에 UPDATE 이벤트 구독 추가
**파일:** `frontend/src/hooks/useChannelRealtime.ts`

- 기존 INSERT, DELETE 구독 체인에 `.on('postgres_changes', { event: 'UPDATE', ... })` 추가
- `payload.new`를 `parseMessage()`로 파싱 후 `updateMessage()` 호출

### 1-7. task-runner를 DELETE+INSERT → UPDATE로 변경
**파일:** `listener/src/task-runner.ts`

**Before (현재):**
```typescript
// thinking 메시지 삽입
insert({ type: 'status', metadata: { type: 'status', status: 'thinking' }, content: '생각하는 중...' })
// 응답 후
delete().eq('id', thinkingMsg.id)
insert({ type: 'text', metadata: { type: 'text' }, content: response })
```

**After (변경):**
```typescript
// thinking 메시지 삽입
insert({ type: 'thinking', metadata: { type: 'thinking' }, content: '' })
// 응답 후
update({ type: 'text', metadata: { type: 'text' }, content: response }).eq('id', thinkingMsg.id)
```

### 1-8. MessagePending 컴포넌트 제거 (선택적)
**파일:** `frontend/src/app/channels/[channelId]/page.tsx`

- thinking 메시지가 인라인으로 표시되므로 별도 `MessagePending` 컴포넌트 불필요
- `runningAgent` 감지 + `<MessagePending />` 렌더링 코드 제거

---

## Part 2: 세션/대화 컨텍스트 관리

### 2-1. 대화 히스토리 조회 함수 추가
**파일:** `listener/src/task-runner.ts`

```typescript
async function fetchConversationHistory(
  supabase: SupabaseClient,
  channelId: string,
  agentUserId: string,
  limit = 20
): Promise<Array<{ role: 'user' | 'assistant'; name: string; content: string }>>
```

- `channel_messages`에서 최근 N개 조회 (type = 'text'만, thinking/status 제외)
- `users` 테이블 JOIN으로 author 이름 조회
- `author_id === agentUserId` → role: 'assistant', 나머지 → role: 'user'
- 총 문자수 ~6000자 제한 (오래된 것부터 잘라냄)

### 2-2. prompt JSON에 대화 히스토리 포함
**파일:** `listener/src/task-runner.ts`

```typescript
const history = await fetchConversationHistory(supabase, message.channel_id, agentUserId);
const prompt = JSON.stringify({
  conversation_history: history,
  message: sanitizedContent,
  requesting_user_id: requestingUserId,
  channel_id: message.channel_id,
  trigger_message_id: triggerMessageId,
});
```

### 2-3. Agent CLAUDE.md에 대화 컨텍스트 활용 지시 추가
**파일:** `listener/agent-context/agent-a/CLAUDE.md` (등 각 에이전트)

- `conversation_history` 필드 설명 추가
- 이전 대화 참조하여 문맥에 맞게 응답하라는 지시

---

## 수정 파일 요약

| # | 파일 | 작업 |
|---|------|------|
| 1 | `supabase/migrations/20260401000001_*.sql` | 새 파일: CHECK 제약 + UPDATE RLS |
| 2 | `frontend/src/types/channel.types.ts` | ThinkingMetadata 타입 + Zod 추가 |
| 3 | `frontend/src/components/channel/message/blocks/ThinkingBlock.tsx` | 새 파일: 애니메이션 컴포넌트 |
| 4 | `frontend/src/components/channel/message/MessageBubble.tsx` | thinking case 추가 |
| 5 | `frontend/src/hooks/useMessageCache.ts` | updateMessage() 추가 |
| 6 | `frontend/src/hooks/useChannelRealtime.ts` | UPDATE 이벤트 구독 추가 |
| 7 | `listener/src/task-runner.ts` | UPDATE 패턴 + 대화 히스토리 |
| 8 | `frontend/src/app/channels/[channelId]/page.tsx` | MessagePending 제거 |
| 9 | `listener/agent-context/agent-a/CLAUDE.md` | 대화 컨텍스트 지시 추가 |

## 검증 방법

1. **tsc --noEmit** — 타입 에러 없는지 확인
2. **SQL 마이그레이션** — Supabase SQL Editor에서 수동 실행 (IPv6 제약)
3. **수동 테스트:**
   - 채널에서 에이전트 @멘션
   - thinking 애니메이션이 메시지 목록에 나타나는지 확인
   - 응답 후 같은 메시지가 부드럽게 텍스트로 전환되는지 확인
   - 메시지 깜빡임/사라짐 없는지 확인
4. **대화 연속성 테스트:**
   - 에이전트에게 연속 2~3개 질문
   - 이전 대화 내용을 기억하고 응답하는지 확인
