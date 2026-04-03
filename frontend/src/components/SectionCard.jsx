export default function SectionCard({ title, subtitle, children, action }) {
  return (
    <section className="card section-card">
      <div className="card-head">
        <div>
          <h2>{title}</h2>
          {subtitle ? <p>{subtitle}</p> : null}
        </div>
        {action}
      </div>
      {children}
    </section>
  );
}
