from typing import Any, Dict, List

DEMO_OPENAPI_SPEC = """openapi: 3.0.3
info:
  title: Store & User Management API
  version: 1.0.0
  description: Official declared API specification for Store and User services.
servers:
  - url: https://api.example.com/v1
paths:
  /users:
    get:
      summary: List all users
      parameters:
        - name: limit
          in: query
          required: false
          schema:
            type: integer
        - name: offset
          in: query
          required: false
          schema:
            type: integer
      responses:
        '200':
          description: A list of users
    post:
      summary: Create a user
      security:
        - BearerAuth: []
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              required:
                - name
                - email
              properties:
                name:
                  type: string
                email:
                  type: string
                role:
                  type: string
      responses:
        '201':
          description: User created

  /users/{id}:
    get:
      summary: Get user by ID
      parameters:
        - name: id
          in: path
          required: true
          schema:
            type: string
      responses:
        '200':
          description: User details

  /products:
    get:
      summary: List inventory products
      parameters:
        - name: category
          in: query
          required: false
          schema:
            type: string
      responses:
        '200':
          description: Product catalog

  /orders:
    post:
      summary: Create customer order
      security:
        - BearerAuth: []
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              required:
                - item_id
                - quantity
              properties:
                item_id:
                  type: string
                quantity:
                  type: integer
                shipping_address:
                  type: string
      responses:
        '201':
          description: Order placed

components:
  securitySchemes:
    BearerAuth:
      type: http
      scheme: bearer
"""

DEMO_TRAFFIC_REQUESTS: List[Dict[str, Any]] = [
    {
        "method": "GET",
        "path": "/users",
        "query_params": {"limit": 10},
        "headers": {"User-Agent": "Mozilla/5.0"},
        "status_code": 200,
        "timestamp": "2026-10-08T10:00:00Z"
    },
    {
        "method": "GET",
        "path": "/users/42",
        "query_params": {},
        "headers": {"User-Agent": "Mozilla/5.0"},
        "status_code": 200,
        "timestamp": "2026-10-08T10:01:15Z"
    },
    {
        "method": "GET",
        "path": "/admin/users",
        "query_params": {},
        "headers": {"User-Agent": "curl/8.1.2"},
        "status_code": 200,
        "timestamp": "2026-10-08T10:02:30Z"
    },
    {
        "method": "GET",
        "path": "/debug",
        "query_params": {"verbose": "1"},
        "headers": {"User-Agent": "Internal-Agent/1.0"},
        "status_code": 200,
        "timestamp": "2026-10-08T10:03:00Z"
    },
    {
        "method": "GET",
        "path": "/products",
        "query_params": {"category": "electronics"},
        "headers": {},
        "status_code": 200,
        "timestamp": "2026-10-08T10:03:45Z"
    },
    {
        "method": "POST",
        "path": "/orders",
        "headers": {
            "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
        },
        "body": {
            "item_id": "prod_9921",
            "quantity": 2,
            "shipping_address": "123 Main St, New York, NY",
            "coupon": "HACK2026_DISCOUNT"
        },
        "status_code": 201,
        "timestamp": "2026-10-08T10:04:12Z"
    },
    {
        "method": "GET",
        "path": "/users",
        "query_params": {"role": "superadmin", "show_deleted": "true"},
        "headers": {},
        "status_code": 200,
        "timestamp": "2026-10-08T10:05:00Z"
    }
]
