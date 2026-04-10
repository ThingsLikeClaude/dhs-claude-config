# agent-memory 전체 삭제 플랜

## Context
`~/.claude/agent-memory/` 디렉토리에 프로젝트 종속 메모리(TITrack, FPGA-ANALYSIS, Ordify 등)와 낡은 범용 리서치 메모리가 혼재. 사용자가 전부 삭제 결정.

## 삭제 대상

```
~/.claude/agent-memory/
├── MEMORY.md                          # 루트 인덱스 (web-search-agent 중복)
├── bkit-report-generator/MEMORY.md    # PDCA 템플릿 패턴
├── data-agent/MEMORY.md               # TITrack 데이터
├── titrack-backend-agent/MEMORY.md    # TITrack 백엔드
├── tlidb-web-crawler/MEMORY.md        # TITrack 크롤러
└── web-search-agent/
    ├── MEMORY.md                      # 범용 리서치 패턴
    ├── altium-file-formats.md         # FPGA 프로젝트
    ├── circuit-schematic-analysis.md  # FPGA 프로젝트
    ├── shorts-subtitle-design.md      # YouTube Shorts
    └── youtube-mcp-servers.md         # YouTube MCP
```

## 실행

```bash
rm -rf ~/.claude/agent-memory
```

단일 명령으로 디렉토리 통째 삭제.

## 검증

```bash
ls ~/.claude/agent-memory  # "No such file or directory" 확인
```
