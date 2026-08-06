# Security and Privacy Baseline

## 1. MVP Data Policy

The competition MVP uses only synthetic, public-domain, licensed, or explicitly authorized sample documents. Do not upload real customer documents, account numbers, resident-registration numbers, signatures, addresses, or transaction histories.

The product UI must state this limitation before upload.

## 2. Threats in Scope

- Sensitive document exposure through storage, logs, analytics, or error tools.
- Malicious or malformed PDF/image input.
- Prompt injection embedded in uploaded documents.
- Cross-user document access through predictable IDs or broken authorization.
- Provider keys leaked through source control, browser bundles, or CI logs.
- Unbounded public use causing model or cloud cost spikes.
- Stale documents surviving beyond the stated retention period.

## 3. Required Controls

### Intake

- Allowlist PDF, PNG, and JPEG by signature and decoded content.
- Set file-size, page-count, pixel-count, and processing-time limits.
- Generate opaque server-side IDs; never use original filenames as storage keys.
- Treat all document text as untrusted data, not instructions.
- Isolate parsing from application credentials and outbound access where practical.

### Storage and transport

- Encrypt traffic with HTTPS and storage with provider-managed encryption.
- Use private object storage and short-lived signed access.
- Apply automatic deletion from `DOCUMENT_RETENTION_HOURS`.
- Store derived facts separately from raw files so deletion can be verified.

### Secrets and permissions

- Store provider keys in a managed secret store for demo deployment.
- Use short-lived CI-to-cloud identity; do not store permanent cloud keys in GitHub.
- Grant the application only the bucket, table, queue, and secret operations it needs.
- Keep QM/agent credentials separate from the product runtime.

### Logging

Allowed: request ID, duration, state transition, provider status code, token counts, rule/formula version, safe error code.

Forbidden: raw document text, full prompts, source excerpts, uploaded filenames containing PII, access tokens, signed URLs, API keys, user answers tied to identity.

## 4. Public Demo Controls

- Use anonymous browser sessions or restricted demo access; do not imply production identity assurance.
- Apply per-session and per-IP request limits.
- Cap document size, processing attempts, and model spend.
- Provide a manual kill switch for new processing while keeping static demo fixtures available.
- Keep an expiration date and teardown owner for every cloud resource.

### P0 configured limits

- Maximum upload size: 10 MB.
- Maximum PDF length: 20 pages.
- Maximum decoded image size: 25,000,000 pixels.
- Processing timeout: 60 seconds.
- Raw document retention: 24 hours.
- Live processing: 3 requests per session per hour and 20 requests per IP per hour.
- Maximum concurrent live processing: 2 requests.
- Daily processing budget: KRW 5,000; warn at 70% and stop new live processing at 100%.
- The kill switch stops new live processing but keeps labeled preprocessed fixtures available.

`.env.example` is the machine-readable bootstrap reference for these limits.

## 5. Incident Minimum

If accidental sensitive data is uploaded:

1. Stop new processing if exposure may continue.
2. Delete source, derived files, caches, and queued copies.
3. Rotate any possibly exposed credential.
4. Preserve safe audit metadata without retaining the sensitive content.
5. Document impact, cause, and prevention before reopening.

## 6. Production Gaps

The MVP is not approved for real customer data. Production use would additionally require formal threat modeling, legal and regulatory review, retention governance, provider agreements, stronger authentication/authorization, audit trails, incident response, model-risk review, and security testing.
