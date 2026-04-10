# SIFT Overlay Window 구현 계획

## Context

SIFT 앱에 게임 오버레이 HUD를 추가한다. 인터뷰 01에서 확정된 요구사항:
- 풀스크린 투명 BrowserWindow (OP.GG Desktop 방식)
- 위젯: 실시간 수익(A) + 구간요약(A) + 드롭알림(B) + 정산알림
- 포커스 감지 (게임 언포커스 시 자동 숨김)
- F12 핫키 토글 + 드래그 위치 저장

현재 `src/ui/overlay/` 디렉토리가 비어있고, Electron 윈도우는 main 1개만 존재.

## 구현 순서 (8단계)

### Step 1: Forge + Vite 멀티윈도우 설정
**변경 파일**: `forge.config.ts`, 새 파일 `vite.overlay.config.ts`, 새 파일 `overlay.html`

- `forge.config.ts`의 `renderer` 배열에 overlay_window 엔트리 추가
- `vite.overlay.config.ts` 생성 (기존 `vite.renderer.config.ts` 복사 + 필요 시 tailwind 포함)
- `overlay.html` 생성 (overlay React 앱의 엔트리 HTML)

### Step 2: 오버레이 BrowserWindow 생성
**변경 파일**: `electron/windows.ts`

```
createOverlayWindow() 추가:
- transparent: true, frame: false
- alwaysOnTop: true (level: 'screen-saver')
- skipTaskbar: true
- ignoreMouseEvents: true (기본값, 드래그 영역만 예외)
- 초기 크기: 300x180 (compact HUD)
- 위치: DB에서 로드 (없으면 화면 우상단)
- show: false (토글 전까지 숨김)
```

### Step 3: IPC 채널 확장
**변경 파일**: `src/shared/ipc-types.ts`, `src/preload.ts`

새 IPC 채널:
```
OVERLAY_TOGGLE: 'overlay:toggle'          // 핫키로 호출
OVERLAY_SET_POSITION: 'overlay:set-position'  // 드래그 후 위치 저장
OVERLAY_GET_POSITION: 'overlay:get-position'
```

SiftApi에 추가:
```
onOverlayToggle(callback): () => void     // Main→Renderer push
setOverlayPosition(x, y): Promise<void>   // Renderer→Main invoke
```

**기존 push 채널 (STATE_UPDATE, RUN_STARTED, RUN_ENDED)은 그대로 재사용** — 오버레이 윈도우에도 같은 데이터 push.

### Step 4: Main process 통합
**변경 파일**: `src/main.ts`, `electron/ipc-handlers.ts`

- `main.ts`: overlayWindow 생성 + globalShortcut 등록 (F12)
- `ipc-handlers.ts`:
  - `createIpcPushCallbacks()` — 양쪽 윈도우에 send
  - overlay position get/set 핸들러 추가
  - 게임 포커스 감지: `setInterval`로 `TorchlightInfinite.exe` 프로세스 포그라운드 확인 → overlay show/hide

### Step 5: 오버레이 React 앱 엔트리
**새 파일**: `src/overlay-renderer.ts`, `src/ui/overlay/OverlayApp.tsx`

- `overlay-renderer.ts`: React root 마운트 + Zustand store 초기화 (기존 `src/renderer.ts` 패턴 복사)
- `OverlayApp.tsx`: 오버레이 루트 컴포넌트

### Step 6: 오버레이 UI 컴포넌트
**새 파일들**: `src/ui/overlay/` 하위

```
src/ui/overlay/
  OverlayApp.tsx      — 루트 (드래그 영역 + 위젯 컨테이너)
  OverlayMetrics.tsx  — 실시간: 구간수익, FE/h, 파밍시간, 판수
  DropAlert.tsx       — 드롭 알림 토스트 (페이드인/아웃)
  SettleAlert.tsx     — 정산 알림 (테두리 flash + 텍스트)
```

디자인:
- 반투명 다크 배경 (`bg-navy-900/80 backdrop-blur`)
- 골드 accent, 게이밍 톤
- 페이드인/슬라이드 애니메이션 (인터뷰 결정)
- 드래그 핸들: 상단 5px grip 영역 (여기서만 `ignoreMouseEvents: false`)

### Step 7: 드롭 알림 + 정산 알림 로직
**변경 파일**: `src/store/app-store.ts` 또는 별도 overlay store

- `onRunEnded` 이벤트 → DropAlert 표시 (아이템명 + 수익)
- 자동정산 발생 시 → SettleAlert 표시 (테두리 flash 0.5s + "30판 완료 · 1,200FE" + 3초 페이드아웃)
- 알림 큐 관리 (여러 드롭이 빠르게 올 경우 스택)

### Step 8: 위치 저장 + 설정 연동
**변경 파일**: `electron/ipc-handlers.ts` (settings), 설정 패널 UI

- 드래그 종료 시 `overlay:set-position` → DB 저장
- 앱 시작 시 DB에서 위치 복원
- 설정 패널에 오버레이 섹션: 핫키 변경, 알림 강도 (테두리만 / 테두리+텍스트 / 끔)

## 핵심 재사용 코드

| 기존 코드 | 위치 | 재사용 방식 |
|-----------|------|-----------|
| `createListener()` | `src/preload.ts:14` | 오버레이도 동일 preload 사용 |
| `useAppStore` | `src/store/app-store.ts` | 오버레이 renderer에서 동일 store 사용 |
| `getSetting/setSetting` | `src/db/repository.ts:24-43` | 위치/설정 저장 |
| IPC push 패턴 | `electron/ipc-handlers.ts:210` | 양쪽 윈도우에 broadcast |
| Tailwind theme | `src/styles/` | 오버레이도 동일 테마 |

## 변경 파일 요약 (15개)

**수정 (6개)**:
1. `forge.config.ts` — overlay renderer 엔트리 추가
2. `electron/windows.ts` — `createOverlayWindow()` 추가
3. `src/main.ts` — overlay 윈도우 생성 + 핫키 + 포커스 감지
4. `electron/ipc-handlers.ts` — dual push + overlay position handlers
5. `src/shared/ipc-types.ts` — overlay IPC 채널 + SiftApi 확장
6. `src/preload.ts` — overlay 전용 API 추가

**신규 (9개)**:
1. `vite.overlay.config.ts` — overlay Vite 설정
2. `overlay.html` — overlay HTML 엔트리
3. `src/overlay-renderer.ts` — overlay React 마운트
4. `src/ui/overlay/OverlayApp.tsx` — 루트 컴포넌트
5. `src/ui/overlay/OverlayMetrics.tsx` — 수익/시간 메트릭
6. `src/ui/overlay/DropAlert.tsx` — 드롭 알림
7. `src/ui/overlay/SettleAlert.tsx` — 정산 알림
8. `src/ui/overlay/overlay.css` — 오버레이 전용 스타일
9. `src/shared/constants.ts` — OVERLAY 상수 추가 (기존 파일)

## 검증 방법

1. `pnpm start` → 앱 실행, F12로 오버레이 토글 확인
2. 오버레이 드래그 → 위치 이동 → 앱 재시작 → 위치 복원 확인
3. 게임 없이 테스트: 오버레이 표시 상태에서 다른 앱 포커스 → 오버레이 숨김 확인
4. 로그 재생 시 오버레이에 수익/시간 실시간 반영 확인
5. `tsc --noEmit` — 타입 에러 없음 확인
