# StorePulse Viva And Interview Questions

Use these questions to prepare for project explanation, viva, resume discussion, and interviews.

## Basic Project Questions

### 1. What is StorePulse?

StorePulse is a full-stack SaaS analytics platform for kirana and small grocery stores. It helps store owners manage inventory, record sales, analyze revenue and profit, detect low stock, forecast demand, and export reports.

### 2. What problem does this project solve?

Small store owners often track sales and stock manually. StorePulse digitizes daily sales, inventory, alerts, and business analytics so owners can make better purchase and restock decisions.

### 3. Why did you choose this tech stack?

Django REST Framework is good for secure and structured APIs, React is suitable for interactive dashboards, MySQL is reliable for relational business data, and Pandas/NumPy are strong for analytics and forecasting.

### 4. Is this only a CRUD application?

No. It includes CRUD, but also stock movement logs, POS sales, invoice totals, automatic inventory deduction, Pandas analytics, basket analysis, demand forecasting, festival comparison, alerts, and report exports.

## Backend Questions

### 5. How is authentication handled?

Authentication uses JWT. The frontend logs in through `/api/auth/login/`, receives access and refresh tokens, stores them locally, and sends the access token in the `Authorization: Bearer <token>` header.

### 6. What happens during registration?

The backend creates a Django user, a store, an owner staff membership, and a user profile with that store as the default store.

### 7. How do you prevent one store owner from seeing another store's data?

Viewsets use store-scoped querysets. Non-admin users only see records for stores where they have an active `StaffMembership`.

### 8. What are the main database relationships?

A store has categories, suppliers, products, inventory logs, sales, staff memberships, and reports. A sale has multiple sale items. Products belong to categories and may belong to suppliers.

### 9. Why do you have `Sale` and `SaleItem` separately?

One invoice can contain many products. `Sale` stores invoice-level data like payment mode and grand total. `SaleItem` stores product-level quantity, unit price, discount, tax, and profit.

### 10. How is inventory reduced after a sale?

When a sale is created, the backend validates stock, creates sale items, subtracts sold quantity from product stock, and creates an `InventoryLog` entry with action `sale`.

### 11. Why use transactions in sale creation?

Sale creation updates multiple tables. A transaction ensures invoice creation, sale items, product stock update, and inventory logs either all succeed together or all roll back.

### 12. How is low stock detected?

Low stock is detected when:

```python
product.quantity <= product.reorder_level
```

### 13. How is profit calculated?

For each sale item:

```python
profit = (unit_price - purchase_price) * quantity - discount
```

### 14. What is the purpose of `InventoryLog`?

It tracks every stock movement such as opening stock, sale, purchase, adjustment, return, and expiry. This gives audit history for inventory changes.

## Analytics Questions

### 15. Where is Pandas used?

Pandas is used in `StoreAnalyticsEngine` to convert sales and product records into data frames, then perform groupby, aggregation, merge, pivot-style analysis, trend analysis, and forecast calculations.

### 16. How is sales trend calculated?

Sales are grouped by day, week, month, or hour. For each period, revenue, profit, and sold units are aggregated.

### 17. How is product performance calculated?

Sale items are grouped by product. The engine calculates quantity sold, revenue, profit, invoice count, margin percentage, and current stock.

### 18. What is basket analysis?

Basket analysis finds products frequently bought together. For every invoice, it creates product pairs and counts how often pairs occur.

Example insight:

`Customers buying Basmati Rice also buy Sunflower Oil.`

### 19. How does demand forecasting work?

The engine looks at recent daily sales, calculates average daily sales, adds a simple trend factor, and predicts next-week demand. It compares predicted demand with current stock to mark shortage risk.

### 20. How is festival analytics India-focused?

The project stores India-focused festival windows like Diwali, Holi, Eid, Raksha Bandhan, and New Year. It compares sales near those dates with baseline periods to detect spikes.

## Frontend Questions

### 21. How does protected routing work?

The `AuthContext` loads the current user from `/api/auth/me/`. If no user is logged in, `ProtectedRoute` redirects to `/auth`.

### 22. How does Axios send JWT tokens?

The Axios client reads `storepulse_access` from local storage and adds it to the request header.

### 23. What happens when the access token expires?

The Axios response interceptor uses the refresh token to request a new access token from `/api/auth/refresh/`.

### 24. Which charts are used?

The frontend uses Recharts for area, line, and bar charts in dashboard and analytics pages.

### 25. What loading and error states are handled?

Pages show loading text while API calls run and display error or empty states when data is unavailable.

## Deployment Questions

### 26. How would you deploy this project?

Deploy backend to Render or Railway with Gunicorn, deploy frontend to Vercel or Netlify, and use a managed MySQL database.

### 27. Which environment variables are required in production?

Important variables:

- `DJANGO_SECRET_KEY`
- `DJANGO_DEBUG=False`
- `DJANGO_ALLOWED_HOSTS`
- `CORS_ALLOWED_ORIGINS`
- `DATABASE_URL` or MySQL variables
- `VITE_API_URL`

### 28. Why is Docker included?

Docker makes the project easier to run consistently across different machines. It defines services for backend, frontend, and MySQL.

## Advanced Questions

### 29. How would you add barcode scanning?

Add a barcode input or camera scanner in the POS page. The scanned barcode would search products by the `barcode` field and add the matched product to the cart.

### 30. How would you add WhatsApp alerts?

Create an alert service that reads low-stock and demand alerts, then sends WhatsApp messages through providers like Twilio or Meta WhatsApp Cloud API.

### 31. How would you improve the demand prediction model?

Use more historical data, add seasonality, festival features, holidays, weather, local events, and train a time-series or regression model.

### 32. What are the limitations of the current project?

The forecast is simple, the demo data is generated, and production payment/invoice compliance can be expanded. It is a strong MVP but can grow with real integrations.

### 33. What makes this project resume-worthy?

It demonstrates full-stack development, REST API design, authentication, relational database design, analytics, forecasting, dashboard UI, reports, and deployment preparation.

## MySQL And Database Questions

### 34. Which database is currently connected?

The project is connected to the MySQL database named `storepulse` through
Django's MySQL backend and PyMySQL. The local host is `127.0.0.1` on port
`3306`.

### 35. How can you prove Django is using MySQL and not SQLite?

Run:

```bash
python manage.py shell -c "from django.db import connection; print(connection.vendor, connection.settings_dict['NAME'])"
```

The expected result is `mysql storepulse`.

### 36. How many database tables are present and why?

There are 20 tables after migrations. Ten are StorePulse domain tables for
stores, staff, profiles, inventory, sales, and reports. Ten are Django
framework tables for authentication, permissions, content types, migrations,
sessions, and admin logs.

### 37. Why is the user table called `auth_user` instead of `accounts_user`?

The project uses Django's standard user model. The `accounts` app adds
StorePulse-specific data through `accounts_userprofile`,
`accounts_staffmembership`, and `accounts_store`, rather than replacing the
authentication table.

### 38. What is the central tenant table?

`accounts_store` is the tenant boundary. Most business records contain a
`store_id`, and API querysets are filtered using the authenticated user's
active memberships.

### 39. Is `StaffMembership` the same as a Django group?

No. Django groups are generic permission containers. `StaffMembership` is a
business relationship that says a particular user is an owner, manager,
cashier, or analyst in a particular store.

### 40. Why separate `Product.quantity` and `InventoryLog`?

`Product.quantity` gives fast access to current stock. `InventoryLog` explains
how that quantity changed over time. Keeping both supports efficient screens
and a complete audit trail.

### 41. Why store product snapshots in `SaleItem`?

Product names, SKUs, and purchase prices may change. Snapshot fields preserve
the values used for the original invoice and profit calculation, so historical
reports remain correct.

### 42. What is database normalization in this project?

Stores, categories, suppliers, products, invoices, and invoice lines are kept
in separate related tables. This reduces unnecessary duplication and update
anomalies. Sale-item snapshots are intentional denormalization for historical
accuracy.

### 43. Which important unique constraints are used?

- One SKU per store.
- One category name per store.
- One supplier name per store.
- One invoice number per store.
- One membership per user/store pair.

These rules allow different stores to reuse their own values while preventing
duplicates inside one store.

### 44. What happens if sale creation fails halfway?

The serializer uses `transaction.atomic()`. Django rolls back the invoice,
sale items, stock changes, and inventory logs, leaving the database consistent.

### 45. Why is `select_for_update()` used during checkout?

It locks each selected product row until the transaction finishes. This helps
prevent concurrent cashiers from both selling stock that is no longer
available.

### 46. Which delete rules are important?

Store-owned data generally cascades when a store is deleted. Categories and
products referenced by history use `PROTECT`. Optional suppliers and creator
references use `SET_NULL` so historical records remain available. A store
owner is protected from deletion while their store exists.

### 47. Which indexes improve performance?

The project indexes product lookup by store/SKU, active and expiry filters,
inventory logs by store/product/action and date, sales by store/date/payment
mode/status, and reports by store/type/date.

### 48. Are analytics values stored in separate tables?

Most analytics are computed on demand from products, completed sales, and sale
items using Pandas. Only report generation history is stored in
`reports_analyticsreport`.

### 49. How are schema changes managed?

Django migration files describe schema changes. `python manage.py migrate`
applies them, while `django_migrations` records which migrations have already
run.

### 50. Why use `DecimalField` for money instead of floating point?

Binary floating point can introduce rounding errors. Django `DecimalField`
stores fixed-precision prices, tax, discounts, totals, and profit suitable for
business calculations.

## Functional Demonstration Questions

### 51. What happens when a product is created?

The product is stored with its current quantity, pricing, reorder level, tax,
and expiry information. The serializer also creates an opening-stock
`InventoryLog`.

### 52. What validations happen before checkout?

The sale must have at least one item. Every product must belong to the active
store, and a completed sale cannot request more stock than is available.

### 53. How is an invoice number generated?

The backend creates a store-scoped number using the `SP-YYYYMMDD-NNNN` format.
A unique database constraint prevents duplicate invoice numbers inside a
store.

### 54. How are GST-ready totals calculated?

For each line:

```text
gross = quantity * unit price
taxable = max(gross - discount, 0)
tax = taxable * tax rate / 100
line total = taxable + tax
```

The invoice aggregates subtotal, discount, tax, grand total, paid amount, and
balance.

### 55. How does the low-stock recommendation work?

A product is low when quantity is less than or equal to its reorder level. The
recommended quantity is the larger of the configured reorder quantity and the
amount required to reach twice the reorder level.

### 56. How is a revenue-drop alert detected?

The engine compares revenue from the latest seven days with the previous seven
days. It creates an alert when current revenue is below 80 percent of the
previous period.

### 57. How is basket confidence calculated?

The engine counts invoices containing both products and divides the pair count
by the individual product count. It reports the stronger direction as the
confidence percentage.

### 58. What should you demonstrate during a project review?

1. Log in with the demo owner.
2. Show inventory, low-stock state, prices, and expiry.
3. Create a POS sale and explain atomic stock reduction.
4. Show the new invoice and inventory log.
5. Open dashboard and analytics charts.
6. Explain basket analysis and demand forecast.
7. Export a CSV, XLSX, or PDF report.
8. Show Swagger API documentation and confirm the MySQL connection.

### 59. What does the demo seed command do?

It creates the demo owner and Patel Smart Kirana, then refreshes seven
categories, three suppliers, twelve products, about sixty days of sales, sale
items, and inventory logs. It must not be run against real store data because
it replaces records belonging to the demo store.

### 60. What would you improve first for production?

Use production secrets and HTTPS, add automated tests and CI, complete email
password reset, make festival calendars configurable, add background jobs for
notifications, code-split the frontend, add backups and monitoring, and use a
managed MySQL service.
