import { useState } from "react";
import { apiRequest } from "../api";

export default function SearchPanel() {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState({ startups: [], users: [] });
  const [error, setError] = useState("");

  async function handleSubmit(event) {
    event.preventDefault();
    setError("");
    try {
      const response = await apiRequest(`/startups/search?q=${encodeURIComponent(query)}`);
      setResults(response);
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <div className="search-panel">
      <form className="search-form" onSubmit={handleSubmit}>
        <input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Search startups and users" />
        <button className="ghost-btn" type="submit">
          Search
        </button>
      </form>
      {error ? <p className="error-text">{error}</p> : null}
      <div className="search-results">
        <div>
          <h3>Startups</h3>
          {results.startups?.map((startup) => (
            <div key={startup.id} className="search-result-item">
              <strong>{startup.name}</strong>
              <span>{startup.domain}</span>
            </div>
          ))}
        </div>
        <div>
          <h3>People</h3>
          {results.users?.map((user) => (
            <div key={user.id} className="search-result-item">
              <strong>{user.fullName}</strong>
              <span>
                {user.role} . {user.email}
              </span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

