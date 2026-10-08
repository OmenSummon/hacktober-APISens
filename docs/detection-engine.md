# API Sentinel Detection Engine & Risk Methodology

This document details the deterministic rules, matching algorithms, and risk scoring equations used by API Sentinel.

---

## 1. Path Normalization Algorithm

Given an observed path $P_{obs}$ and an OpenAPI template set $\{T_1, T_2, \dots, T_n\}$:

### Phase 1: OpenAPI Pattern Matching
1. Convert each OpenAPI path template into a regular expression:
   - `/users/{id}` $\rightarrow$ `^/users/([^/]+)$`
   - `/orgs/{org_id}/repos/{repo_id}` $\rightarrow$ `^/orgs/([^/]+)/repos/([^/]+)$`
2. Test $P_{obs}$ against each compiled regex.
3. If matched, return the canonical template string.

### Phase 2: Heuristic Token Identification
If no OpenAPI template matches:
1. Split path into segments by `/`.
2. Evaluate each segment against token detectors:
   - **Integer ID**: Regular expression `^\d+$` (e.g. `42`, `1001`) $\rightarrow$ `{id}`
   - **UUID**: Standard 8-4-4-4-12 hex format $\rightarrow$ `{id}`
   - **MongoDB ObjectId**: 24-char hex string $\rightarrow$ `{id}`
3. Reserved segments (e.g. `v1`, `v2`, `admin`, `api`, `debug`, `health`, `metrics`, `users`, `products`) are explicitly excluded from dynamic token replacement.

---

## 2. Detection Categories

| Type | Severity | OWASP API Top 10 | Trigger Condition |
| :--- | :--- | :--- | :--- |
| **`SHADOW_ENDPOINT`** | `HIGH` / `CRITICAL` | API9: Improper Inventory Management | Observed endpoint does not exist anywhere in the OpenAPI specification. Marked `CRITICAL` if path contains sensitive keywords (`admin`, `debug`, `internal`, `secret`, `actuator`, `test`). |
| **`UNDOCUMENTED_METHOD`** | `HIGH` | API9: Improper Inventory Management | Path exists in specification, but observed HTTP method (e.g. `POST`, `DELETE`) is not documented for that path. |
| **`AUTH_MISMATCH`** | `HIGH` | API8: Security Misconfiguration | Endpoint requires `security` scheme in OpenAPI, but incoming requests lack `Authorization`, `X-API-Key`, or session tokens. |
| **`PARAMETER_DRIFT`** | `MEDIUM` | API9: Improper Inventory Management | Observed query parameter is not present in documented endpoint parameters list. |
| **`SCHEMA_DRIFT`** | `MEDIUM` / `LOW` | API9 / API8 | Observed JSON body contains fields not listed in documented request body schema `properties`. |

---

## 3. Deterministic Risk Scoring Formula

Each finding is evaluated using a base score $S_{base} \in [0, 100]$:

$$S_{base} = \begin{cases}
95 & \text{if } \text{type} = \text{SHADOW\_ENDPOINT} \land \text{is\_sensitive}(path) \\
85 & \text{if } \text{type} = \text{SHADOW\_ENDPOINT} \land \neg \text{is\_authenticated} \\
75 & \text{if } \text{type} = \text{SHADOW\_ENDPOINT} \\
70 & \text{if } \text{type} = \text{UNDOCUMENTED\_METHOD} \\
70 & \text{if } \text{type} = \text{AUTH\_MISMATCH} \\
45 & \text{if } \text{type} = \text{PARAMETER\_DRIFT} \\
40 & \text{if } \text{type} = \text{SCHEMA\_DRIFT} \\
20 & \text{otherwise}
\end{cases}$$

The overall system risk score $R_{system} \in [0, 100]$ is computed as:

$$R_{system} = \min\left(100, \; \text{round}\left(S_{max} \times 0.6 + \min(40, N_{findings} \times 5)\right)\right)$$

Where:
- $S_{max}$ is the highest individual finding score (0 if no findings).
- $N_{findings}$ is the total count of security discrepancies found.

### Qualitative Risk Levels:
- **`CRITICAL`**: $R_{system} \ge 90$
- **`HIGH`**: $75 \le R_{system} < 90$
- **`MEDIUM`**: $40 \le R_{system} < 75$
- **`LOW`**: $1 \le R_{system} < 40$
- **`CLEAN`**: $R_{system} = 0$
