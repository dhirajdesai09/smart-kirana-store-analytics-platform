import { Minus, Plus, ReceiptText, Search, ShoppingCart, Trash2 } from "lucide-react";
import { useEffect, useMemo, useState } from "react";

import api from "../api/client.js";
import EmptyState from "../components/EmptyState.jsx";
import PageHeader from "../components/PageHeader.jsx";
import StatusPill from "../components/StatusPill.jsx";
import { useAuth } from "../context/AuthContext.jsx";
import { money } from "../utils/format.js";

export default function Sales() {
  const { stores } = useAuth();
  const storeId = stores[0]?.id;
  const [products, setProducts] = useState([]);
  const [cart, setCart] = useState([]);
  const [query, setQuery] = useState("");
  const [customer, setCustomer] = useState({ customer_name: "", customer_phone: "", payment_mode: "upi" });
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState("");

  useEffect(() => {
    api.get("/products/?page_size=100&ordering=name")
      .then(({ data }) => setProducts(data.results || data))
      .finally(() => setLoading(false));
  }, []);

  const filtered = useMemo(() => products.filter((product) =>
    [product.name, product.sku, product.barcode].join(" ").toLowerCase().includes(query.toLowerCase())
  ), [products, query]);

  const addToCart = (product) => {
    setCart((current) => {
      const existing = current.find((item) => item.product === product.id);
      if (existing) {
        return current.map((item) => item.product === product.id ? { ...item, quantity: Number(item.quantity) + 1 } : item);
      }
      return [
        ...current,
        {
          product: product.id,
          name: product.name,
          sku: product.sku,
          quantity: 1,
          unit_price: Number(product.selling_price),
          discount: 0,
          tax_rate: Number(product.tax_rate || 0)
        }
      ];
    });
  };

  const updateCart = (productId, field, value) => {
    setCart((current) => current.map((item) =>
      item.product === productId ? { ...item, [field]: value } : item
    ));
  };

  const removeCart = (productId) => setCart((current) => current.filter((item) => item.product !== productId));

  const totals = cart.reduce((acc, item) => {
    const gross = Number(item.quantity || 0) * Number(item.unit_price || 0);
    const discount = Number(item.discount || 0);
    const taxable = Math.max(gross - discount, 0);
    const tax = taxable * Number(item.tax_rate || 0) / 100;
    return {
      subtotal: acc.subtotal + gross,
      discount: acc.discount + discount,
      tax: acc.tax + tax,
      total: acc.total + taxable + tax
    };
  }, { subtotal: 0, discount: 0, tax: 0, total: 0 });

  const checkout = async () => {
    if (!cart.length) return;
    setSaving(true);
    setMessage("");
    try {
      const { data } = await api.post("/sales/", {
        store: storeId,
        ...customer,
        paid_amount: totals.total.toFixed(2),
        sale_time: new Date().toISOString(),
        items: cart.map((item) => ({
          product: item.product,
          quantity: item.quantity,
          unit_price: item.unit_price,
          discount: item.discount,
          tax_rate: item.tax_rate
        }))
      });
      setMessage(`Invoice ${data.invoice_number} saved.`);
      setCart([]);
      api.get("/products/?page_size=100&ordering=name").then(({ data: productData }) => setProducts(productData.results || productData));
    } catch (err) {
      setMessage(err.response?.data?.items || err.response?.data?.detail || "Checkout failed.");
    } finally {
      setSaving(false);
    }
  };

  return (
    <section className="page-stack">
      <PageHeader eyebrow="Checkout" title="Sales POS" />
      {message ? <div className={message.includes("saved") ? "success-banner" : "error-banner"}>{message}</div> : null}
      <div className="sales-layout">
        <article className="panel product-picker">
          <div className="toolbar">
            <div className="search-box">
              <Search size={17} />
              <input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Search product or scan barcode" />
            </div>
          </div>
          {loading ? <div className="content-loader">Loading products...</div> : filtered.length ? (
            <div className="product-grid">
              {filtered.map((product) => (
                <button key={product.id} className="product-tile" onClick={() => addToCart(product)} disabled={Number(product.quantity) <= 0}>
                  <span>{product.category_name}</span>
                  <strong>{product.name}</strong>
                  <small>{product.sku}</small>
                  <div>
                    <b>{money(product.selling_price)}</b>
                    <StatusPill tone={product.is_low_stock ? "red" : "green"}>{product.quantity}</StatusPill>
                  </div>
                </button>
              ))}
            </div>
          ) : <EmptyState title="No product match" detail="Try a product name, SKU, or barcode." />}
        </article>

        <article className="panel cart-panel">
          <div className="panel-title">
            <h2>Invoice</h2>
            <ShoppingCart size={18} />
          </div>
          <div className="customer-grid">
            <input placeholder="Customer name" value={customer.customer_name} onChange={(event) => setCustomer({ ...customer, customer_name: event.target.value })} />
            <input placeholder="Phone" value={customer.customer_phone} onChange={(event) => setCustomer({ ...customer, customer_phone: event.target.value })} />
            <select value={customer.payment_mode} onChange={(event) => setCustomer({ ...customer, payment_mode: event.target.value })}>
              <option value="upi">UPI</option>
              <option value="cash">Cash</option>
              <option value="card">Card</option>
              <option value="credit">Credit</option>
              <option value="mixed">Mixed</option>
            </select>
          </div>
          <div className="cart-lines">
            {cart.length ? cart.map((item) => (
              <div className="cart-line" key={item.product}>
                <div>
                  <strong>{item.name}</strong>
                  <small>{item.sku}</small>
                </div>
                <div className="qty-control">
                  <button title="Decrease quantity" onClick={() => updateCart(item.product, "quantity", Math.max(1, Number(item.quantity) - 1))}><Minus size={14} /></button>
                  <input value={item.quantity} type="number" min="1" onChange={(event) => updateCart(item.product, "quantity", event.target.value)} />
                  <button title="Increase quantity" onClick={() => updateCart(item.product, "quantity", Number(item.quantity) + 1)}><Plus size={14} /></button>
                </div>
                <input className="price-input" value={item.discount} type="number" min="0" onChange={(event) => updateCart(item.product, "discount", event.target.value)} />
                <strong>{money(Number(item.quantity) * Number(item.unit_price) - Number(item.discount || 0))}</strong>
                <button title="Remove item" onClick={() => removeCart(item.product)}><Trash2 size={15} /></button>
              </div>
            )) : <EmptyState title="Cart is empty" detail="Select products to build an invoice." />}
          </div>
          <div className="totals">
            <span>Subtotal <strong>{money(totals.subtotal)}</strong></span>
            <span>Discount <strong>{money(totals.discount)}</strong></span>
            <span>GST <strong>{money(totals.tax)}</strong></span>
            <span className="grand-total">Total <strong>{money(totals.total)}</strong></span>
          </div>
          <button className="primary-button checkout-button" disabled={!cart.length || saving} onClick={checkout}>
            <ReceiptText size={18} />
            {saving ? "Saving..." : "Complete sale"}
          </button>
        </article>
      </div>
    </section>
  );
}
