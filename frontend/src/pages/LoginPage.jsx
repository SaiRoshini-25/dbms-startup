import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../auth";

export default function LoginPage() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [form, setForm] = useState({ email: "", password: "" });
  const [error, setError] = useState("");

  function handleChange(event) {
    const { name, value } = event.target;
    setForm((current) => ({ ...current, [name]: value }));
  }

  async function handleSubmit(event) {
    event.preventDefault();
    setError("");
    try {
      await login(form);
      navigate("/");
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <main className="auth-shell">
      <div className="auth-panel">
        <div className="auth-showcase">
          <span className="eyebrow">Incubator OS</span>
          <h1>Role-based access for founders, investors, and admins.</h1>
          <p className="muted-text">
            Coordinate startup progress, funding signals, and reporting from a single operational workspace.
          </p>
          <div className="auth-feature-list">
            <div className="auth-feature">
              <strong>Cohort visibility</strong>
              <span>Track startup readiness, milestones, and funding movement in one place.</span>
            </div>
            <div className="auth-feature">
              <strong>Role-based workflows</strong>
              <span>Give each user a focused workspace without losing shared context.</span>
            </div>
            <div className="auth-feature">
              <strong>Faster decisions</strong>
              <span>Search, review notifications, and act on investor activity with less friction.</span>
            </div>
          </div>
        </div>
        <div className="auth-form-card">
          <div className="form-intro">
            <h2>Sign in</h2>
            <p className="muted-text">Use your registered account to continue into the workspace.</p>
          </div>
          <form onSubmit={handleSubmit} className="auth-form">
            <input type="email" name="email" placeholder="Email" onChange={handleChange} value={form.email} required />
            <input
              type="password"
              name="password"
              placeholder="Password"
              onChange={handleChange}
              value={form.password}
              required
            />
            {error ? <p className="error-text">{error}</p> : null}
            <button className="primary-btn" type="submit">
              Sign In
            </button>
            <p className="muted-text">
              New user? <Link to="/register">Register</Link>
            </p>
          </form>
        </div>
      </div>
    </main>
  );
}
