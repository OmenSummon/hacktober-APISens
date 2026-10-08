from typing import Any, Dict, Optional
import httpx

from app.config import settings
from app.models.findings import Finding, FindingType
from app.services.remediation import RemediationService


class LocalAIClient:
    """
    Local AI Security Advisor using Ollama, with an infallible
    deterministic rule-based fallback when Ollama is offline or unavailable.
    """

    def __init__(
        self,
        base_url: str = settings.OLLAMA_BASE_URL,
        model: str = settings.OLLAMA_MODEL,
        timeout_seconds: float = settings.OLLAMA_TIMEOUT_SECONDS,
    ):
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.timeout_seconds = timeout_seconds

    async def is_available(self) -> bool:
        """Checks if local Ollama daemon is reachable."""
        try:
            async with httpx.AsyncClient(timeout=1.0) as client:
                res = await client.get(f"{self.base_url}/api/tags")
                return res.status_code == 200
        except Exception:
            return False

    async def analyze_finding(
        self, finding: Finding, custom_model: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Analyzes a detected security finding.
        Queries Ollama if available; seamlessly falls back to deterministic analysis.
        """
        model_name = custom_model or self.model
        ollama_ready = await self.is_available()

        if ollama_ready:
            try:
                ai_result = await self._query_ollama(finding, model_name)
                if ai_result:
                    return ai_result
            except Exception:
                # Silently fall back to deterministic analyzer
                pass

        return self._generate_deterministic_analysis(finding)

    async def _query_ollama(self, finding: Finding, model_name: str) -> Optional[Dict[str, Any]]:
        prompt = (
            f"You are a cybersecurity expert specializing in OWASP API Security.\n"
            f"Analyze this detected API discrepancy:\n"
            f"Type: {finding.type.value}\n"
            f"Severity: {finding.severity.value}\n"
            f"Endpoint: {finding.endpoint}\n"
            f"Description: {finding.description}\n"
            f"Observed Count: {finding.observed_count}\n"
            f"Details: {finding.details.model_dump_json()}\n\n"
            f"Provide a brief, high-impact security analysis covering:\n"
            f"1. Root cause explanation\n"
            f"2. Security impact (OWASP risk)\n"
            f"3. Concrete remediation steps\n"
            f"4. Whether this should be added to the OpenAPI specification (true/false)\n"
        )

        async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
            resp = await client.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": model_name,
                    "prompt": prompt,
                    "stream": False,
                },
            )
            if resp.status_code == 200:
                data = resp.json()
                response_text = data.get("response", "")
                patch = RemediationService.generate_patch(finding)

                should_add = (
                    finding.type == FindingType.SHADOW_ENDPOINT
                    and not any(
                        kw in finding.path.lower()
                        for kw in ("debug", "admin", "test", "internal", "root")
                    )
                )

                return {
                    "provider": "ollama",
                    "model": model_name,
                    "explanation": response_text.strip(),
                    "security_impact": (
                        "Evaluated via local Ollama LLM. "
                        f"Aligned with {finding.details.owasp_category or 'OWASP API Security'}."
                    ),
                    "recommended_remediation": (
                        "Verify endpoint ownership, enforce API gateway access controls, "
                        "and update specification documentation."
                    ),
                    "should_add_to_openapi": should_add,
                    "suggested_openapi_patch": patch,
                }
        return None

    def _generate_deterministic_analysis(self, finding: Finding) -> Dict[str, Any]:
        """
        Deterministic, rule-based cybersecurity analysis when Ollama is offline.
        """
        patch = RemediationService.generate_patch(finding)

        if finding.type == FindingType.SHADOW_ENDPOINT:
            is_sensitive = any(
                kw in finding.path.lower()
                for kw in ("admin", "debug", "test", "internal", "root", "actuator")
            )
            if is_sensitive:
                explanation = (
                    f"The shadow endpoint '{finding.endpoint}' appears to be an internal, "
                    f"administrative, or diagnostic utility that was deployed to production "
                    f"without authorization or OpenAPI documentation."
                )
                impact = (
                    "CRITICAL RISK (OWASP API8 & API9): Diagnostic/admin endpoints often lack "
                    "sufficient rate limiting and authorization checks. Threat actors targeting "
                    "this endpoint may bypass business logic or exfiltrate configuration secrets."
                )
                remediation = (
                    "1. Immediately block public traffic to this endpoint at the API Gateway or WAF.\n"
                    "2. Disable debug/development modes in production server configuration.\n"
                    "3. If legitimate, enforce strict RBAC, audit logging, and document in OpenAPI."
                )
                should_add = False
            else:
                explanation = (
                    f"The endpoint '{finding.endpoint}' was observed receiving active requests "
                    f"but is completely absent from the declared OpenAPI documentation."
                )
                impact = (
                    "HIGH RISK (OWASP API9: Improper Inventory Management): Undocumented API endpoints "
                    "divert traffic away from automated CI/CD security scanning, creating a blind spot."
                )
                remediation = (
                    "1. Confirm if this is a newly deployed feature or legacy route.\n"
                    "2. If legitimate, import the suggested OpenAPI patch into your specification.\n"
                    "3. If deprecated or obsolete, decommission the route."
                )
                should_add = True

        elif finding.type == FindingType.PARAMETER_DRIFT:
            explanation = (
                f"Observed requests passed query parameters not defined in the OpenAPI schema "
                f"for '{finding.endpoint}'."
            )
            impact = (
                "MEDIUM RISK (OWASP API9): Undocumented query parameters can be remnants of "
                "hidden debugging flags, test modes, or internal SQL/ORM query filtering parameters."
            )
            remediation = (
                "1. Audit backend route handlers for undeclared parameter access.\n"
                "2. Explicitly validate and reject unexpected query parameters at the schema validator.\n"
                "3. Document legitimate parameters in the OpenAPI contract."
            )
            should_add = True

        elif finding.type == FindingType.SCHEMA_DRIFT:
            explanation = (
                f"Observed request payloads for '{finding.endpoint}' contain extra fields "
                f"({finding.details.undocumented_field}) not declared in the request body schema."
            )
            impact = (
                "MEDIUM RISK (OWASP API3: Broken Object Property Level Authorization): Accepting "
                "undocumented payload properties makes the application vulnerable to Mass Assignment "
                "attacks if backend models blindly bind request bodies to database entities."
            )
            remediation = (
                "1. Configure input validation (e.g. Pydantic 'extra=forbid' or strict JSON Schema) "
                "to reject unexpected fields.\n"
                "2. Review ORM data mapping to ensure mass assignment cannot alter privileged fields.\n"
                "3. Update OpenAPI schema if the property is a valid, planned enhancement."
            )
            should_add = True

        elif finding.type == FindingType.AUTH_MISMATCH:
            explanation = (
                f"Endpoint '{finding.endpoint}' is documented as requiring authentication, "
                f"yet unauthenticated requests are succeeding."
            )
            impact = (
                "HIGH RISK (OWASP API8 & API2): Broken access control allowing anonymous users "
                "to interact with authenticated application logic."
            )
            remediation = (
                "1. Inspect route middleware or security decorators on the backend handler.\n"
                "2. Ensure authentication filters are applied before route execution.\n"
                "3. Verify that reverse proxy headers (e.g. X-Forwarded-User) cannot be spoofed."
            )
            should_add = False

        else:
            explanation = (
                f"Discrepancy detected between documented OpenAPI specification and observed traffic."
            )
            impact = "Inconsistent API inventory increases operational and security attack surface."
            remediation = "Reconcile codebase with OpenAPI contract."
            should_add = False

        return {
            "provider": "deterministic_engine",
            "model": "rule-based-security-advisor-v1",
            "explanation": explanation,
            "security_impact": impact,
            "recommended_remediation": remediation,
            "should_add_to_openapi": should_add,
            "suggested_openapi_patch": patch,
        }


local_ai_client = LocalAIClient()
