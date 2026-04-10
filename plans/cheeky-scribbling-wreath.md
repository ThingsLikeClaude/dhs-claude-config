# 에이전트 상태 아바타 (글래스모피즘) - TopBar 우측 배치

## Context
검색바 오른쪽, 유저 아바타 왼쪽에 AI 에이전트(오디, 파이)의 상태 아바타를 배치한다.
각 아바타는 글래스모피즘 스타일로, 에이전트 상태(idle/running/error/offline)를 실시간 표시한다.

## 수정 파일
- `frontend/src/components/channel/layout/ChannelTopBar.tsx` — 유일한 수정 대상

## 구현 내용

### 1. 데이터 fetching
- `useQuery` + `queryKeys.agents.profiles()` + `getAgentProfiles()` (기존 패턴 재사용)
- `useAgentRealtime()` 훅으로 실시간 상태 업데이트 (기존 훅 재사용)
- heartbeat 기반 effective status 계산 (180초 타임아웃, AgentStatusCard 패턴 재사용)

### 2. 글래스모피즘 에이전트 아바타
검색바와 유저 아바타 사이에 배치. 각 에이전트별 작은 아바타 컴포넌트:

```
[< > 🕐 [🔍 검색              ]] [🤖오디] [🤖파이] [👤]
```

스타일:
- **배경**: `bg-white/10 backdrop-blur-md` (글래스모피즘)
- **테두리**: `border border-white/20 rounded-lg`
- **크기**: `h-7 px-2` (TopBar h-10에 맞춤)
- **상태 인디케이터**: 우하단 작은 점 (green/yellow/red/gray)
  - idle: `bg-green-400`
  - running: `bg-yellow-400` + pulse 애니메이션
  - error: `bg-red-400`
  - offline: `bg-gray-400`
- **아이콘**: Bot (lucide) `size-3.5` + 이름 텍스트 `text-[11px]`
- hover 시 `bg-white/20` + 툴팁으로 상세 상태 표시

### 3. 레이아웃 변경
현재: `[nav+검색(flex-1)] [아바타]`
변경: `[nav+검색(flex-1)] [에이전트아바타들] [유저아바타]`

에이전트 아바타 영역은 `shrink-0`으로 검색바를 밀지 않음.

## 검증
- `pnpm tsc --noEmit` 타입 체크
- 브라우저에서 채널 페이지 진입 후 TopBar 확인
- 에이전트가 없을 때 빈 영역 (graceful empty state)
