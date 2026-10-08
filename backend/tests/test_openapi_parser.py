from app.services.demo_data import DEMO_OPENAPI_SPEC
from app.services.openapi_parser import OpenAPIParser


def test_parse_yaml_spec():
    spec = OpenAPIParser.parse(DEMO_OPENAPI_SPEC)
    assert spec.title == "Store & User Management API"
    assert spec.version == "1.0.0"
    assert len(spec.endpoints) == 5  # GET /users, POST /users, GET /users/{id}, GET /products, POST /orders

    # Verify GET /users parameters
    get_users = next(ep for ep in spec.endpoints if ep.method == "GET" and ep.path == "/users")
    assert any(p.name == "limit" and p.in_location == "query" for p in get_users.parameters)
    assert any(p.name == "offset" and p.in_location == "query" for p in get_users.parameters)
    assert get_users.is_authenticated is False

    # Verify POST /orders authentication and requestBody
    post_orders = next(ep for ep in spec.endpoints if ep.method == "POST" and ep.path == "/orders")
    assert post_orders.is_authenticated is True
    assert post_orders.request_body_schema is not None
    assert "item_id" in post_orders.request_body_schema.get("properties", {})


def test_parse_json_spec():
    json_spec = """{
      "openapi": "3.0.0",
      "info": {"title": "Mini API", "version": "2.0.0"},
      "paths": {
        "/status": {
          "get": {
            "summary": "Status check",
            "responses": {"200": {"description": "OK"}}
          }
        }
      }
    }"""
    spec = OpenAPIParser.parse(json_spec)
    assert spec.title == "Mini API"
    assert len(spec.endpoints) == 1
    assert spec.endpoints[0].method == "GET"
    assert spec.endpoints[0].path == "/status"
