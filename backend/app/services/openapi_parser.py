import json
from typing import Any, Dict, List, Optional
import yaml

from app.models.openapi import NormalizedEndpoint, NormalizedParameter, NormalizedSpec


class OpenAPIParser:
    """
    Parses OpenAPI 3.x specifications in YAML or JSON and extracts
    a normalized internal representation.
    """

    SUPPORTED_METHODS = {"get", "post", "put", "delete", "patch", "options", "head"}

    @classmethod
    def parse(cls, content: str | bytes | Dict[str, Any]) -> NormalizedSpec:
        """
        Parses raw YAML, JSON string, or python dict into NormalizedSpec.
        """
        raw_dict: Dict[str, Any]
        if isinstance(content, dict):
            raw_dict = content
        elif isinstance(content, (bytes, str)):
            text = content.decode("utf-8") if isinstance(content, bytes) else content
            text = text.strip()
            # Attempt JSON first, then YAML
            if text.startswith("{") or text.startswith("["):
                try:
                    raw_dict = json.loads(text)
                except json.JSONDecodeError:
                    raw_dict = yaml.safe_load(text)
            else:
                raw_dict = yaml.safe_load(text)
        else:
            raise ValueError("Unsupported OpenAPI input type")

        if not isinstance(raw_dict, dict):
            raise ValueError("Invalid OpenAPI spec: root must be a mapping/object")

        openapi_version = str(raw_dict.get("openapi", "3.0.0"))
        info = raw_dict.get("info", {})
        title = info.get("title", "API Specification")
        version = info.get("version", "1.0.0")
        description = info.get("description")

        global_security = raw_dict.get("security", [])
        paths_obj = raw_dict.get("paths", {})
        components = raw_dict.get("components", {})
        schemas = components.get("schemas", {})

        endpoints: List[NormalizedEndpoint] = []

        for raw_path, path_item in paths_obj.items():
            if not isinstance(path_item, dict):
                continue

            # Path-level parameters
            path_level_params = path_item.get("parameters", [])

            for method_key, operation in path_item.items():
                method_lower = method_key.lower()
                if method_lower not in cls.SUPPORTED_METHODS:
                    continue

                if not isinstance(operation, dict):
                    continue

                # Combine path-level and operation-level parameters
                op_params = operation.get("parameters", [])
                all_params_raw = path_level_params + op_params
                normalized_params = cls._parse_parameters(all_params_raw)

                # Request body schema
                req_body_schema = cls._parse_request_body(
                    operation.get("requestBody", {}), schemas
                )

                # Response schemas
                response_schemas = cls._parse_responses(
                    operation.get("responses", {}), schemas
                )

                # Security
                op_security = operation.get("security", global_security)
                sec_schemes, is_auth = cls._parse_security(op_security)

                endpoint = NormalizedEndpoint(
                    method=method_lower.upper(),
                    path=raw_path.strip(),
                    summary=operation.get("summary"),
                    description=operation.get("description"),
                    parameters=normalized_params,
                    request_body_schema=req_body_schema,
                    response_schemas=response_schemas,
                    security=sec_schemes,
                    is_authenticated=is_auth,
                )
                endpoints.append(endpoint)

        return NormalizedSpec(
            title=title,
            version=version,
            description=description,
            endpoints=endpoints,
            raw_paths_count=len(paths_obj),
        )

    @classmethod
    def _parse_parameters(cls, params_list: List[Dict[str, Any]]) -> List[NormalizedParameter]:
        parsed: List[NormalizedParameter] = []
        for p in params_list:
            if not isinstance(p, dict):
                continue
            name = p.get("name")
            in_loc = p.get("in", "query")
            if not name:
                continue

            schema = p.get("schema", {})
            param_type = schema.get("type", "string") if isinstance(schema, dict) else "string"
            default_val = schema.get("default") if isinstance(schema, dict) else None

            parsed.append(
                NormalizedParameter(
                    name=name,
                    in_location=in_loc,
                    required=bool(p.get("required", False)),
                    param_type=param_type,
                    default=default_val,
                    description=p.get("description"),
                )
            )
        return parsed

    @classmethod
    def _parse_request_body(
        cls, req_body: Dict[str, Any], schemas: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        if not req_body or not isinstance(req_body, dict):
            return None

        content = req_body.get("content", {})
        # Look for application/json or fallback to first media type
        json_content = content.get("application/json") or next(iter(content.values()), None)
        if not json_content or not isinstance(json_content, dict):
            return None

        schema = json_content.get("schema", {})
        return cls._resolve_schema(schema, schemas)

    @classmethod
    def _parse_responses(
        cls, responses: Dict[str, Any], schemas: Dict[str, Any]
    ) -> Dict[str, Any]:
        result: Dict[str, Any] = {}
        for code, resp_obj in responses.items():
            if not isinstance(resp_obj, dict):
                continue
            content = resp_obj.get("content", {})
            json_content = content.get("application/json") or next(
                iter(content.values()), None
            )
            if json_content and isinstance(json_content, dict):
                schema = json_content.get("schema", {})
                result[str(code)] = cls._resolve_schema(schema, schemas)
            else:
                result[str(code)] = {"description": resp_obj.get("description", "")}
        return result

    @classmethod
    def _resolve_schema(cls, schema: Dict[str, Any], schemas: Dict[str, Any]) -> Dict[str, Any]:
        """Resolves local #/components/schemas/ references for basic schemas."""
        if not isinstance(schema, dict):
            return {}

        ref = schema.get("$ref")
        if ref and isinstance(ref, str) and ref.startswith("#/components/schemas/"):
            schema_name = ref.replace("#/components/schemas/", "")
            resolved = schemas.get(schema_name, {})
            if isinstance(resolved, dict):
                return resolved

        # Handle items ref if array
        if schema.get("type") == "array" and "items" in schema:
            items = schema["items"]
            if isinstance(items, dict) and "$ref" in items:
                ref = items["$ref"]
                schema_name = ref.replace("#/components/schemas/", "")
                return {"type": "array", "items": schemas.get(schema_name, {})}

        return schema

    @classmethod
    def _parse_security(cls, security_reqs: List[Any]) -> tuple[List[str], bool]:
        if not security_reqs or not isinstance(security_reqs, list):
            return [], False

        schemes: List[str] = []
        for sec_item in security_reqs:
            if isinstance(sec_item, dict):
                for k in sec_item.keys():
                    schemes.append(k)

        is_auth = len(schemes) > 0
        return schemes, is_auth
