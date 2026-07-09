export default function MetricCard({ label, value, helper, tone = "blue", icon: Icon }) {
  return (
    <div className={`metric-card tone-${tone}`}>
      <div className="metric-icon">{Icon ? <Icon size={18} /> : null}</div>
      <div>
        <span>{label}</span>
        <strong>{value}</strong>
        {helper ? <small>{helper}</small> : null}
      </div>
    </div>
  );
}
