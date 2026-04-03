import SectionCard from "../components/SectionCard";
import StartupForm from "../components/StartupForm";
import { useWorkspace } from "../components/AppShell";

export default function StartupsPage() {
  const {
    startups,
    isAdmin,
    isStartupRep,
    isInvestor,
    commitmentForm,
    setCommitmentForm,
    handleCreateStartup,
    handleInterest,
    loading,
    pendingActions,
    getInterestStatusForStartup,
    shouldRequestEquityForStartup
  } = useWorkspace();

  return (
    <div className="page-grid">
      <SectionCard title="Startup Directory" subtitle="Browse registered startups and profile details.">
        {loading.startups ? <p className="muted-text">Loading startups...</p> : null}
        <div className="startup-list">
          {startups.map((startup) => {
            const interestState = getInterestStatusForStartup(startup);
            const requiresEquity = shouldRequestEquityForStartup(startup);
            return (
              <article key={startup.id} className="startup-item">
                <div>
                  <h3>{startup.name}</h3>
                  <p>
                    {startup.domain} . {startup.fundingStage} . Team {startup.teamSize}
                  </p>
                  <p>
                    Status: {startup.isPublished ? "Published" : "Draft"} . Raised {startup.totalRaised || 0} / {startup.targetAmount || 0}
                  </p>
                  <small>{startup.description || "No description available."}</small>
                  {startup.fundingRequirements ? <small>Investor requirements: {startup.fundingRequirements}</small> : null}
                  {isInvestor ? <small>{interestState.helper}</small> : null}
                  {isInvestor && startup.isPublished ? (
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
                      {requiresEquity ? (
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
                      ) : (
                        <small className="muted-text">This follow-up contribution does not request extra equity.</small>
                      )}
                      <textarea
                        rows="2"
                        placeholder="Optional note"
                        value={commitmentForm[startup.id]?.investorNotes || ""}
                        onChange={(event) =>
                          setCommitmentForm((current) => ({
                            ...current,
                            [startup.id]: { ...(current[startup.id] || {}), investorNotes: event.target.value }
                          }))
                        }
                        disabled={interestState.disabled}
                      />
                      <button
                        className="primary-btn"
                        type="button"
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

      {isAdmin ? (
        <SectionCard title="Add Startup" subtitle="Create a new incubator startup profile.">
          <StartupForm onSubmit={handleCreateStartup} submitLabel="Add Startup" />
        </SectionCard>
      ) : null}

      {isStartupRep ? (
        <SectionCard title="Create My Startup" subtitle="Register your startup into the incubator. After creation it will appear under My Startups as a draft until you publish it.">
          <StartupForm onSubmit={handleCreateStartup} showMemberRole submitLabel="Create Startup" />
        </SectionCard>
      ) : null}
    </div>
  );
}
