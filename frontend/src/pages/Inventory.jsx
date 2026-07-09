import { Edit3, PackagePlus, Plus, Search, Trash2 } from "lucide-react";
import { useEffect, useMemo, useState } from "react";

import api from "../api/client.js";
import EmptyState from "../components/EmptyState.jsx";
import PageHeader from "../components/PageHeader.jsx";
import StatusPill from "../components/StatusPill.jsx";
import { useAuth } from "../context/AuthContext.jsx";
import { money } from "../utils/format.js";

const productDefaults = {
  name: "",
  sku: "",
  barcode: "",
  category: "",
  supplier: "",
  unit: "piece",
  quantity: 0,
  reorder_level: 10,
  reorder_quantity: 25,
  purchase_price: 0,
  selling_price: 0,
  tax_rate: 0,
  expiry_date: ""
};

export default function Inventory() {
  const { stores } = useAuth();
  const storeId = stores[0]?.id;
  const [products, setProducts] = useState([]);
  const [categories, setCategories] = useState([]);
  const [suppliers, setSuppliers] = useState([]);
  const [query, setQuery] = useState("");
  const [lowOnly, setLowOnly] = useState(false);
  const [form, setForm] = useState(productDefaults);
  const [editingId, setEditingId] = useState(null);
  const [categoryName, setCategoryName] = useState("");
  const [supplierName, setSupplierName] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const load = () => {
    setLoading(true);
    Promise.all([
      api.get("/products/?page_size=100"),
      api.get("/categories/?page_size=100"),
      api.get("/suppliers/?page_size=100")
    ])
      .then(([productResponse, categoryResponse, supplierResponse]) => {
        setProducts(productResponse.data.results || productResponse.data);
        setCategories(categoryResponse.data.results || categoryResponse.data);
        setSuppliers(supplierResponse.data.results || supplierResponse.data);
      })
      .catch((err) => setError(err.response?.data?.detail || "Inventory data is unavailable."))
      .finally(() => setLoading(false));
  };

  useEffect(load, []);

  const filtered = useMemo(() => {
    return products.filter((product) => {
      const matches = [product.name, product.sku, product.category_name, product.supplier_name]
        .join(" ")
        .toLowerCase()
        .includes(query.toLowerCase());
      return matches && (!lowOnly || product.is_low_stock);
    });
  }, [products, query, lowOnly]);

  const update = (event) => setForm({ ...form, [event.target.name]: event.target.value });

  const reset = () => {
    setForm(productDefaults);
    setEditingId(null);
  };

  const submitProduct = async (event) => {
    event.preventDefault();
    const payload = {
      ...form,
      store: storeId,
      supplier: form.supplier || null,
      expiry_date: form.expiry_date || null
    };
    if (editingId) {
      await api.patch(`/products/${editingId}/`, payload);
    } else {
      await api.post("/products/", payload);
    }
    reset();
    load();
  };

  const editProduct = (product) => {
    setEditingId(product.id);
    setForm({
      ...productDefaults,
      ...product,
      category: product.category,
      supplier: product.supplier || "",
      expiry_date: product.expiry_date || ""
    });
  };

  const deleteProduct = async (product) => {
    await api.delete(`/products/${product.id}/`);
    load();
  };

  const addCategory = async (event) => {
    event.preventDefault();
    if (!categoryName.trim()) return;
    await api.post("/categories/", { store: storeId, name: categoryName, color: "#0ea5e9" });
    setCategoryName("");
    load();
  };

  const addSupplier = async (event) => {
    event.preventDefault();
    if (!supplierName.trim()) return;
    await api.post("/suppliers/", { store: storeId, name: supplierName });
    setSupplierName("");
    load();
  };

  return (
    <section className="page-stack">
      <PageHeader
        eyebrow="Stock control"
        title="Inventory"
        actions={
          <button className="ghost-button" onClick={() => setLowOnly((value) => !value)}>
            {lowOnly ? "All stock" : "Low stock"}
          </button>
        }
      />
      {error ? <div className="error-banner">{error}</div> : null}
      <div className="inventory-layout">
        <article className="panel form-panel">
          <div className="panel-title">
            <h2>{editingId ? "Edit Product" : "Add Product"}</h2>
            <PackagePlus size={18} />
          </div>
          <div className="quick-create">
            <form onSubmit={addCategory}>
              <input value={categoryName} onChange={(event) => setCategoryName(event.target.value)} placeholder="New category" />
              <button title="Add category" type="submit"><Plus size={16} /></button>
            </form>
            <form onSubmit={addSupplier}>
              <input value={supplierName} onChange={(event) => setSupplierName(event.target.value)} placeholder="New supplier" />
              <button title="Add supplier" type="submit"><Plus size={16} /></button>
            </form>
          </div>
          <form onSubmit={submitProduct} className="form-grid compact">
            <label className="span-2">
              Product name
              <input name="name" value={form.name} onChange={update} required />
            </label>
            <label>
              SKU
              <input name="sku" value={form.sku} onChange={update} required />
            </label>
            <label>
              Barcode
              <input name="barcode" value={form.barcode} onChange={update} />
            </label>
            <label>
              Category
              <select name="category" value={form.category} onChange={update} required>
                <option value="">Select</option>
                {categories.map((category) => <option key={category.id} value={category.id}>{category.name}</option>)}
              </select>
            </label>
            <label>
              Supplier
              <select name="supplier" value={form.supplier || ""} onChange={update}>
                <option value="">None</option>
                {suppliers.map((supplier) => <option key={supplier.id} value={supplier.id}>{supplier.name}</option>)}
              </select>
            </label>
            {["quantity", "reorder_level", "reorder_quantity", "purchase_price", "selling_price", "tax_rate"].map((field) => (
              <label key={field}>
                {field.replaceAll("_", " ")}
                <input name={field} type="number" step="0.01" value={form[field]} onChange={update} required />
              </label>
            ))}
            <label>
              Unit
              <select name="unit" value={form.unit} onChange={update}>
                <option value="piece">Piece</option>
                <option value="kg">Kg</option>
                <option value="litre">Litre</option>
                <option value="packet">Packet</option>
              </select>
            </label>
            <label>
              Expiry
              <input name="expiry_date" type="date" value={form.expiry_date} onChange={update} />
            </label>
            <button className="primary-button span-2" disabled={!categories.length}>{editingId ? "Save changes" : "Add product"}</button>
            {editingId ? <button className="secondary-button span-2" type="button" onClick={reset}>Cancel edit</button> : null}
          </form>
        </article>

        <article className="panel table-panel">
          <div className="toolbar">
            <div className="search-box">
              <Search size={17} />
              <input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Search products, SKU, category" />
            </div>
            <StatusPill tone="blue">{filtered.length} products</StatusPill>
          </div>
          {loading ? <div className="content-loader">Loading inventory...</div> : filtered.length ? (
            <div className="table-wrap">
              <table>
                <thead>
                  <tr>
                    <th>Product</th>
                    <th>Category</th>
                    <th>Stock</th>
                    <th>Sell</th>
                    <th>Margin</th>
                    <th></th>
                  </tr>
                </thead>
                <tbody>
                  {filtered.map((product) => (
                    <tr key={product.id}>
                      <td>
                        <strong>{product.name}</strong>
                        <small>{product.sku}</small>
                      </td>
                      <td>{product.category_name}</td>
                      <td>
                        <StatusPill tone={product.is_low_stock ? "red" : "green"}>{product.quantity}</StatusPill>
                      </td>
                      <td>{money(product.selling_price)}</td>
                      <td>{Number(product.profit_margin_percent || 0).toFixed(1)}%</td>
                      <td className="row-actions">
                        <button title="Edit product" onClick={() => editProduct(product)}><Edit3 size={15} /></button>
                        <button title="Delete product" onClick={() => deleteProduct(product)}><Trash2 size={15} /></button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : <EmptyState title="No products found" detail="Add products or adjust the current filters." />}
        </article>
      </div>
    </section>
  );
}
