# StorePulse Project Documentation

Version: 1.1  
Database: MySQL (`storepulse`)  
Last verified: July 4, 2026

## 1. Project Overview

StorePulse is a full-stack SaaS analytics platform for small grocery and kirana store owners. It helps owners manage inventory, record daily sales, analyze revenue and profit, detect low stock, predict demand, study festival sales, and export business reports.

The project is designed to feel like a real startup SaaS product instead of a simple CRUD app.

## 2. Main Users

- Store owner: manages store, inventory, staff, reports, and analytics.
- Manager: helps manage inventory, sales, and staff operations.
- Cashier: records sales through the POS page.
- Analyst: reviews analytics and reports.

## 3. Tech Stack

- Backend: Django, Django REST Framework
- Authentication: JWT using Simple JWT
- Database: MySQL for production, SQLite for quick local demo
- Analytics: Pandas and NumPy
- Frontend: React, Vite, React Router, Axios
- Charts: Recharts
- Reports: CSV, Excel, PDF
- Deployment: Docker, Render/Railway/Vercel-ready

## 4. Folder Structure

```text
backend/
  storepulse/
    settings.py
    urls.py
    asgi.py
    wsgi.py
  apps/
    accounts/
    inventory/
    sales/
    analytics_engine/
    reports/
    common/

frontend/
  src/
    api/
    components/
    context/
    layouts/
    pages/
    styles/
    utils/
```

## 5. Backend Modules

### Accounts Module

Files:

- `backend/apps/accounts/models.py`
- `backend/apps/accounts/serializers.py`
- `backend/apps/accounts/views.py`

Responsibilities:

- Store owner registration
- Login through JWT
- User profile
- Store profile
- Staff membership
- Role-based store access

Important models:

- `Store`
- `StaffMembership`
- `UserProfile`

When a user registers, the backend creates:

- Django user
- Store
- Owner staff membership
- User profile with default store

### Inventory Module

Files:

- `backend/apps/inventory/models.py`
- `backend/apps/inventory/serializers.py`
- `backend/apps/inventory/views.py`

Responsibilities:

- Product categories
- Supplier details
- Product CRUD
- SKU/barcode fields
- Quantity, reorder level, purchase price, selling price
- Expiry date
- Inventory logs
- Low-stock detection
- Restock recommendations

Important models:

- `Category`
- `Supplier`
- `Product`
- `InventoryLog`

Low-stock logic:

```python
product.quantity <= product.reorder_level
```

Profit margin logic:

```python
(selling_price - purchase_price) / selling_price * 100
```

### Sales Module

Files:

- `backend/apps/sales/models.py`
- `backend/apps/sales/serializers.py`
- `backend/apps/sales/views.py`

Responsibilities:

- POS-style sales entry
- Multiple products in one sale
- Invoice number generation
- Discounts
- GST-ready tax fields
- Payment mode
- Profit calculation
- Automatic stock reduction
- Inventory log entry after sale

Important models:

- `Sale`
- `SaleItem`

Sale flow:

1. Cashier selects products in frontend POS.
2. Frontend sends sale with nested `items`.
3. Backend validates stock.
4. Backend creates invoice.
5. Backend creates sale items.
6. Backend reduces product quantity.
7. Backend writes inventory logs.

### Analytics Engine Module

Files:

- `backend/apps/analytics_engine/services.py`
- `backend/apps/analytics_engine/views.py`

Responsibilities:

- Dashboard KPIs
- Sales trends
- Product performance
- Fast-moving and slow-moving products
- Category analysis
- Basket analysis
- Demand forecast
- Festival analytics
- Alerts

Pandas operations used:

- `DataFrame.from_records`
- `groupby`
- `agg`
- `merge`
- `pivot_table`
- date bucketing
- moving averages
- pair counting for basket analysis

### Reports Module

Files:

- `backend/apps/reports/models.py`
- `backend/apps/reports/views.py`

Responsibilities:

- Sales reports
- Profit reports
- Inventory reports
- Supplier reports
- CSV export
- Excel export
- PDF export
- Report history

## 6. Frontend Pages

### Login/Register

File: `frontend/src/pages/AuthPage.jsx`

Features:

- Login
- Register owner and store
- Stores JWT tokens in local storage

### Dashboard

File: `frontend/src/pages/Dashboard.jsx`

Shows:

- Total revenue
- Daily revenue
- Gross margin
- Inventory value
- Sales trend chart
- Top products chart
- Low-stock table
- Alerts

### Inventory

File: `frontend/src/pages/Inventory.jsx`

Features:

- Add/edit/delete products
- Create categories and suppliers
- Search products
- Low-stock filter
- View price, stock, margin

### Sales POS

File: `frontend/src/pages/Sales.jsx`

Features:

- Search products
- Add products to cart
- Adjust quantity
- Add discount
- Select payment mode
- Generate sale invoice
- Backend updates stock automatically

### Analytics

File: `frontend/src/pages/Analytics.jsx`

Shows:

- Revenue and profit trends
- Category revenue
- Demand forecast
- Frequently bought together rules
- Festival sales comparison

### Reports

File: `frontend/src/pages/Reports.jsx`

Features:

- Select report type
- Select date range
- Export CSV, Excel, or PDF
- View report history

### Settings

File: `frontend/src/pages/Settings.jsx`

Features:

- Owner profile
- Store info
- Add staff
- Assign staff roles

## 7. API Summary

Authentication:

- `POST /api/auth/register/`
- `POST /api/auth/login/`
- `POST /api/auth/refresh/`
- `GET /api/auth/me/`

Inventory:

- `/api/categories/`
- `/api/suppliers/`
- `/api/products/`
- `/api/inventory-logs/`

Sales:

- `/api/sales/`

Analytics:

- `/api/analytics/summary/`
- `/api/analytics/sales-trend/`
- `/api/analytics/product-performance/`
- `/api/analytics/basket/`
- `/api/analytics/demand-forecast/`
- `/api/analytics/festivals/`
- `/api/analytics/alerts/`

Reports:

- `/api/analytics-reports/`
- `/api/reports/export/`

## 8. MySQL Database Design

The local application uses the MySQL database `storepulse` with the `utf8mb4`
character set. Django migrations create 20 tables: 10 StorePulse domain tables
and 10 Django framework tables.

### 8.1 StorePulse Domain Tables

| Table | Model | Purpose | Important fields and relationships |
| --- | --- | --- | --- |
| `accounts_store` | `Store` | Stores each kirana business or branch. It is the main tenant boundary. | `owner_id -> auth_user`; name, GSTIN, phone, address, city, state, currency |
| `accounts_staffmembership` | `StaffMembership` | Connects users to stores and assigns owner, manager, cashier, or analyst roles. | `user_id -> auth_user`; `store_id -> accounts_store`; role, active status; unique user/store pair |
| `accounts_userprofile` | `UserProfile` | Extends Django users with StorePulse-specific preferences. | One-to-one `user_id -> auth_user`; `default_store_id -> accounts_store`; phone, avatar URL, timezone |
| `inventory_category` | `Category` | Groups products inside one store for inventory and category analytics. | `store_id -> accounts_store`; name, description, color; unique store/name pair |
| `inventory_supplier` | `Supplier` | Stores vendor contact, GST, address, and delivery lead-time information. | `store_id -> accounts_store`; name, phone, email, GSTIN, lead time; unique store/name pair |
| `inventory_product` | `Product` | Stores the live product catalog and current stock position. | Store, category and optional supplier FKs; SKU, barcode, unit, quantity, reorder settings, prices, tax, expiry |
| `inventory_inventorylog` | `InventoryLog` | Provides an audit trail for every stock movement. | Store, product and creator FKs; action, quantity change, resulting quantity, reference, note, timestamp |
| `sales_sale` | `Sale` | Stores invoice-level POS information and calculated totals. | Store and creator FKs; invoice, customer/GST fields, payment mode, subtotal, discount, tax, total, paid/balance, status, time |
| `sales_saleitem` | `SaleItem` | Stores each product line belonging to a sale. | `sale_id -> sales_sale`; `product_id -> inventory_product`; quantity, price snapshots, discount, tax, line total, profit |
| `reports_analyticsreport` | `AnalyticsReport` | Records report generation history and export metadata. | Store and generator FKs; report type, title, date range, file path, JSON metadata, creation time |

### 8.2 Django Framework Tables

| Table | Purpose |
| --- | --- |
| `auth_user` | Stores login identity, hashed password, email, name, active/staff flags, and login timestamps. |
| `auth_group` | Stores reusable Django permission groups. StorePulse business roles are kept separately in `accounts_staffmembership`. |
| `auth_permission` | Stores Django model-level add, change, delete, and view permissions. |
| `auth_group_permissions` | Many-to-many bridge between groups and permissions. |
| `auth_user_groups` | Many-to-many bridge between users and groups. |
| `auth_user_user_permissions` | Stores permissions assigned directly to individual users. |
| `django_content_type` | Identifies installed app models and supports Django’s permission framework. |
| `django_migrations` | Records applied migration names so schema changes run exactly once and in order. |
| `django_session` | Stores server-side Django admin sessions. JWT API authentication does not depend on this table. |
| `django_admin_log` | Audits create, update, and delete actions performed through Django Admin. |

### 8.3 Main Relationships

```text
auth_user
  |-- 1:1 --> accounts_userprofile
  |-- 1:N --> accounts_store (owner)
  |-- M:N --> accounts_store through accounts_staffmembership
  |-- 1:N --> inventory_inventorylog (created_by)
  |-- 1:N --> sales_sale (created_by)
  `-- 1:N --> reports_analyticsreport (generated_by)

accounts_store
  |-- 1:N --> inventory_category
  |-- 1:N --> inventory_supplier
  |-- 1:N --> inventory_product
  |-- 1:N --> inventory_inventorylog
  |-- 1:N --> sales_sale
  `-- 1:N --> reports_analyticsreport

inventory_category -- 1:N --> inventory_product
inventory_supplier -- 1:N --> inventory_product
inventory_product  -- 1:N --> inventory_inventorylog
sales_sale         -- 1:N --> sales_saleitem
inventory_product  -- 1:N --> sales_saleitem
```

### 8.4 Constraints and Delete Rules

- SKU is unique inside a store, but different stores may use the same SKU.
- Category and supplier names are unique inside each store.
- Invoice number is unique inside each store.
- A user can have only one membership per store.
- Purchase and selling prices cannot be negative.
- Deleting a store cascades to its business data.
- A category with products is protected from deletion.
- Removing a supplier keeps products and sets their supplier to `NULL`.
- A product referenced by a sale item is protected to preserve invoice history.
- Deleting a sale cascades to its line items.
- Creator references on historical sales, stock logs, and reports become
  `NULL` when that user is deleted. A store owner cannot be deleted while their
  store still exists because `Store.owner` uses `PROTECT`.

### 8.5 Why Snapshot Fields Exist

`sales_saleitem` stores `product_name_snapshot`, `sku_snapshot`, and
`purchase_price_snapshot`. Product names and costs may change later, but an old
invoice and its profit must still represent the values that applied when the
sale happened.

### 8.6 Transaction-Safe Checkout

Sale creation runs inside `transaction.atomic()`:

1. Validate that every product belongs to the active store and has enough stock.
2. Create the invoice in `sales_sale`.
3. Lock each product row with `select_for_update()`.
4. Calculate and create each `sales_saleitem`.
5. Reduce `inventory_product.quantity`.
6. Insert a matching `inventory_inventorylog`.
7. Save invoice totals.

If any step fails, MySQL rolls the complete checkout back.

### 8.7 Important Indexes

- Products: store/SKU, store/active status, store/expiry date.
- Inventory logs: store/date, product/date, action/date.
- Sales: store/date, store/payment mode, store/status.
- Sale items: product and sale foreign keys.
- Reports: store/report type/date.

These indexes support store-scoped filtering, recent activity, low-stock and
expiry workflows, sales history, and reporting.

## 9. Security

- JWT authentication protects APIs.
- Access tokens last 60 minutes and refresh tokens last 7 days.
- Store-scoped querysets prevent one store from seeing another store's data.
- Staff roles support owner, manager, cashier, and analyst.
- Owners and managers can manage staff memberships.
- Django password hashing is used; passwords are never stored as plain text.
- CORS is configured through environment variables.
- Sensitive settings are moved into `.env`.

## 10. Deployment

Backend:

- Render or Railway
- Gunicorn command
- Managed MySQL through `DATABASE_URL`

Frontend:

- Vercel or Netlify
- Build command: `npm run build`
- Output directory: `dist`

Database:

- MySQL is the active local and primary production database.
- `DATABASE_URL` can configure a managed database.
- SQLite remains available only as an optional lightweight development mode.

## 11. End-to-End Business Workflows

### Registration

Registration creates `auth_user`, `accounts_store`,
`accounts_staffmembership`, and `accounts_userprofile` records in one database
transaction. The new membership role is `owner`, and the store becomes the
profile's default store.

### Product Creation and Restocking

Creating a product inserts the product and an opening-stock inventory log.
Later stock adjustments are posted through the inventory log API; the API
updates both current quantity and audit history in one transaction.

### POS Sale

The React cart sends one nested sale request. Django creates a unique invoice,
calculates subtotal, discount, GST, total, balance, and line profit, updates
stock, and records sale inventory movements atomically.

### Analytics

The analytics engine loads store-scoped ORM querysets into Pandas DataFrames.
It uses `groupby`, aggregation, merge, pivot tables, combinations, rolling
history, and NumPy trend calculations to produce dashboard KPIs, sales trends,
product performance, basket pairs, demand forecasts, festival comparisons,
and alerts.

### Reports

The report endpoint builds a Pandas DataFrame for sales, profit, inventory, or
supplier data and returns CSV, XLSX, or PDF. Every export also creates a
`reports_analyticsreport` history record.

## 12. Current Demo Data

Running `python manage.py seed_demo` creates or refreshes:

- Demo owner: `owner@storepulse.local`
- Store: Patel Smart Kirana
- 7 product categories
- 3 suppliers
- 12 products
- Approximately 60 days of invoices and sale items
- Opening and sale inventory movements

The seed command is intentionally repeatable, but it deletes and recreates
sales, products, categories, and suppliers for the demo store. Do not run it
against real store data.
