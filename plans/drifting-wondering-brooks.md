# 채팅 화면 UI 다듬기 Plan

## Context
맥미니 리스너 셋업 완료 후, 채널 채팅 화면 전체 UI를 슬랙 수준으로 다듬는 작업.
현재 기능은 동작하지만 시각적 완성도가 낮음.

## 현재 상태 요약
- 메시지 버블: 에이전트("AI") vs 사람(이름 2글자) 구분 있으나 단순
- 가상 스크롤 미사용 (전체 렌더링)
- 타임스탬프: HH:mm만 표시, 날짜 그룹핑 없음
- 에이전트 메시지에 특별한 스타일링 없음 (보라색 등)

## 수정 대상 파일

| 파일 | 변경 내용 |
|------|----------|
| `components/channel/message/MessageBubble.tsx` | 에이전트/사람 버블 시각 차별화, 아바타 개선, 시간 그룹핑 |
| `components/channel/message/MessageList.tsx` | 날짜 구분선, 스크롤 개선 |
| `components/channel/message/MessageInput.tsx` | 입력창 디자인 개선 |
| `components/channel/layout/ChannelHeader.tsx` | 헤더 디자인, 온라인 멤버 수 |
| `components/channel/message/blocks/StatusBlock.tsx` | "생각하는 중..." 애니메이션 |

## 작업 목록

### 1. MessageBubble 개선
- [ ] 에이전트 메시지: 보라색 좌측 보더 + 미묘한 배경색
- [ ] 사람 메시지: 기본 스타일 유지
- [ ] 아바타: Google avatar URL 사용 (있으면), 없으면 이니셜
- [ ] 에이전트 아바타: Bot 아이콘 + 보라색 링
- [ ] 연속 메시지(같은 사람, 2분 이내): 아바타 숨기고 콤팩트하게
- [ ] hover 시 시간 + 액션 버튼 표시

### 2. MessageList 날짜 구분
- [ ] 날짜가 바뀔 때 "── 3월 31일 월요일 ──" 구분선
- [ ] "오늘", "어제" 상대 표시
- [ ] 새 메시지 알림 바 ("↓ 새 메시지 N개")

### 3. MessageInput 개선
- [ ] 둥근 입력 영역 (슬랙 스타일)
- [ ] 전송 버튼 아이콘화 (Send 아이콘)
- [ ] 에이전트 처리 중일 때 입력창 위에 타이핑 인디케이터

### 4. ChannelHeader
- [ ] 채널 아이콘 (#general, 🤖agent-a)
- [ ] 멤버 수 + 온라인 수 표시
- [ ] 탭 스타일 개선

### 5. "생각하는 중..." 표시 개선
- [ ] StatusBlock에 타이핑 애니메이션 (···) 
- [ ] 에이전트 아바타 옆에 말풍선 형태로

## 디자인 참고
- Ordify 브랜드 컬러: #2E3976 (딥 인디고)
- 에이전트 컬러: purple-500/600 계열
- 기존 shadcn/ui 컴포넌트 최대 활용
- 다크모드 대응 필수

## 검증 방법
1. `npx tsc --noEmit` (frontend 디렉토리)
2. 브라우저에서 /channels/general 접속
3. 메시지 여러 개 보내서 그룹핑/날짜 구분 확인
4. @Agent A 멘션 → "생각하는 중..." 애니메이션 확인
5. 다크/라이트 모드 전환 확인
