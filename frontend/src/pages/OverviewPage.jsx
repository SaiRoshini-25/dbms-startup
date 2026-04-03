import SectionCard from "../components/SectionCard";
import SearchPanel from "../components/SearchPanel";
import { useWorkspace } from "../components/AppShell";

export default function OverviewPage() {
  const { startups, filters, setFilters, isInvestor, commitmentForm, setCommitmentForm, handleInterest, loading, pendingActions, getInterestStatusForStartup } =
    useWorkspace();
  const publishedStartups = startups.filter((startup) => startup.isPublished).length;
  const openRounds = startups.filter(
    (startup) => !startup.fundingRounds?.length || startup.fundingRounds.some((round) => round.roundStatus === "OPEN")
  ).length;
  const averageScore = startups.length
    ? Math.round(
        startups.reduce((total, startup) => total + Number(startup.performanceScore || 0), 0) / startups.length
      )
    : 0;

  return (
    <>
      <section className="hero overview-hero">
        <div>
          <span className="eyebrow">Overview</span>
          <h1>One place to monitor startups, investors, and execution momentum.</h1>
          <p>
            Review the latest cohort activity, narrow the directory with filters, and move quickly from discovery to
            action.
          </p>
        </div>
        <div className="hero-meta hero-metric-grid">
          <div className="metric">
            <strong>{publishedStartups}</strong>
            <span>Published startups</span>
          </div>
          <div className="metric">
            <strong>{openRounds}</strong>
            <span>Open funding tracks</span>
          </div>
          <div className="metric">
            <strong>{averageScore}</strong>
            <span>Average score</span>
          </div>
        </div>
      </section>

      <section className="filters">
        <input
          placeholder="Filter by domain"
          value={filters.domain}
          onChange={(event) => setFilters((current) => ({ ...current, domain: event.target.value }))}
        />
        <select
          value={filters.fundingStage}
          onChange={(event) => setFilters((current) => ({ ...current, fundingStage: event.target.value }))}
        >
          <option value="">All stages</option>
          <option value="Pre-Seed">Pre-Seed</option>
          <option value="Seed">Seed</option>
          <option value="Series A">Series A</option>
          <option value="Series B">Series B</option>
        </select>
        <input
          type="number"
          min="0"
          max="100"
          placeholder="Min score"
          value={filters.minScore}
          onChange={(event) => setFilters((current) => ({ ...current, minScore: event.target.value }))}
        />
      </section>

      <div className="page-grid">
        <SectionCard title="Search" subtitle="Cross-entity search across startups and users.">
          <SearchPanel />
        </SectionCard>
        <SectionCard title="Startup Directory" subtitle="Shared pipeline view with current cohort status.">
          {loading.startups ? <p className="muted-text">Loading startups...</p> : null}
          <div className="startup-list">
            {!startups.length ? <p className="empty-state">No startups match the current filters.</p> : null}
            {startups.map((startup) => {
              const interestState = getInterestStatusForStartup(startup);
              return (
                <article key={startup.id} className="startup-item">
                  <div className="startup-item-main">
                    <div className="startup-item-head">
                      <div>
                        <h3>{startup.name}</h3>
                        <p>
                          {startup.domain} . {startup.fundingStage} . Team {startup.teamSize}
                        </p>
                      </div>
                      <span className={`status-pill ${startup.isPublished ? "status-accepted" : "status-draft"}`}>
                        {startup.isPublished ? "Published" : "Draft"}
                      </span>
                    </div>
                    <div className="tag-row">
                      <span className="info-chip">Funding {startup.fundingStatus}</span>
                      <span className="info-chip">Score {startup.performanceScore ?? "N/A"}</span>
                      <span className="info-chip">Raised {startup.totalRaised || 0}</span>
                    </div>
                    {isInvestor ? <p className="muted-text">{interestState.helper}</p> : null}
                    {isInvestor ? (
                      <div className="form-grid compact-form">
                        <input
                          type="number"
                          min="0"
                          placeholder="Amount you will contribute"
                          value={commitmentForm[startup.id]?.requestedAmount || ""}
                          onChange={(event) =>
                            setCommitmentForm((current) => ({
                              ...current,
                              [startup.id]: { ...(current[startup.id] || {}), requestedAmount: event.target.value }
                            }))
                          }
                          disabled={interestState.disabled}
                        />
                        <input
                          type="number"
                          min="0"
                          max="100"
                          step="0.1"
                          placeholder="Equity % expected"
                          value={commitmentForm[startup.id]?.equityPercentage || ""}
                          onChange={(event) =>
                            setCommitmentForm((current) => ({
                              ...current,
                              [startup.id]: { ...(current[startup.id] || {}), equityPercentage: event.target.value }
                            }))
                          }
                          disabled={interestState.disabled}
                        />
                        <button
                          className="primary-btn"
                          onClick={() => handleInterest(startup.id)}
                          disabled={interestState.disabled || pendingActions[`interest-${startup.id}`]}
                        >
                          {pendingActions[`interest-${startup.id}`] ? "Submitting..." : interestState.label}
                        </button>
                      </div>
                    ) : null}
                  </div>
                </article>
              );
            })}
          </div>
        </SectionCard>
      </div>
    </>
  );
}
