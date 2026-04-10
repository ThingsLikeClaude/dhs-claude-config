# Electron 데스크톱 앱 계획 - Ordify

## Context
Ordify를 .exe 설치 파일로 배포 가능한 독립 데스크톱 앱으로 만든다. URL 래핑 방식으로 `ordify-beta.vercel.app`을 Electron 창에서 여는 구조. 웹 배포와 항상 동기화되어 별도 업데이트 불필요.

## 구조
프로젝트 루트에 `electron/` 디렉토리를 별도 생성 (frontend와 분리).

```
ordify-release/
├── frontend/          ← 기존 Next.js 앱 (변경 없음)
└── electron/          ← 신규 Electron 앱
    ├── package.json
    ├── main.js        ← Electron 메인 프로세스
    ├── preload.js     ← 보안 프리로드 스크립트
    └── icon.png       ← 앱 아이콘 (기존 512x512 복사)
```

## 변경/생성 파일 (4개, 모두 신규)

### 1. `electron/package.json`
- electron, electron-builder 의존성
- 빌드 스크립트 (`electron-builder --win`)
- electron-builder 설정 (appId, productName, icon, nsis 설정)

### 2. `electron/main.js`
- BrowserWindow 생성 (1280x800, 타이틀바 포함)
- `ordify-beta.vercel.app` 로드
- 메뉴바 숨김 (앱처럼 보이도록)
- 외부 링크는 기본 브라우저에서 열기

### 3. `electron/preload.js`
- contextIsolation 보안 설정용 빈 프리로드

### 4. `electron/icon.png`
- `frontend/public/android-chrome-512x512.png` 복사

## 빌드 & 실행

```bash
cd electron
npm install
npm start          # 개발 테스트
npm run build      # .exe 생성 → electron/dist/
```

## 검증
1. `npm start`로 Electron 앱 실행 → ordify-beta.vercel.app 정상 로드 확인
2. 로그인 동작 확인
3. `npm run build`로 .exe 생성 확인
