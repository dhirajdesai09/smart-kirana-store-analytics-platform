import { Download, FileSpreadsheet } from "lucide-react";
import { useEffect, useState } from "react";

import api from "../api/client.js";
import EmptyState from "../components/EmptyState.jsx";
import PageHeader from "../components/PageHeader.jsx";
import StatusPill from "../components/StatusPill.jsx";

const reportTypes = [
  { type: "sales", label: "Sales Report" },
  { type: "profit", label: "Profit Report" },
  { type: "inventory", label: "Inventory Report" },
  { type: "supplier", label: "Supplier Report" }
];

export default function Reports() {
  const [reports, setReports] = useState([]);
  const [range, setRange] = useState({ start: "", end: "" });
  const [format, setFormat] = useState("csv");

  const load = () => {
    api.get("/analytics-reports/?page_size=50").then(({ data }) => setReports(data.results || data));
  };

  useEffect(load, []);

  const download = async (type) => {
    const params = new URLSearchParams({ type, format });
    if (range.start) params.set("start", range.start);
    if (range.end) params.set("end", range.end);
    const response = await api.get(`/reports/export/?${params.toString()}`, { responseType: "blob" });
    const url = URL.createObjectURL(response.data);
    const extension = format === "xlsx" ? "xlsx" : format === "pdf" ? "pdf" : "csv";
    const link = document.createElement("a");
    link.href = url;
    link.download = `storepulse-${type}-report.${extension}`;
    link.click();
    URL.revokeObjectURL(url);
    load();
  };

  return (
    <section className="page-stack">
      <PageHeader eyebrow="Exports" title="Reports" />
      <div className="report-controls panel">
        <label>
          Start
          <input type="date" value={range.start} onChange={(event) => setRange({ ...range, start: event.target.value })} />
        </label>
        <label>
          End
          <input type="date" value={range.end} onChange={(event) => setRange({ ...range, end: event.target.value })} />
        </label>
        <label>
          Format
          <select value={format} onChange={(event) => setFormat(event.target.value)}>
            <option value="csv">CSV</option>
            <option value="xlsx">Excel</option>
            <option value="pdf">PDF</option>
          </select>
        </label>
      </div>
      <div className="report-grid">
        {reportTypes.map((report) => (
          <button className="report-card" key={report.type} onClick={() => download(report.type)}>
            <FileSpreadsheet size={22} />
            <strong>{report.label}</strong>
            <span>Download {format.toUpperCase()}</span>
            <Download size={18} />
          </button>
        ))}
      </div>
      <article className="panel">
        <div className="panel-title">
          <h2>Report History</h2>
          <StatusPill tone="blue">{reports.length}</StatusPill>
        </div>
        {reports.length ? (
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>Title</th>
                  <th>Type</th>
                  <th>Period</th>
                  <th>Rows</th>
                  <th>Created</th>
                </tr>
              </thead>
              <tbody>
                {reports.map((report) => (
                  <tr key={report.id}>
                    <td>{report.title}</td>
                    <td>{report.report_type}</td>
                    <td>{report.period_start || "All"} - {report.period_end || "Now"}</td>
                    <td>{report.metadata?.rows ?? "-"}</td>
                    <td>{new Date(report.created_at).toLocaleString("en-IN")}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : <EmptyState title="No report exports yet" detail="Downloaded reports are recorded here." />}
      </article>
    </section>
  );
}
