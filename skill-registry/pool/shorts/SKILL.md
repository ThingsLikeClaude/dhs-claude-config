---
name: shorts
description: |
  YouTube Shorts 자동 생성. 주제 입력 → 리서치→대본→이미지→TTS→자막→컴파일 → final.mp4 출력.
argument-hint: "주제 (e.g., '인류가 풀지 못한 미스터리')"
user-invocable: true
---

# Shorts Pipeline Skill

`/shorts "주제"` → 완성된 YouTube Shorts 영상 (output/{id}/final.mp4)

## Execution Flow

Execute phases sequentially. Report progress after each phase. All paths are relative to project root.

### Phase 1: 프로젝트 초기화

```bash
node scripts/init-project.js
```

Parse stdout JSON → extract `projectId` and `outputDir`. Use these in all subsequent steps.

### Phase 2: 리서치

**반드시 NotebookLM Skill을 사용하여 리서치한다.** web-search-agent나 WebSearch를 먼저 시도하지 마라.

1. **NotebookLM Skill** (`/notebooklm`): 노트북 생성 → 주제 관련 웹 소스 3~5개 추가 → 트렌드/후킹/팩트 질문
   - 주제에 대한 구체적 수치, 최신 데이터, 논란 포인트를 반드시 수집
   - NotebookLM이 사용 불가능한 경우에만 아래 폴백 사용
2. **WebSearch fallback**: NotebookLM 실패 시에만 WebSearch로 3-5개 소스 수집
3. **Knowledge fallback**: 위 둘 다 실패 시 Claude의 지식으로 생성

Write result to `{outputDir}/research.json`:
```json
{
  "topic": "주제",
  "trends": ["관련 트렌드 키워드들"],
  "hooks": ["시선 잡는 후킹 문장 3개"],
  "facts": [{ "key": "핵심 수치/사실", "value": "구체적 데이터" }],
  "style": "informative-shock"
}
```

### Phase 3: 대본 생성

Read `config/default.json` to get `style.tonePresets` for the visual tone. Default tone: `warm-cinematic`.

**Claude directly writes** `{outputDir}/script.json`. No subprocess. Follow these rules:

- **7~9 scenes**, 45~55초 total duration
- **Scene 1**: 강력한 후킹 — 3초 안에 시선 잡기 (충격/궁금증/숫자)
- **Last scene**: CTA — 댓글/구독 유도
- **Each scene**: 3~7초 분량
- **tts_text**: **음슴체**로 작성 (~임, ~음, ~됨, ~함, ~인듯). 예: "이거 진짜 소름임", "알고 나면 충격받음", "근데 이게 실화임"
- **image_prompt**: 반드시 스타일 프리픽스로 시작 (e.g., `"warm lighting, cinematic composition, consistent color grading, professional photography, [scene 설명], 9:16 vertical composition, high quality"`)
- 리서치의 facts/numbers를 적극 활용
- **text** 필드는 화면에 표시할 핵심 키워드 (짧게, 10자 이내)

Output JSON structure:
```json
{
  "title": "영상 제목",
  "scenes": [
    {
      "id": 1,
      "text": "화면 텍스트 (짧게)",
      "tts_text": "TTS로 읽을 구어체 텍스트",
      "duration_hint": 5,
      "image_prompt": "style prefix, scene description in English, 9:16 vertical composition, high quality",
      "style_tags": ["tag1", "tag2"],
      "motion_prompt": "slow zoom in"
    }
  ],
  "metadata": {
    "total_scenes": 7,
    "target_duration": 50,
    "visual_tone": "warm-cinematic",
    "font_style": "bold-impact"
  }
}
```

### Phase 4: 이미지 생성

```bash
node scripts/gen-images.js {projectId}
```

Generates 1080x1920 images via Gemini Nano Banana 2 (`gemini-3.1-flash-image-preview`). Stdout is JSON with results. Log progress from stderr. Some scenes may fail — that's OK.

### Phase 5: 영상 변환

Read `config/default.json` → check `grok.enabled`.

**If `grok.enabled: true`**: Use Playwright MCP to automate grok.com:
1. `browser_navigate` → `https://grok.com`
2. `browser_snapshot` → check login status
3. If not logged in → tell user to log in manually, wait
4. For each scene with an image:
   - Navigate to grok.com/imagine (or appropriate page)
   - `browser_snapshot` to understand current DOM
   - Upload image via `browser_file_upload`
   - Enter motion prompt
   - Click generate and wait for result
   - Download result video
5. Save to `{outputDir}/videos/{sceneId}.mp4`

**If `grok.enabled: false`**: Skip entirely. The compile step automatically uses Ken Burns effect on images.

### Phase 6: TTS → 자막 → 컴파일

Run sequentially:

```bash
node scripts/gen-tts.js {projectId}
node scripts/gen-subtitles.js {projectId}
node scripts/compile.js {projectId}
```

Each script reads `script.json` and writes to the appropriate subdirectory. `compile.js` produces `final.mp4`.

**TTS 호흡 포인트**: tts_text에 쉼표(`,`)를 넣으면 TTS가 짧게 쉼. 단, 너무 많이 넣으면 뚝뚝 끊김. 마침표(`.`) 끊기만으로 충분한 경우가 많음.

**자막-TTS 싱크**: gen-subtitles.js가 자동으로 TTS durationMs에 맞춰 자막 타이밍을 생성함. 자막에는 호흡용 쉼표가 자동 제거됨.

**검증**: 컴파일 전에 TTS-자막 싱크가 0ms 차이인지 확인할 것.

Report the final video path to the user.

## Error Recovery

| Phase | On Failure |
|-------|-----------|
| Research | Use Claude's knowledge as fallback data |
| Script | Retry generation (Claude can't really fail here) |
| Images | Failed scenes skipped; compile uses available images |
| Video | Failed scenes get Ken Burns effect automatically |
| TTS | **Fatal** — stop and report error |
| Compile | Report error, suggest: `node scripts/compile.js {projectId}` |

## Style Tones

Available in `config/default.json` → `style.tonePresets`:
- `warm-cinematic` (default): warm lighting, cinematic composition
- `dark-dramatic`: dark moody, high contrast, dramatic shadows
- `bright-clean`: bright natural, clean white, minimal

User can specify tone: `/shorts "주제" --tone dark-dramatic`
Parse `--tone` from args if present, otherwise use default.
