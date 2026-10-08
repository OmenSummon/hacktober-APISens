from typing import Any, Dict
import yaml

from app.models.findings import Finding, FindingType


class RemediationService:
    """
    Generates suggested OpenAPI 3.0 YAML patches and diff proposals
    for detected shadow endpoints and schema/parameter drifts.
    """

    @classmethod
    def generate_patch(cls, finding: Finding) -> str:
        """
        Generates a clean OpenAPI 3.0 YAML snippet addressing the finding.
        """
        if finding.type == FindingType.SHADOW_ENDPOINT:
            method_lower = finding.method.lower()
            clean_path = finding.path

            # Generate operation ID
            op_parts = [finding.method.lower()] + [
                p.capitalize() for p in clean_path.strip("/").split("/") if p and not p.startswith("{")
            ]
            op_id = "".join(op_parts) or "customOperation"

            patch_dict: Dict[str, Any] = {
                "paths": {
                    clean_path: {
                        method_lower: {
                            "summary": f"Documented endpoint for {finding.endpoint}",
                            "operationId": op_id,
                            "security": [{"BearerAuth": []}],
                            "responses": {
                                "200": {
                                    "description": "Successful operation",
                                    "content": {
                                        "application/json": {
                                            "schema": {
                                                "type": "object"
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
            return yaml.dump(patch_dict, sort_keys=False)

        elif finding.type == FindingType.PARAMETER_DRIFT:
            params = finding.details.undocumented_params or []
            param_items = [
                {
                    "name": p,
                    "in": "query",
                    "required": False,
                    "schema": {"type": "string"},
                    "description": f"Observed parameter '{p}'"
                }
                for p in params
            ]
            patch_dict = {
                "paths": {
                    finding.path: {
                        finding.method.lower(): {
                            "parameters": param_items
                        }
                    }
                }
            }
            return yaml.dump(patch_dict, sort_keys=False)

        elif finding.type == FindingType.SCHEMA_DRIFT:
            field_name = finding.details.undocumented_field or "extra_property"
            obs_val = finding.details.observed_value
            inferred_type = "string"
            if isinstance(obs_val, int):
                inferred_type = "integer"
            elif isinstance(obs_val, bool):
                inferred_type = "boolean"
            elif isinstance(obs_val, list):
                inferred_type = "array"
            elif isinstance(obs_val, dict):
                inferred_type = "object"

            patch_dict = {
                "paths": {
                    finding.path: {
                        finding.method.lower(): {
                            "requestBody": {
                                "content": {
                                    "application/json": {
                                        "schema": {
                                            "properties": {
                                                field_name: {
                                                    "type": inferred_type,
                                                    "description": f"Discovered payload field '{field_name}'"
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
            return yaml.dump(patch_dict, sort_keys=False)

        else:
            return (
                f"# Security Notice for {finding.endpoint}\n"
                f"# Discrepancy: {finding.title}\n"
                f"# Recommendation: Align endpoint implementation with specification and enforce authorization.\n"
            )
