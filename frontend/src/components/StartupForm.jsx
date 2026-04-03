import { useState } from "react";

const initialState = {
  name: "",
  domain: "",
  fundingStage: "Pre-Seed",
  foundingDate: "",
  teamSize: 1,
  headquartersCity: "",
  websiteUrl: "",
  description: "",
  incubatorStatus: "ACTIVE",
  fundingStatus: "BOOTSTRAPPED",
  fundingRequirements: "",
  targetAmount: "",
  performanceScore: "",
  memberRole: "Founder"
};

export default function StartupForm({ onSubmit, showMemberRole = false, submitLabel = "Add Startup" }) {
  const [form, setForm] = useState(initialState);

  function handleChange(event) {
    const { name, value } = event.target;
    setForm((current) => ({ ...current, [name]: value }));
  }

  async function handleSubmit(event) {
    event.preventDefault();
    await onSubmit({
      ...form,
      teamSize: Number(form.teamSize),
      targetAmount: form.targetAmount ? Number(form.targetAmount) : 0,
      performanceScore: form.performanceScore ? Number(form.performanceScore) : null
    });
    setForm(initialState);
  }

  return (
    <form className="form-grid" onSubmit={handleSubmit}>
      <input name="name" placeholder="Startup name" value={form.name} onChange={handleChange} required />
      <input name="domain" placeholder="Domain" value={form.domain} onChange={handleChange} required />
      <select name="fundingStage" value={form.fundingStage} onChange={handleChange}>
        <option>Pre-Seed</option>
        <option>Seed</option>
        <option>Series A</option>
        <option>Series B</option>
      </select>
      <input name="foundingDate" type="date" value={form.foundingDate} onChange={handleChange} required />
      <input name="teamSize" type="number" min="1" value={form.teamSize} onChange={handleChange} required />
      <input name="headquartersCity" placeholder="City" value={form.headquartersCity} onChange={handleChange} />
      <input name="websiteUrl" placeholder="Website" value={form.websiteUrl} onChange={handleChange} />
      {showMemberRole ? (
        <input name="memberRole" placeholder="Your role in startup" value={form.memberRole} onChange={handleChange} />
      ) : null}
      <input
        name="targetAmount"
        type="number"
        min="0"
        step="1000"
        placeholder="Target amount"
        value={form.targetAmount}
        onChange={handleChange}
      />
      <input
        name="performanceScore"
        type="number"
        min="0"
        max="100"
        step="0.1"
        placeholder="Performance score"
        value={form.performanceScore}
        onChange={handleChange}
      />
      <textarea
        name="fundingRequirements"
        placeholder="Funding requirements for investors"
        value={form.fundingRequirements}
        onChange={handleChange}
        rows="3"
      />
      <textarea
        name="description"
        placeholder="Short description"
        value={form.description}
        onChange={handleChange}
        rows="4"
      />
      <button className="primary-btn" type="submit">
        {submitLabel}
      </button>
    </form>
  );
}
