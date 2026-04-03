import { NavLink, Outlet, useOutletContext } from "react-router-dom";
import { useAuth } from "../auth";
import { useWorkspaceData } from "../hooks/useWorkspaceData";

function navItemsForRole(role) {
  const common = [
    { to: "/", label: "Overview" },
    { to: "/startups", label: "Startups" },
    { to: "/notifications", label: "Notifications" }
  ];
  if (role === "ADMIN") {
    return [...common, { to: "/funding", label: "Funding" }];
  }
  if (role === "INVESTOR") {
    return [...common, { to: "/interests", label: "My Interests" }, { to: "/portfolio", label: "Portfolio" }];
  }
  if (role === "STARTUP_REP") {
    return [...common, { to: "/my-startups", label: "My Startups" }];
  }
  return common;
}

export function useWorkspace() {
  return useOutletContext();
}

export default function AppShell() {
  const { user, logout } = useAuth();
  const workspace = useWorkspaceData(user);
  const navItems = navItemsForRole(user?.role);
  const roleLabel = (user?.role || "Workspace").replaceAll("_", " ");
  const workspaceStats = [
    { label: "Tracked startups", value: workspace.startupCount },
    { label: "Active cohort", value: workspace.activeCount },
    { label: "Unread alerts", value: workspace.notifications.filter((item) => !item.isRead).length }
  ];

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand-block">
          <span className="eyebrow">SIMS Platform</span>
          <h1>Incubator OS</h1>
          <p>{roleLabel}</p>
        </div>

        <div className="sidebar-summary">
          <strong>{user?.fullName || "Workspace User"}</strong>
          <span>{user?.email}</span>
          <div className="sidebar-summary-grid">
            {workspaceStats.map((item) => (
              <div key={item.label} className="sidebar-stat">
                <strong>{item.value}</strong>
                <span>{item.label}</span>
              </div>
            ))}
          </div>
        </div>

        <nav className="side-nav">
          {navItems.map((item) => (
            <NavLink key={item.to} to={item.to} end={item.to === "/"} className={({ isActive }) => `nav-link${isActive ? " active" : ""}`}>
              {item.label}
            </NavLink>
          ))}
        </nav>

        <button className="ghost-btn sidebar-logout" onClick={logout}>
          Logout
        </button>
      </aside>

      <main className="workspace">
        <header className="workspace-hero">
          <div className="workspace-hero-copy">
            <span className="eyebrow">Startup Incubator Management System</span>
            <h2>Keep the cohort, pipeline, and investor activity in one operational view.</h2>
            <p>
              {workspace.startupCount} startups are in the system and {workspace.activeCount} are currently active across
              the incubator.
            </p>
          </div>
          <div className="workspace-hero-metrics">
            {workspaceStats.map((item) => (
              <div key={item.label} className="hero-stat">
                <span>{item.label}</span>
                <strong>{item.value}</strong>
              </div>
            ))}
          </div>
        </header>

        <Outlet context={workspace} />
      </main>
    </div>
  );
}
