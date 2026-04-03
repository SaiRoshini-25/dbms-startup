import SectionCard from "../components/SectionCard";
import { useWorkspace } from "../components/AppShell";

export default function PortfolioPage() {
  const { portfolio, loading } = useWorkspace();

  return (
    <SectionCard title="Investor Portfolio" subtitle="Commitments, approvals, and round-level holdings.">
      {loading.portfolio ? <p className="muted-text">Loading portfolio...</p> : null}
      <div className="table-list">
        {portfolio.map((item) => (
          <div key={`${item.entryType}-${item.id}`} className="table-row">
            <span>
              <strong>{item.startupName}</strong>
              <br />
              {item.entryType === "COMMITMENT" ? "Commitment" : item.roundName}
            </span>
            <span>{item.entryType === "COMMITMENT" ? item.approvedAmount || item.requestedAmount : item.amountRaised}</span>
            <span>{`${item.equityPercentage}%`}</span>
            <span>{item.status || item.roundStatus}</span>
          </div>
        ))}
        {!loading.portfolio && !portfolio.length ? (
          <p className="muted-text">No commitments or funding-round holdings yet.</p>
        ) : null}
      </div>
    </SectionCard>
  );
}
