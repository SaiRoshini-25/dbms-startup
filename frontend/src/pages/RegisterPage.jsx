import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../auth";

export default function RegisterPage() {
  const { register } = useAuth();
  const navigate = useNavigate();
  const [form, setForm] = useState({
    fullName: "",
    email: "",
    password: "",
    phone: "",
    organizationName: "",
    role: "STARTUP_REP"
  });
  const [error, setError] = useState("");

  function handleChange(event) {
    const { name, value } = event.target;
    setForm((current) => ({ ...current, [name]: value }));
  }

  async function handleSubmit(event) {
    event.preventDefault();
    setError("");
    try {
      await register(form);
      navigate("/login");
    } catch (err) {
      setError(err.status === 409 ? "This email is already registered. Sign in instead." : err.message);
    }
  }

  return (
    <main className="auth-shell">
      <div className="auth-panel">
        <div className="auth-showcase">
          <span className="eyebrow">Open Registration</span>
          <h1>Create an investor or startup representative account.</h1>
          <p className="muted-text">
            Start with the role you need today and move directly into the relevant workspace after registration.
          </p>
          <div className="auth-feature-list">
            <div className="auth-feature">
              <strong>Founders</strong>
              <span>Register your startup, publish updates, and manage incoming investor interest.</span>
            </div>
            <div className="auth-feature">
              <strong>Investors</strong>
              <span>Discover startups, record interest, and maintain portfolio visibility.</span>
            </div>
          </div>
        </div>
        <div className="auth-form-card">
          <div className="form-intro">
            <h2>Create account</h2>
            <p className="muted-text">Set up access for the incubator workspace.</p>
          </div>
          <form onSubmit={handleSubmit} className="auth-form">
            <input name="fullName" placeholder="Full name" value={form.fullName} onChange={handleChange} required />
            <input name="email" type="email" placeholder="Email" value={form.email} onChange={handleChange} required />
            <input
              name="password"
              type="password"
              placeholder="Password"
              value={form.password}
              onChange={handleChange}
              required
            />
            <input name="phone" placeholder="Phone" value={form.phone} onChange={handleChange} />
            <input
              name="organizationName"
              placeholder="Organization"
              value={form.organizationName}
              onChange={handleChange}
            />
            <select name="role" value={form.role} onChange={handleChange}>
              <option value="STARTUP_REP">Startup Representative</option>
              <option value="INVESTOR">Investor</option>
            </select>
            {error ? <p className="error-text">{error}</p> : null}
            <button className="primary-btn" type="submit">
              Register
            </button>
            <p className="muted-text">
              Already have access? <Link to="/login">Sign in</Link>
            </p>
          </form>
        </div>
      </div>
    </main>
  );
}
