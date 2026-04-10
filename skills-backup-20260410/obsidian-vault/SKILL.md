---
name: obsidian-vault
description: |
  Obsidian 볼트의 md 문서 생성, 검색, 관리 워크플로우.
  검색 친화적 태깅 + 구조화된 frontmatter를 적용한다.

  Use proactively when: md 파일 생성, 문서 검색/탐색, 노트 관리

  Triggers: md 생성, 문서 작성, 노트, 태그, frontmatter, 검색, 문서 찾기,
  버그 기록, TIL, 결정 기록, 세션 요약, note, document, create note,
  search notes, find document, tag, markdown

  Do NOT use for: md가 아닌 파일, 코드 내 주석, CLI 명령어 상세 (obsidian:obsidian-cli 참조)
---

# Obsidian Vault Workflow

> **태깅 철학**: 태그는 형식을 채우는 것이 아니라
> **"나중에 이 문서를 어떤 키워드로 검색할까?"** 가 기준이다.

---

## 1. 범용 frontmatter 스키마

md 파일 생성 시 YAML frontmatter에 다음 필드를 포함한다.

### 필수 필드

```yaml
---
tags: [프로젝트, 문서유형, 도메인/기능, ...내용기반 키워드]
date: 2026-03-11
---
```

| 필드 | 타입 | 필수 | 설명 |
|------|------|:----:|------|
| `tags` | list | ✅ | 검색 친화적 키워드 태그 |
| `date` | string | ✅ | `YYYY-MM-DD` 형식 |

### 권장 필드 (PDCA/프로젝트 문서)

```yaml
---
tags: [ordify, plan, procurement, modal, ux, v3]
date: 2026-03-09
feature: procurement-modal-system
status: completed
phase: plan
aliases:
  - 품의서 모달 시스템
related:
  - "[[procurement-modal-system.design]]"
---
```

| 필드 | 타입 | 필수 | 설명 |
|------|------|:----:|------|
| `feature` | string | 권장 | feature 식별자 (kebab-case). Dataview로 같은 feature PDCA 전체 조회 |
| `status` | string | 권장 | `completed`, `in-progress`, `pending`, `archived`, `deprecated` |
| `phase` | string | 권장 | `plan`, `design`, `analysis`, `report`, `note`, `index` |
| `aliases` | list | 선택 | 한글 제목 등 대체 검색어. Obsidian 검색 시 활용 |
| `related` | list | 선택 | 관련 문서 wikilink `[[파일명]]` (확장자 제외) |

### 분석/보고서 전용 필드

| 필드 | 타입 | 필수 | 설명 |
|------|------|:----:|------|
| `match-rate` | number | 선택 | 갭분석 점수 (0~100, % 제외). analysis/report 문서에만 |

---

## 2. 태깅 규칙

### 핵심 원칙

1. **검색어 = 태그** — Claude가 검색할 때 쓸 법한 단어가 태그
2. **내용 기반** — 파일명/경로보다 **내용에서 드러나는 키워드**가 중요
3. **자유 태깅** — 고정 개수 없음. 3개일 수도 12개일 수도 있다
4. **kebab-case** — 모든 태그는 kebab-case

### 태그 구성

| 역할 | 예시 | 규칙 |
|------|------|------|
| 프로젝트 | `ordify`, `stalab` | 항상 1개 포함 |
| 문서 유형 | `plan`, `design`, `bug`, `til`, `decision` | 1개 이상 |
| 도메인/기능 | `web`, `db`, `auth`, `fpga` | 해당되는 것 모두 |
| 내용 키워드 | `modal`, `inline-edit`, `supabase` | 자유롭게 추가 |
| 상태 | `completed`, `in-progress`, `archived` | 해당 시 |

### 예시

```yaml
# 웹 프로젝트 버그 기록
tags: [ordify, bug, web, inline-edit, datagrid, tanstack]
date: 2026-03-11
feature: datagrid-inline-edit-fix
status: completed
phase: note
aliases:
  - DataGrid 인라인 편집 버그 수정

# FPGA 학습 노트
tags: [stalab, til, fpga, timing, clock-domain-crossing]
date: 2026-03-11

# 기술 결정 기록
tags: [blog-test, decision, web, nextjs, server-action, caching]
date: 2026-03-11
status: completed
phase: note
aliases:
  - Next.js 캐싱 전략 결정
```

---

## 3. 노트 자동 생성 워크플로우

### 생성 트리거

| 상황 | 노트 위치 | 필수 태그 |
|------|----------|----------|
| 버그 해결 | `2-notes/{domain}/{project}/` | `[프로젝트, bug, ...]` |
| 중요 결정 | `2-notes/{domain}/{project}/` | `[프로젝트, decision, ...]` |
| 새로운 학습 | `2-notes/{domain}/{project}/` | `[프로젝트, til, ...]` |
| 세션 종료 요약 | `2-notes/daily/` | `[session, ...]` |

### 파일명 규칙
- **kebab-case**: `ordify-인라인-편집-버그-수정.md`
- 프로젝트명 접두사 권장

### 생성 방법

#### Obsidian CLI (Obsidian 실행 중일 때, 권장)
```bash
obsidian create name="노트명" content="---\ntags: [프로젝트, 유형, 도메인]\ndate: YYYY-MM-DD\n---\n\n# 제목\n\n내용" silent
```

#### 파일 시스템 직접 (Obsidian 꺼져있을 때)
Write 도구로 파일 생성. 태깅 규칙만 준수하면 됨.

### 위키링크
- 관련 노트끼리 `[[노트명]]` 위키링크로 연결
- 설계 → 버그 → 해결 TIL 순서로 링크 체인 유지
- frontmatter `related` 필드에도 주요 참조 문서 기록

---

## 4. CLI 검색 주요 패턴

> 상세 명령어는 `obsidian:obsidian-cli` 스킬 참조

| 용도 | 명령어 |
|------|--------|
| 키워드 검색 | `obsidian search query="키워드" limit=N` |
| 이름으로 읽기 | `obsidian read file="노트이름"` |
| 경로로 읽기 | `obsidian read path="경로/파일.md"` |
| 노트 생성 | `obsidian create name="이름" content="내용" silent` |
| 태그 목록 | `obsidian tags counts sort=count` |
| 특정 태그 정보 | `obsidian tag name="태그" verbose` |
| 백링크 | `obsidian backlinks file="노트이름"` |
| 프로퍼티 설정 | `obsidian property:set name="tags" value="[...]" file="이름"` |

---

## 5. Dataview 쿼리 패턴

frontmatter 필드를 활용한 Dataview 쿼리 예시:

```dataview
# 특정 feature의 PDCA 전체 추적
TABLE phase, status, match-rate
FROM "1-projects/web/ordify/docs"
WHERE feature = "procurement-modal-system"
SORT phase ASC
```

```dataview
# 분석 문서 match-rate 순 정렬
TABLE feature, match-rate, status
FROM "1-projects/web/ordify/docs"
WHERE phase = "analysis"
SORT match-rate ASC
```

```dataview
# 진행 중인 작업만
TABLE feature, phase, date
WHERE status = "in-progress"
SORT date DESC
```

---

## 6. 프로젝트별 오버라이드

프로젝트 내 `.claude/skills/`에 태깅 스킬이 있으면
이 범용 규칙 대신 해당 프로젝트의 태깅 규칙을 **우선 적용**한다.

| 프로젝트 | 스킬 | 오버라이드 내용 |
|----------|------|----------------|
| Ordify | `obsidian-tagging` | Ordify 전용 기능영역 태그 + 기술 키워드 사전 |
| 기타 | 없음 | 이 스킬의 범용 규칙 적용 |

프로젝트 태깅 스킬을 만들려면:
1. `.claude/skills/{스킬명}/SKILL.md` 생성
2. 프로젝트 전용 태그/키워드 사전 정의
3. 이 스킬의 범용 frontmatter 스키마를 확장하는 형태로 작성
