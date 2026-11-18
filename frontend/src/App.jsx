import { useState } from "react";
import Learn from "./Learn.jsx";
import Profile from "./Profile.jsx";

export default function App() {
  const [userId, setUserId] = useState(() => localStorage.getItem("userId") || "");
  const [draft, setDraft] = useState("");
  const [tab, setTab] = useState("learn");

  const login = (e) => {
    e.preventDefault();
    const id = draft.trim();
    if (!id) return;
    localStorage.setItem("userId", id);
    setUserId(id);
  };

  const logout = () => {
    localStorage.removeItem("userId");
    setUserId("");
    setDraft("");
  };

  if (!userId) {
    return (
      <main className="card narrow">
        <h1>Персоналізоване навчання</h1>
        <p className="muted">Введіть ім’я або ідентифікатор, щоб почати.</p>
        <form onSubmit={login} className="row">
          <input value={draft} onChange={(e) => setDraft(e.target.value)} placeholder="Наприклад, violetta" autoFocus />
          <button type="submit">Увійти</button>
        </form>
      </main>
    );
  }

  return (
    <div className="layout">
      <header>
        <strong>Персоналізоване навчання</strong>
        <nav>
          <button className={tab === "learn" ? "tab active" : "tab"} onClick={() => setTab("learn")}>Навчання</button>
          <button className={tab === "profile" ? "tab active" : "tab"} onClick={() => setTab("profile")}>Профіль</button>
        </nav>
        <span className="muted">
          {userId} · <a href="#" onClick={(e) => { e.preventDefault(); logout(); }}>вийти</a>
        </span>
      </header>
      <main>
        {tab === "learn" ? <Learn userId={userId} /> : <Profile userId={userId} />}
      </main>
    </div>
  );
}
