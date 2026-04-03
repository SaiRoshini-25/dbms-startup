import { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import { apiRequest } from "../api";

function createFeedback(type, message) {
  return { id: `${Date.now()}-${Math.random().toString(36).slice(2, 8)}`, type, message };
}

function getInvestorInterest(startup, userId) {
  const investorInterests = (startup?.interests || []).filter((interest) => interest.investorId === userId);
  return investorInterests.sort((left, right) => new Date(right.createdAt || 0) - new Date(left.createdAt || 0))[0] || null;
}

function hasAcceptedInvestorInterest(startup, userId) {
  return (startup?.interests || []).some((interest) => interest.investorId === userId && interest.status === "ACCEPTED");
}
export function useWorkspaceData(user) {
  const [startups, setStartups] = useState([]);
  const [interests, setInterests] = useState([]);
  const [portfolio, setPortfolio] = useState([]);
  const [myStartups, setMyStartups] = useState([]);
  const [editingFundingRound, setEditingFundingRound] = useState(null);
  const [editingStartupId, setEditingStartupId] = useState(null);
  const [startupForm, setStartupForm] = useState({});
  const [milestoneForm, setMilestoneForm] = useState({});
  const [commitmentForm, setCommitmentForm] = useState({});
  const [commitmentDecisionForm, setCommitmentDecisionForm] = useState({});
  const [notifications, setNotifications] = useState([]);
  const [feedbacks, setFeedbacks] = useState([]);
  const [filters, setFilters] = useState({ domain: "", fundingStage: "", minScore: "" });
  const [loading, setLoading] = useState({
    startups: false,
    interests: false,
    portfolio: false,
    myStartups: false,
    notifications: false
  });
  const [pendingActions, setPendingActions] = useState({});
  const navigate = useNavigate();

  const isAdmin = user?.role === "ADMIN";
  const isInvestor = user?.role === "INVESTOR";
  const isStartupRep = user?.role === "STARTUP_REP";

  const startupCount = startups.length;
  const activeCount = useMemo(
    () => startups.filter((startup) => startup.incubatorStatus === "ACTIVE").length,
    [startups]
  );

  function pushFeedback(type, message) {
    setFeedbacks((current) => [...current, createFeedback(type, message)]);
  }

  function dismissFeedback(id) {
    setFeedbacks((current) => current.filter((item) => item.id !== id));
  }

  function setLoadingState(key, value) {
    setLoading((current) => ({ ...current, [key]: value }));
  }

  function setActionPending(key, value) {
    setPendingActions((current) => ({ ...current, [key]: value }));
  }

  async function loadStartups() {
    setLoadingState("startups", true);
    try {
      const params = new URLSearchParams();
      if (filters.domain) params.set("domain", filters.domain);
      if (filters.fundingStage) params.set("fundingStage", filters.fundingStage);
      if (filters.minScore) params.set("minScore", filters.minScore);
      const queryString = params.toString();
      const response = await apiRequest(`/startups${queryString ? `?${queryString}` : ""}`);
      setStartups(response.items);
    } finally {
      setLoadingState("startups", false);
    }
  }

  async function loadPortfolio() {
    if (!isInvestor) {
      setPortfolio([]);
      return;
    }
    setLoadingState("portfolio", true);
    try {
      const response = await apiRequest("/investors/portfolio");
      setPortfolio(response.items);
    } finally {
      setLoadingState("portfolio", false);
    }
  }

  async function loadInvestorInterests() {
    if (!isInvestor) {
      setInterests([]);
      return;
    }
    setLoadingState("interests", true);
    try {
      const response = await apiRequest("/investors/interests");
      setInterests(response.items);
    } finally {
      setLoadingState("interests", false);
    }
  }

  async function loadMyStartups() {
    if (!isStartupRep) {
      setMyStartups([]);
      return;
    }
    setLoadingState("myStartups", true);
    try {
      const response = await apiRequest("/startups/my");
      setMyStartups(response.items);
    } finally {
      setLoadingState("myStartups", false);
    }
  }

  async function loadNotifications() {
    setLoadingState("notifications", true);
    try {
      const response = await apiRequest("/notifications");
      setNotifications(response.items);
    } finally {
      setLoadingState("notifications", false);
    }
  }

  useEffect(() => {
    if (!user) return;
    loadStartups().catch((err) => pushFeedback("error", err.message));
  }, [user, filters.domain, filters.fundingStage, filters.minScore]);

  useEffect(() => {
    if (!user) return undefined;

    async function refreshWorkspace() {
      try {
        await loadStartups();
        const tasks = [loadNotifications()];
        if (user.role === "INVESTOR") tasks.push(loadPortfolio(), loadInvestorInterests());
        if (user.role === "STARTUP_REP") tasks.push(loadMyStartups());
        await Promise.all(tasks);
      } catch (err) {
        pushFeedback("error", err.message);
      }
    }

    const intervalId = window.setInterval(refreshWorkspace, 15000);
    const handleFocus = () => {
      if (document.visibilityState === "hidden") return;
      refreshWorkspace();
    };

    window.addEventListener("focus", handleFocus);
    document.addEventListener("visibilitychange", handleFocus);

    return () => {
      window.clearInterval(intervalId);
      window.removeEventListener("focus", handleFocus);
      document.removeEventListener("visibilitychange", handleFocus);
    };
  }, [user, filters.domain, filters.fundingStage, filters.minScore]);

  useEffect(() => {
    if (!user) return;
    loadPortfolio().catch((err) => pushFeedback("error", err.message));
    loadInvestorInterests().catch((err) => pushFeedback("error", err.message));
    loadMyStartups().catch((err) => pushFeedback("error", err.message));
    loadNotifications().catch((err) => pushFeedback("error", err.message));
  }, [user?.role]);

  async function handleCreateStartup(payload) {
    try {
      setActionPending("create-startup", true);
      await apiRequest("/startups", {
        method: "POST",
        body: JSON.stringify(payload)
      });
      loadStartups();
      loadMyStartups();
      if (user?.role === "STARTUP_REP") {
        navigate("/my-startups");
      }
    } catch (err) {
      pushFeedback("error", err.message);
    } finally {
      setActionPending("create-startup", false);
    }
  }

  async function handleInterest(startupId) {
    if (!isInvestor) {
      return;
    }

    const startup = startups.find((item) => item.id === startupId);
    if (!startup?.acceptingInvestment) {
      return;
    }

    const form = commitmentForm[startupId] || {};
    const requestedAmount = Number(form.requestedAmount);
    const requiresEquity = !hasAcceptedInvestorInterest(startup, user?.id);
    const equityPercentage = requiresEquity ? Number(form.equityPercentage) : 0;
    if (!Number.isFinite(requestedAmount) || requestedAmount < 0) {
      return;
    }
    if (requiresEquity && (!Number.isFinite(equityPercentage) || equityPercentage < 0)) {
      return;
    }

    const optimisticInterest = {
      id: `temp-${startupId}`,
      startupId,
      investorId: user?.id,
      investorName: user?.fullName,
      notes: form.investorNotes || "",
      pipelineStage: "OFFER_SUBMITTED",
      status: "INITIATED",
      commitment: {
        requestedAmount,
        equityPercentage,
        investorNotes: form.investorNotes || "",
        status: "PENDING"
      }
    };
    setActionPending(`interest-${startupId}`, true);
    setStartups((current) =>
      current.map((item) =>
        item.id === startupId ? { ...item, interests: [...(item.interests || []), optimisticInterest] } : item
      )
    );

    try {
      await apiRequest("/investors/interest", {
        method: "POST",
        body: JSON.stringify({
          startupId,
          requestedAmount,
          ...(requiresEquity ? { equityPercentage } : {}),
          investorNotes: form.investorNotes || ""
        })
      });
      setCommitmentForm((current) => ({
        ...current,
        [startupId]: { requestedAmount: "", equityPercentage: "", investorNotes: "" }
      }));
      loadStartups();
      loadPortfolio();
      loadInvestorInterests();
      loadNotifications();
    } catch (err) {
      setStartups((current) =>
        current.map((item) =>
          item.id === startupId
            ? { ...item, interests: (item.interests || []).filter((interest) => interest.id !== optimisticInterest.id) }
            : item
        )
      );
    } finally {
      setActionPending(`interest-${startupId}`, false);
    }
  }

  async function handlePublishStartup(startupId) {
    try {
      await apiRequest(`/startups/${startupId}/publish`, { method: "PUT" });
      pushFeedback("success", "Startup published.");
      loadMyStartups();
      loadStartups();
      loadNotifications();
    } catch (err) {
      pushFeedback("error", err.message);
    }
  }

  async function handleCreateFundingRound(payload) {
    try {
      const path = editingFundingRound
        ? `/startups/${payload.startupId}/funding-rounds/${editingFundingRound.id}`
        : `/startups/${payload.startupId}/funding-rounds`;
      await apiRequest(path, {
        method: editingFundingRound ? "PUT" : "POST",
        body: JSON.stringify({
          roundName: payload.roundName,
          roundType: payload.roundType,
          amountRaised: payload.amountRaised,
          equityPercentage: payload.equityPercentage,
          leadInvestorId: payload.leadInvestorId,
          mouStatus: payload.mouStatus,
          roundStatus: payload.roundStatus,
          announcedOn: payload.announcedOn,
          closedOn: payload.closedOn,
          investmentRequirements: payload.investmentRequirements
        })
      });
      setEditingFundingRound(null);
      pushFeedback("success", editingFundingRound ? "Funding round updated." : "Funding round saved.");
      loadStartups();
    } catch (err) {
      pushFeedback("error", err.message);
    }
  }

  async function handleAcceptInterest(interestId) {
    try {
      setActionPending(`accept-interest-${interestId}`, true);
      await apiRequest(`/investors/interest/${interestId}/accept`, {
        method: "PUT",
        body: JSON.stringify({ responseNotes: "Startup accepted investor interest" })
      });
      loadMyStartups();
      loadStartups();
      loadInvestorInterests();
      loadNotifications();
    } catch (err) {
      pushFeedback("error", err.message);
    } finally {
      setActionPending(`accept-interest-${interestId}`, false);
    }
  }

  async function handleRejectInterest(interestId) {
    try {
      setActionPending(`reject-interest-${interestId}`, true);
      await apiRequest(`/investors/interest/${interestId}/reject`, {
        method: "PUT",
        body: JSON.stringify({ responseNotes: "Startup rejected investor interest" })
      });
      loadMyStartups();
      loadStartups();
      loadInvestorInterests();
      loadNotifications();
    } catch (err) {
      pushFeedback("error", err.message);
    } finally {
      setActionPending(`reject-interest-${interestId}`, false);
    }
  }

  async function handleCommitmentDecision(commitmentId, startupId, decision) {
    try {
      const form = commitmentDecisionForm[commitmentId] || {};
      await apiRequest(`/startups/commitments/${commitmentId}/decision`, {
        method: "PUT",
        body: JSON.stringify({
          decision,
          approvedAmount: form.approvedAmount ? Number(form.approvedAmount) : undefined,
          decisionNotes: form.decisionNotes || ""
        })
      });
      pushFeedback("success", `Commitment ${decision.toLowerCase()}.`);
      setCommitmentDecisionForm((current) => ({
        ...current,
        [commitmentId]: { approvedAmount: "", decisionNotes: "" }
      }));
      loadMyStartups();
      loadStartups();
      loadPortfolio();
      loadInvestorInterests();
      loadNotifications();
      if (startupId) {
        setEditingStartupId(startupId);
      }
    } catch (err) {
      pushFeedback("error", err.message);
    }
  }

  async function handleUpdateStartup(event, startupId) {
    event.preventDefault();
    try {
      await apiRequest(`/startups/${startupId}`, {
        method: "PUT",
        body: JSON.stringify(startupForm[startupId] || {})
      });
      pushFeedback("success", "Startup profile updated.");
      setEditingStartupId(null);
      loadMyStartups();
      loadStartups();
    } catch (err) {
      pushFeedback("error", err.message);
    }
  }

  async function handleCreateMilestone(event, startupId) {
    event.preventDefault();
    try {
      await apiRequest(`/startups/${startupId}/milestones`, {
        method: "POST",
        body: JSON.stringify(milestoneForm[startupId] || {})
      });
      pushFeedback("success", "Milestone added.");
      setMilestoneForm((current) => ({
        ...current,
        [startupId]: { title: "", description: "", status: "PENDING", progressPercent: 0 }
      }));
      loadMyStartups();
      loadStartups();
    } catch (err) {
      pushFeedback("error", err.message);
    }
  }

  async function handleMarkNotificationRead(notificationId) {
    const currentNotifications = notifications;
    setNotifications((current) => current.filter((item) => item.id !== notificationId));
    try {
      await apiRequest(`/notifications/${notificationId}/read`, { method: "PUT" });
    } catch (err) {
      setNotifications(currentNotifications);
      pushFeedback("error", err.message);
    }
  }

  function getInterestStatusForStartup(startup) {
    const interest = getInvestorInterest(startup, user?.id);
    if (!startup?.isPublished) {
      return { disabled: true, label: "Draft", helper: "This startup must be published before investors can engage." };
    }
    if (!startup?.acceptingInvestment) {
      return { disabled: true, label: "Closed", helper: "This startup is not accepting further investment right now." };
    }
    if (!interest) {
      return { disabled: false, label: "Express Interest", helper: "Signal interest to begin the investor pipeline." };
    }
    if (interest.status === "ACCEPTED") {
      return { disabled: false, label: "Contribute Again", helper: "Your earlier offer was accepted. You can submit another contribution at any time." };
    }
    if (interest.status === "REJECTED") {
      return { disabled: false, label: "Submit Revised Offer", helper: "Your earlier offer was rejected. You can send a revised one anytime." };
    }
    return { disabled: false, label: "Add Another Offer", helper: "You can submit multiple offers for the same startup whenever you want." };
  }

  return {
    user,
    startups,
    interests,
    portfolio,
    myStartups,
    editingFundingRound,
    setEditingFundingRound,
    editingStartupId,
    setEditingStartupId,
    startupForm,
    setStartupForm,
    milestoneForm,
    setMilestoneForm,
    commitmentForm,
    setCommitmentForm,
    commitmentDecisionForm,
    setCommitmentDecisionForm,
    notifications,
    feedbacks,
    dismissFeedback,
    loading,
    pendingActions,
    filters,
    setFilters,
    isAdmin,
    isInvestor,
    isStartupRep,
    startupCount,
    activeCount,
    handleCreateStartup,
    handleInterest,
    handlePublishStartup,
    handleCreateFundingRound,
    handleAcceptInterest,
    shouldRequestEquityForStartup(startup) {
      return !hasAcceptedInvestorInterest(startup, user?.id);
    },
    handleRejectInterest,
    handleCommitmentDecision,
    handleUpdateStartup,
    handleCreateMilestone,
    handleMarkNotificationRead,
    getInterestStatusForStartup
  };
}
