# 링크 임베딩 (OG Preview Card) 구현 계획

## Context
현재 채팅 에디터에서 링크를 삽입하면 단순 파란색 텍스트 하이퍼링크로만 표시됨.
카카오톡/노션처럼 URL의 OG 메타데이터(제목, 설명, 썸네일)를 카드 형태로 보여주는 임베딩 기능이 필요.
- **에디터**: 링크 삽입 시 에디터 아래(액션바 위)에 프리뷰 카드 표시
- **메시지 렌더링**: 보낸 메시지에서도 링크 프리뷰 카드 표시

## 구현 단계

### Step 1: OG 메타데이터 서버 액션 생성
**파일**: `frontend/src/app/actions/og-metadata.ts` (신규)

- `fetchOgMetadata(url: string)` 서버 액션
- Node.js `fetch`로 URL 접근 → HTML 파싱 → og:title, og:description, og:image, favicon 추출
- 정규식 기반 경량 파싱 (cheerio 같은 의존성 불필요)
- 타임아웃 5초, 에러 시 null 반환 (UI 블로킹 방지)
- 반환 타입: `{ title, description, image, favicon, url }`

### Step 2: LinkPreviewCard 컴포넌트
**파일**: `frontend/src/components/channel/message/LinkPreviewCard.tsx` (신규)

- 재사용 가능한 프리뷰 카드 (에디터 + 렌더링 모두 사용)
- 썸네일 이미지 + 제목 + 설명 + URL 도메인
- 에디터용: X 버튼으로 프리뷰 제거 가능 (`onRemove` prop)
- 메시지용: 클릭 시 새 탭 열기
- 카카오톡 스타일 컴팩트 카드 디자인

### Step 3: MessageInput 수정
**파일**: `frontend/src/components/channel/message/MessageInput.tsx`

- `linkPreviews` 상태 추가: `Array<{ url, title, description, image, favicon }>`
- `handleInsertLink` 수정: 링크 삽입 시 `fetchOgMetadata` 호출 → 프리뷰 상태에 추가
- JSX: EditorContent와 액션바 사이에 LinkPreviewCard 렌더링
- `handleSubmit` 수정: 프리뷰 데이터를 metadata에 포함하여 전송
- 전송 후 프리뷰 상태 초기화

### Step 4: ThreadInput 동일 적용
**파일**: `frontend/src/components/channel/panel/ThreadInput.tsx`

- MessageInput과 동일한 패턴으로 링크 프리뷰 추가

### Step 5: 메시지 렌더링에 프리뷰 카드 추가
**파일**: `frontend/src/components/channel/message/blocks/TextBlock.tsx`

- metadata에 `linkPreviews` 있으면 텍스트 아래에 LinkPreviewCard 렌더링
- 기존 텍스트 내 링크는 그대로 유지 (프리뷰 카드가 추가로 표시)

### Step 6: 타입 확장
**파일**: `frontend/src/types/channel.types.ts`

- `LinkPreview` 인터페이스 추가
- `TextMetadata`에 `linkPreviews?: LinkPreview[]` 필드 추가

## 데이터 흐름

```
[에디터에서 링크 삽입]
  → LinkPopover에서 URL 입력
  → handleInsertLink: Tiptap에 <a> 삽입 + fetchOgMetadata(url) 호출
  → OG 데이터 수신 → linkPreviews 상태에 추가
  → 에디터 아래에 LinkPreviewCard 표시

[메시지 전송]
  → handleSubmit: content_html + metadata.linkPreviews 함께 전송
  → Supabase channel_messages에 저장

[메시지 렌더링]
  → TextBlock: content_html 렌더 + metadata.linkPreviews로 카드 렌더
```

## 검증 방법
1. 채팅 에디터에서 링크 버튼 클릭 → URL 입력 → 프리뷰 카드가 에디터 아래에 표시되는지 확인
2. X 버튼으로 프리뷰 제거 가능한지 확인
3. 메시지 전송 후 메시지 본문 아래에 프리뷰 카드가 표시되는지 확인
4. 스레드 입력에서도 동일하게 동작하는지 확인
5. 잘못된 URL이나 OG 데이터 없는 사이트에서 graceful 처리되는지 확인
