import FundingRoundForm from "../components/FundingRoundForm";
import SectionCard from "../components/SectionCard";
import { useWorkspace } from "../components/AppShell";

export default function FundingPage() {
  const { startups, editingFundingRound, setEditingFundingRound, handleCreateFundingRound } = useWorkspace();

  return (
    <div className="page-grid">
      <SectionCard title="Funding Rounds" subtitle="Create and manage investment rounds with investor requirements.">
        <FundingRoundForm
          startups={startups}
          onSubmit={handleCreateFundingRound}
          initialValue={editingFundingRound}
          onCancel={() => setEditingFundingRound(null)}
        />
      </SectionCard>
      <SectionCard title="Existing Rounds" subtitle="Review and edit current funding round records.">
        <div className="table-list">
          {startups.flatMap((startup) =>
            (startup.fundingRounds || []).map((round) => (
              <div key={round.id} className="table-row">
                <span>
                  <strong>{startup.name}</strong>
                  <br />
                  {round.roundName}
                </span>
                <span>
                  {round.amountRaised} . {round.roundStatus}
                  <br />
                  {round.mouStatus} {round.announcedOn ? `. Announced ${round.announcedOn}` : ""}
                  {round.closedOn ? ` . Closed ${round.closedOn}` : ""}
                </span>
                <button className="ghost-btn" type="button" onClick={() => setEditingFundingRound({ ...round, startupId: startup.id })}>
                  Edit
                </button>
              </div>
            ))
          )}
        </div>
      </SectionCard>
    </div>
  );
}
