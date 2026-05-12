import { useState, useRef, useEffect } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import CitationFootnotes from "./CitationFootnotes";

export default function ChatWindow({ history, loading, onSend }) {
  const [input, setInput] = useState("");
  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [history, loading]);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!input.trim() || loading) return;
    onSend(input.trim());
    setInput("");
  };

  return (
    <div>
      <div
        style={{
          height: "500px",
          overflowY: "auto",
          border: "1px solid #ccc",
          borderRadius: "8px",
          padding: "1rem",
          marginBottom: "0.75rem",
          background: "#fafafa",
        }}
      >
        {history.length === 0 && (
          <p style={{ color: "#999", textAlign: "center", marginTop: "2rem" }}>
            Ask an HR question to get started.
          </p>
        )}
        {history.map((msg, i) => (
          <div
            key={i}
            style={{
              display: "flex",
              justifyContent: msg.role === "user" ? "flex-end" : "flex-start",
              marginBottom: "1rem",
            }}
          >
            <div style={{ maxWidth: "70%" }}>
              <div
                style={{
                  display: "inline-block",
                  background: msg.role === "user" ? "#0070f3" : "#e8e8e8",
                  color: msg.role === "user" ? "white" : "black",
                  padding: "0.6rem 1rem",
                  borderRadius: "12px",
                  wordBreak: "break-word",
                }}
              >
                {msg.role === "user" ? (
                  msg.content
                ) : (
                  <ReactMarkdown remarkPlugins={[remarkGfm]}>{msg.content}</ReactMarkdown>
                )}
              </div>
              {msg.citations && <CitationFootnotes citations={msg.citations} />}
            </div>
          </div>
        ))}
        {loading && (
          <div style={{ color: "#999", fontStyle: "italic" }}>Thinking...</div>
        )}
        <div ref={bottomRef} />
      </div>
      <form onSubmit={handleSubmit} style={{ display: "flex", gap: "0.5rem" }}>
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask an HR question..."
          disabled={loading}
          style={{
            flex: 1,
            padding: "0.6rem 0.8rem",
            fontSize: "1rem",
            border: "1px solid #ccc",
            borderRadius: "6px",
          }}
        />
        <button
          type="submit"
          disabled={loading || !input.trim()}
          style={{
            padding: "0.6rem 1.2rem",
            fontSize: "1rem",
            background: "#0070f3",
            color: "white",
            border: "none",
            borderRadius: "6px",
            cursor: loading ? "not-allowed" : "pointer",
          }}
        >
          Send
        </button>
      </form>
    </div>
  );
}
