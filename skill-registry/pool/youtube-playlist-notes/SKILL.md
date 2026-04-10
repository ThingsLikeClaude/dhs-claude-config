---
name: youtube-playlist-notes
description: |
  YouTube 재생목록의 모든 영상을 자막 기반으로 분석하여 Obsidian 노트를 자동 생성한다.

  Use proactively when: 사용자가 YouTube 재생목록 URL/ID를 제공하고 노트 생성을 요청할 때

  Triggers: 유튜브 재생목록, playlist notes, 영상 노트, youtube playlist, 재생목록 정리, 플레이리스트 노트

  Do NOT use for: 단일 영상 요약, 채널 전체 크롤링, 영상 다운로드
argument-hint: "[playlist URL or ID or -TAG]"
user-invocable: true
---

# YouTube Playlist Notes

YouTube 재생목록 → 자막 추출 → Obsidian 노트 자동 생성 스킬.
에이전트 팀(리더 + 워커 1-3명)이 병렬로 영상을 처리한다.

## Prerequisites

- `youtube-mcp` MCP 서버 활성화 필수
- Obsidian 볼트: `D:\vault\`

## Output Paths

- 노트: `D:\vault\2-notes\youtube\{playlistTag}\{video-title}.md`
- 자막: `D:\vault\5-archive\youtube-scripts\{playlistTag}\{videoId}.json`
- 폴더 미존재 시 `mkdir -p`로 자동 생성

## Playlist Tags

자주 사용하는 재생목록에 태그를 부여하여 `-TAG`로 빠르게 호출한다.

| Tag | Playlist ID | Playlist Name |
|-----|-------------|---------------|
| AI | PL6zyEzZX7dg0I1IY3nPd6BmrZq37RJyWk | AI KNOWLEDGEBASE |

사용법: `/youtube-playlist-notes -AI` → AI KNOWLEDGEBASE 재생목록 자동 처리

## Workflow

리더(메인 세션)가 Step 1-4, 6-7을 실행. 워커(Agent)가 Step 5를 병렬 실행. Step 7 검증은 리더가 직접 또는 추가 Agent로 병렬 수행.

### Step 1: 입력 파싱

**태그 확인 우선**: 인수가 `-TAG` 형식이면 위 Playlist Tags 테이블에서 매칭하여 playlist ID로 변환한다.
- `-AI` → `PL6zyEzZX7dg0I1IY3nPd6BmrZq37RJyWk`
- 매칭 실패 시 "알 수 없는 태그입니다" 메시지 후 종료

URL에서 playlist ID 추출:
- `https://www.youtube.com/playlist?list=PLxxxxxx` → `PLxxxxxx`
- `https://www.youtube.com/watch?v=xxx&list=PLxxxxxx` → `PLxxxxxx`
- `PLxxxxxx` (직접 입력)

### Step 2: 재생목록 정보 + 영상 목록 조회

```
mcp__youtube-mcp__playlists_getPlaylist({ playlistId })
→ playlistName = snippet.title
→ totalCount = contentDetails.itemCount
→ playlistTag = toKebab(playlistName)

mcp__youtube-mcp__playlists_getPlaylistItems({ playlistId, maxResults: 50 })
→ 각 영상에서 추출:
  videoId    = snippet.resourceId.videoId   (NOT contentDetails.videoId)
  title      = snippet.title
  channel    = snippet.videoOwnerChannelTitle  (실제 영상 제작자, channelTitle은 재생목록 소유자)
  description = snippet.description  (타임스탬프가 포함되어 있을 수 있음)
  publishedAt = contentDetails.videoPublishedAt
```

#### 50개 초과 재생목록 처리 (페이지네이션)

youtube-mcp는 pageToken을 지원하지 않으므로, 50개 초과 재생목록은 `yt-dlp`로 전체 목록을 가져온다.

```bash
yt-dlp --flat-playlist --print "%(id)s\t%(title)s\t%(channel)s\t%(upload_date)s" \
  "https://www.youtube.com/playlist?list={playlistId}" 2>/dev/null
```

- MCP로 먼저 50개 조회 → totalCount > 50이면 yt-dlp 병행
- yt-dlp 결과에서 MCP 결과에 없는 videoId를 추출하여 추가
- yt-dlp 출력의 인코딩이 깨질 수 있으므로, videoId만 신뢰하고 title/channel은 `mcp__youtube-mcp__videos_getVideo`로 개별 재조회
- yt-dlp 미설치 시: "yt-dlp가 필요합니다. pip install yt-dlp" 안내

처리 영상 개수 제한은 없다. 재생목록의 모든 영상을 중복 체크 후 미처리분을 전부 처리한다.

### Step 3: 중복 체크

```
Grep: pattern="video-id: {videoId}" path="D:/vault/2-notes/youtube/{playlistTag}/"
→ 매칭되면 skipList에 추가

Glob: "D:/vault/5-archive/youtube-scripts/{playlistTag}/{videoId}.json"
→ 자막 아카이브 존재하면 자막 추출 스킵 (아카이브 재사용)
```

대상 0개이면 "모든 영상이 이미 처리되었습니다" 보고 후 종료.

### Step 4: 워커 분배

처리 대상 영상 수에 따라 워커 수 결정:
- 1-3개: 워커 1명
- 4-9개: 워커 2명
- 10개+: 워커 3명

라운드로빈 분배: 워커 A=[0,3,6...], B=[1,4,7...], C=[2,5,8...]

### Step 5: 워커 실행 (Agent 병렬 호출)

**워커를 하나의 메시지에서 동시에 Agent 호출하여 병렬 실행한다.**

```
Agent(
  subagent_type: "general-purpose",
  mode: "bypassPermissions",
  name: "playlist-worker-{A|B|C}",
  prompt: <아래 워커 프롬프트 + 할당 영상 목록>
)
```

#### 워커 프롬프트 템플릿

```
당신은 YouTube 영상 요약 전문가입니다.
할당된 영상들에 대해 순서대로 처리하세요.

## 설정
- playlistName: {playlistName}
- playlistTag: {playlistTag}
- 오늘 날짜: {YYYY-MM-DD}
- 노트 경로: D:/vault/2-notes/youtube/{playlistTag}/
- 자막 경로: D:/vault/5-archive/youtube-scripts/{playlistTag}/

## 할당 영상
{JSON array of assigned videos}

## 각 영상 처리 절차

### 1. 자막 추출
mcp__youtube-mcp__transcripts_getTranscript({ videoId: "{videoId}" })

응답 형식 주의: [{ type: "text", text: "{JSON string}" }]
→ JSON.parse가 필요한 래핑 구조. text 필드 안의 JSON에서 transcript 배열을 추출.

실패 시 → noSubtitle 플래그 설정, 에러 무시하고 다음 진행.

### 2. 자막 아카이브 저장
폴더: mkdir -p "D:/vault/5-archive/youtube-scripts/{playlistTag}/"
파일: {videoId}.json

저장 포맷:
{
  "videoId": "{videoId}",
  "title": "{title}",
  "channel": "{channel}",
  "language": "{자막 lang 값}",
  "fetchedAt": "{오늘 날짜}",
  "transcript": [{자막 배열 원본}]
}

이미 아카이브가 존재하면 자막 추출 건너뛰고 기존 파일 Read로 불러와서 사용.

### 3. 노트 생성
폴더: mkdir -p "D:/vault/2-notes/youtube/{playlistTag}/"
파일명: {toCleanKorean(title)}.md

toCleanKorean 규칙:
- 제목의 핵심 키워드 2-4개만 추출하여 한국어 중심 파일명 생성
- 영문 제목은 한국어로 의역 (예: "AI agent design patterns" → "ai-에이전트-디자인-패턴")
- 접두어/장식 제거: [풀버전], [2026 튜토리얼], 이모지, 따옴표, 느낌표 등
- 채널명, 부제목, 수식어 제거 (핵심 주제만)
- 공백 → 하이픈, 연속 하이픈 → 단일 하이픈
- 최대 30자 (초과 시 잘림)
- 중복 방지는 video-id frontmatter로 처리하므로 파일명 유니크 불필요

노트 포맷:

---
tags: [youtube, {playlistTag}]
date: {오늘 YYYY-MM-DD}
video-id: {videoId}
channel: {channel}
url: https://www.youtube.com/watch?v={videoId}
playlist: {playlistName}
published: {publishedAt → YYYY-MM-DD}
rating: 0
reviewed: false
---

# {원본 title}

> **{channel}** | [YouTube에서 보기](https://www.youtube.com/watch?v={videoId})

## 핵심 요약

{자막 전체를 읽고 3-5문장으로 핵심 내용 요약. 반드시 한국어로 작성.}

## 타임스탬프

| 시간 | 내용 |
|------|------|
| 0:00 | ... |

타임스탬프 규칙:
1. description에 타임스탬프가 있으면 그것을 우선 사용
2. 없으면 자막 offset으로 주제 전환점 탐지하여 5-15개 생성
3. offset(초) → M:SS 변환: floor(s/60):floor(s%60).padStart(2,'0')

## 상세 노트

{자막 내용을 주제별로 구조화한 상세 정리}
- ### 소제목으로 주제 구분
- 핵심 키워드 **볼드**
- 코드/명령어는 `코드블록`
- 자막 내용의 80% 이상 커버하도록 상세하게 작성

## 언어 처리 규칙

자막 lang 값으로 언어를 판단한다:
- **한국어 (ko)**: 원문 그대로 노트 작성
- **비한국어 (en, ja, zh 등)**: 핵심 요약, 타임스탬프, 상세 노트 모두 **한국어로 번역**하여 작성
  - 고유명사, 기술 용어, 코드는 원문 유지 (예: "Hugging Face", "SFT", `npx skills add`)
  - frontmatter의 title은 원본 유지 (검색/중복체크용)
  - 노트 본문 `# 제목` 아래에 원본 제목 병기: `> 원제: {original title}`

### 자막 없는 영상 처리

## 핵심 요약

> 이 영상은 자막을 사용할 수 없어 메타데이터 기반으로 작성되었습니다.

{description에서 추출 가능한 정보를 정리}

## 상세 노트

{description 내용 재구성}

### 4. 결과 보고
모든 영상 처리 후 다음 형식으로 결과를 반환:
- videoId | title | status(created/no-subtitle/error) | filePath
```

### Step 6: 결과 취합 (리더)

워커들의 결과를 수집하여 최종 보고:

```
📊 YouTube Playlist Notes 결과
─────────────────────────────────
재생목록: {playlistName} ({totalCount}개 영상)
─────────────────────────────────
✅ 생성: {created}개
⏭️ 스킵 (중복): {skipped}개
⚠️ 자막 없음: {noSubtitle}개
❌ 실패: {error}개
─────────────────────────────────
📁 노트: D:\vault\2-notes\youtube\{playlistTag}\
📁 자막: D:\vault\5-archive\youtube-scripts\{playlistTag}\
```

### Step 7: Gemini 교차 검증

**Prerequisites**: `gemini-cli` MCP 서버 활성화 필수. 미연결 시 검증 스킵하고 Step 6 결과만 보고.

Step 6에서 생성(created)된 노트들을 대상으로 Gemini에게 요약 정확도를 교차 검증받는다.

#### 검증 대상 선정

- status=created인 노트만 검증 (스킵/실패 제외)
- noSubtitle 노트는 검증 불가 → 스킵

#### 검증 실행

생성된 노트마다 다음을 수행:

1. **자막 원본 로드**: `D:/vault/5-archive/youtube-scripts/{playlistTag}/{videoId}.json`에서 transcript 배열 읽기
2. **생성된 노트 로드**: `D:/vault/2-notes/youtube/{playlistTag}/{fileName}.md` 읽기
3. **Gemini에게 검증 요청**:

```
mcp__gemini-cli__ask-gemini({
  prompt: `
당신은 YouTube 영상 요약 품질 검증 전문가입니다.

아래 [원본 자막]과 [생성된 노트]를 비교하여 요약의 정확도를 검증하세요.

## 검증 기준
1. **사실 정확성**: 노트에 원본에 없는 내용이 추가되거나, 원본 내용이 왜곡되었는지
2. **핵심 누락**: 원본의 중요한 주제/개념이 노트에서 빠졌는지
3. **타임스탬프 정확도**: 타임스탬프가 실제 자막 시간과 대략 일치하는지

## 출력 형식 (반드시 이 JSON 형식으로만 응답)
{
  "videoId": "{videoId}",
  "score": <1-10 정수>,
  "issues": [
    { "type": "factual|missing|timestamp", "severity": "high|medium|low", "detail": "구체적 설명" }
  ],
  "summary": "한 줄 종합 평가"
}

## 채점 기준
- 9-10: 정확하고 완전한 요약
- 7-8: 사소한 누락이나 부정확함 있지만 전체적으로 양호
- 5-6: 중요 내용 누락 또는 부분적 왜곡
- 1-4: 심각한 오류 또는 대부분 부정확

[원본 자막]
{자막 JSON의 transcript 배열에서 text만 추출하여 연결한 plain text — 최대 30000자, 초과 시 앞뒤 15000자씩}

[생성된 노트]
{노트 파일의 전체 내용}
`,
  model: "gemini-2.5-flash"
})
```

#### 응답 파싱

Gemini 응답에서 JSON 블록을 추출하여 파싱한다.
JSON 파싱 실패 시 해당 영상은 `verify-error`로 처리하고 계속 진행.

#### 검증 결과 처리

score 기준에 따라 노트 frontmatter에 검증 결과를 기록:

```yaml
# 노트 frontmatter에 추가/업데이트
gemini-verified: true
gemini-score: 8
gemini-issues: "사소한 타임스탬프 오차"  # issues가 있을 때만
```

score < 7인 노트는 별도 경고 목록에 추가.

#### 검증 결과 보고

Step 6 결과 아래에 검증 보고를 추가:

```
🔍 Gemini 교차 검증 결과
─────────────────────────────────
검증 대상: {verified}개
─────────────────────────────────
✅ 양호 (7+): {good}개  (평균 {avgGoodScore}점)
⚠️ 주의 (5-6): {warn}개
❌ 부정확 (<5): {bad}개
🔇 검증 불가: {skipVerify}개 (자막 없음/에러)
─────────────────────────────────
전체 평균: {avgScore}/10

⚠️ 주의/부정확 노트:
- {fileName}: {score}점 — {summary}
- ...
```

#### 병렬 처리

검증 대상이 3개 이상이면 Agent를 사용하여 병렬 검증:
- 리더가 직접 검증: 3개 이하
- Agent 1명 추가 분배: 4-6개
- Agent 2명 추가 분배: 7개 이상

각 Agent에게 할당된 노트+자막 쌍을 전달하고, Gemini 호출 및 frontmatter 업데이트까지 수행하게 한다.

### Step 7.5: 저품질 노트 자동 재생성

Step 7에서 `gemini-score < 7`인 노트를 자동으로 재생성한다.

#### 대상 수집

- Step 7 결과에서 score < 7인 노트 필터
- 대상 0개 → 스킵, Step 8로 진행
- noSubtitle 노트는 재생성 대상에서 제외

#### 재생성 실행

대상 노트를 워커에게 재할당 (기존 Step 5 워커 프롬프트 재사용):
- 대상 1-2개 → 워커 1명
- 대상 3개+ → 워커 2명 (라운드로빈)

**재생성 프롬프트에 Gemini 피드백 포함**:
```
이전 Gemini 검증에서 다음 문제가 지적되었습니다:
- score: {score}/10
- issues: {issues 목록}

위 피드백을 반영하여 개선된 노트를 작성하세요.
특히 지적된 사실 오류, 누락 내용, 타임스탬프 부정확성을 수정하세요.
```

- 자막 아카이브는 재사용 (재추출 불필요)
- 기존 노트 파일 덮어쓰기 (Write)

#### Gemini 재검증

재생성된 노트에 대해 Step 7과 동일한 검증을 1회 수행.
결과 무관 최종 반영 (무한 루프 방지).

frontmatter 업데이트:
```yaml
gemini-score: {새 점수}
gemini-issues: "{새 이슈}"  # 있으면
gemini-regen: true           # 재생성 이력 표시
```

#### 재생성 결과 보고

```
🔄 자동 재생성 결과
─────────────────────────────────
대상: {regenTarget}개
─────────────────────────────────
✅ 개선됨: {improved}개 (평균 +{delta}점)
➡️ 변동 없음: {unchanged}개
─────────────────────────────────
```

**제약**: 최대 1회 재시도. 자막 불완전 케이스는 재생성으로도 개선 불가.

### Step 8: 노트별 인포그래픽 HTML 생성

모든 노트(생성+기존)를 대상으로 **visualize 스킬 + 레퍼런스 템플릿** 기반 인포그래픽 HTML을 생성한다.
최대 3 Agent를 한 메시지에서 동시 스폰하여 병렬 처리.

#### 레퍼런스 템플릿

```
경로: ~/.claude/templates/visualize/youtube-notes.html
```

이 템플릿은 디자인 시스템(폰트, 색상, 컴포넌트 CSS, 애니메이션, 메뉴, JS)을 통일한다.
Agent는 이 템플릿을 Read로 읽은 후, 노트 내용에 맞는 컴포넌트를 조합하여 HTML을 생성한다.

#### 중복 체크

```
Glob: "D:/vault/2-notes/youtube/{playlistTag}/visualize/{노트명}.html"
→ 이미 존재하면 vizSkipList에 추가
```

대상 0개이면 "모든 인포그래픽이 이미 존재합니다" 보고 후 Step 9로.

#### Agent 분배

```
노트 수별 Agent 수:
- 1-3개: Agent 1명
- 4-9개: Agent 2명
- 10개+: Agent 3명 (최대)

분배: 라운드로빈
Agent A=[0,3,6...], B=[1,4,7...], C=[2,5,8...]
```

#### Agent 스폰

```
Agent(
  subagent_type: "general-purpose",
  mode: "bypassPermissions",
  name: "viz-worker-{A|B|C}",
  prompt: <아래 시각화 워커 프롬프트 + 할당 노트 목록>
)
```

**모든 Agent를 하나의 메시지에서 동시 호출. 최대 3개.**

#### 시각화 워커 프롬프트 템플릿

```
당신은 YouTube 노트를 인포그래픽 HTML로 변환하는 전문가입니다.

## 설정
- playlistTag: {playlistTag}
- 저장 경로: D:/vault/2-notes/youtube/{playlistTag}/visualize/
- 폴더 없으면 mkdir -p로 생성

## 레퍼런스 템플릿 (필수)

1. 먼저 Read로 레퍼런스 템플릿을 읽으세요:
   ~/.claude/templates/visualize/youtube-notes.html

2. 이 템플릿의 디자인 시스템을 반드시 따르세요:
   - CSS: 동일한 custom properties, 폰트 (Noto Sans KR + Inter), 색상 체계
   - 구조: .hero → section들 → .footer 순서
   - 컴포넌트: 템플릿에 정의된 클래스만 사용
     (.definition-box, .compare-grid, .timeline, .layer-stack,
      .alert-box, .concept-grid, .analogy, .strategy-list,
      .stat-grid, .insight-box, .card)
   - JS: 동일한 menu/theme/reveal/download/timestamp 로직
   - 애니메이션: fadeInUp + data-reveal scroll reveal

3. 콘텐츠에 맞게 컴포넌트를 선택하세요:
   - 비교 있으면 → .compare-grid (type-a / type-b)
   - 순서/역사 → .timeline
   - 핵심 정의 → .definition-box
   - 계층 구조 → .layer-stack
   - 주의사항 → .alert-box
   - 개념 나열 → .concept-grid
   - 비유 → .analogy
   - 단계 → .strategy-list
   - 수치 → .stat-grid
   - 핵심 인사이트 → .insight-box

4. 타임스탬프 섹션은 항상 마지막에 배치 (검색 가능)

## 할당 노트
{JSON array: [{ notePath, noteTitle, videoId }]}

## 각 노트 처리 절차

1. Read로 레퍼런스 템플릿 읽기 (첫 노트 처리 전 1회)
2. Read로 노트 MD 파일 읽기
3. frontmatter, 핵심 요약, 타임스탬프, 상세 노트 섹션 추출
4. 레퍼런스 템플릿의 CSS/JS를 그대로 사용하고, 콘텐츠 섹션만 노트에 맞게 구성
5. Write로 저장: D:/vault/2-notes/youtube/{playlistTag}/visualize/{노트명}.html
6. 결과 보고: videoId | noteTitle | status(created/error) | htmlPath
```

#### 결과 보고

```
🎨 인포그래픽 생성 결과
─────────────────────────────────
대상: {vizTarget}개
─────────────────────────────────
✅ 생성: {vizCreated}개
⏭️ 스킵 (기존): {vizSkipped}개
❌ 실패: {vizFailed}개
─────────────────────────────────
📁 D:\vault\2-notes\youtube\{playlistTag}\visualize\
```

### Step 9: 재생목록 인덱스 MD 생성

리더가 직접 생성. 재생목록의 모든 노트를 한눈에 파악하는 인덱스 파일.

#### 데이터 수집

1. Glob으로 `D:/vault/2-notes/youtube/{playlistTag}/*.md` 전체 노트 목록 (index 파일 자체 제외)
2. 각 노트의 frontmatter에서 추출:
   - video-id, channel, gemini-score, gemini-regen, url, published
3. Glob으로 `visualize/{노트명}.html` 존재 여부 확인
4. 통계 계산: 평균 점수, 양호/주의/부정확 개수

#### 인덱스 파일 생성

파일: `D:/vault/2-notes/youtube/{playlistTag}/{playlistTag}-index.md`

포맷:
```
---
tags: [youtube, {playlistTag}, index]
date: {오늘 YYYY-MM-DD}
playlist-id: {playlistId}
playlist-url: https://www.youtube.com/playlist?list={playlistId}
total-videos: {count}
avg-gemini-score: {avg}
---

# {playlistName}

> {totalCount}개 영상 | [YouTube에서 보기]({playlist-url}) | 생성일: {date}

## 영상 목록

| # | 영상 | 채널 | Gemini | 시각화 |
|---|------|------|--------|--------|
| 1 | [[{노트명}]] | {channel} | {score}/10 | [보기](visualize/{노트명}.html) |
| ... |

## 통계

- 전체 평균 Gemini 점수: {avg}/10
- 양호 (7+): {good}개
- 주의 (5-6): {warn}개
- 부정확 (<5): {bad}개
- 자막 없음: {noSubtitle}개
- 재생성됨: {regen}개
```

기존 인덱스 파일이 있으면 덮어쓰기 (항상 최신 반영).

#### v2 최종 보고

Step 9 완료 후 전체 결과를 종합 보고:

```
📊 YouTube Playlist Notes v2 결과
─────────────────────────────────────────────
재생목록: {playlistName} ({totalCount}개 영상)
─────────────────────────────────────────────

📝 노트: ✅{created} ⏭️{skipped} ⚠️{noSub} ❌{error}
🔍 검증: 평균 {avg}/10 (양호{good} 주의{warn} 부정확{bad})
🔄 재생성: {regenTarget}개 → 개선{improved} 변동없음{unchanged}
🎨 인포그래픽: ✅{vizCreated} ⏭️{vizSkipped} ❌{vizFailed}

📁 노트: D:\vault\2-notes\youtube\{playlistTag}\
📁 자막: D:\vault\5-archive\youtube-scripts\{playlistTag}\
📁 시각화: D:\vault\2-notes\youtube\{playlistTag}\visualize\
📁 인덱스: {playlistTag}-index.md
─────────────────────────────────────────────
```

## Error Handling

| 상황 | 처리 |
|------|------|
| 재생목록 ID 무효 | "유효하지 않은 재생목록입니다" 메시지 후 종료 |
| youtube-mcp 미연결 | "youtube-mcp 서버가 활성화되어 있지 않습니다" 안내 |
| 자막 추출 실패 | 해당 영상 no-subtitle 처리, 나머지 계속 |
| 워커 에이전트 실패 | 실패 영상 목록 보고, 수동 재처리 안내 |
| gemini-cli 미연결 | "Gemini 검증을 건너뜁니다" 안내 후 Step 6 결과만 보고 |
| Gemini 응답 JSON 파싱 실패 | 해당 영상 verify-error 처리, 나머지 계속 |
| Gemini 응답 timeout | 해당 영상 verify-error 처리, 나머지 계속 |
