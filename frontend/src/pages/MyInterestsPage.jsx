import SectionCard from "../components/SectionCard";
import { useWorkspace } from "../components/AppShell";

export default function MyInterestsPage() {
  const { interests, loading } = useWorkspace();

  return (
    <SectionCard title="My Interests" subtitle="Track the offers you have submitted to startups.">
      {loading.interests ? <p className="muted-text">Loading submitted offers...</p> : null}
      <div className="table-list">
        {interests.map((interest) => (
          <div key={interest.id} className="interest-card">
            <div className="interest-card-head">
              <div>
                <h3>{interest.startupName}</h3>
                <p>{interest.status}</p>
              </div>
              <span className={`status-pill status-${interest.status.toLowerCase()}`}>{interest.status}</span>
            </div>
            {interest.commitment ? (
              <div className="mini-item">
                <strong>Offer</strong>
                <span>
                  {interest.commitment.requestedAmount} for {interest.commitment.equityPercentage}%
                </span>
                {interest.commitment.investorNotes ? <span>Note: {interest.commitment.investorNotes}</span> : null}
              </div>
            ) : null}
            {interest.responseNotes ? <p className="muted-text">Startup response: {interest.responseNotes}</p> : null}
          </div>
        ))}
        {!loading.interests && !interests.length ? (
          <p className="muted-text">No investor interests yet. Submit an offer from the startup directory.</p>
        ) : null}
      </div>
    </SectionCard>
  );
}
