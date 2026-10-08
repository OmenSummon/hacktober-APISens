from app.services.normalizer import PathNormalizer


def test_match_against_templates_numeric():
    templates = ["/users/{id}", "/products", "/orders/{orderId}"]
    
    # Matching numeric parameter
    matched = PathNormalizer.match_against_templates("/users/42", templates)
    assert matched == "/users/{id}"

    matched_1 = PathNormalizer.match_against_templates("/users/1", templates)
    assert matched_1 == "/users/{id}"


def test_match_against_templates_uuid_and_slashes():
    templates = ["/orders/{id}"]
    uuid_str = "b9f1a0e1-4c6e-41d3-a442-8877bc954378"
    
    matched = PathNormalizer.match_against_templates(f"/orders/{uuid_str}", templates)
    assert matched == "/orders/{id}"

    # Trailing slash tolerance
    matched_slash = PathNormalizer.match_against_templates(f"/orders/{uuid_str}/", templates)
    assert matched_slash == "/orders/{id}"


def test_preserves_static_keywords():
    # Admin and debug should NOT be converted to {id}
    templates = ["/users/{id}"]
    
    resolved, is_matched = PathNormalizer.resolve_path("/admin/users", templates)
    assert is_matched is False
    assert resolved == "/admin/users"

    resolved_debug, _ = PathNormalizer.resolve_path("/debug", templates)
    assert resolved_debug == "/debug"


def test_heuristic_normalization_for_unregistered_id():
    # If route is unknown, e.g. /customers/999, it converts to /customers/{id}
    templates = ["/users/{id}"]
    
    resolved, is_matched = PathNormalizer.resolve_path("/customers/999", templates)
    assert is_matched is False
    assert resolved == "/customers/{id}"
