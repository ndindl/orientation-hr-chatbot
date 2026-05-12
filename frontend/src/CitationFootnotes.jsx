export default function CitationFootnotes({ citations }) {
  if (!citations || citations.length === 0) return null;
  return (
    <div style={{ fontSize: "0.75rem", color: "#666", marginTop: "0.4rem", textAlign: "left" }}>
      {citations.map((c, i) => (
        <div key={i}>
          [{i + 1}] {c.source_file}, p. {c.page_number}
        </div>
      ))}
    </div>
  );
}
