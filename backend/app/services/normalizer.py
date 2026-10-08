import re
from typing import List, Optional, Tuple

# UUID regex pattern
UUID_REGEX = re.compile(
    r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$"
)
# Mongo / 24-hex ObjectId pattern
OBJECTID_REGEX = re.compile(r"^[0-9a-fA-F]{24}$")
# Pure numeric ID pattern (1 or more digits)
NUMERIC_ID_REGEX = re.compile(r"^\d+$")

# Static words that should NEVER be treated as dynamic parameter variables
STATIC_KEYWORDS = {
    "v1", "v2", "v3", "api", "admin", "debug", "health", "status",
    "metrics", "auth", "login", "logout", "token", "me", "users",
    "products", "orders", "items", "checkout", "cart", "webhooks",
    "search", "filter", "reports", "config", "settings", "internal"
}


class PathNormalizer:
    """
    Normalizes observed API request paths and maps them to parameterized
    templates (e.g. /users/42 -> /users/{id}).
    """

    @staticmethod
    def template_to_regex(template_path: str) -> re.Pattern:
        """
        Converts OpenAPI template path like '/users/{id}/orders/{order_id}'
        into regex '^/users/([^/]+)/orders/([^/]+)$'.
        """
        # Escape special regex characters except {param}
        parts = template_path.strip().split("/")
        pattern_parts = []
        for part in parts:
            if not part:
                continue
            if part.startswith("{") and part.endswith("}"):
                # parameter placeholder
                pattern_parts.append(r"([^/]+)")
            else:
                pattern_parts.append(re.escape(part))
        regex_str = "^/" + "/".join(pattern_parts) + "$" if pattern_parts else "^/$"
        return re.compile(regex_str, re.IGNORECASE)

    @classmethod
    def match_against_templates(
        cls, observed_path: str, declared_templates: List[str]
    ) -> Optional[str]:
        """
        Attempts to match an observed path against known OpenAPI path templates.
        Returns the matching template if found, otherwise None.
        """
        clean_obs = observed_path.strip()
        if not clean_obs.startswith("/"):
            clean_obs = "/" + clean_obs
        if len(clean_obs) > 1 and clean_obs.endswith("/"):
            clean_obs = clean_obs.rstrip("/")

        for template in declared_templates:
            clean_tpl = template.strip()
            if not clean_tpl.startswith("/"):
                clean_tpl = "/" + clean_tpl
            if len(clean_tpl) > 1 and clean_tpl.endswith("/"):
                clean_tpl = clean_tpl.rstrip("/")

            regex = cls.template_to_regex(clean_tpl)
            if regex.match(clean_obs):
                return clean_tpl

        return None

    @classmethod
    def normalize_heuristically(cls, observed_path: str) -> str:
        """
        Heuristically converts numeric IDs, UUIDs, or ObjectIDs into '{id}'
        if no OpenAPI template matches, preserving known keywords.
        """
        clean_path = observed_path.strip()
        if not clean_path.startswith("/"):
            clean_path = "/" + clean_path
        if len(clean_path) > 1 and clean_path.endswith("/"):
            clean_path = clean_path.rstrip("/")

        if clean_path == "/":
            return "/"

        segments = clean_path.split("/")
        normalized_segments = []

        for seg in segments:
            if not seg:
                continue
            
            lower_seg = seg.lower()
            if lower_seg in STATIC_KEYWORDS:
                normalized_segments.append(seg)
            elif UUID_REGEX.match(seg) or OBJECTID_REGEX.match(seg) or NUMERIC_ID_REGEX.match(seg):
                normalized_segments.append("{id}")
            else:
                normalized_segments.append(seg)

        return "/" + "/".join(normalized_segments)

    @classmethod
    def resolve_path(cls, observed_path: str, declared_templates: List[str]) -> Tuple[str, bool]:
        """
        Resolves an observed path:
        1. Checks declared OpenAPI templates first.
        2. Falls back to heuristic normalization.
        Returns: (resolved_path, is_matched_to_spec)
        """
        matched = cls.match_against_templates(observed_path, declared_templates)
        if matched:
            return matched, True
        
        return cls.normalize_heuristically(observed_path), False
