const BASE = import.meta.env.VITE_API_URL || "http://localhost:8000";

async function request(path, options) {
  const res = await fetch(BASE + path, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!res.ok) throw new Error(`Помилка сервера (${res.status})`);
  return res.json();
}

export const api = {
  topics: () => request("/topics"),
  recommendation: (uid) => request(`/recommendation/${encodeURIComponent(uid)}`),
  question: (topicId, exclude) =>
    request(`/topics/${topicId}/question${exclude ? `?exclude=${exclude}` : ""}`),
  check: (body) => request("/answers/check", { method: "POST", body: JSON.stringify(body) }),
  profile: (uid) => request(`/profile/${encodeURIComponent(uid)}`),
};
