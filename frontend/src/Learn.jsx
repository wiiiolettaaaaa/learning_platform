import { useCallback, useEffect, useState } from "react";
import { api } from "./api.js";

export default function Learn({ userId }) {
  const [topics, setTopics] = useState({});
  const [rec, setRec] = useState(null);
  const [question, setQuestion] = useState(null);
  const [result, setResult] = useState(null); // { correct, correct_choice, mastery, choice }
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  const loadNext = useCallback(async (excludeQuestion) => {
    setLoading(true);
    setError("");
    setResult(null);
    try {
      const list = await api.topics();
      setTopics(Object.fromEntries(list.map((t) => [t.id, t.title])));
      const r = await api.recommendation(userId);
      setRec(r);
      if (r.topic_id) setQuestion(await api.question(r.topic_id, excludeQuestion));
      else setQuestion(null);
    } catch (e) {
      setError(e.message + ". Перевірте, чи запущено бекенд на порту 8000.");
    } finally {
      setLoading(false);
    }
  }, [userId]);

  useEffect(() => { loadNext(); }, [loadNext]);

  const answer = async (choice) => {
    if (result) return;
    try {
      const res = await api.check({
        user_id: userId,
        topic_id: question.topic_id,
        question_id: question.id,
        choice,
      });
      setResult({ ...res, choice });
    } catch (e) {
      setError(e.message);
    }
  };

  if (loading) return <p className="muted">Завантаження…</p>;
  if (error) return <p className="error">{error}</p>;
  if (rec && rec.message) return <div className="card"><h2>🎉 {rec.message}</h2></div>;

  return (
    <div className="card">
      <div className="badge">{rec.kind === "review" ? "Повторення" : "Нова тема"}</div>
      <h2>{topics[rec.topic_id] || rec.topic_id}</h2>
      <p className="muted">{rec.explanation}</p>

      <h3>{question.text}</h3>
      <div className="options">
        {question.options.map((o, i) => {
          let cls = "option";
          if (result) {
            if (i === result.correct_choice) cls += " right";
            else if (i === result.choice) cls += " wrong";
          }
          return (
            <button key={i} className={cls} disabled={!!result} onClick={() => answer(i)}>{o}</button>
          );
        })}
      </div>

      {result && (
        <div className="feedback">
          <p>
            {result.correct ? "✅ Правильно!" : "❌ Неправильно."} Рівень засвоєння теми:{" "}
            <strong>{Math.round(result.mastery * 100)}%</strong>
          </p>
          <button onClick={() => loadNext(question.id)}>Далі</button>
        </div>
      )}
    </div>
  );
}
