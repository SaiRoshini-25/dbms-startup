import SectionCard from "../components/SectionCard";
import { useWorkspace } from "../components/AppShell";

function formatNotificationTime(value) {
  if (!value) return "Recent";

  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return "Recent";

  return new Intl.DateTimeFormat("en-IN", {
    day: "numeric",
    month: "short",
    hour: "numeric",
    minute: "2-digit"
  }).format(date);
}

export default function NotificationsPage() {
  const { notifications, handleMarkNotificationRead, loading } = useWorkspace();
  const unreadCount = notifications.filter((notification) => !notification.isRead).length;

  return (
    <div className="page-grid notifications-layout">
      <section className="hero notifications-hero">
        <div>
          <span className="eyebrow">Inbox</span>
          <h1>Clear alerts as you process them.</h1>
          <p>
            Notifications now disappear once marked as read, so this view stays focused on items that still need
            attention.
          </p>
        </div>
        <div className="hero-meta hero-metric-grid">
          <div className="metric">
            <strong>{notifications.length}</strong>
            <span>Total visible</span>
          </div>
          <div className="metric">
            <strong>{unreadCount}</strong>
            <span>Need action</span>
          </div>
        </div>
      </section>

      <SectionCard
        title="Notifications"
        subtitle="System-generated alerts for investor interest, assignments, approvals, and workspace updates."
      >
        {loading.notifications ? <p className="muted-text">Loading notifications...</p> : null}
        <div className="notification-list">
          {!notifications.length ? (
            <div className="empty-state notification-empty-state">
              <strong>Inbox clear.</strong>
              <span>No notifications are waiting for you right now.</span>
            </div>
          ) : null}
          {notifications.map((notification) => (
            <article key={notification.id} className="notification-card">
              <div className="notification-card-main">
                <div className="notification-card-head">
                  <div>
                    <h3>{notification.title}</h3>
                    <p>{notification.message}</p>
                  </div>
                  <span className="info-chip">{formatNotificationTime(notification.createdAt)}</span>
                </div>
              </div>
              <button className="ghost-btn" type="button" onClick={() => handleMarkNotificationRead(notification.id)}>
                Mark Read
              </button>
            </article>
          ))}
        </div>
      </SectionCard>
    </div>
  );
}
