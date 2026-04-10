# 스레드 UI 수정 플랜

## Context
스레드 답글이 작동하지만 UI가 미완성:
1. 메인 채널 메시지에 "N개의 댓글" ThreadPreview가 안 뜸
2. @멘션으로 에이전트 호출 시 스레드 패널이 자동으로 안 열림

## 수정 사항

### 1. `getMessages` reply_count 매핑 복원
**파일**: `frontend/src/app/actions/channels.ts` (line ~105)
- `reply_count`, `last_reply_at` 필드가 매핑에서 누락됨
- `author_role` 뒤에 두 필드 추가

### 2. MessageInput — 에이전트 멘션 시 스레드 자동 열기
**파일**: `frontend/src/components/channel/message/MessageInput.tsx`
- `useRightPanelStore`의 `openThread` import (이미 있을 수 있음 — 확인 필요)
- `mutation.onSuccess`에서 `mentionIds`에 에이전트 ID가 포함되면 `openThread(realMsg.id, channelId)` 호출
- 에이전트 판별: `usersMap`에서 `role === 'agent'`인 사용자 ID 체크

### 3. 검증
- `tsc --noEmit`으로 타입 체크
- 수동 테스트: 메인 채널에서 @오디 멘션 → 스레드 자동 열림 + ThreadPreview 표시 확인
