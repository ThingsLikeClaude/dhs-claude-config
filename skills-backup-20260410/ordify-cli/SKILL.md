---
name: ordify-cli
description: Ordify 구매관리 시스템 CLI 스킬. 품의서 조회/승인/반려/발주, 대시보드 통계, 사용자/거래처 관리를 자연어로 실행. "품의서 보여줘", "승인해줘", "통계", "거래처 검색" 등의 자연어 명령을 ordify CLI로 변환하여 실행합니다.
---

# Ordify CLI Skill

Ordify 구매관리 시스템의 CLI 도구를 자연어로 실행하는 스킬입니다.
사용자의 자연어 요청을 적절한 `ordify` CLI 명령으로 변환하여 Bash로 실행합니다.

## 사용 가능한 명령어

### 품의서 관리
| 명령어 | 설명 | 예시 |
|--------|------|------|
| `ordify list` | 품의서 목록 | `ordify list -s pending` |
| `ordify show <번호>` | 품의서 상세 | `ordify show 801-26-015` |
| `ordify approve <번호>` | 승인 | `ordify approve 801-26-015 -f` |
| `ordify reject <번호> -r "사유"` | 반려 | `ordify reject 801-26-015 -r "예산 초과"` |
| `ordify order <번호>` | 발주 | `ordify order 801-26-015 --pre-order` |

### 통계/대시보드
| 명령어 | 설명 | 예시 |
|--------|------|------|
| `ordify stats` | 전체 통계 | `ordify stats` |
| `ordify summary` | 월간 요약 | `ordify summary -m 3 -y 2026` |

### 마스터 데이터
| 명령어 | 설명 | 예시 |
|--------|------|------|
| `ordify users` | 사용자 목록 | `ordify users` |
| `ordify teams` | 팀 목록 | `ordify teams` |
| `ordify suppliers` | 거래처 목록 | `ordify suppliers -q "반도체"` |

### 설정
| 명령어 | 설명 |
|--------|------|
| `ordify config` | 연결 상태 확인 |

## 자연어 → CLI 변환 규칙

사용자가 자연어로 요청하면, 아래 규칙에 따라 적절한 CLI 명령으로 변환하여 **Bash 도구로 실행**합니다.

### 조회 요청
| 자연어 | CLI 명령 |
|--------|----------|
| "품의서 보여줘" / "목록" | `ordify list` |
| "미승인 품의서" / "승인대기" | `ordify list -s pending` |
| "이번 달 품의서" | `ordify list -m <현재월> -y <현재년>` |
| "801-26-015 상세" | `ordify show 801-26-015` |
| "삼성 관련 품의서" | `ordify list -q "삼성"` |
| "발주 완료된 것만" | `ordify list -s ordered` |

### 상태 변경 요청
| 자연어 | CLI 명령 |
|--------|----------|
| "801-26-015 승인해줘" | `ordify approve 801-26-015 -f` |
| "반려해줘, 예산 초과" | `ordify reject 801-26-015 -r "예산 초과"` |
| "발주 처리해줘" | `ordify order 801-26-015` |
| "선발주로 처리" | `ordify order 801-26-015 --pre-order` |

### 통계/보고
| 자연어 | CLI 명령 |
|--------|----------|
| "현황 알려줘" / "통계" | `ordify stats` |
| "3월 요약" | `ordify summary -m 3` |
| "이번 달 요약" | `ordify summary` |

### 마스터 데이터
| 자연어 | CLI 명령 |
|--------|----------|
| "사용자 목록" / "직원 보여줘" | `ordify users` |
| "팀 목록" | `ordify teams` |
| "거래처 찾아줘" | `ordify suppliers` |
| "반도체 거래처" | `ordify suppliers -q "반도체"` |

## 실행 규칙

1. **항상 Bash 도구로 실행**: `ordify` 명령을 Bash 도구를 통해 실행합니다.
2. **결과 해석**: CLI 출력(Rich 테이블)을 읽고 사용자에게 자연어로 요약합니다.
3. **연속 작업 지원**: "승인대기 품의서 보여주고, 첫 번째거 승인해줘" 같은 연속 요청을 순차 실행합니다.
4. **확인 필요 작업**: 상태 변경(승인/반려/발주)은 `-f` 플래그로 확인을 건너뛰되, 사용자에게 결과를 명확히 보고합니다.
5. **오류 처리**: 명령 실패 시 에러 메시지를 해석하여 사용자에게 원인과 해결책을 안내합니다.

## 환경 설정

CLI는 `frontend/.env.local`의 Supabase 키를 자동으로 찾습니다.
Ordify 프로젝트 디렉토리에서 실행하세요.
