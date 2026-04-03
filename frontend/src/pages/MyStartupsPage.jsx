import SectionCard from "../components/SectionCard";
import { useWorkspace } from "../components/AppShell";

function getFundingHistoryItems(startup) {
  const recordedRounds = (startup.fundingRounds || []).map((round) => ({
    id: `round-${round.id}`,
    title: round.roundName,
    summary: `${round.amountRaised} . ${round.roundStatus}`,
    extra: round.investmentRequirements ? `Needs: ${round.investmentRequirements}` : null,
    sortDate: round.createdAt || ""
  }));

  const approvedCommitments = (startup.commitments || [])
    .filter((commitment) => commitment.status === "APPROVED")
    .map((commitment) => ({
      id: `commitment-${commitment.id}`,
      title: `Approved commitment from ${commitment.investorName || "Investor"}`,
      summary: `${commitment.approvedAmount || commitment.requestedAmount} . ${commitment.equityPercentage}% equity`,
      extra: commitment.startupRequirements ? `Requirements: ${commitment.startupRequirements}` : null,
      sortDate: commitment.agreedAt || commitment.createdAt || ""
    }));

  return [...recordedRounds, ...approvedCommitments].sort((left, right) => {
    const leftTime = left.sortDate ? new Date(left.sortDate).getTime() : 0;
    const rightTime = right.sortDate ? new Date(right.sortDate).getTime() : 0;
    return rightTime - leftTime;
  });
}

export default function MyStartupsPage() {
  const {
    myStartups,
    editingStartupId,
    setEditingStartupId,
    startupForm,
    setStartupForm,
    milestoneForm,
    setMilestoneForm,
    handleUpdateStartup,
    handleCreateMilestone,
    handlePublishStartup,
    handleAcceptInterest,
    handleRejectInterest,
    loading,
    pendingActions
  } = useWorkspace();

  return (
    <SectionCard title="My Startups" subtitle="Update your startup profile, milestones, and investor pipeline.">
      {loading.myStartups ? <p className="muted-text">Loading startup workspace...</p> : null}
      <div className="table-list">
        {myStartups.map((startup) => {
          const fundingHistoryItems = getFundingHistoryItems(startup);

          return (
          <div key={startup.id} className="rep-startup">
            <div className="rep-startup-head">
              <h3>{startup.name}</h3>
              <span>
                {startup.domain} . {startup.fundingStage}
              </span>
            </div>
            <div className="rep-actions">
              <button
                className="ghost-btn"
                type="button"
                onClick={() => {
                  setEditingStartupId(startup.id);
                  setStartupForm((current) => ({
                    ...current,
                    [startup.id]: {
                      description: startup.description || "",
                      teamSize: startup.teamSize,
                      fundingStatus: startup.fundingStatus || "",
                      fundingRequirements: startup.fundingRequirements || "",
                      performanceScore: startup.performanceScore || ""
                    }
                  }));
                }}
              >
                Update Profile
              </button>
              {!startup.isPublished ? (
                <button className="primary-btn" type="button" onClick={() => handlePublishStartup(startup.id)}>
                  Publish Startup
                </button>
              ) : null}
            </div>

            <div className="stats-row">
              <span>Published: {startup.isPublished ? "Yes" : "No"}</span>
              <span>Target: {startup.targetAmount || 0}</span>
              <span>Raised: {startup.totalRaised || 0}</span>
              <span>Equity Allocated: {startup.equityAllocated || 0}%</span>
              <span>Investors: {startup.investorCount || 0}</span>
            </div>

            {editingStartupId === startup.id ? (
              <form className="form-grid" onSubmit={(event) => handleUpdateStartup(event, startup.id)}>
                <textarea
                  rows="3"
                  placeholder="Description"
                  value={startupForm[startup.id]?.description || ""}
                  onChange={(event) =>
                    setStartupForm((current) => ({
                      ...current,
                      [startup.id]: { ...(current[startup.id] || {}), description: event.target.value }
                    }))
                  }
                />
                <input
                  type="number"
                  min="1"
                  placeholder="Team size"
                  value={startupForm[startup.id]?.teamSize || ""}
                  onChange={(event) =>
                    setStartupForm((current) => ({
                      ...current,
                      [startup.id]: { ...(current[startup.id] || {}), teamSize: Number(event.target.value) }
                    }))
                  }
                />
                <input
                  placeholder="Funding status"
                  value={startupForm[startup.id]?.fundingStatus || ""}
                  onChange={(event) =>
                    setStartupForm((current) => ({
                      ...current,
                      [startup.id]: { ...(current[startup.id] || {}), fundingStatus: event.target.value }
                    }))
                  }
                />
                <textarea
                  rows="3"
                  placeholder="Funding requirements"
                  value={startupForm[startup.id]?.fundingRequirements || ""}
                  onChange={(event) =>
                    setStartupForm((current) => ({
                      ...current,
                      [startup.id]: { ...(current[startup.id] || {}), fundingRequirements: event.target.value }
                    }))
                  }
                />
                <input
                  type="number"
                  min="0"
                  step="1000"
                  placeholder="Target amount"
                  value={startupForm[startup.id]?.targetAmount || startup.targetAmount || ""}
                  onChange={(event) =>
                    setStartupForm((current) => ({
                      ...current,
                      [startup.id]: { ...(current[startup.id] || {}), targetAmount: Number(event.target.value) }
                    }))
                  }
                />
                <input
                  type="number"
                  min="0"
                  max="100"
                  step="0.1"
                  placeholder="Performance score"
                  value={startupForm[startup.id]?.performanceScore || ""}
                  onChange={(event) =>
                    setStartupForm((current) => ({
                      ...current,
                      [startup.id]: { ...(current[startup.id] || {}), performanceScore: Number(event.target.value) }
                    }))
                  }
                />
                <button className="primary-btn" type="submit">
                  Save Startup
                </button>
              </form>
            ) : null}

            <div className="rep-columns">
              <div>
                <h4>Milestones</h4>
                {startup.milestones.length ? (
                  startup.milestones.map((milestone) => (
                    <div key={milestone.id} className="mini-item">
                      <strong>{milestone.title}</strong>
                      <span>
                        {milestone.status} . {milestone.progressPercent}%
                      </span>
                    </div>
                  ))
                ) : (
                  <p className="muted-text">No milestones yet.</p>
                )}
                <form className="form-grid compact-form" onSubmit={(event) => handleCreateMilestone(event, startup.id)}>
                  <input
                    placeholder="Milestone title"
                    value={milestoneForm[startup.id]?.title || ""}
                    onChange={(event) =>
                      setMilestoneForm((current) => ({
                        ...current,
                        [startup.id]: { ...(current[startup.id] || {}), title: event.target.value }
                      }))
                    }
                  />
                  <input
                    placeholder="Description"
                    value={milestoneForm[startup.id]?.description || ""}
                    onChange={(event) =>
                      setMilestoneForm((current) => ({
                        ...current,
                        [startup.id]: { ...(current[startup.id] || {}), description: event.target.value }
                      }))
                    }
                  />
                  <select
                    value={milestoneForm[startup.id]?.status || "PENDING"}
                    onChange={(event) =>
                      setMilestoneForm((current) => ({
                        ...current,
                        [startup.id]: { ...(current[startup.id] || {}), status: event.target.value }
                      }))
                    }
                  >
                    <option value="PENDING">PENDING</option>
                    <option value="IN_PROGRESS">IN_PROGRESS</option>
                    <option value="COMPLETED">COMPLETED</option>
                  </select>
                  <input
                    type="number"
                    min="0"
                    max="100"
                    placeholder="Progress %"
                    value={milestoneForm[startup.id]?.progressPercent || 0}
                    onChange={(event) =>
                      setMilestoneForm((current) => ({
                        ...current,
                        [startup.id]: { ...(current[startup.id] || {}), progressPercent: Number(event.target.value) }
                      }))
                    }
                  />
                  <button className="ghost-btn" type="submit">
                    Add Milestone
                  </button>
                </form>
              </div>

              <div>
                <h4>Funding History</h4>
                {fundingHistoryItems.length ? (
                  fundingHistoryItems.map((item) => (
                    <div key={item.id} className="mini-item">
                      <strong>{item.title}</strong>
                      <span>{item.summary}</span>
                      {item.extra ? <span>{item.extra}</span> : null}
                    </div>
                  ))
                ) : (
                  <p className="muted-text">No funding activity yet. Approved offers and funding rounds will appear here.</p>
                )}
              </div>

              <div>
                <h4>Investor Offers</h4>
                {startup.interests.length ? (
                  startup.interests.map((interest) => {
                    const relatedCommitment = startup.commitments.find((commitment) => commitment.interestId === interest.id);
                    const canRespond = interest.status === "INITIATED";
                    return (
                      <div key={interest.id} className="mini-item interest-card">
                        <strong>{interest.investorName}</strong>
                        <span>{interest.status}</span>
                        {relatedCommitment ? (
                          <span>
                            Offer {relatedCommitment.requestedAmount} for {relatedCommitment.equityPercentage}%
                          </span>
                        ) : null}
                        {relatedCommitment?.investorNotes ? <span>Note: {relatedCommitment.investorNotes}</span> : null}
                        {interest.responseNotes ? <span>Response: {interest.responseNotes}</span> : null}
                        {canRespond ? (
                          <div className="inline-stack">
                            <button
                              className="primary-btn"
                              type="button"
                              onClick={() => handleAcceptInterest(interest.id)}
                              disabled={pendingActions[`accept-interest-${interest.id}`]}
                            >
                              {pendingActions[`accept-interest-${interest.id}`] ? "Accepting..." : "Accept"}
                            </button>
                            <button
                              className="ghost-btn"
                              type="button"
                              onClick={() => handleRejectInterest(interest.id)}
                              disabled={pendingActions[`reject-interest-${interest.id}`]}
                            >
                              {pendingActions[`reject-interest-${interest.id}`] ? "Rejecting..." : "Reject"}
                            </button>
                          </div>
                        ) : null}
                      </div>
                    );
                  })
                ) : (
                  <p className="muted-text">No investor offers yet.</p>
                )}
              </div>
            </div>
          </div>
          );
        })}
        {!myStartups.length ? <p className="muted-text">No startup assignments found.</p> : null}
      </div>
    </SectionCard>
  );
}
