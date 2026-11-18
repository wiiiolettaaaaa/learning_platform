import { useEffect, useState } from "react";
import { api } from "./api.js";

export default function Profile({ userId }) {
  const [topics, setTopics] = useState([]);
  const [profile, setProfile] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    Promise.all([api.topics(), api.profile(userId)])
      .then(([t, p]) => { setTopics(t); setProfile(p); })
      .catch((e) => setError(e.message + ". Перевірте, чи запущено бекенд на порту 8000."));
  }, [userId]);

  if (error) return <p className="error">{error}</p>;
  if (!profile) return <p className="muted">Завантаження…</p>;

  const risk = profile.dropout_risk;
  const riskLabel = risk < 0.3 ? "низький" : risk < 0.6 ? "середній" : "високий";

  return (
    <div className="card">
      <h2>Профіль знань</h2>
      {topics.map((t) => {
        const p = profile.mastery[t.id] ?? 0;
        return (
          <div key={t.id} className="topic">
            <div className="row between">
              <span>{t.title}</span>
              <span className="muted">{Math.round(p * 100)}%</span>
            </div>
            <div className="bar"><div className="fill" style={{ width: `${p * 100}%` }} /></div>
          </div>
        );
      })}
      <h3>Ризик відсіву</h3>
      <p>
        <strong>{riskLabel}</strong> <span className="muted">({risk})</span>
      </p>
    </div>
  );
}
