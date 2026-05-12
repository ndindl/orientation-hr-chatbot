export default function LanguageSelector({ language, onChange }) {
  return (
    <div style={{ marginBottom: "1rem" }}>
      <label htmlFor="lang-select" style={{ marginRight: "0.5rem", fontWeight: "bold" }}>
        Language / Idioma:
      </label>
      <select
        id="lang-select"
        value={language}
        onChange={(e) => onChange(e.target.value)}
        style={{ padding: "0.25rem 0.5rem", fontSize: "1rem" }}
      >
        <option value="en">English</option>
        <option value="es">Español</option>
      </select>
    </div>
  );
}
