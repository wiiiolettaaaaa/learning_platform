import { useCallback, useEffect, useState } from "react";
import { api } from "./api.js";

const riskInfo = (r) =>
  r < 0.3 ? { label: "низький", cls: "low" } : r < 0.6 ? { label: "середній", cls: "mid" } : { label: "високий", cls: "high" };

const pct = (v) => (v === null || v === undefined ? "—" : `${Math.round(v * 100)}%`);

export default function Teacher() {
  const [students, setStudents] = useState([]);
  const [topics, setTopics] = useState([]);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  const load = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      const [s, t] = await Promise.all([api.teacherStudents(), api.teacherTopics()]);
      setStudents(s);
      setTopics(t);
    } catch (e) {
      setError(e.message + ". Перевірте, чи запущено бекенд на порту 8000.");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { load(); }, [load]);

  if (error) return <p className="error">{error}</p>;

  const answered = topics.filter((t) => t.accuracy !== null);
  const weakest = answered.length ? answered.reduce((a, b) => (b.accuracy < a.accuracy ? b : a)) : null;

  return (
    <div className="stack">
      <div className="card">
        <div className="row between">
          <h2>Студенти</h2>
          <button onClick={load} disabled={loading}>{loading ? "Оновлення…" : "Оновити"}</button>
        </div>
        {students.length === 0 ? (
          <p className="muted">Поки немає студентів. Зайдіть під іншим іменем і дайте кілька відповідей.</p>
        ) : (
          <table>
            <thead>
              <tr><th>Студент</th><th>Середнє засвоєння</th><th>Спроб за тиждень</th><th>Днів без практики</th><th>Ризик відсіву</th></tr>
            </thead>
            <tbody>
              {students.map((s) => {
                const r = riskInfo(s.dropout_risk);
                return (
                  <tr key={s.user_id}>
                    <td>{s.user_id}</td>
                    <td>{pct(s.avg_mastery)}</td>
                    <td>{s.attempts_last_week}</td>
                    <td>{s.days_inactive}</td>
                    <td><span className={`pill ${r.cls}`}>{r.label} ({s.dropout_risk})</span></td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        )}
      </div>

      <div className="card">
        <h2>Теми</h2>
        {weakest && (
          <p className="muted">Найскладніша тема за часткою правильних відповідей: <strong>{weakest.title}</strong> ({pct(weakest.accuracy)}).</p>
        )}
        <table>
          <thead>
            <tr><th>Тема</th><th>Спроб</th><th>Правильних</th><th>Середнє засвоєння</th></tr>
          </thead>
          <tbody>
            {topics.map((t) => (
              <tr key={t.topic_id} className={weakest && t.topic_id === weakest.topic_id ? "weak" : ""}>
                <td>{t.title}</td>
                <td>{t.attempts}</td>
                <td>{pct(t.accuracy)}</td>
                <td>{pct(t.avg_mastery)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
