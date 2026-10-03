const orgApprovals = [
  { name: "PSG Design Club", type: "club", owner: "Aanya Iyer", status: "Pending" },
  { name: "CSE Department", type: "department", owner: "Dr. R. Narayan", status: "Pending" },
  { name: "Campus Lens Studio", type: "business", owner: "S. Manikandan", status: "Needs review" },
];

const flaggedItems = [
  { title: "Exam prep tutoring package", reason: "Academic dishonesty keyword match", severity: "High" },
  { title: "Write my assignment in C++", reason: "Forbidden content pattern", severity: "High" },
  { title: "Campus reels for fest promo", reason: "Manual review required", severity: "Low" },
];

const moderationQueue = [
  { id: "MR-1042", item: "Poster accepted applicant without contract signature", owner: "Arun Kumar" },
  { id: "MR-1043", item: "Refund dispute on delayed delivery", owner: "Priya Sundaram" },
  { id: "MR-1044", item: "Repeated spam report for student profile", owner: "Admin" },
];

export default function Home() {
  return (
    <main className="page-shell">
      <header className="topbar">
        <div>
          <p className="eyebrow">Velai admin</p>
          <h1>Moderation dashboard</h1>
        </div>
        <button className="primary-btn">Review queue</button>
      </header>

      <section className="stats-grid">
        <article className="stat-card">
          <span className="stat-label">Approved orgs</span>
          <strong>18</strong>
          <small>+3 this week</small>
        </article>
        <article className="stat-card">
          <span className="stat-label">Pending approvals</span>
          <strong>7</strong>
          <small>2 urgent</small>
        </article>
        <article className="stat-card">
          <span className="stat-label">Flagged gigs</span>
          <strong>4</strong>
          <small>2 require action</small>
        </article>
        <article className="stat-card accent">
          <span className="stat-label">Open disputes</span>
          <strong>2</strong>
          <small>1 escalated</small>
        </article>
      </section>

      <section className="content-grid">
        <div className="panel">
          <div className="panel-header">
            <h2>Organisation approvals</h2>
            <span className="pill neutral">7 queued</span>
          </div>

          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>Name</th>
                  <th>Type</th>
                  <th>Owner</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                {orgApprovals.map((org) => (
                  <tr key={org.name}>
                    <td>{org.name}</td>
                    <td>{org.type}</td>
                    <td>{org.owner}</td>
                    <td>
                      <span className={`status ${org.status === "Pending" ? "warning" : "danger"}`}>
                        {org.status}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        <div className="panel">
          <div className="panel-header">
            <h2>Flagged content</h2>
            <span className="pill danger">AI + rules</span>
          </div>

          <ul className="list-stack">
            {flaggedItems.map((item) => (
              <li key={item.title} className="list-item">
                <div>
                  <strong>{item.title}</strong>
                  <small>{item.reason}</small>
                </div>
                <span className={`severity ${item.severity === "High" ? "high" : "low"}`}>
                  {item.severity}
                </span>
              </li>
            ))}
          </ul>
        </div>
      </section>

      <section className="panel">
        <div className="panel-header">
          <h2>Moderation queue</h2>
          <span className="pill info">Live</span>
        </div>

        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>ID</th>
                <th>Issue</th>
                <th>Owner</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              {moderationQueue.map((entry) => (
                <tr key={entry.id}>
                  <td>{entry.id}</td>
                  <td>{entry.item}</td>
                  <td>{entry.owner}</td>
                  <td>
                    <button className="ghost-btn">Review</button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
    </main>
  );
}
