import { useState } from "react";
import ChatWindow from "./ChatWindow";
import LanguageSelector from "./LanguageSelector";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

export default function App() {
  const [language, setLanguage] = useState("en");
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(false);

  const sendMessage = async (message) => {
    const userMsg = { role: "user", content: message };
    const updatedHistory = [...history, userMsg];
    setHistory(updatedHistory);
    setLoading(true);

    try {
      const res = await fetch(`${API_URL}/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          message,
          language,
          // Strip citations before sending — backend only accepts role + content
          history: history.map(({ role, content }) => ({ role, content })),
        }),
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      setHistory([
        ...updatedHistory,
        { role: "assistant", content: data.answer, citations: data.citations },
      ]);
    } catch {
      setHistory([
        ...updatedHistory,
        {
          role: "assistant",
          content: "Sorry, something went wrong. Please try again.",
          citations: [],
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div
      style={{
        maxWidth: "800px",
        margin: "2rem auto",
        padding: "0 1rem",
        fontFamily: "system-ui, sans-serif",
      }}
    >
      <h1 style={{ marginBottom: "0.25rem" }}>ABC Widgets HR Assistant</h1>
      <p style={{ color: "#666", marginBottom: "1.5rem", fontSize: "0.9rem" }}>
        Ask questions about HR policies, benefits, leave, and more.
      </p>
      <LanguageSelector language={language} onChange={setLanguage} />
      <ChatWindow history={history} loading={loading} onSend={sendMessage} />
    </div>
  );
}
