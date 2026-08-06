# MVP Risk Register

| ID | Risk | Likelihood | Impact | Preventive action | Fallback/owner |
|---|---|---:|---:|---|---|
| R-01 | OCR misses a material clause | Medium | High | Golden annotations; page-level evidence; critical-fact recall gate | Use labeled preprocessed fixture; backend owner |
| R-02 | LLM invents or overstates a condition | Medium | High | Schema constraints; verified-fact allowlist; unsupported-claim review | Replace with `needs_review`; AI owner |
| R-03 | Money calculation is wrong | Low–Medium | Critical | Pure deterministic functions; independent fixtures; versioned formulas | Disable affected simulation; backend owner |
| R-04 | Explanation modes change facts or numbers | Medium | High | Generate from immutable snapshot; consistency tests | Fall back to static grounded templates; frontend/AI owner |
| R-05 | Arbitrary upload exposes sensitive data | Medium | High | Synthetic-only notice; private storage; deletion TTL; no content logs | Delete/rotate/investigate; infra owner |
| R-06 | Malicious PDF or document prompt injection | Medium | High | File limits; parser isolation; document text treated as data | Reject upload/use fixture; backend owner |
| R-07 | External AI/OCR provider times out during demo | Medium | High | Warm-up; timeout; cached grounded output | Preprocessed primary fixture; demo operator |
| R-08 | Public demo produces uncontrolled cost | Medium | Medium–High | Rate and spend limits; budget alerts; kill switch | Disable new processing; infra owner |
| R-09 | Accessibility is added too late | Medium | High | Semantic components and keyboard test in every slice | Freeze new features; frontend owner |
| R-10 | Three product types cause scope failure | High | High | Deposit-first P0; loans/insurance remain P1 | Cut P1 without weakening P0; product owner |
| R-11 | QM/harness instability blocks development | Medium | Medium | Product repo and CI independent of QM; pinned QM version | Use local coding tools and GitHub directly; both |
| R-12 | Domain/OAuth change breaks callbacks | Low–Medium | Medium | Use stable provider URL until P0; freeze DNS before demo | Revert to provider URL; infra owner |

Review this register at each milestone exit. Any new critical risk requires an owner and fallback before feature work continues.
