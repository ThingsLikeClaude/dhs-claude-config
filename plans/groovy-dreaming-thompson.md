# 서식(Rich Text) 저장 및 렌더링 구현 플랜

## Context

현재 Tiptap 에디터로 서식 UI(굵게, 기울임, 목록, 코드블록 등)를 제공하지만, 전송 시 `editor.getText()`로 plain text만 추출하여 DB에 저장. 서식이 완전히 소실됨.

**사용자 불만:**
- 번호목록, 글머리목록, 인라인코드, 코드블록 등 서식이 전혀 적용 안 됨
- 링크 삽입이 `window.prompt`로 투박함

**슬랙 방식 참고:** 슬랙은 Block Kit JSON + mrkdwn 포맷으로 저장, 클라이언트에서 HTML 렌더링. 우리는 Tiptap이 이미 있으므로 **HTML 저장 + HTML 렌더링** 방식이 가장 효율적.

## 구현 계획

### Step 1: DB 스키마 — `content_html` 컬럼 추가
- **파일**: `supabase/migrations/` 새 마이그레이션
- `channel_messages` 테이블에 `content_html text` 컬럼 추가 (nullable)
- `content`는 plain text 유지 (검색, 미리보기, 멘션 감지용)
- `content_html`에 Tiptap HTML 저장

### Step 2: 타입 업데이트
- **파일**: `frontend/src/types/channel.types.ts`
  - `ChannelMessage`에 `content_html?: string` 추가
- **파일**: `frontend/src/types/database.types.ts`
  - `channel_messages` Row/Insert/Update에 `content_html` 추가

### Step 3: 메시지 전송 — HTML 함께 저장
- **파일**: `frontend/src/components/channel/message/MessageInput.tsx`
  - `handleSubmit`에서 `editor.getHTML()` 추출 → `content_html`로 전달
  - `editor.getText()`는 `content`용으로 유지
- **파일**: `frontend/src/components/channel/panel/ThreadInput.tsx`
  - 동일하게 `editor.getHTML()` 추출
- **파일**: `frontend/src/app/actions/channels.ts`
  - `sendMessage`, `sendThreadReply` 함수에 `contentHtml` 파라미터 추가
  - DB insert 시 `content_html` 포함

### Step 4: 메시지 렌더링 — HTML 표시
- **파일**: `frontend/src/components/channel/message/blocks/TextBlock.tsx`
  - `content_html`이 있으면 sanitize 후 HTML 렌더링
  - 없으면 기존 plain text + 멘션 하이라이트 유지 (하위호환)
  - HTML 내부의 `@이름` 패턴도 멘션 하이라이트 적용
  - Tailwind prose 클래스로 일관된 타이포그래피
- **파일**: `frontend/src/components/channel/panel/ThreadPanel.tsx`
  - SimplifiedMessage에서도 TextBlock에 `content_html` 전달

### Step 5: 링크 삽입 UX 개선
- **파일**: `frontend/src/components/channel/message/MessageInput.tsx`
  - `window.prompt` → 인라인 팝오버 UI (URL + 텍스트 입력)
- **파일**: `frontend/src/components/channel/panel/ThreadInput.tsx`
  - 동일 적용

### Step 6: DOMPurify 설치
- `pnpm add dompurify @types/dompurify`
- XSS 방지를 위한 HTML sanitize

## 수정 파일 목록

| 파일 | 변경 |
|------|------|
| `supabase/migrations/새파일` | content_html 컬럼 추가 |
| `frontend/src/types/channel.types.ts` | content_html 필드 추가 |
| `frontend/src/types/database.types.ts` | content_html 필드 추가 |
| `frontend/src/app/actions/channels.ts` | sendMessage/sendThreadReply에 HTML 저장 |
| `frontend/src/components/channel/message/MessageInput.tsx` | getHTML() 추출 + 링크 팝오버 |
| `frontend/src/components/channel/panel/ThreadInput.tsx` | getHTML() 추출 + 링크 팝오버 |
| `frontend/src/components/channel/message/blocks/TextBlock.tsx` | HTML 렌더링 지원 |
| `frontend/src/components/channel/panel/ThreadPanel.tsx` | content_html 전달 |
| `frontend/src/components/channel/message/MessageBubble.tsx` | content_html 전달 |

## 검증 방법

1. `tsc --noEmit` 타입 체크
2. 채널에서 굵게/기울임/목록/코드블록 서식 메시지 전송 → DB에 content_html 저장 확인
3. 전송된 메시지가 서식 적용된 채로 채팅창에 표시되는지 확인
4. 스레드 답글에서도 동일하게 동작하는지 확인
5. 기존 plain text 메시지가 정상 표시되는지 확인 (하위호환)
