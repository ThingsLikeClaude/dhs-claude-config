# Ordify DDD-Lite 리팩토링 계획

## Context

Ordify의 비즈니스 로직(상태 전이, 검증, 권한, 도메인 간 자동생성)이 Server Action에 절차적으로 혼재되어 있다. 이로 인해:
- AI 프롬프트에서 "품의서 승인"이라 하면 confirm인지 approve인지 혼란
- 비즈니스 규칙이 Supabase에 종속되어 단위 테스트 불가
- 품의서 생성 시 delivery/statement 자동생성이 강결합 (dynamic import)
- 같은 검증 로직이 crud.ts 여러 곳에 반복

DDD-Lite를 적용하여 **순수 도메인 레이어**를 추출하고, Server Action은 "얇은 컨트롤러"로 유지한다.

## 디렉토리 구조

```
frontend/src/domain/                    # NEW: Supabase 의존 없는 순수 도메인
├── procurement/
│   ├── procurement-status.ts           # 상태 전이 규칙 + is_confirmed 동기화
│   ├── procurement-rules.ts            # 불변규칙 (최소1품목, 수량>0, 단가>=0)
│   ├── procurement-number.ts           # 번호 포맷팅 (801-YY-NNN)
│   └── procurement-policies.ts         # 자기승인방지, 수정/삭제 권한, 소급승인
├── events.ts                           # DomainEvent → SideEffect 매핑 (순수 함수)
└── index.ts                            # barrel export

frontend/src/app/actions/procurements/
└── _side-effects.ts                    # NEW: SideEffect 실행기 (인프라 의존)
```

## Phase 1: Value Objects — 상태 전이 + 번호 (의존성 없음)

### 1-1. `domain/procurement/procurement-status.ts`
**추출 원본**: `types/procurement.types.ts` L231-240 (PROCUREMENT_STATUS_TRANSITIONS)

```typescript
// 순수 함수 인터페이스
canTransition(current, target, { isManager }): { ok, reason? }
getAvailableTransitions(current, { isManager }): ProcurementStatus[]
deriveConfirmationState(newStatus): { is_confirmed?, confirmed_by?, confirmed_at? }
```

- `PROCUREMENT_STATUS_TRANSITIONS`를 domain/으로 이동
- `types/procurement.types.ts`에서 re-export하여 기존 import 유지
- `deriveConfirmationState`: services/supabase/procurements.ts L871-879의 is_confirmed 동기화 로직 추출

### 1-2. `domain/procurement/procurement-number.ts`
**추출 원본**: `app/actions/procurements/forms.ts` L37-62

```typescript
formatProcurementNumber(year, sequence): string  // "801-26-001"
parseProcurementNumber(number): { buildingCode, year, sequence } | null
nextSequence(lastNumber, year): string
```

- DB 조회(시퀀스)는 Server Action에 남기고, 포맷팅 규칙만 도메인으로

## Phase 2: Aggregate Rules — 검증 로직 추출

### 2-1. `domain/procurement/procurement-rules.ts`
**추출 원본**: `crud.ts` 인라인 검증들

```typescript
validateMinimumItems(items): { ok, reason? }      // L351-353, L1096-1097
validateItemValues({ quantity, unit_price }): { ok, reason? }  // L360-366
canEdit({ status }, { isManager }): boolean        // L511-518
canDelete({ user_id }, { userId, isManager }): boolean  // L593-598
canDeleteItem(currentItemCount): boolean           // L1096-1097
```

### 2-2. Server Action 변경
- `createProcurementAction`: L342-366의 inline 검증 → `validateMinimumItems` + `validateItemValues` 호출
- `addProcurementItemAction`: L898-909 → 도메인 함수 호출
- `updateProcurementAction`: L511-518 → `canEdit` 호출
- `deleteProcurementAction`: L593-598 → `canDelete` 호출
- `deleteProcurementItemAction`: L1096-1097 → `canDeleteItem` 호출

## Phase 3: Policies — 권한/자기승인 추출

### 3-1. `domain/procurement/procurement-policies.ts`
**추출 원본**: `workflow.ts`

```typescript
canApprove({ user_id }, { userId }): { ok, reason? }  // L89-93
canRequestRetroactiveApproval({ status, is_pre_order, retroactive_approved_at }): { ok, reason? }  // L253-261
canApproveRetroactively({ user_id, ... }, { userId }): { ok, reason? }  // L300-321
```

### 3-2. Server Action 변경
- `workflow.ts`의 `transitionStatus`: L64-93 검증 → 도메인 함수 호출
- `services/supabase/procurements.ts`의 `updateProcurementStatus`: L871-879 → `deriveConfirmationState()` 호출

## Phase 4: 도메인 이벤트 — 결합도 감소

### 4-1. `domain/events.ts`
```typescript
type DomainEvent =
  | { type: 'PROCUREMENT_CREATED'; procurementId: string }
  | { type: 'PROCUREMENT_ORDERED'; procurementId: string }
  | { type: 'PRE_ORDER_ACTIVATED'; procurementId: string }

type SideEffect =
  | { type: 'GENERATE_DELIVERY_ITEMS'; procurementId: string }
  | { type: 'GENERATE_STATEMENTS'; procurementId: string }
  | { type: 'REVALIDATE_PATHS'; paths: string[] }

// 순수 함수: 이벤트 → 부수효과 목록
resolveSideEffects(event: DomainEvent): SideEffect[]
```

### 4-2. `app/actions/procurements/_side-effects.ts`
```typescript
// 인프라 함수: SideEffect 배열 실행
executeSideEffects(effects: SideEffect[]): Promise<void>
```

- `generateDeliveryItemsForProcurement` dynamic import를 여기에 집중
- `generateStatementsForProcurement`도 여기로 이동

### 4-3. Server Action 변경 (5곳)
| 파일 | 함수 | 현재 | 변경 후 |
|------|------|------|---------|
| crud.ts | createProcurementAction L382-389 | delivery 직접 호출 | `resolveSideEffects('CREATED')` → `executeSideEffects` |
| crud.ts | togglePreOrderAction L1284-1292 | delivery+statement 직접 호출 | `resolveSideEffects('PRE_ORDER')` → `executeSideEffects` |
| workflow.ts | markOrderedAction L169-173 | delivery 직접 호출 | `resolveSideEffects('ORDERED')` → `executeSideEffects` |
| workflow.ts | preOrderAction L228-232 | delivery 직접 호출 | `resolveSideEffects('PRE_ORDER')` → `executeSideEffects` |
| workflow.ts | forceChangeStatusAction L492-495 | delivery 직접 호출 | `resolveSideEffects('ORDERED')` → `executeSideEffects` |

## Phase 5: 유비쿼터스 언어 + 문서

### 5-1. CLAUDE.md에 도메인 용어 사전 추가

| 한국어 | 코드 | 설명 |
|--------|------|------|
| 품의서 | Procurement | 구매 요청 문서 (Aggregate Root) |
| 품목 | ProcurementItem | 품의서 내 개별 구매 항목 (Entity) |
| 품의번호 | ProcurementNumber | 801-YY-NNN 패턴 (Value Object) |
| 승인 | approve (status: approved) | 부서장이 품의서를 승인 |
| 확정 | confirm (is_confirmed) | **[레거시]** boolean 플래그. approve와 혼용 중 |
| 발주 | order (status: ordered) | 공급사에 발주 |
| 선발주 | preOrder (is_pre_order) | 승인 생략 긴급 발주 |
| 소급 승인 | retroactiveApproval | 선발주 후 사후 승인 2단계 |
| 입고 | delivery/receiving | 물품 도착 (DeliveryItem으로 추적) |
| 거래명세서 | statement | 납품업체별 거래 증빙 |

### 5-2. `.claude/docs/project-structure.md` 업데이트
- `domain/` 디렉토리 설명 추가

## Critical Files

| 파일 | 역할 |
|------|------|
| `frontend/src/types/procurement.types.ts` | PROCUREMENT_STATUS_TRANSITIONS 원본 → domain/으로 이동, re-export |
| `frontend/src/app/actions/procurements/crud.ts` | 검증 로직 추출 + delivery 직접 호출 제거 |
| `frontend/src/app/actions/procurements/workflow.ts` | 상태 전이 + 정책 검증 추출 + delivery 직접 호출 제거 |
| `frontend/src/services/supabase/procurements.ts` | is_confirmed 동기화 → deriveConfirmationState() 호출 |
| `frontend/src/app/actions/delivery.ts` | generateDeliveryItemsForProcurement (이동 대상 아님, 호출 방식만 변경) |

## Verification

각 Phase 완료 후:
1. `pnpm tsc --noEmit` — 타입 체크 통과
2. `pnpm build` — 빌드 성공
3. 수동 테스트:
   - 품의서 생성 → delivery_items 자동 생성 확인
   - 품의서 승인/반려 → 상태 전이 확인
   - 선발주 → delivery + statement 자동 생성 확인
   - 품목 추가/삭제 → 최소 1품목 검증 확인

## 제외 사항 (YAGNI)

- Repository 패턴: Supabase 클라이언트가 이미 추상화 역할
- Bounded Context 분리: 1인 개발에서 불필요
- CQRS: 프로젝트 규모에 비해 과잉
- is_confirmed/status 이중 상태 제거: 별도 마이그레이션으로 분리
- 단위 테스트 작성: 도메인 레이어 완성 후 별도 작업으로
