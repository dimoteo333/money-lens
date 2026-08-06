# Money Lens

> 금융상품에 동의하기 전에, 사용자가 중요한 조건과 자신의 돈에 미치는 영향을 이해하도록 돕는 의사결정 지원 서비스

Money Lens는 긴 금융상품 설명서를 단순히 요약하는 데서 멈추지 않습니다. 문서에서 중요한 사실을 근거와 함께 추출하고, 결정론적 계산으로 금전 시나리오를 보여주며, 사용자가 핵심 조건을 이해했는지 확인합니다.

Money Lens는 금융·법률·신용·투자 자문이 아니며 상품 가입을 추천하거나 적합성·자격을 판단하지 않습니다.

## 현재 상태

이 저장소는 경쟁용 MVP의 **harness-first 기준선**을 만드는 단계입니다.

- 제품 목표, 안전 경계, 데이터 계약, 품질 기준을 먼저 고정합니다.
- 아직 Next.js 또는 FastAPI 애플리케이션 코드는 scaffold하지 않았습니다.
- P0는 정기예금 한 가지 흐름을 끝까지 검증한 뒤 확장합니다.
- 사람과 AI Agent는 동일한 문서와 GitHub Issue를 작업 기준으로 사용합니다.

## 해결하려는 문제

금융상품은 중요한 조건을 공개하지만, 정보가 제공됐다는 사실이 사용자의 이해를 보장하지는 않습니다. 사용자는 다음과 같은 조건이 자신의 돈에 어떤 영향을 주는지 놓치기 쉽습니다.

- 우대금리를 받기 위한 조건
- 만기 전 해지 시 적용되는 낮은 이자율
- 원금 보호와 예금자보호 범위
- 변동금리 노출
- 보험 보장 제외 또는 감액 조건
- 자동 갱신이나 특정 자격 유지 조건

Money Lens가 사용자를 대신해 결정을 내리지는 않습니다. 대신 다음 질문에 근거를 갖고 답할 수 있도록 돕습니다.

1. 나는 무엇에 동의하려는가?
2. 내 돈에는 어떤 일이 생길 수 있는가?
3. 어떤 조건을 더 주의해서 봐야 하는가?
4. 나는 중요한 내용을 제대로 이해했는가?
5. 가입 전에 무엇을 추가로 물어봐야 하는가?

핵심 원칙은 다음과 같습니다.

> “설명했다”에서 끝내지 않고, 중요한 조건을 사용자가 이해했는지 확인한다.

## P0 데모 흐름

1. **문서 업로드 또는 선택**
   - PDF, PNG, JPEG를 받습니다.
   - live 처리 실패에 대비해 동일한 데이터 계약을 사용하는 preprocessed fixture를 제공합니다.
2. **근거가 연결된 사실 확인**
   - 만기, 기본·우대금리, 중도해지, 예금자보호 등 고영향 사실을 페이지와 정확한 발췌문에 연결합니다.
3. **중요 조건과 위험 검토**
   - 검증된 사실에 버전이 있는 결정론적 규칙을 적용합니다.
   - 불명확하거나 충돌하는 근거는 `needs_review`로 표시합니다.
4. **중도해지 금전 시나리오**
   - 사용자가 예치금액, 가입일, 해지일을 입력합니다.
   - 버전이 있는 순수 계산 함수만 authoritative 결과를 생성합니다.
5. **이해 확인과 재설명**
   - 중요한 조건에 관한 짧은 질문을 제시합니다.
   - 오답 또는 “잘 모르겠음”에는 같은 사실을 다른 방식으로 다시 설명합니다.
6. **한 페이지 리포트**
   - 인쇄 가능한 HTML로 사실, 가정, 계산 결과, 미확정 항목을 분리합니다.

## 설명 방식

P0는 동일한 검증 사실을 다음 세 가지 방식으로 표현합니다.

- **쉬운 설명(Plain Language):** 짧은 문장과 쉬운 용어
- **숫자 우선(Number-First):** 금액, 금리, 날짜, 차이를 먼저 표시
- **예시 우선(Example-First):** 예시임을 명확히 밝힌 구체적 상황부터 설명

설명 방식을 바꿔도 사실, 숫자, 상태, 위험 수준은 달라지지 않아야 합니다.

## 신뢰 경계

| 영역 | authoritative 주체 | 반드시 지킬 조건 |
|---|---|---|
| OCR·문서 구조 | OCR/layout adapter | 페이지와 좌표 정보를 보존 |
| 사실 추출 | schema-constrained extractor의 후보 결과 | 검증되지 않은 후보를 확정 사실로 사용하지 않음 |
| 사실 검증 | product-specific validator | 근거 부족·모호함·충돌을 `needs_review`로 처리 |
| 위험 판단 | 버전이 있는 결정론적 규칙 | matched rule과 근거 fact ID를 기록 |
| 금융 계산 | 테스트된 순수 함수 | LLM이 계산 결과를 만들거나 수정하지 못함 |
| 맞춤 설명 | 검증된 snapshot에 grounded된 생성 | 새로운 사실·숫자·보장·추천을 추가하지 않음 |
| UI·리포트 | immutable review snapshot | 불확실성, 근거, 가정, 버전을 숨기지 않음 |

LLM은 설명을 바꿀 수 있지만 authoritative 금융 계산을 수행하지 않습니다.

## 상태 모델

근거 검증 상태와 사용자에게 보여주는 검토 수준을 분리합니다.

### Fact status

- `verified`
- `needs_review`
- `not_found`
- `not_applicable`

### Review level

- `critical`
- `caution`
- `confirmed`
- `needs_review`

confidence 점수만으로 사실을 `verified`로 승격할 수 없습니다.

## P0 대표 자료와 계산 상태

- 참고 상품: **신한 SOL메이트 정기예금 상품설명서**
- 기준 버전: **2026-06-15**
- 원본 PDF는 저장소에 커밋하지 않고 로컬 검증에만 사용합니다.
- P0 시나리오는 만기 전 해지 시 예상 세전 이자와 만기 유지 시 이자의 차이를 보여줍니다.
- 경과월수와 윤년 일수 분모 등 공개 문서로 확정되지 않은 계산 세부값은 신한은행의 공식 확인 전까지 authoritative formula로 구현하지 않습니다.

원본 자료가 공개 URL로 조회된다는 사실만으로 재배포 권한을 가정하지 않습니다.

## 제안된 기술 방향

ADR-0003의 acceptance spike가 끝날 때까지 아래 구성은 `Proposed` 상태입니다.

- Monorepo
- Web: Next.js 16, TypeScript, Node.js 24 LTS, npm
- API: FastAPI, Python 3.12, `venv`와 고정된 `requirements.txt`
- 로컬 metadata: 메모리 저장소
- 로컬 문서 저장: Docker Compose 기반 MinIO
- CI: GitHub Actions
- P0 리포트: 인쇄 가능한 HTML
- 수동 접근성 기준: macOS VoiceOver, 키보드 전용 흐름, 200% 확대, 모바일 reflow

## 데모 운영 한도

| 항목 | P0 기준 |
|---|---:|
| 파일 크기 | 10 MB |
| PDF 페이지 | 20 |
| 이미지 픽셀 | 25,000,000 |
| 처리 timeout | 60초 |
| 문서 보관 | 24시간 |
| 세션별 live 처리 | 시간당 3회 |
| IP별 live 처리 | 시간당 20회 |
| 동시 처리 | 2건 |
| 일일 처리 예산 | 5,000원 |
| 예산 경고 | 70% |
| 신규 live 처리 중단 | 100% |

예산이 소진되거나 외부 provider가 실패해도 명확히 표시된 preprocessed fixture는 계속 사용할 수 있어야 합니다.

## 저장소 안내

다음 순서가 제품·구현 판단의 기준입니다.

1. [`README.md`](README.md) — 제품 목적, P0 흐름, 신뢰 경계
2. [`docs/PRD.md`](docs/PRD.md) — 우선순위와 acceptance criteria
3. [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) — 구성 요소와 trust boundary
4. [`docs/DATA_CONTRACTS.md`](docs/DATA_CONTRACTS.md) — authoritative 데이터 형태
5. [`docs/QUALITY_PLAN.md`](docs/QUALITY_PLAN.md) — 테스트와 release gate
6. [`docs/decisions/`](docs/decisions/) — 변경 비용이 큰 결정의 기록
7. [`AGENTS.md`](AGENTS.md) — coding Agent의 작업 계약

추가 문서:

- [`docs/DEMO_SCRIPT.md`](docs/DEMO_SCRIPT.md) — 3분 데모 흐름과 fallback
- [`docs/TASKS.md`](docs/TASKS.md) — milestone backlog
- [`docs/SECURITY_PRIVACY.md`](docs/SECURITY_PRIVACY.md) — 보안·개인정보 기준
- [`docs/ACCESSIBILITY.md`](docs/ACCESSIBILITY.md) — WCAG 2.2 AA 목표와 수동 검사
- [`CONTRIBUTING.md`](CONTRIBUTING.md) — branch, Issue, PR 규칙

문서가 충돌하면 편한 해석을 선택하지 말고 작업을 멈춘 뒤 PR에 충돌을 기록합니다.

## 사람과 AI Agent의 작업 방식

모든 변경은 GitHub Issue 하나에 연결합니다.

1. Issue와 acceptance criteria를 확인합니다.
2. 관련 계약, 테스트, ADR을 읽습니다.
3. 큰 수정 전에 짧은 구현 계획을 공유합니다.
4. 가장 작은 완전한 수직 결과만 구현합니다.
5. 테스트와 fixture를 함께 갱신합니다.
6. 저장소에 적힌 검사를 모두 실행합니다.
7. PR을 만들고 사람 리뷰와 CI를 통과시킵니다.

Agent는 직접 배포하지 않으며 실제 고객 문서, PII, 자격증명, document text가 포함된 prompt나 로그를 커밋하지 않습니다.

## 현재 로컬 검사

애플리케이션 scaffold 전에는 다음 검사가 필수입니다.

```bash
python3 -m json.tool schemas/product-facts.schema.json >/dev/null
```

코드가 추가되면 `AGENTS.md`와 CI에 install, lint, type-check, test, build, end-to-end 명령을 동일하게 기록합니다.

## 라이선스와 고지

코드는 [Apache License 2.0](LICENSE)에 따라 제공됩니다.

Money Lens의 결과는 의사결정을 돕기 위한 정보이며 금융·법률·신용·투자 자문 또는 상품 추천이 아닙니다.
