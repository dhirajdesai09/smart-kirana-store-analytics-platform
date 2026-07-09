# StorePulse API

Base URL: `/api`

Authentication uses JWT:

- `POST /auth/register/`
- `POST /auth/login/`
- `POST /auth/refresh/`
- `GET/PATCH /auth/me/`
- `POST /auth/password-reset/`

Store and staff:

- `/stores/`
- `/staff/`

Inventory:

- `/categories/`
- `/suppliers/`
- `/products/`
- `/inventory-logs/`

Sales:

- `/sales/`
- Nested `items` create invoice lines and stock logs.
- Query with `start=YYYY-MM-DD`, `end=YYYY-MM-DD`, `payment_mode`, `status`, search, ordering, and pagination.

Analytics:

- `GET /analytics/summary/`
- `GET /analytics/sales-trend/?period=day|week|month|hour`
- `GET /analytics/product-performance/`
- `GET /analytics/basket/`
- `GET /analytics/demand-forecast/?days=7`
- `GET /analytics/festivals/`
- `GET /analytics/alerts/`

Reports:

- `/analytics-reports/`
- `GET /reports/export/?type=sales|profit|inventory|supplier&format=csv|xlsx|pdf`

Interactive OpenAPI docs are available at `/api/docs/`.
