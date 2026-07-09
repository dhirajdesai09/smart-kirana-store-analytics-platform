export default function PageHeader({ eyebrow, title, actions }) {
  return (
    <div className="page-header">
      <div>
        {eyebrow ? <span className="eyebrow">{eyebrow}</span> : null}
        <h1>{title}</h1>
      </div>
      {actions ? <div className="page-actions">{actions}</div> : null}
    </div>
  );
}
