import { useEffect, useState } from "react";

const initialState = {
  startupId: "",
  roundName: "",
  roundType: "Seed",
  amountRaised: "",
  equityPercentage: "",
  leadInvestorId: "",
  mouStatus: "PENDING",
  roundStatus: "OPEN",
  announcedOn: "",
  closedOn: "",
  investmentRequirements: ""
};

export default function FundingRoundForm({ startups, onSubmit, initialValue, onCancel }) {
  const [form, setForm] = useState(initialState);

  useEffect(() => {
    if (initialValue) {
      setForm({
        startupId: String(initialValue.startupId ?? ""),
        roundName: initialValue.roundName ?? "",
        roundType: initialValue.roundType ?? "Seed",
        amountRaised: String(initialValue.amountRaised ?? ""),
        equityPercentage: String(initialValue.equityPercentage ?? ""),
        leadInvestorId: initialValue.leadInvestorId ? String(initialValue.leadInvestorId) : "",
        mouStatus: initialValue.mouStatus ?? "PENDING",
        roundStatus: initialValue.roundStatus ?? "OPEN",
        announcedOn: initialValue.announcedOn ?? "",
        closedOn: initialValue.closedOn ?? "",
        investmentRequirements: initialValue.investmentRequirements ?? ""
      });
    } else {
      setForm(initialState);
    }
  }, [initialValue]);

  function handleChange(event) {
    const { name, value } = event.target;
    setForm((current) => ({ ...current, [name]: value }));
  }

  async function handleSubmit(event) {
    event.preventDefault();
    await onSubmit({
      ...form,
      startupId: Number(form.startupId),
      amountRaised: Number(form.amountRaised),
      equityPercentage: Number(form.equityPercentage),
      leadInvestorId: form.leadInvestorId ? Number(form.leadInvestorId) : null,
      announcedOn: form.announcedOn || null,
      closedOn: form.closedOn || null,
      investmentRequirements: form.investmentRequirements
    });
    setForm(initialState);
  }

  return (
    <form className="form-grid" onSubmit={handleSubmit}>
      <select name="startupId" value={form.startupId} onChange={handleChange} required>
        <option value="">Select startup</option>
        {startups.map((startup) => (
          <option key={startup.id} value={startup.id}>
            {startup.name}
          </option>
        ))}
      </select>
      <input name="roundName" placeholder="Round name" value={form.roundName} onChange={handleChange} required />
      <select name="roundType" value={form.roundType} onChange={handleChange}>
        <option>Pre-Seed</option>
        <option>Seed</option>
        <option>Series A</option>
        <option>Series B</option>
      </select>
      <input
        name="amountRaised"
        type="number"
        min="0"
        placeholder="Amount raised"
        value={form.amountRaised}
        onChange={handleChange}
        required
      />
      <input
        name="equityPercentage"
        type="number"
        min="0"
        max="100"
        step="0.1"
        placeholder="Equity %"
        value={form.equityPercentage}
        onChange={handleChange}
        required
      />
      <input
        name="leadInvestorId"
        type="number"
        min="1"
        placeholder="Lead investor user ID"
        value={form.leadInvestorId}
        onChange={handleChange}
      />
      <select name="mouStatus" value={form.mouStatus} onChange={handleChange}>
        <option>PENDING</option>
        <option>SIGNED</option>
        <option>CANCELLED</option>
      </select>
      <select name="roundStatus" value={form.roundStatus} onChange={handleChange}>
        <option>OPEN</option>
        <option>CLOSED</option>
        <option>IN_PROGRESS</option>
      </select>
      <input name="announcedOn" type="date" value={form.announcedOn} onChange={handleChange} />
      <input name="closedOn" type="date" value={form.closedOn} onChange={handleChange} />
      <textarea
        name="investmentRequirements"
        placeholder="Requirements or requests for the investor"
        value={form.investmentRequirements}
        onChange={handleChange}
        rows="4"
      />
      <button className="primary-btn" type="submit">
        {initialValue ? "Update Funding Round" : "Save Funding Round"}
      </button>
      {initialValue ? (
        <button className="ghost-btn" type="button" onClick={onCancel}>
          Cancel Edit
        </button>
      ) : null}
    </form>
  );
}
