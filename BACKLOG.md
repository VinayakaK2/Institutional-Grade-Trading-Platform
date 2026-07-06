# Project Backlog

## Phase 2.5 Post-Freeze Recommendations
These items were identified as minor engineering recommendations during the Phase 2.5 freeze and are targeted for inclusion in Phase 2.6 or later.

1. **Introduce dataset-level Certification IDs:**
   - Every certification run should generate a unique Certification ID.
   - This ID should be attached to:
     - ValidationReport
     - CleaningResult
     - Canonical Dataset
     - Quarantine Records
   - This allows complete traceability of every certification run.

2. **Persist Validation Metrics:**
   - Besides reports, persist aggregated metrics such as:
     - `validation_duration`
     - `cleaning_duration`
     - `records_processed`
     - `records_rejected`
     - `anomaly_count`
     - `gap_count`
   - These metrics will later feed dashboards and operational monitoring.

3. **Future-proof replay support:**
   - The current Quarantine implementation preserves rejected records.
   - During Phase 2.6+, ensure the `CertificationPipeline` can replay quarantined datasets after validation rules are updated without requiring another provider download.

## Phase 2.6 Post-Freeze Recommendations
These items were identified as minor engineering recommendations during the Phase 2.6 freeze and are targeted for inclusion in Phase 2.7 or later.

1. **Deterministic Processing Order**:
   - Ensure the adjustment pipeline explicitly documents that multiple corporate actions are applied in deterministic chronological order.

2. **Document Rounding Policy**:
   - Explicitly document the rounding policy (Prices: full floating-point precision, Volume: floor() to integer) to avoid ambiguity.

3. **Multi-Action Regression Tests**:
   - Ensure the processing order for multiple corporate actions on different dates for the same symbol is fully deterministic and covered by regression tests.
