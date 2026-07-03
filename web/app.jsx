// Diagnostic Assessment Copilot — Dashboard
// Source Serif 4 · Inter · JetBrains Mono · marigold accent · warm paper palette

const DS = {
  paper:       "oklch(0.985 0.005 80)",
  paper2:      "oklch(0.965 0.007 80)",
  paper3:      "oklch(0.935 0.009 80)",
  rule:        "oklch(0.88 0.008 80)",
  ruleStrong:  "oklch(0.78 0.01 80)",
  ink:         "oklch(0.22 0.01 60)",
  ink2:        "oklch(0.38 0.01 60)",
  ink3:        "oklch(0.55 0.01 60)",
  inkMuted:    "oklch(0.68 0.008 60)",
  accent:      "oklch(0.65 0.14 70)",
  accentSoft:  "oklch(0.92 0.05 70)",
  accentInk:   "oklch(0.42 0.14 60)",
  goalFg:      "oklch(0.38 0.09 245)",
  goalBg:      "oklch(0.96 0.02 240)",
  goalBorder:  "oklch(0.78 0.08 240)",
  badFg:       "oklch(0.42 0.10 335)",
  badBg:       "oklch(0.96 0.02 330)",
  badBorder:   "oklch(0.78 0.09 330)",
  matchFg:     "oklch(0.38 0.09 150)",
  matchBg:     "oklch(0.96 0.02 150)",
  matchBorder: "oklch(0.78 0.08 150)",
  partialFg:   "oklch(0.45 0.12 70)",
  partialBg:   "oklch(0.96 0.05 70)",
  mismatchFg:  "oklch(0.55 0.12 25)",
  mismatchBg:  "oklch(0.96 0.04 25)",
  r:           3,
  rlg:         6,
};

const FS = "'Source Serif 4', 'Source Serif Pro', Georgia, serif";
const FN = "'Inter', -apple-system, BlinkMacSystemFont, sans-serif";
const FM = "'JetBrains Mono', ui-monospace, Menlo, monospace";

// "anthropic/claude-opus-4-6" -> "Opus 4.6" (provider stripped, title-cased).
function modelLabel(id) {
  if (!id) return "";
  const name = id.replace(/^[^/]+\//, "").replace(/^claude-/, "");
  const m = name.match(/^(opus|sonnet|haiku)-(\d+)-(\d+)/);
  if (m) return `${m[1][0].toUpperCase()}${m[1].slice(1)} ${m[2]}.${m[3]}`;
  return name;
}

/* ── LaTeX + Figure rendering ──────────────────────────────────── */

function renderLatex(text) {
  if (typeof katex === "undefined") return text;
  const parts = [];
  const regex = /\$\$([\s\S]+?)\$\$|\$([^$\n]+?)\$/g;
  let last = 0;
  let match;
  while ((match = regex.exec(text)) !== null) {
    if (match.index > last) parts.push(text.slice(last, match.index));
    const expr = match[1] || match[2];
    const displayMode = !!match[1];
    try {
      parts.push(katex.renderToString(expr, { throwOnError: false, displayMode }));
    } catch {
      parts.push(match[0]);
    }
    last = regex.lastIndex;
  }
  if (last < text.length) parts.push(text.slice(last));
  return parts.join("");
}

function splitTextAndFigures(text, figureData) {
  if (!figureData || Object.keys(figureData).length === 0) {
    return [{ type: "text", value: text }];
  }
  const regex = /\[FIGURE:([^\]]+)\]/g;
  const segments = [];
  let last = 0;
  let match;
  while ((match = regex.exec(text)) !== null) {
    if (match.index > last) segments.push({ type: "text", value: text.slice(last, match.index) });
    segments.push({ type: "figure", id: match[1] });
    last = regex.lastIndex;
  }
  if (last < text.length) segments.push({ type: "text", value: text.slice(last) });
  return segments;
}

// Truncate a preview without slicing through a `$…$` math span: a dangling `$`
// leaves KaTeX unable to match the delimiter, so it renders as raw literal text
// (e.g. "… standard deviation $\sigma"). Drop the unterminated fragment first.
function truncatePreview(text, n) {
  if (!text || text.length <= n) return text || "";
  let cut = text.slice(0, n);
  const openDollars = (cut.match(/(?<!\\)\$/g) || []).length % 2 === 1;
  if (openDollars) {
    const last = cut.lastIndexOf("$");
    if (last > 0) cut = cut.slice(0, last);
  }
  return cut.trimEnd() + "…";
}

function RichText({ text, figureData, style, as: Tag = "span" }) {
  const segments = splitTextAndFigures(text, figureData);
  return (
    <Tag style={style}>
      {segments.map((seg, i) => {
        if (seg.type === "figure") {
          const data = figureData?.[seg.id];
          if (!data) return <span key={i} style={{ color: DS.inkMuted, fontFamily: FM, fontSize: 11 }}>[Figure {seg.id} not available]</span>;
          return (
            <img key={i} src={`data:image/png;base64,${data}`} alt={seg.id}
              style={{ display: "block", maxWidth: "100%", margin: "12px auto", borderRadius: DS.rlg, border: `1px solid ${DS.rule}` }} />
          );
        }
        const html = renderLatex(seg.value);
        return <span key={i} dangerouslySetInnerHTML={{ __html: html }} />;
      })}
    </Tag>
  );
}

/* ── Primitives ─────────────────────────────────────────────────── */

function FacetTag({ id, selected = true, onClick, tip = true, small = false, dimmed = false }) {
  const facet = FACET_MAP.facets.find(f => f.id === id);
  const isGoal = facet?.type === "goal";
  const [hov, setHov] = React.useState(false);
  return (
    <span onClick={onClick} onMouseEnter={() => setHov(true)} onMouseLeave={() => setHov(false)} style={{
      position: "relative", display: "inline-flex", alignItems: "center",
      padding: small ? "1px 5px" : "2px 7px",
      borderRadius: DS.r,
      fontSize: small ? 10 : 10.5,
      fontWeight: 600, letterSpacing: "0.04em",
      fontFamily: FM, textTransform: "uppercase",
      cursor: onClick ? "pointer" : "default", userSelect: "none",
      opacity: dimmed ? 0.35 : 1,
      background: selected ? (isGoal ? DS.goalBg : DS.badBg) : DS.paper3,
      color:      selected ? (isGoal ? DS.goalFg : DS.badFg) : DS.inkMuted,
      border: `1px solid ${selected ? (isGoal ? DS.goalBorder : DS.badBorder) : DS.ruleStrong}`,
      transition: "all 0.12s",
    }}>
      {id}
      {tip && hov && facet && (
        <span style={{
          position: "absolute", bottom: "calc(100% + 6px)", left: "50%",
          transform: "translateX(-50%)", background: DS.ink, color: DS.paper,
          fontSize: 11, fontFamily: FN, fontWeight: 400, padding: "6px 10px",
          borderRadius: DS.rlg, width: 240, zIndex: 300, lineHeight: 1.5,
          pointerEvents: "none", boxShadow: "0 4px 16px rgba(0,0,0,0.2)", whiteSpace: "normal",
        }}>
          <strong style={{ fontFamily: FM, fontSize: 10 }}>{id}</strong>
          <span style={{ color: selected ? (isGoal ? DS.goalFg : DS.badFg) : DS.inkMuted, marginLeft: 4, fontSize: 10 }}>
            {facet.type === "goal" ? "goal" : "misconception"}
          </span>
          <br />
          {facet.text}
        </span>
      )}
    </span>
  );
}

function TagRow({ tags, small }) {
  return (
    <div style={{ display: "flex", flexWrap: "wrap", gap: 3 }}>
      {tags.map(t => <FacetTag key={t} id={t} small={small} />)}
    </div>
  );
}

function AgreeBadge({ v }) {
  const map = {
    match:    { label: "Match",    fg: DS.matchFg,    bg: DS.matchBg },
    partial:  { label: "Partial",  fg: DS.partialFg,  bg: DS.partialBg },
    mismatch: { label: "Mismatch", fg: DS.mismatchFg, bg: DS.mismatchBg },
  };
  const s = map[v] || map.mismatch;
  return (
    <span style={{
      padding: "2px 7px", borderRadius: DS.r,
      fontSize: 10, fontWeight: 600, letterSpacing: "0.08em",
      textTransform: "uppercase", fontFamily: FM,
      background: s.bg, color: s.fg,
    }}>{s.label}</span>
  );
}

function ScoreBar({ value, color }) {
  return (
    <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
      <div style={{ flex: 1, height: 3, borderRadius: 2, background: DS.paper3 }}>
        <div style={{ width: `${value * 100}%`, height: "100%", borderRadius: 2, background: color || DS.accent, transition: "width 0.4s" }} />
      </div>
      <span style={{ fontSize: 10.5, fontFamily: FM, color: DS.inkMuted, minWidth: 28, textAlign: "right", letterSpacing: "0.04em" }}>
        {Math.round(value * 100)}%
      </span>
    </div>
  );
}

function Rule() { return <div style={{ height: 1, background: DS.rule }} />; }

function MonoLabel({ children, action, style: extraStyle }) {
  return (
    <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 8, ...extraStyle }}>
      <div style={{ fontSize: 10.5, fontWeight: 600, letterSpacing: "0.12em", textTransform: "uppercase", color: DS.ink3, fontFamily: FM }}>
        {children}
      </div>
      {action}
    </div>
  );
}

function Btn({ children, onClick, disabled, variant = "ghost", small, title }) {
  const pad = small ? "4px 9px" : "6px 12px";
  const fz  = small ? 11.5 : 12.5;
  const base = { border: "none", borderRadius: DS.r, fontFamily: FN, fontWeight: 500, cursor: disabled ? "not-allowed" : "pointer", transition: "all 0.15s", fontSize: fz, padding: pad, display: "inline-flex", alignItems: "center", gap: 5, opacity: disabled ? 0.4 : 1 };
  const styles = {
    primary: { ...base, background: DS.ink,  color: DS.paper,  border: `1px solid ${DS.ink}` },
    accent:  { ...base, background: DS.accent, color: "#fff", border: `1px solid ${DS.accent}` },
    ghost:   { ...base, background: DS.paper, color: DS.ink,   border: `1px solid ${DS.ruleStrong}` },
    danger:  { ...base, background: "transparent", color: DS.mismatchFg, border: `1px solid ${DS.mismatchFg}` },
  };
  return <button onClick={disabled ? undefined : onClick} disabled={disabled} style={styles[variant]} title={title}>{children}</button>;
}

function FormField({ label, children }) {
  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 5 }}>
      <label style={{ fontSize: 11.5, color: DS.ink2, fontWeight: 500, fontFamily: FN }}>{label}</label>
      {children}
    </div>
  );
}

function Select({ value, onChange, options }) {
  return (
    <select value={value} onChange={e => onChange(e.target.value)} style={{
      border: `1px solid ${DS.ruleStrong}`, background: DS.paper, borderRadius: DS.r,
      padding: "6px 9px", fontSize: 13, color: DS.ink, fontFamily: FN,
      outline: "none", cursor: "pointer", width: "100%",
    }}>
      {options.map(o => <option key={o.value} value={o.value}>{o.label}</option>)}
    </select>
  );
}

/* ── Facet Map Modal ─────────────────────────────────────────────── */

function FacetMapModal({ onClose }) {
  const goals = FACET_MAP.facets.filter(f => f.type === "goal");
  const bads  = FACET_MAP.facets.filter(f => f.type === "problematic");
  return (
    <div style={{ position: "absolute", inset: 0, background: "rgba(20,18,14,0.45)", backdropFilter: "blur(3px)", zIndex: 400, display: "flex", alignItems: "center", justifyContent: "center", borderRadius: DS.rlg }}
      onClick={e => { if (e.target === e.currentTarget) onClose(); }}>
      <div style={{ background: DS.paper, borderRadius: DS.rlg + 2, width: 640, maxHeight: "82%", display: "flex", flexDirection: "column", boxShadow: "0 20px 60px rgba(0,0,0,0.2)", overflow: "hidden" }}>
        <div style={{ padding: "16px 24px", borderBottom: `1px solid ${DS.rule}`, display: "flex", alignItems: "baseline", justifyContent: "space-between", flexShrink: 0 }}>
          <div>
            <span style={{ fontFamily: FS, fontSize: 20, fontWeight: 500, color: DS.ink, letterSpacing: "-0.01em" }}>Facet Map</span>
            <span style={{ fontFamily: FM, fontSize: 10.5, letterSpacing: "0.08em", textTransform: "uppercase", color: DS.inkMuted, marginLeft: 12 }}>Confidence Intervals</span>
          </div>
          <button onClick={onClose} style={{ background: "none", border: "none", fontSize: 18, cursor: "pointer", color: DS.inkMuted, lineHeight: 1 }}>×</button>
        </div>
        <div style={{ overflowY: "auto", padding: "22px 24px", display: "flex", flexDirection: "column", gap: 24 }}>
          {[{ label: "Goal Facets (A) — what students should understand", items: goals, fg: DS.goalFg, bg: DS.goalBg, border: DS.goalBorder },
            { label: "Problematic Facets (B) — common misconceptions", items: bads, fg: DS.badFg, bg: DS.badBg, border: DS.badBorder }
          ].map(group => (
            <div key={group.label}>
              <div style={{ fontFamily: FM, fontSize: 10.5, fontWeight: 600, letterSpacing: "0.1em", textTransform: "uppercase", color: group.fg, marginBottom: 12 }}>{group.label}</div>
              <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
                {group.items.map(f => (
                  <div key={f.id} style={{ display: "flex", gap: 12, alignItems: "flex-start", padding: "10px 12px", borderRadius: DS.rlg, background: group.bg, border: `1px solid ${group.border}` }}>
                    <FacetTag id={f.id} tip={false} />
                    <span style={{ fontSize: 13.5, lineHeight: 1.6, color: DS.ink, fontFamily: FS, flex: 1 }}>{f.text}</span>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

/* ── API Key Modal ───────────────────────────────────────────────── */

function ApiKeyModal({ onClose, onSaved }) {
  const [key, setKey]         = React.useState("");
  const [persist, setPersist] = React.useState(true);
  const [saving, setSaving]   = React.useState(false);
  const [error, setError]     = React.useState(null);
  const inputRef = React.useRef(null);

  React.useEffect(() => { inputRef.current?.focus(); }, []);

  const handleSubmit = async () => {
    const trimmed = key.trim();
    if (!trimmed || saving) return;
    setError(null);
    setSaving(true);
    try {
      const resp = await fetch("/api/key", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ api_key: trimmed, persist }),
      });
      const j = await resp.json().catch(() => ({}));
      if (!resp.ok) throw new Error(j.error || `Server returned ${resp.status}`);
      onSaved(j);
    } catch (e) {
      setError(e && e.message ? e.message : "Could not save the API key.");
      setSaving(false);
    }
  };

  return (
    <div style={{ position: "absolute", inset: 0, background: "rgba(20,18,14,0.45)", backdropFilter: "blur(3px)", zIndex: 400, display: "flex", alignItems: "center", justifyContent: "center", borderRadius: DS.rlg }}
      onClick={e => { if (e.target === e.currentTarget) onClose(); }}>
      <div style={{ background: DS.paper, borderRadius: DS.rlg + 2, width: 460, display: "flex", flexDirection: "column", boxShadow: "0 20px 60px rgba(0,0,0,0.2)", overflow: "hidden" }}>
        <div style={{ padding: "16px 24px", borderBottom: `1px solid ${DS.rule}`, display: "flex", alignItems: "baseline", justifyContent: "space-between" }}>
          <span style={{ fontFamily: FS, fontSize: 20, fontWeight: 500, color: DS.ink, letterSpacing: "-0.01em" }}>Claude API Key</span>
          <button onClick={onClose} style={{ background: "none", border: "none", fontSize: 18, cursor: "pointer", color: DS.inkMuted, lineHeight: 1 }}>×</button>
        </div>
        <div style={{ padding: "20px 24px", display: "flex", flexDirection: "column", gap: 14 }}>
          <div style={{ fontSize: 13, color: DS.ink2, lineHeight: 1.65, fontFamily: FS }}>
            Generation, evaluation, and simulation all call Claude models, so the
            backend needs an <code style={{ fontFamily: FM, fontSize: 11.5, background: DS.paper3, padding: "1px 4px", borderRadius: 2 }}>ANTHROPIC_API_KEY</code>.
            Paste a key below to set or replace it. You can create one in the <a href="https://console.anthropic.com/settings/keys" target="_blank" rel="noreferrer" style={{ color: DS.accentInk }}>Anthropic Console</a>.
          </div>
          <FormField label="API key">
            <input ref={inputRef} type="password" value={key}
              onChange={e => { setKey(e.target.value); setError(null); }}
              onKeyDown={e => { if (e.key === "Enter") handleSubmit(); }}
              placeholder="sk-ant-…"
              autoComplete="off" spellCheck={false}
              style={{
                border: `1px solid ${error ? DS.mismatchFg : DS.ruleStrong}`, background: DS.paper,
                borderRadius: DS.r, padding: "8px 10px", fontSize: 13, color: DS.ink,
                fontFamily: FM, outline: "none", width: "100%", boxSizing: "border-box",
              }} />
          </FormField>
          <div onClick={() => setPersist(v => !v)} style={{ display: "flex", alignItems: "center", gap: 8, cursor: "pointer", userSelect: "none" }}>
            <div style={{ width: 32, height: 16, borderRadius: 8, position: "relative", background: persist ? DS.accent : DS.ruleStrong, transition: "background 0.15s", flexShrink: 0 }}>
              <div style={{ width: 12, height: 12, borderRadius: 6, background: "#fff", position: "absolute", top: 2, left: persist ? 18 : 2, transition: "left 0.15s" }} />
            </div>
            <span style={{ fontSize: 11.5, fontWeight: 500, color: persist ? DS.accentInk : DS.ink2, fontFamily: FN }}>
              Save to <code style={{ fontFamily: FM, fontSize: 10.5 }}>.env</code> so future sessions don't ask again
            </span>
          </div>
          {error && (
            <div style={{ fontSize: 10.5, color: DS.mismatchFg, fontFamily: FM, letterSpacing: "0.02em", lineHeight: 1.6, padding: "6px 8px", background: DS.mismatchBg, borderRadius: DS.r, border: `1px solid ${DS.mismatchFg}` }}>
              {error}
            </div>
          )}
          <button onClick={handleSubmit} disabled={!key.trim() || saving} style={{
            padding: "8px 0", borderRadius: DS.r,
            background: key.trim() && !saving ? DS.ink : DS.paper3,
            color: key.trim() && !saving ? DS.paper : DS.inkMuted,
            border: `1px solid ${key.trim() && !saving ? DS.ink : DS.ruleStrong}`,
            fontSize: 12.5, fontWeight: 500, cursor: key.trim() && !saving ? "pointer" : "not-allowed",
            fontFamily: FN, transition: "all 0.15s",
          }}>
            {saving ? "Verifying…" : "Verify & Save Key"}
          </button>
          <div style={{ fontSize: 10.5, color: DS.inkMuted, fontFamily: FS, fontStyle: "italic", lineHeight: 1.6 }}>
            The key is sent only to the local dashboard server and verified with a token-free Anthropic API call. It never leaves this machine otherwise.
          </div>
        </div>
      </div>
    </div>
  );
}

/* ── Corpus Evaluation Panel ───────────────────────────────────── */

function CorpusEval({ corpus }) {
  const sd = corpus.semantic_diversity || {};
  const fc = corpus.facet_coverage || {};
  const qm = corpus.facet_qmatrix_diversity || null;
  // Diversity = 1 − similarity. Mean diversity comes from mean similarity; min
  // diversity is the *least distinct* (most similar) pair, i.e. 1 − max
  // similarity — the actionable near-duplicate signal.
  const meanDiv = 1 - (sd.mean_pairwise_similarity ?? 0);
  const minDiv  = 1 - (sd.max_pairwise_similarity ?? 0);
  const qmMeanDiv = qm ? 1 - (qm.mean_pairwise_similarity ?? 0) : null;
  const qmMinDiv  = qm ? 1 - (qm.max_pairwise_similarity ?? 0) : null;
  // Mean over items of each item's closest-expert (max) similarity; falls back
  // to the older mean-based field for results saved before the switch.
  const expertMax = corpus.expert_similarity_max ?? corpus.expert_similarity_mean ?? null;

  const divSub = (mean, min) =>
    `mean div ${mean.toFixed(3)} · min div ${min.toFixed(3)}`;

  const Card = ({ label, value, sub, color, hint }) => (
    <div style={{ flex: 1, minWidth: 150, background: DS.paper, border: `1px solid ${DS.ruleStrong}`, borderRadius: DS.rlg, padding: "16px 20px" }}>
      <MonoLabel>{label}</MonoLabel>
      <div style={{ fontSize: 26, fontWeight: 600, fontFamily: FN, color: color || DS.ink, lineHeight: 1 }}>{value}</div>
      {sub && <div style={{ marginTop: 8, fontSize: 11.5, fontFamily: FM, color: DS.inkMuted }}>{sub}</div>}
      {hint && <div style={{ marginTop: 6, fontSize: 10.5, fontFamily: FS, fontStyle: "italic", color: DS.ink3, lineHeight: 1.5 }}>{hint}</div>}
    </div>
  );

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
      <MonoLabel style={{ marginBottom: 0 }}>Corpus Evaluation</MonoLabel>
      <div style={{ display: "flex", gap: 12, flexWrap: "wrap" }}>
        <Card
          label="Semantic Diversity"
          value={meanDiv.toFixed(2)}
          sub={divSub(meanDiv, minDiv)}
          color={meanDiv >= 0.4 ? DS.matchFg : meanDiv >= 0.25 ? DS.partialFg : DS.mismatchFg}
          hint="Mean pairwise diversity (1 − similarity of stem + permutation-invariant option match). Higher = items are more distinct from each other; min div = the least distinct (most similar) pair."
        />
        {qm != null && (
          <Card
            label="Facet Q-matrix Diversity"
            value={qmMeanDiv.toFixed(2)}
            sub={divSub(qmMeanDiv, qmMinDiv)}
            color={qmMeanDiv >= 0.4 ? DS.matchFg : qmMeanDiv >= 0.25 ? DS.partialFg : DS.mismatchFg}
            hint="Mean pairwise diversity (1 − similarity) of per-item Facet Q-matrices (options × facets, permutation-invariant option match). Higher = items probe more distinct facet structures; min div = the least distinct (most similar) pair."
          />
        )}
        {expertMax != null && (
          <Card
            label="Similarity to Experts"
            value={expertMax.toFixed(2)}
            sub={`${corpus.n_expert_refs || 0} expert items`}
            color={DS.goalFg}
            hint="Mean over items of each item's closest-expert (max) similarity (stem + permutation-invariant option match; higher = closer in style)."
          />
        )}
        <Card
          label="Facet Coverage"
          value={`${fc.covered_facets ?? 0}/${fc.total_facets_in_map ?? 0}`}
          sub={`uniformity ${(fc.uniformity ?? 0).toFixed(3)}`}
          color={(fc.covered_facets === fc.total_facets_in_map) ? DS.matchFg : DS.partialFg}
          hint="Facets touched by ≥1 option. Uniformity (entropy) is 1.0 when spread evenly."
        />
      </div>
    </div>
  );
}

/* ── Facet Coverage Panel ──────────────────────────────────────── */

function FacetCoverage({ items }) {
  const facetCounts = {};
  FACET_MAP.facets.forEach(f => { facetCounts[f.id] = 0; });
  items.forEach(r => {
    (r.item.target_facets || []).forEach(fid => {
      facetCounts[fid] = (facetCounts[fid] || 0) + 1;
    });
  });
  const goals = FACET_MAP.facets.filter(f => f.type === "goal");
  const bads  = FACET_MAP.facets.filter(f => f.type === "problematic");
  const totalFacets = FACET_MAP.facets.length;
  const coveredCount = FACET_MAP.facets.filter(f => facetCounts[f.id] > 0).length;

  return (
    <div style={{ background: DS.paper, border: `1px solid ${DS.ruleStrong}`, borderRadius: DS.rlg, padding: "16px 20px" }}>
      <MonoLabel action={
        <span style={{ fontSize: 10.5, fontFamily: FM, color: coveredCount === totalFacets ? DS.matchFg : DS.partialFg, fontWeight: 600 }}>
          {coveredCount}/{totalFacets}
        </span>
      }>Facet Coverage</MonoLabel>
      <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
        <div>
          <div style={{ fontSize: 10, color: DS.inkMuted, fontFamily: FM, letterSpacing: "0.08em", textTransform: "uppercase", marginBottom: 5 }}>Goal (A)</div>
          <div style={{ display: "flex", flexWrap: "wrap", gap: "10px 14px", paddingTop: 8 }}>
            {goals.map(f => {
              const count = facetCounts[f.id];
              return (
                <span key={f.id} style={{ position: "relative", display: "inline-flex", marginRight: count > 0 ? 4 : 0 }}>
                  <FacetTag id={f.id} selected={count > 0} dimmed={count === 0} />
                  {count > 0 && (
                    <span style={{
                      position: "absolute", top: -7, right: -7,
                      background: DS.goalFg, color: "#fff",
                      fontSize: 8, fontWeight: 700, fontFamily: FM,
                      width: 15, height: 15, borderRadius: 8,
                      display: "flex", alignItems: "center", justifyContent: "center",
                    }}>{count}</span>
                  )}
                </span>
              );
            })}
          </div>
        </div>
        <div>
          <div style={{ fontSize: 10, color: DS.inkMuted, fontFamily: FM, letterSpacing: "0.08em", textTransform: "uppercase", marginBottom: 5 }}>Problematic (B)</div>
          <div style={{ display: "flex", flexWrap: "wrap", gap: "10px 14px", paddingTop: 8 }}>
            {bads.map(f => {
              const count = facetCounts[f.id];
              return (
                <span key={f.id} style={{ position: "relative", display: "inline-flex", marginRight: count > 0 ? 4 : 0 }}>
                  <FacetTag id={f.id} selected={count > 0} dimmed={count === 0} />
                  {count > 0 && (
                    <span style={{
                      position: "absolute", top: -7, right: -7,
                      background: DS.badFg, color: "#fff",
                      fontSize: 8, fontWeight: 700, fontFamily: FM,
                      width: 15, height: 15, borderRadius: 8,
                      display: "flex", alignItems: "center", justifyContent: "center",
                    }}>{count}</span>
                  )}
                </span>
              );
            })}
          </div>
        </div>
      </div>
    </div>
  );
}

/* ── Aggregate bar ───────────────────────────────────────────────── */

function AggregateBar({ items }) {
  const judged = items.filter(r => r.judge_report);
  const avgAgreement  = judged.length ? judged.reduce((s, r) => s + r.judge_report.overall_agreement, 0)  / judged.length : null;
  const avgConfidence = judged.length ? judged.reduce((s, r) => s + r.judge_report.overall_confidence, 0) / judged.length : null;

  const withEval = items.filter(r => r.eval_scores);
  const hasEval = withEval.length > 0;
  const withNatural = withEval.filter(r => r.eval_scores.naturalness_overall != null);
  const correctPct  = hasEval ? Math.round(withEval.filter(r => r.eval_scores.correctness_pass).length / withEval.length * 100) : null;
  const avgNatural  = withNatural.length ? (withNatural.reduce((s, r) => s + r.eval_scores.naturalness_overall, 0) / withNatural.length) : null;
  const avgLatency  = hasEval ? (withEval.reduce((s, r) => s + r.eval_scores.latency_score, 0) / withEval.length) : null;

  const stats = [
    { label: "Items",          value: items.length,                                  color: DS.ink },
  ];
  if (judged.length) {
    stats.push(
      { label: "Avg. Agreement", value: `${Math.round(avgAgreement * 100)}%`,           color: DS.matchFg },
      { label: "Avg. Confidence",value: `${Math.round(avgConfidence * 100)}%`,          color: DS.goalFg },
    );
  }
  if (hasEval) {
    stats.push(
      { label: "Correctness",  value: `${correctPct}%`,                    color: correctPct === 100 ? DS.matchFg : DS.mismatchFg },
    );
    if (avgNatural != null) {
      stats.push({ label: "Naturalness", value: `${avgNatural.toFixed(1)}/5`, color: DS.goalFg });
    }
    stats.push(
      { label: "Facet Latency", value: `${avgLatency.toFixed(1)}/4`,       color: DS.accent },
    );
  }

  return (
    <div style={{ background: DS.paper, border: `1px solid ${DS.ruleStrong}`, borderRadius: DS.rlg, overflow: "hidden" }}>
      <div style={{ padding: "14px 20px", display: "flex", gap: 32, flexWrap: "wrap" }}>
        {stats.map(s => (
          <div key={s.label} style={{ display: "flex", flexDirection: "column", gap: 2 }}>
            <div style={{ fontSize: 22, fontWeight: 600, fontFamily: FN, color: s.color, lineHeight: 1 }}>{s.value}</div>
            <div style={{ fontSize: 10.5, letterSpacing: "0.1em", textTransform: "uppercase", color: DS.inkMuted, fontFamily: FM }}>{s.label}</div>
          </div>
        ))}
      </div>
    </div>
  );
}

/* ── Item list row ───────────────────────────────────────────────── */

function ItemRow({ result, index, selected, onClick }) {
  const { item, judge_report } = result;
  const isAuto = !!result.facet_selection_reasoning;
  const agree = judge_report ? judge_report.overall_agreement : null;
  const agreeColor = agree == null ? DS.inkMuted : agree >= 0.9 ? DS.matchFg : agree >= 0.7 ? DS.partialFg : DS.mismatchFg;
  return (
    <div onClick={onClick} style={{
      padding: "11px 16px", cursor: "pointer",
      background: selected ? DS.accentSoft : "transparent",
      borderLeft: `3px solid ${selected ? DS.accent : "transparent"}`,
      transition: "background 0.1s", display: "flex", flexDirection: "column", gap: 6,
    }}
      onMouseEnter={e => { if (!selected) e.currentTarget.style.background = DS.paper2; }}
      onMouseLeave={e => { if (!selected) e.currentTarget.style.background = "transparent"; }}>
      <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
        <span style={{
          width: 18, height: 18, borderRadius: 2, flexShrink: 0,
          background: selected ? DS.accent : DS.paper3,
          color: selected ? "#fff" : DS.inkMuted,
          display: "flex", alignItems: "center", justifyContent: "center",
          fontSize: 10, fontWeight: 600, fontFamily: FM, letterSpacing: "0.04em",
        }}>{index + 1}</span>
        <div style={{ flex: 1, fontSize: 12.5, lineHeight: 1.4, color: DS.ink2, fontFamily: FS, fontStyle: "italic", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
          <RichText text={truncatePreview(item.stem, 85)} />
        </div>
        {isAuto && (
          <span style={{ fontSize: 9, fontFamily: FM, fontWeight: 600, letterSpacing: "0.06em", textTransform: "uppercase", color: DS.accent, background: DS.accentSoft, padding: "1px 5px", borderRadius: DS.r, flexShrink: 0 }}>auto</span>
        )}
      </div>
      <div style={{ display: "flex", gap: 10, alignItems: "center", paddingLeft: 26 }}>
        {judge_report ? (
          <>
            <span style={{ fontSize: 10.5, fontFamily: FM, color: agreeColor, fontWeight: 600, letterSpacing: "0.04em" }}>{Math.round(agree * 100)}% agree</span>
            <span style={{ fontSize: 10.5, fontFamily: FM, color: DS.inkMuted, letterSpacing: "0.04em" }}>{Math.round(judge_report.overall_confidence * 100)}% conf</span>
          </>
        ) : (
          <span style={{ fontSize: 10.5, fontFamily: FM, color: DS.inkMuted, letterSpacing: "0.04em", fontStyle: "italic" }}>not judged</span>
        )}
        {result.eval_scores && (
          <>
            <span style={{ fontSize: 10.5, fontFamily: FM, color: result.eval_scores.correctness_pass ? DS.matchFg : DS.mismatchFg, fontWeight: 600, letterSpacing: "0.04em" }}>{result.eval_scores.correctness_pass ? "correct" : "wrong"}</span>
            <span style={{ fontSize: 10.5, fontFamily: FM, color: DS.inkMuted, letterSpacing: "0.04em" }}>{result.eval_scores.naturalness_overall != null ? `N${result.eval_scores.naturalness_overall} ` : ""}L{result.eval_scores.latency_score}</span>
          </>
        )}
        <div style={{ flex: 1 }} />
        <TagRow tags={item.target_facets.slice(0, 3)} small />
      </div>
    </div>
  );
}

/* ── Facet Q-matrix (per item) ─────────────────────────────────── */

function FacetQMatrix({ item }) {
  // Columns are the facets this item actually probes (union of the options'
  // tags), ordered as they appear in the facet map so goal facets (A*) sort
  // before problematic ones (B*). Facets tagged by no option are all-zero
  // columns and omitted to keep the grid compact — the corpus metric still
  // scores over the full facet vocabulary.
  const tagged = new Set();
  item.options.forEach(o => (o.facet_tags || []).forEach(t => tagged.add(t)));
  const facets = FACET_MAP.facets.filter(f => tagged.has(f.id));

  if (!facets.length) {
    return (
      <div style={{ background: DS.paper, border: `1px solid ${DS.ruleStrong}`, borderRadius: DS.rlg, padding: "16px 20px" }}>
        <MonoLabel>Facet Q-matrix</MonoLabel>
        <div style={{ fontSize: 12, fontFamily: FS, fontStyle: "italic", color: DS.ink3 }}>No facet tags on this item.</div>
      </div>
    );
  }

  const cell = 26;
  const grid = { display: "grid", gridTemplateColumns: `28px repeat(${facets.length}, ${cell}px)`, gap: 4, alignItems: "center" };

  return (
    <div style={{ background: DS.paper, border: `1px solid ${DS.ruleStrong}`, borderRadius: DS.rlg, padding: "16px 20px" }}>
      <MonoLabel>Facet Q-matrix</MonoLabel>
      <div style={{ overflowX: "auto" }}>
        <div style={{ display: "inline-flex", flexDirection: "column", gap: 4 }}>
          {/* Header: facet ids */}
          <div style={grid}>
            <span />
            {facets.map(f => (
              <div key={f.id} style={{ display: "flex", justifyContent: "center" }}>
                <FacetTag id={f.id} small />
              </div>
            ))}
          </div>
          {/* One row per option */}
          {item.options.map(opt => {
            const tags = new Set(opt.facet_tags || []);
            return (
              <div key={opt.id} style={grid}>
                <span style={{
                  width: 20, height: 20, borderRadius: 2, flexShrink: 0,
                  background: opt.is_correct ? DS.matchFg : DS.paper3,
                  color: opt.is_correct ? "#fff" : DS.inkMuted,
                  display: "flex", alignItems: "center", justifyContent: "center",
                  fontSize: 10, fontWeight: 600, fontFamily: FM, letterSpacing: "0.04em",
                }}>{opt.id}</span>
                {facets.map(f => {
                  const on = tags.has(f.id);
                  const isGoal = f.type === "goal";
                  return (
                    <div key={f.id} style={{ display: "flex", justifyContent: "center" }}>
                      <span title={`${opt.id} ${on ? "probes" : "does not probe"} ${f.id}`} style={{
                        width: cell - 8, height: cell - 8, borderRadius: DS.r,
                        background: on ? (isGoal ? DS.goalFg : DS.badFg) : DS.paper2,
                        border: `1px solid ${on ? (isGoal ? DS.goalFg : DS.badFg) : DS.rule}`,
                      }} />
                    </div>
                  );
                })}
              </div>
            );
          })}
        </div>
      </div>
      <div style={{ marginTop: 8, fontSize: 10.5, fontFamily: FS, fontStyle: "italic", color: DS.ink3, lineHeight: 1.5 }}>
        Rows = options, columns = facets probed by this item ({facets.length} of {FACET_MAP.facets.length}; all-zero facets omitted). Filled cell = option carries that facet tag.
      </div>
    </div>
  );
}

/* ── Item detail ──────────────────────────────────────────────────── */

function ItemDetail({ result, onSimulate, simulating }) {
  const [tab, setTab] = React.useState("item");
  // Key the reset on the item identity, not the result object: simulation /
  // evaluation frames replace the object and must not yank the tab back.
  const itemKey = result.created_at || result.item.stem;
  React.useEffect(() => { setTab("item"); }, [itemKey]);
  // If judging was skipped, never land on the Judge Report tab.
  React.useEffect(() => { if (!result.judge_report && tab === "judge") setTab("item"); }, [result.judge_report, tab]);

  const item = result.item;
  const jr   = result.judge_report;

  const tabStyle = active => ({
    padding: "9px 16px", border: "none", background: "transparent",
    borderBottom: `2px solid ${active ? DS.accent : "transparent"}`,
    color: active ? DS.accentInk : DS.inkMuted,
    fontFamily: FM, fontSize: 10.5, fontWeight: 600, letterSpacing: "0.06em",
    textTransform: "uppercase", cursor: "pointer", marginBottom: -1,
  });

  return (
    <div style={{ display: "flex", flexDirection: "column", height: "100%" }}>
      <div style={{ display: "flex", borderBottom: `1px solid ${DS.rule}`, padding: "0 20px", flexShrink: 0, background: DS.paper, alignItems: "center" }}>
        <button style={tabStyle(tab === "item")} onClick={() => setTab("item")}>Generated Item</button>
        {jr && <button style={tabStyle(tab === "judge")} onClick={() => setTab("judge")}>Judge Report</button>}
        {result.eval_scores && <button style={tabStyle(tab === "eval")} onClick={() => setTab("eval")}>Evaluation</button>}
        <button style={tabStyle(tab === "sim")} onClick={() => setTab("sim")}>
          Students{result.simulation?.runs?.length ? ` (${new Set(result.simulation.runs.map(f => f.attempt.persona_key)).size})` : ""}
        </button>
        <div style={{ flex: 1 }} />
        {jr && (
          <div style={{ display: "flex", alignItems: "center", gap: 10, paddingRight: 4 }}>
            <span style={{ fontSize: 10.5, fontFamily: FM, color: DS.inkMuted, letterSpacing: "0.04em" }}>
              agree <strong style={{ color: DS.matchFg }}>{Math.round(jr.overall_agreement * 100)}%</strong>
            </span>
            <span style={{ fontSize: 10.5, fontFamily: FM, color: DS.inkMuted, letterSpacing: "0.04em" }}>
              conf <strong style={{ color: DS.ink }}>{Math.round(jr.overall_confidence * 100)}%</strong>
            </span>
          </div>
        )}
      </div>

      <div style={{ flex: 1, overflowY: "auto", padding: "20px 22px", display: "flex", flexDirection: "column", gap: 14, background: DS.paper2 }}>
        {tab === "item" && (
          <>
            {/* Stem */}
            <div style={{ background: DS.paper, border: `1px solid ${DS.ruleStrong}`, borderRadius: DS.rlg, padding: "18px 20px" }}>
              <MonoLabel action={<TagRow tags={item.target_facets} />}>Stem</MonoLabel>
              <RichText as="p" text={item.stem} figureData={result.figure_data} style={{ fontSize: 16, lineHeight: 1.7, color: DS.ink, fontFamily: FS, margin: 0 }} />
            </div>

            {/* Options */}
            <div style={{ background: DS.paper, border: `1px solid ${DS.ruleStrong}`, borderRadius: DS.rlg, padding: "16px 20px" }}>
              <MonoLabel>Options</MonoLabel>
              <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
                {item.options.map(opt => (
                  <div key={opt.id} style={{
                    border: `1px solid ${opt.is_correct ? DS.matchBorder : DS.rule}`,
                    borderLeft: `3px solid ${opt.is_correct ? DS.matchFg : DS.rule}`,
                    borderRadius: DS.rlg, padding: "11px 13px",
                    background: opt.is_correct ? DS.matchBg : DS.paper,
                    display: "flex", flexDirection: "column", gap: 8,
                  }}>
                    <div style={{ display: "flex", alignItems: "flex-start", gap: 10 }}>
                      <span style={{
                        width: 20, height: 20, borderRadius: 2, flexShrink: 0,
                        background: opt.is_correct ? DS.matchFg : DS.paper3,
                        color: opt.is_correct ? "#fff" : DS.inkMuted,
                        display: "flex", alignItems: "center", justifyContent: "center",
                        fontSize: 10, fontWeight: 600, fontFamily: FM, letterSpacing: "0.04em",
                      }}>{opt.id}</span>
                      <RichText text={opt.text} figureData={result.figure_data} style={{ fontSize: 14, lineHeight: 1.65, color: DS.ink, fontFamily: FS }} />
                    </div>
                    <div style={{ paddingLeft: 30, display: "flex", gap: 6, flexWrap: "wrap", alignItems: "flex-start" }}>
                      <TagRow tags={opt.facet_tags} />
                      <span style={{ fontSize: 11.5, color: DS.ink3, fontFamily: FS, fontStyle: "italic", lineHeight: 1.5 }}>— {opt.rationale}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Facet Q-matrix */}
            <FacetQMatrix item={item} />

            <div style={{ background: DS.paper, border: `1px solid ${DS.ruleStrong}`, borderRadius: DS.rlg, padding: "14px 20px" }}>
              <MonoLabel>Explanation</MonoLabel>
              <RichText as="p" text={item.explanation} figureData={result.figure_data} style={{ margin: 0, fontSize: 13.5, lineHeight: 1.75, color: DS.ink2, fontFamily: FS, fontStyle: "italic" }} />
            </div>
          </>
        )}

        {tab === "judge" && (
          <>
            <div style={{ background: DS.paper, border: `1px solid ${DS.ruleStrong}`, borderRadius: DS.rlg, padding: "16px 20px", display: "flex", gap: 28, flexWrap: "wrap" }}>
              <div>
                <MonoLabel>Agreement</MonoLabel>
                <div style={{ fontSize: 26, fontWeight: 600, fontFamily: FN, color: DS.matchFg, lineHeight: 1 }}>{Math.round(jr.overall_agreement * 100)}%</div>
              </div>
              <div>
                <MonoLabel>Confidence</MonoLabel>
                <div style={{ fontSize: 26, fontWeight: 600, fontFamily: FN, color: DS.ink, lineHeight: 1 }}>{Math.round(jr.overall_confidence * 100)}%</div>
              </div>
            </div>

            <div style={{ background: DS.paper, border: `1px solid ${DS.ruleStrong}`, borderRadius: DS.rlg, padding: "16px 20px", display: "flex", flexDirection: "column", gap: 14 }}>
              <MonoLabel>Option Assessments</MonoLabel>
              {jr.option_assessments.map((oa, i) => {
                const opt = result.item.options.find(o => o.id === oa.option_id);
                return (
                  <React.Fragment key={oa.option_id}>
                    {i > 0 && <Rule />}
                    <div style={{ display: "flex", gap: 12, alignItems: "flex-start", paddingTop: i > 0 ? 14 : 0 }}>
                      <span style={{ width: 20, height: 20, borderRadius: 2, flexShrink: 0, background: DS.paper3, color: DS.inkMuted, display: "flex", alignItems: "center", justifyContent: "center", fontSize: 10, fontWeight: 600, fontFamily: FM, letterSpacing: "0.04em" }}>{oa.option_id}</span>
                      <div style={{ flex: 1, display: "flex", flexDirection: "column", gap: 7 }}>
                        <RichText as="p" text={opt?.text || ""} figureData={result.figure_data} style={{ margin: 0, fontSize: 13.5, color: DS.ink2, fontFamily: FS, fontStyle: "italic", lineHeight: 1.5 }} />
                        <div style={{ display: "flex", gap: 8, flexWrap: "wrap", alignItems: "center" }}>
                          <AgreeBadge v={oa.agreement} />
                          <div style={{ display: "flex", gap: 5, alignItems: "center" }}>
                            <span style={{ fontSize: 10.5, color: DS.inkMuted, fontFamily: FM, letterSpacing: "0.04em", textTransform: "uppercase" }}>Gen</span>
                            <TagRow tags={oa.generator_tags} small />
                          </div>
                          <div style={{ display: "flex", gap: 5, alignItems: "center" }}>
                            <span style={{ fontSize: 10.5, color: DS.inkMuted, fontFamily: FM, letterSpacing: "0.04em", textTransform: "uppercase" }}>Judge</span>
                            <TagRow tags={oa.judge_tags} small />
                          </div>
                        </div>
                        <ScoreBar value={oa.confidence} color={oa.agreement === "match" ? DS.matchFg : oa.agreement === "partial" ? DS.partialFg : DS.mismatchFg} />
                        <p style={{ margin: 0, fontSize: 12, color: DS.ink3, fontFamily: FS, fontStyle: "italic", lineHeight: 1.6, paddingLeft: 10, borderLeft: `2px solid ${DS.rule}` }}>{oa.reasoning}</p>
                      </div>
                    </div>
                  </React.Fragment>
                );
              })}
            </div>
          </>
        )}

        {tab === "sim" && (
          <StudentSimPanel result={result} onSimulate={onSimulate} simulating={simulating} />
        )}

        {tab === "eval" && result.eval_scores && (() => {
          const ev = result.eval_scores;
          const bucketColor = b => b === "highly_latent" ? DS.matchFg : b === "latent" ? DS.goalFg : b === "surface" ? DS.partialFg : DS.mismatchFg;
          const bucketLabel = b => b === "highly_latent" ? "Highly Latent" : b === "latent" ? "Latent" : b === "surface" ? "Surface" : "Paraphrase";
          return (
            <>
              {/* Score cards */}
              <div style={{ display: "flex", gap: 12, flexWrap: "wrap" }}>
                <div style={{ flex: 1, minWidth: 140, background: DS.paper, border: `1px solid ${DS.ruleStrong}`, borderRadius: DS.rlg, padding: "16px 20px" }}>
                  <MonoLabel>Correctness</MonoLabel>
                  <div style={{ fontSize: 26, fontWeight: 600, fontFamily: FN, color: ev.correctness_pass ? DS.matchFg : DS.mismatchFg, lineHeight: 1 }}>
                    {ev.correctness_pass ? "Pass" : "Fail"}
                  </div>
                  {ev.correctness_flagged_distractors.length > 0 && (
                    <div style={{ marginTop: 8, fontSize: 11.5, color: DS.mismatchFg, fontFamily: FM }}>
                      Flagged: {ev.correctness_flagged_distractors.join(", ")}
                    </div>
                  )}
                </div>
                {ev.naturalness_overall != null && (
                <div style={{ flex: 1, minWidth: 140, background: DS.paper, border: `1px solid ${DS.ruleStrong}`, borderRadius: DS.rlg, padding: "16px 20px" }}>
                  <MonoLabel>Naturalness</MonoLabel>
                  <div style={{ fontSize: 26, fontWeight: 600, fontFamily: FN, color: DS.goalFg, lineHeight: 1 }}>{ev.naturalness_overall}/5</div>
                  <div style={{ marginTop: 8, display: "flex", gap: 16 }}>
                    <span style={{ fontSize: 11.5, fontFamily: FM, color: DS.inkMuted }}>Stem: {ev.naturalness_stem}</span>
                    <span style={{ fontSize: 11.5, fontFamily: FM, color: DS.inkMuted }}>Options: {ev.naturalness_options}</span>
                  </div>
                </div>
                )}
                {result.similarity_with_experts && (
                <div style={{ flex: 1, minWidth: 140, background: DS.paper, border: `1px solid ${DS.ruleStrong}`, borderRadius: DS.rlg, padding: "16px 20px" }}>
                  <MonoLabel>Expert Similarity</MonoLabel>
                  <div style={{ fontSize: 26, fontWeight: 600, fontFamily: FN, color: DS.goalFg, lineHeight: 1 }}>{result.similarity_with_experts.max_similarity.toFixed(2)}</div>
                  <div style={{ marginTop: 8, display: "flex", gap: 16 }}>
                    <span style={{ fontSize: 11.5, fontFamily: FM, color: DS.inkMuted }}>≈ {result.similarity_with_experts.most_similar_to}</span>
                  </div>
                </div>
                )}
                <div style={{ flex: 1, minWidth: 140, background: DS.paper, border: `1px solid ${DS.ruleStrong}`, borderRadius: DS.rlg, padding: "16px 20px" }}>
                  <MonoLabel>Facet Latency</MonoLabel>
                  <div style={{ fontSize: 26, fontWeight: 600, fontFamily: FN, color: bucketColor(ev.latency_bucket), lineHeight: 1 }}>{ev.latency_score}/4</div>
                  <div style={{ marginTop: 8 }}>
                    <span style={{
                      padding: "2px 7px", borderRadius: DS.r,
                      fontSize: 10, fontWeight: 600, letterSpacing: "0.08em",
                      textTransform: "uppercase", fontFamily: FM,
                      background: DS.paper3, color: bucketColor(ev.latency_bucket),
                    }}>{bucketLabel(ev.latency_bucket)}</span>
                    <span style={{ fontSize: 11.5, fontFamily: FM, color: DS.inkMuted, marginLeft: 8 }}>sim={ev.latency_similarity.toFixed(3)}</span>
                  </div>
                </div>
                {ev.figure_spoiler != null && (
                <div style={{ flex: 1, minWidth: 140, background: DS.paper, border: `1px solid ${DS.ruleStrong}`, borderRadius: DS.rlg, padding: "16px 20px" }}>
                  <MonoLabel>Figure Spoiler</MonoLabel>
                  <div style={{ fontSize: 26, fontWeight: 600, fontFamily: FN, color: ev.figure_spoiler ? DS.mismatchFg : DS.matchFg, lineHeight: 1 }}>
                    {ev.figure_spoiler ? "Gives away" : "Clean"}
                  </div>
                  {ev.figure_spoiler && ev.figure_spoiler_leaked_via && (
                    <div style={{ marginTop: 8, fontSize: 11.5, color: DS.mismatchFg, fontFamily: FM }}>
                      via {ev.figure_spoiler_leaked_via}
                    </div>
                  )}
                </div>
                )}
              </div>

              {/* Per-option latency */}
              {ev.latency_option_details && ev.latency_option_details.length > 0 && (
                <div style={{ background: DS.paper, border: `1px solid ${DS.ruleStrong}`, borderRadius: DS.rlg, padding: "16px 20px" }}>
                  <MonoLabel>Per-Option Facet Latency</MonoLabel>
                  <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
                    {ev.latency_option_details.map((od, i) => {
                      const opt = result.item.options.find(o => o.id === od.option_id);
                      return (
                        <React.Fragment key={od.option_id}>
                          {i > 0 && <Rule />}
                          <div style={{ display: "flex", gap: 12, alignItems: "flex-start", paddingTop: i > 0 ? 10 : 0 }}>
                            <span style={{ width: 20, height: 20, borderRadius: 2, flexShrink: 0, background: DS.paper3, color: DS.inkMuted, display: "flex", alignItems: "center", justifyContent: "center", fontSize: 10, fontWeight: 600, fontFamily: FM }}>{od.option_id}</span>
                            <div style={{ flex: 1, display: "flex", flexDirection: "column", gap: 6 }}>
                              <RichText as="p" text={opt?.text || ""} figureData={result.figure_data} style={{ margin: 0, fontSize: 13, color: DS.ink2, fontFamily: FS, fontStyle: "italic", lineHeight: 1.5 }} />
                              <div style={{ display: "flex", gap: 8, alignItems: "center" }}>
                                <span style={{
                                  padding: "2px 7px", borderRadius: DS.r,
                                  fontSize: 10, fontWeight: 600, letterSpacing: "0.08em",
                                  textTransform: "uppercase", fontFamily: FM,
                                  background: DS.paper3, color: bucketColor(od.bucket),
                                }}>{od.score}/4 · {bucketLabel(od.bucket)}</span>
                                <span style={{ fontSize: 10.5, fontFamily: FM, color: DS.inkMuted }}>sim={od.similarity.toFixed(3)}</span>
                                <TagRow tags={od.facet_tags} small />
                              </div>
                              <ScoreBar value={1 - od.similarity} color={bucketColor(od.bucket)} />
                            </div>
                          </div>
                        </React.Fragment>
                      );
                    })}
                  </div>
                </div>
              )}
            </>
          );
        })()}
      </div>
    </div>
  );
}

/* ── Student Simulator panel ─────────────────────────────────────── */

function SimBadge({ ok, yes, no }) {
  return (
    <span style={{
      padding: "2px 8px", borderRadius: DS.r, fontSize: 10, fontWeight: 600,
      letterSpacing: "0.06em", textTransform: "uppercase", fontFamily: FM,
      background: ok ? DS.matchBg : DS.mismatchBg, color: ok ? DS.matchFg : DS.mismatchFg,
    }}>{ok ? yes : no}</span>
  );
}

function SimOptionChip({ id, isTarget, isCorrect, isControl }) {
  // Target options use the misconception palette for persona runs (the option
  // the misconception is keyed to) and green for the control (the key).
  const bg = isTarget ? (isControl ? DS.matchBg : DS.badBg)
           : isCorrect ? DS.matchBg : DS.paper3;
  const fg = isTarget ? (isControl ? DS.matchFg : DS.badFg)
           : isCorrect ? DS.matchFg : DS.ink2;
  return (
    <span style={{
      padding: "2px 8px", borderRadius: DS.r, fontSize: 11, fontWeight: 600,
      fontFamily: FM, letterSpacing: "0.04em", background: bg, color: fg,
      border: `1px solid ${isTarget || isCorrect ? fg : DS.ruleStrong}`,
    }}>{id}</span>
  );
}

function SimSampleRow({ frame, isControl, correctIds, figureData, divider, showJudgeReasoning }) {
  const a = frame.attempt;
  const targets = frame.target_option_ids || [];
  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 9, paddingTop: divider ? 12 : 0, borderTop: divider ? `1px solid ${DS.rule}` : "none" }}>
      <div style={{ display: "flex", gap: 8, alignItems: "center", flexWrap: "wrap" }}>
        <span style={{ fontSize: 10.5, fontFamily: FM, color: DS.inkMuted, letterSpacing: "0.06em", textTransform: "uppercase" }}>picked</span>
        {frame.selected_ids.length > 0
          ? frame.selected_ids.map(id => (
              <SimOptionChip key={id} id={id} isTarget={targets.includes(id)}
                isCorrect={correctIds.includes(id)} isControl={isControl} />
            ))
          : <span style={{ fontSize: 11.5, fontFamily: FM, color: DS.inkMuted, fontStyle: "italic" }}>no option</span>}
        {a.fallback_used && (
          <span style={{ fontSize: 10.5, fontFamily: FM, color: DS.partialFg, letterSpacing: "0.02em" }}>
            via select fallback — open answer matched no option
          </span>
        )}
        <div style={{ flex: 1 }} />
        <SimBadge ok={frame.hit}
          yes={isControl ? "answered correctly" : "picked target"}
          no={isControl ? "answered incorrectly" : "missed target"} />
      </div>

      {/* Student prose is free-form natural language (often with literal "$"
          dollar amounts), so render it verbatim — NOT through the LaTeX
          renderer, which would parse $…$ pairs as math and mangle the text. */}
      <div style={{ paddingLeft: 10, borderLeft: `2px solid ${DS.rule}`, display: "flex", flexDirection: "column", gap: 6 }}>
        <p style={{ margin: 0, fontSize: 13, lineHeight: 1.7, color: DS.ink2, fontFamily: FS, fontStyle: "italic", whiteSpace: "pre-wrap" }}>
          {a.student_reasoning}
        </p>
        <div style={{ fontSize: 12.5, color: DS.ink, fontFamily: FS, whiteSpace: "pre-wrap" }}>
          <span style={{ fontSize: 10.5, fontFamily: FM, color: DS.inkMuted, letterSpacing: "0.06em", textTransform: "uppercase", marginRight: 6 }}>final answer</span>
          {a.student_answer}
        </div>
        {a.fallback_used && a.fallback_answer && (
          <div style={{ fontSize: 12, color: DS.ink3, fontFamily: FS, whiteSpace: "pre-wrap" }}>
            <span style={{ fontSize: 10.5, fontFamily: FM, color: DS.partialFg, letterSpacing: "0.06em", textTransform: "uppercase", marginRight: 6 }}>select-mode pick</span>
            {a.fallback_answer}
          </div>
        )}
      </div>

      {!isControl && a.exhibited_facet_ids != null && (() => {
        // Did the judge infer (at least) the misconception(s) this distractor
        // is keyed to from the student's reasoning?
        const selected = (a.persona_facets || []).filter(
          id => FACET_MAP.facets.find(f => f.id === id)?.type === "problematic");
        const inferred = a.exhibited_facet_ids;
        const matches = selected.length > 0 && selected.every(id => inferred.includes(id));
        return (
          <div style={{ display: "flex", gap: 7, alignItems: "flex-start", flexWrap: "wrap" }}>
            <span style={{ fontSize: 10.5, fontFamily: FM, color: DS.inkMuted, letterSpacing: "0.06em", textTransform: "uppercase", marginTop: 2 }}>
              facet inferred from student's reasoning:
            </span>
            {inferred.length > 0
              ? <TagRow tags={inferred} small />
              : <span style={{ fontSize: 11.5, fontFamily: FM, color: a.judged_reasoning_correct ? DS.matchFg : DS.inkMuted }}>
                  {a.judged_reasoning_correct ? "none — reasoning judged sound" : "none"}
                </span>}
            <div style={{ flex: 1 }} />
            <SimBadge ok={matches}
              yes="matches selected facet(s)" no="differs from selected" />
            {showJudgeReasoning && a.lineup_judge_reasoning && (
              <span style={{ flexBasis: "100%", fontSize: 11.5, color: DS.ink3, fontFamily: FS, fontStyle: "italic", lineHeight: 1.55 }}>
                {a.lineup_judge_reasoning}
              </span>
            )}
          </div>
        );
      })()}
    </div>
  );
}

function SimPersonaCard({ personaKey, frames, result, showJudgeReasoning }) {
  const isControl = personaKey === "control";
  const sorted = [...frames].sort((a, b) => a.attempt.sample_index - b.attempt.sample_index);
  const facets = sorted[0].attempt.persona_facets || [];
  const badFacets  = facets.filter(id => FACET_MAP.facets.find(f => f.id === id)?.type !== "goal");
  const goalFacets = facets.filter(id => FACET_MAP.facets.find(f => f.id === id)?.type === "goal");
  const targets = sorted[0].target_option_ids || [];
  const correctIds = result.item.options.filter(o => o.is_correct).map(o => o.id);
  return (
    <div style={{ background: DS.paper, border: `1px solid ${DS.ruleStrong}`, borderRadius: DS.rlg, padding: "16px 20px", display: "flex", flexDirection: "column", gap: 12 }}>
      <div style={{ display: "flex", alignItems: "center", gap: 9, flexWrap: "wrap" }}>
        <span style={{ fontSize: 11, fontWeight: 600, fontFamily: FM, letterSpacing: "0.08em", textTransform: "uppercase", color: isControl ? DS.goalFg : DS.badFg }}>
          {isControl ? "Control student — no misconceptions" : "Student holding"}
        </span>
        {!isControl && <TagRow tags={badFacets} />}
        {!isControl && goalFacets.length > 0 && (
          <>
            <span style={{ fontSize: 11, fontWeight: 600, fontFamily: FM, letterSpacing: "0.08em", textTransform: "uppercase", color: DS.goalFg }}>
              · correctly understands
            </span>
            <TagRow tags={goalFacets} />
          </>
        )}
        <span style={{ fontSize: 10.5, fontFamily: FM, color: DS.inkMuted, letterSpacing: "0.03em" }}>
          {isControl
            ? `correct answer: ${targets.join(", ") || "—"}`
            : `keyed option${targets.length > 1 ? "s" : ""}: ${targets.join(", ") || "—"}`}
        </span>
      </div>
      {sorted.map((f, i) => (
        <SimSampleRow key={i} frame={f} isControl={isControl}
          correctIds={correctIds} figureData={result.figure_data} divider={i > 0}
          showJudgeReasoning={showJudgeReasoning} />
      ))}
    </div>
  );
}

function StudentSimPanel({ result, onSimulate, simulating }) {
  const sim = result.simulation;
  // Blind-judge reasoning is verbose; hidden by default, toggled here.
  const [showJudgeReasoning, setShowJudgeReasoning] = React.useState(false);

  if (!sim) {
    return (
      <div style={{ background: DS.paper, border: `1px solid ${DS.ruleStrong}`, borderRadius: DS.rlg, padding: "32px 28px", textAlign: "center" }}>
        <div style={{ fontFamily: FS, fontSize: 17, fontStyle: "italic", color: DS.ink2, marginBottom: 8 }}>
          Simulate students on this item
        </div>
        <p style={{ margin: "0 auto 18px", maxWidth: 460, fontSize: 12.5, lineHeight: 1.7, color: DS.ink3, fontFamily: FS }}>
          A control student (correct understanding) and one simulated student per
          misconception keyed to this item's distractors each answer the question
          open-ended. Their free answers are blindly mapped onto the options, and the
          misconception inferred from each student's reasoning is checked against the
          one its distractor is keyed to. Only distractors the judge agrees are keyed
          to their misconception are simulated.
        </p>
        <Btn variant="accent" onClick={onSimulate} disabled={simulating}>
          {simulating ? "A simulation is running…" : "Run Student Simulator"}
        </Btn>
      </div>
    );
  }

  if (sim.skipped) {
    return (
      <div style={{ background: DS.paper, border: `1px solid ${DS.ruleStrong}`, borderRadius: DS.rlg, padding: "24px 28px", textAlign: "center", fontSize: 13, color: DS.ink3, fontFamily: FS, fontStyle: "italic" }}>
        {sim.skipped}
      </div>
    );
  }

  const byPersona = {};
  (sim.runs || []).forEach(f => {
    (byPersona[f.attempt.persona_key] = byPersona[f.attempt.persona_key] || []).push(f);
  });
  const keys = Object.keys(byPersona).sort((a, b) =>
    a === "control" ? -1 : b === "control" ? 1 : a.localeCompare(b));

  return (
    <>
      <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
        <MonoLabel style={{ marginBottom: 0 }}>Student Simulator</MonoLabel>
        {sim.running && (
          <span style={{ fontSize: 11, fontFamily: FM, color: DS.accentInk, letterSpacing: "0.03em" }}>
            running — students answer one at a time…
          </span>
        )}
        <div style={{ flex: 1 }} />
        <button onClick={() => setShowJudgeReasoning(v => !v)} style={{
          background: "none", border: "none", cursor: "pointer", fontFamily: FM,
          fontSize: 10.5, fontWeight: 600, letterSpacing: "0.04em", textTransform: "uppercase",
          color: showJudgeReasoning ? DS.accentInk : DS.inkMuted,
        }}>
          {showJudgeReasoning ? "Hide judge reasoning" : "Show judge reasoning"}
        </button>
        {!sim.running && (
          <Btn small onClick={onSimulate} disabled={simulating}>Re-run</Btn>
        )}
      </div>
      {sim.note && (
        <div style={{ fontSize: 11.5, fontFamily: FS, fontStyle: "italic", color: DS.partialFg, lineHeight: 1.5, padding: "8px 12px", background: DS.partialBg, borderRadius: DS.rlg, border: `1px solid ${DS.partialFg}` }}>
          {sim.note}
        </div>
      )}
      {keys.length === 0 && sim.running && (
        <div style={{ background: DS.paper, border: `1px solid ${DS.ruleStrong}`, borderRadius: DS.rlg, padding: "24px 28px", textAlign: "center", fontSize: 13, color: DS.ink3, fontFamily: FS, fontStyle: "italic" }}>
          Waiting for the first student to finish…
        </div>
      )}
      {keys.map(k => (
        <SimPersonaCard key={k} personaKey={k} frames={byPersona[k]} result={result}
          showJudgeReasoning={showJudgeReasoning} />
      ))}
    </>
  );
}

/* ── Simulator aggregates ────────────────────────────────────────── */

function computeSimStats(results) {
  let matchedHits = 0, matchedTotal = 0;
  let controlOk = 0, controlTotal = 0;
  let lineupOk = 0, lineupTotal = 0;
  const gaps = [];

  const perItem = results.map(r => {
    const runs = r.simulation?.runs || [];
    if (!runs.length) return null;
    const byPersona = {};
    runs.forEach(f => {
      (byPersona[f.attempt.persona_key] = byPersona[f.attempt.persona_key] || []).push(f);
    });
    const itemGaps = [];
    let itemControlOk = null;
    Object.keys(byPersona).forEach(key => {
      const frames = byPersona[key];
      if (key === "control") {
        frames.forEach(f => { controlTotal++; if (f.hit) controlOk++; });
        itemControlOk = frames.every(f => f.hit);
        return;
      }
      let hits = 0;
      frames.forEach(f => {
        matchedTotal++;
        if (f.hit) { matchedHits++; hits++; }
        if (f.attempt.exhibited_facet_ids != null) {
          lineupTotal++;
          const badIds = (f.attempt.persona_facets || []).filter(id =>
            FACET_MAP.facets.find(x => x.id === id)?.type === "problematic");
          if (badIds.every(id => f.attempt.exhibited_facet_ids.includes(id))) lineupOk++;
        }
      });
      // Selection gap for this persona's keyed option(s): matched rate minus
      // the rate at which every OTHER student on the item lands there.
      const targets = frames[0].target_option_ids || [];
      const others = runs.filter(f => f.attempt.persona_key !== key);
      const matchedRate = hits / frames.length;
      const othersRate = others.length
        ? others.filter(f => targets.some(t => (f.selected_ids || []).includes(t))).length / others.length
        : 0;
      itemGaps.push(matchedRate - othersRate);
    });
    const gap = itemGaps.length
      ? itemGaps.reduce((s, x) => s + x, 0) / itemGaps.length : null;
    if (gap != null) gaps.push(gap);
    return { gap, controlOk: itemControlOk };
  });

  if (!perItem.some(Boolean)) return null;
  return {
    perItem,
    nItems: perItem.filter(Boolean).length,
    meanGap: gaps.length ? gaps.reduce((s, x) => s + x, 0) / gaps.length : null,
    matchedRate: matchedTotal ? matchedHits / matchedTotal : null,
    controlRate: controlTotal ? controlOk / controlTotal : null,
    lineupRate: lineupTotal ? lineupOk / lineupTotal : null,
  };
}

function SimAggregate({ stats }) {
  const pct = v => v == null ? "—" : `${Math.round(v * 100)}%`;
  const signedPct = v => v == null ? "—" : `${v > 0 ? "+" : ""}${Math.round(v * 100)}%`;
  const gapColor   = v => v == null ? DS.inkMuted : v >= 0.5 ? DS.matchFg : v > 0 ? DS.partialFg : DS.mismatchFg;
  const rateColor  = (v, hi, mid) => v == null ? DS.inkMuted : v >= hi ? DS.matchFg : v >= mid ? DS.partialFg : DS.mismatchFg;

  const Card = ({ label, value, color, hint }) => (
    <div style={{ flex: 1, minWidth: 150, background: DS.paper, border: `1px solid ${DS.ruleStrong}`, borderRadius: DS.rlg, padding: "16px 20px" }}>
      <MonoLabel>{label}</MonoLabel>
      <div style={{ fontSize: 26, fontWeight: 600, fontFamily: FN, color, lineHeight: 1 }}>{value}</div>
      {hint && <div style={{ marginTop: 6, fontSize: 10.5, fontFamily: FS, fontStyle: "italic", color: DS.ink3, lineHeight: 1.5 }}>{hint}</div>}
    </div>
  );

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
      <MonoLabel style={{ marginBottom: 0 }} action={
        <span style={{ fontSize: 10, fontFamily: FM, color: DS.inkMuted, letterSpacing: "0.03em", textTransform: "none" }}>
          {stats.nItems} item{stats.nItems > 1 ? "s" : ""} simulated · 1 sample per student — gaps are coarse, read in aggregate
        </span>
      }>Student Simulator</MonoLabel>
      <div style={{ display: "flex", gap: 12, flexWrap: "wrap" }}>
        <Card
          label="Selection Gap"
          value={signedPct(stats.meanGap)}
          color={gapColor(stats.meanGap)}
          hint="How much more often a misconception's own student picks its keyed option than the other students do. The discrimination signal: high = distractors attract their misconception and only theirs."
        />
        <Card
          label="Misconception Hit"
          value={pct(stats.matchedRate)}
          color={rateColor(stats.matchedRate, 0.6, 0.3)}
          hint="Raw rate: the matched student picked its keyed option. Can be high even when distractors also attract the wrong students — read alongside the gap."
        />
        <Card
          label="Control Accuracy"
          value={pct(stats.controlRate)}
          color={rateColor(stats.controlRate, 0.999, 0.75)}
          hint="The no-misconception student lands exactly on the answer key. A guardrail: if controls miss, item answers (or the answer mapping) are suspect and the gap shouldn't be trusted."
        />
        <Card
          label="Judge Fidelity"
          value={pct(stats.lineupRate)}
          color={rateColor(stats.lineupRate, 0.8, 0.5)}
          hint="A blind judge, shown all candidate misconceptions, found the persona's misconception(s) in its reasoning — i.e. the simulated student really was reasoning the way we claimed."
        />
      </div>
    </div>
  );
}

/* ── File loader helper ──────────────────────────────────────────── */

function loadJsonFiles(fileList) {
  return Promise.all(
    Array.from(fileList)
      .filter(f => f.name.endsWith(".json"))
      .map(f => new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = () => {
          try { resolve(JSON.parse(reader.result)); }
          catch (e) { reject(e); }
        };
        reader.onerror = reject;
        reader.readAsText(f);
      }))
  ).then(items =>
    items
      // judge_report may be absent (judging skipped) — only the item is required.
      .filter(item => item.item)
      .sort((a, b) => (a.created_at || "").localeCompare(b.created_at || ""))
  );
}

/* ── Exporters (HTML / LaTeX for non-CS reviewers) ──────────────── */

function downloadText(filename, text, mime) {
  const blob = new Blob([text], { type: mime });
  const a = document.createElement("a");
  a.href = URL.createObjectURL(blob);
  a.download = filename;
  a.click();
}

function _correctIds(item) {
  return item.correct_option_ids && item.correct_option_ids.length
    ? item.correct_option_ids
    : item.options.filter(o => o.is_correct).map(o => o.id);
}

// A safe, per-item figure filename so that reused ids (every item tends to call
// its figure "fig1") don't collide inside the shared figures/ folder.
function figFilename(itemIdx, id) {
  const safe = String(id).replace(/[^A-Za-z0-9_-]/g, "_");
  return `item${itemIdx + 1}_${safe}.png`;
}

// LaTeX: option text / stems are model-authored with LaTeX math, so they pass
// through mostly unescaped. The one exception is a bare "%": the model writes it
// constantly ("95% confidence") but LaTeX reads it as a comment, silently eating
// the rest of the line (including the closing brace of any \textit{…} wrapper) and
// breaking compilation. So escape any "%" that isn't already \-escaped. Option
// ids/answers (labels) get their full set of specials escaped via escId.
//
// figureMode:
//   "note"    → figures become an italic placeholder note (plain .tex, no images)
//   "include" → figures become \includegraphics of figures/<file>.png (used for
//               the zip export, which ships the images alongside the .tex)
function toLatex(results, { figureMode = "note" } = {}) {
  const escId = s => String(s).replace(/[_&%#$]/g, c => "\\" + c);
  const escPct = s => (s || "").replace(/(?<!\\)%/g, "\\%");
  const anyFigures = figureMode === "include" &&
    results.some(r => r.figure_data && Object.keys(r.figure_data).length);
  const figRepl = (itemIdx, figData) => text => escPct(text || "").replace(
    /\[FIGURE:([^\]]+)\]/g, (_, id) => {
      if (figureMode === "include" && figData && figData[id])
        return `\\par\\begin{center}\\includegraphics[max width=\\linewidth,max height=0.4\\textheight]{figures/${figFilename(itemIdx, id)}}\\end{center}\\par `;
      return `\\par\\textit{[Figure: ${escId(id)} — see HTML/JSON export]}\\par `;
    });
  const out = [
    "\\documentclass[11pt]{article}",
    "\\usepackage{amsmath,amssymb}",
  ];
  if (anyFigures) out.push("\\usepackage{graphicx}", "\\usepackage[export]{adjustbox}");
  out.push(
    "\\usepackage[margin=1in]{geometry}",
    "\\title{Generated Assessment Items}", "\\date{}",
    "\\begin{document}", "\\maketitle", "",
  );
  results.forEach((r, i) => {
    const item = r.item;
    const figNote = figRepl(i, r.figure_data);
    const correct = new Set(_correctIds(item));
    out.push(`\\section*{Item ${i + 1}}`);
    if ((item.target_facets || []).length)
      out.push(`\\textbf{Target facets:} ${escId(item.target_facets.join(", "))}\\\\[4pt]`);
    out.push(figNote(item.stem), "", "\\begin{itemize}");
    item.options.forEach(o => {
      const mark = correct.has(o.id) ? " $\\checkmark$" : "";
      out.push(`  \\item[\\textbf{${escId(o.id)}.}] ${figNote(o.text)}${mark}`);
      if (o.rationale) out.push(`    \\par\\smallskip\\textit{${figNote(o.rationale)}}`);
    });
    out.push("\\end{itemize}");
    out.push(`\\textbf{Correct answer:} ${escId([...correct].join(", "))}\\\\[4pt]`);
    if (item.explanation) out.push(`\\textbf{Explanation:} ${escPct(item.explanation)}`);
    out.push("\\bigskip", "");
  });
  out.push("\\end{document}");
  return out.join("\n");
}

// Bundle the LaTeX doc + all referenced figures into a .zip so a reviewer can
// unzip and compile straight away with the figures resolved from figures/.
async function downloadLatexZip(results) {
  const zip = new JSZip();
  zip.file("assessment_items.tex", toLatex(results, { figureMode: "include" }));
  const figures = zip.folder("figures");
  results.forEach((r, i) => {
    const figData = r.figure_data || {};
    Object.entries(figData).forEach(([id, b64]) => {
      if (b64) figures.file(figFilename(i, id), b64, { base64: true });
    });
  });
  const blob = await zip.generateAsync({ type: "blob" });
  const a = document.createElement("a");
  a.href = URL.createObjectURL(blob);
  a.download = "assessment_items.zip";
  a.click();
}

// Self-contained HTML: the most portable export. Math renders as MathML (native
// in modern browsers — no external CSS or fonts needed), figures embed as
// base64 data-URIs, so the single .html file opens anywhere and prints to PDF.
function escHtml(s) {
  return String(s).replace(/[&<>]/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;" }[c]));
}

// Convert model text ($…$ math + [FIGURE:id] tags + prose) to an HTML fragment.
// Math → KaTeX MathML; figures → inline <img>; all other text is HTML-escaped.
function textToHtml(text, figData) {
  const mathToHtml = t => {
    if (typeof katex === "undefined") return escHtml(t);
    const regex = /\$\$([\s\S]+?)\$\$|\$([^$\n]+?)\$/g;
    const parts = [];
    let last = 0, match;
    while ((match = regex.exec(t)) !== null) {
      if (match.index > last) parts.push(escHtml(t.slice(last, match.index)));
      const expr = match[1] || match[2];
      try {
        parts.push(katex.renderToString(expr, { throwOnError: false, displayMode: !!match[1], output: "mathml" }));
      } catch {
        parts.push(escHtml(match[0]));
      }
      last = regex.lastIndex;
    }
    if (last < t.length) parts.push(escHtml(t.slice(last)));
    return parts.join("");
  };
  return splitTextAndFigures(text || "", figData).map(seg => {
    if (seg.type === "figure") {
      const data = figData?.[seg.id];
      return data
        ? `<img src="data:image/png;base64,${data}" alt="${escHtml(seg.id)}" />`
        : `<em class="missing">[Figure ${escHtml(seg.id)} unavailable]</em>`;
    }
    return mathToHtml(seg.value);
  }).join("");
}

function toHtml(results) {
  const sections = results.map((r, i) => {
    const item = r.item, figData = r.figure_data || {};
    const correct = new Set(_correctIds(item));
    const facets = (item.target_facets || []).length
      ? `<p class="meta"><strong>Target facets:</strong> ${escHtml(item.target_facets.join(", "))}</p>` : "";
    const opts = item.options.map(o => {
      const mark = correct.has(o.id) ? ' <span class="ok">✓</span>' : "";
      const tags = (o.facet_tags || []).length ? ` <span class="tags">(${escHtml(o.facet_tags.join(", "))})</span>` : "";
      const rat = o.rationale ? `<div class="rationale">${textToHtml(o.rationale, figData)}</div>` : "";
      return `      <li><span class="oid">${escHtml(o.id)}.</span> ${textToHtml(o.text, figData)}${mark}${tags}${rat}</li>`;
    }).join("\n");
    const expl = item.explanation
      ? `<p class="expl"><strong>Explanation:</strong> ${textToHtml(item.explanation, figData)}</p>` : "";
    return `  <section>
    <h2>Item ${i + 1}</h2>
    ${facets}
    <div class="stem">${textToHtml(item.stem, figData)}</div>
    <ul class="options">
${opts}
    </ul>
    <p class="answer"><strong>Correct answer:</strong> ${escHtml([...correct].join(", "))}</p>
    ${expl}
  </section>`;
  }).join("\n");
  const css = `
    :root { color-scheme: light; }
    body { max-width: 820px; margin: 40px auto; padding: 0 24px;
      font-family: Georgia, 'Times New Roman', serif; color: #1a1a1a; line-height: 1.6; }
    h1 { font-size: 26px; font-weight: 700; margin-bottom: 28px; }
    h2 { font-size: 18px; margin: 0 0 8px; padding-top: 20px; }
    section { border-top: 1px solid #ddd; padding-bottom: 8px; }
    section:first-of-type { border-top: none; }
    .meta, .tags { font-size: 13px; color: #666; }
    .stem { margin: 10px 0; }
    ul.options { list-style: none; padding: 0; margin: 12px 0; }
    ul.options > li { margin: 10px 0; padding-left: 26px; text-indent: -26px; }
    .oid { font-weight: 700; }
    .ok { color: #0a7d38; font-weight: 700; }
    .rationale { font-style: italic; color: #555; font-size: 14px; margin: 4px 0 0 26px; text-indent: 0; }
    .answer { font-size: 14px; }
    .expl { font-size: 14px; background: #f6f6f4; padding: 10px 14px; border-radius: 6px; }
    img { display: block; max-width: 100%; margin: 14px auto; border: 1px solid #ddd; border-radius: 8px; }
    .missing { color: #999; }
    math { font-size: 1.05em; }
    @media print { body { margin: 0; max-width: none; } section { page-break-inside: avoid; } }`;
  return `<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>Generated Assessment Items</title>
<style>${css}
</style>
</head>
<body>
<h1>Generated Assessment Items</h1>
${sections}
</body>
</html>`;
}

/* ── Main app ────────────────────────────────────────────────────── */

function VariationA() {
  const allGoalIds = FACET_MAP.facets.filter(f => f.type === "goal").map(f => f.id);
  const allBadIds  = FACET_MAP.facets.filter(f => f.type === "problematic").map(f => f.id);

  const [autoSelect,  setAutoSelect]  = React.useState(true);
  const [selectedFacets, setSelectedFacets] = React.useState([]);
  const [format,     setFormat]     = React.useState("single_select");
  const [bookMode,   setBookMode]   = React.useState("none");
  const [numOptions, setNumOptions] = React.useState(4);
  const [nItems,     setNItems]     = React.useState(4);
  const [figFrac,    setFigFrac]    = React.useState(0);

  const [runEval,    setRunEval]    = React.useState(false);
  const [skipJudge,  setSkipJudge]  = React.useState(false);
  // Judging is forced off for large batches (it is the slow step); above 10
  // items the toggle locks on regardless of the user's choice.
  const judgeForced = nItems > 10;
  const skipJudgeEffective = skipJudge || judgeForced;

  const [results,     setResults]     = React.useState([]);
  const [loadedPath,  setLoadedPath]  = React.useState(null);
  const [loadError,   setLoadError]   = React.useState(null);
  const [selected,    setSelected]    = React.useState(0);
  const [view,        setView]        = React.useState("list");
  const [showFacetMap, setShowFacetMap] = React.useState(false);

  // Generation backend state
  const [generating,  setGenerating]  = React.useState(false);
  const [genProgress, setGenProgress] = React.useState({ done: 0, total: 0 });
  const [genError,    setGenError]    = React.useState(null);
  const [models,      setModels]      = React.useState({ generator_model: null, judge_model: null, eval_model: null });
  // User-selected generator / judge models (null until config loads, then the
  // backend defaults; user picks override).
  const [genModel,    setGenModel]    = React.useState(null);
  const [judgeModel,  setJudgeModel]  = React.useState(null);

  // Anthropic API key state: null = unknown (no backend yet), true/false from /api/config.
  const [hasApiKey,    setHasApiKey]    = React.useState(null);
  const [showKeyModal, setShowKeyModal] = React.useState(false);
  const [keyNotice,    setKeyNotice]    = React.useState(null);

  // Evaluation backend state
  const [evaluating,   setEvaluating]   = React.useState(false);
  const [evalProgress, setEvalProgress] = React.useState({ done: 0, total: 0 });
  const [evalError,    setEvalError]    = React.useState(null);
  const [corpusEval,   setCorpusEval]   = React.useState(null);

  // Student simulator backend state
  const [simulating, setSimulating] = React.useState(false);
  const [simStatus,  setSimStatus]  = React.useState(null);
  const [simError,   setSimError]   = React.useState(null);

  const fileInputRef = React.useRef(null);
  const dirInputRef  = React.useRef(null);

  // Fetch the backend's default models (and detect whether a backend is present).
  React.useEffect(() => {
    fetch("/api/config")
      .then(r => (r.ok ? r.json() : null))
      .then(cfg => {
        if (!cfg) return;
        setModels(cfg);
        setGenModel(g => g || cfg.generator_model);
        setJudgeModel(j => j || cfg.judge_model);
        if ("has_anthropic_key" in cfg) {
          setHasApiKey(cfg.has_anthropic_key);
          if (!cfg.has_anthropic_key) setShowKeyModal(true);
        }
      })
      .catch(() => {});
  }, []);

  const handleKeySaved = resp => {
    setHasApiKey(true);
    setShowKeyModal(false);
    setKeyNotice(resp && resp.detail ? resp.detail : "API key saved.");
  };

  const handleGenerate = async () => {
    setGenError(null);
    setGenerating(true);
    setGenProgress({ done: 0, total: nItems });
    setResults([]);
    setCorpusEval(null);
    setEvalError(null);
    setLoadedPath(null);
    setSelected(0);
    setView("list");

    const body = {
      topic: "confidence_intervals",
      auto_select_facets: autoSelect,
      target_facets: autoSelect ? [] : selectedFacets,
      response_format: format,
      num_options: numOptions,
      book_context_mode: bookMode,
      n_items: nItems,
      min_frac_with_figures: figFrac,
      run_eval: runEval,
      skip_judge: skipJudgeEffective,
      generator_model: genModel || undefined,
      judge_model: judgeModel || undefined,
    };

    try {
      const resp = await fetch("/api/generate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });
      if (!resp.ok || !resp.body) {
        let msg = `Server returned ${resp.status}`;
        try { const j = await resp.json(); if (j.error) msg = j.error; } catch {}
        throw new Error(msg);
      }

      const reader = resp.body.getReader();
      const decoder = new TextDecoder();
      let buffer = "";
      let first = true;

      const handleFrame = frame => {
        if (frame.type === "meta") {
          setGenProgress({ done: 0, total: frame.n_items });
        } else if (frame.type === "item") {
          setResults(prev => [...prev, frame.artifact]);
          setGenProgress(p => ({ done: frame.index, total: p.total }));
          if (first) { setSelected(0); first = false; }
        } else if (frame.type === "error") {
          setGenError(frame.message || "Generation failed.");
        }
      };

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        buffer += decoder.decode(value, { stream: true });
        let nl;
        while ((nl = buffer.indexOf("\n")) >= 0) {
          const line = buffer.slice(0, nl).trim();
          buffer = buffer.slice(nl + 1);
          if (line) { try { handleFrame(JSON.parse(line)); } catch {} }
        }
      }
    } catch (e) {
      setGenError(
        (e && e.message ? e.message : "Generation request failed.") +
        " — is the dashboard backend running? Start it with: python scripts/serve_dashboard.py"
      );
    } finally {
      setGenerating(false);
    }
  };

  const handleEvaluate = async () => {
    if (!results.length) return;
    setEvalError(null);
    setEvaluating(true);
    setEvalProgress({ done: 0, total: results.length });

    try {
      const resp = await fetch("/api/evaluate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ topic: "confidence_intervals", artifacts: results }),
      });
      if (!resp.ok || !resp.body) {
        let msg = `Server returned ${resp.status}`;
        try { const j = await resp.json(); if (j.error) msg = j.error; } catch {}
        throw new Error(msg);
      }

      const reader = resp.body.getReader();
      const decoder = new TextDecoder();
      let buffer = "";

      const handleFrame = frame => {
        if (frame.type === "meta") {
          setEvalProgress({ done: 0, total: frame.n_items });
        } else if (frame.type === "item") {
          // Merge per-item correctness + facet latency into the matching result.
          setResults(prev => prev.map((r, i) =>
            i === frame.index - 1 ? { ...r, eval_scores: { ...(r.eval_scores || {}), ...frame.eval_scores } } : r
          ));
          setEvalProgress(p => ({ done: frame.index, total: p.total }));
        } else if (frame.type === "expert_similarity") {
          setResults(prev => prev.map((r, i) =>
            i === frame.index - 1 ? { ...r, similarity_with_experts: frame.similarity_with_experts } : r
          ));
        } else if (frame.type === "corpus") {
          setCorpusEval(frame.corpus);
        } else if (frame.type === "error") {
          setEvalError(frame.message || "Evaluation failed.");
        }
      };

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        buffer += decoder.decode(value, { stream: true });
        let nl;
        while ((nl = buffer.indexOf("\n")) >= 0) {
          const line = buffer.slice(0, nl).trim();
          buffer = buffer.slice(nl + 1);
          if (line) { try { handleFrame(JSON.parse(line)); } catch {} }
        }
      }
      setView("aggregate");
    } catch (e) {
      setEvalError(
        (e && e.message ? e.message : "Evaluation request failed.") +
        " — is the dashboard backend running? Start it with: python scripts/serve_dashboard.py"
      );
    } finally {
      setEvaluating(false);
    }
  };

  const handleSimulate = async (indices) => {
    if (!results.length || simulating) return;
    setSimError(null);
    setSimulating(true);
    setSimStatus("Starting student simulator…");

    const targetSet = indices == null ? null : new Set(indices);
    const inScope = i => targetSet == null || targetSet.has(i);
    setResults(prev => prev.map((r, i) =>
      inScope(i) ? { ...r, simulation: { running: true, runs: [] } } : r
    ));

    const mergeSim = (itemIndex, update) =>
      setResults(prev => prev.map((r, i) => {
        if (i !== itemIndex) return r;
        const sim = r.simulation || { running: true, runs: [] };
        return { ...r, simulation: { ...sim, ...update(sim) } };
      }));

    try {
      const resp = await fetch("/api/simulate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ topic: "confidence_intervals", artifacts: results, indices }),
      });
      if (!resp.ok || !resp.body) {
        let msg = `Server returned ${resp.status}`;
        try { const j = await resp.json(); if (j.error) msg = j.error; } catch {}
        throw new Error(msg);
      }

      const reader = resp.body.getReader();
      const decoder = new TextDecoder();
      let buffer = "";

      const handleFrame = frame => {
        if (frame.type === "meta") {
          setSimStatus(`Simulating with ${(frame.student_model || "").replace(/^anthropic\//, "")}…`);
        } else if (frame.type === "status") {
          setSimStatus(frame.message);
        } else if (frame.type === "attempt") {
          mergeSim(frame.item_index, sim => ({ runs: [...(sim.runs || []), frame] }));
        } else if (frame.type === "item_skipped") {
          mergeSim(frame.item_index, () => ({ running: false, skipped: frame.reason }));
        } else if (frame.type === "item_note") {
          mergeSim(frame.item_index, () => ({ note: frame.message }));
        } else if (frame.type === "item_done") {
          mergeSim(frame.item_index, () => ({ running: false }));
        } else if (frame.type === "attempt_error") {
          setSimError(frame.message || "A student run failed.");
        } else if (frame.type === "error") {
          setSimError(frame.message || "Simulation failed.");
        }
      };

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        buffer += decoder.decode(value, { stream: true });
        let nl;
        while ((nl = buffer.indexOf("\n")) >= 0) {
          const line = buffer.slice(0, nl).trim();
          buffer = buffer.slice(nl + 1);
          if (line) { try { handleFrame(JSON.parse(line)); } catch {} }
        }
      }
    } catch (e) {
      setSimError(
        (e && e.message ? e.message : "Simulation request failed.") +
        " — is the dashboard backend running? Start it with: python scripts/serve_dashboard.py"
      );
    } finally {
      // Clear any still-running flags (e.g. the stream errored mid-item).
      setResults(prev => prev.map((r, i) =>
        inScope(i) && r.simulation?.running
          ? { ...r, simulation: { ...r.simulation, running: false } } : r
      ));
      setSimulating(false);
      setSimStatus(null);
    }
  };

  const handleFilesSelected = (fileList, label) => {
    setLoadError(null);
    loadJsonFiles(fileList).then(items => {
      if (items.length === 0) {
        setLoadError("No valid artifact JSON files found.");
        return;
      }
      setResults(items);
      setCorpusEval(null);
      setEvalError(null);
      setSelected(0);
      setView("list");
      setLoadedPath(label || `${items.length} file(s)`);
    }).catch(() => setLoadError("Failed to parse JSON files."));
  };

  const toggleFacet = id =>
    setSelectedFacets(prev => prev.includes(id) ? prev.filter(f => f !== id) : [...prev, id]);

  const canRun = (autoSelect || selectedFacets.length > 0) && !generating;
  const simStats = computeSimStats(results);

  // Generator/judge dropdown choices: the backend's list, plus whatever is
  // currently selected (so a default not in the list still shows).
  const modelOptions = [...new Set([
    ...(models.model_choices || []),
    genModel, judgeModel, models.generator_model, models.judge_model,
  ].filter(Boolean))].map(id => ({ value: id, label: modelLabel(id) }));

  const handleExport = () =>
    downloadText("assessment_items.json", JSON.stringify(results, null, 2), "application/json");
  // With figures, ship a .zip (tex + figures/ folder) so it compiles as-is;
  // without figures, the plain .tex is friendlier than a single-file zip.
  const hasFigures = results.some(r => r.figure_data && Object.keys(r.figure_data).length);
  const handleExportTex = () =>
    hasFigures
      ? downloadLatexZip(results)
      : downloadText("assessment_items.tex", toLatex(results), "application/x-tex");
  const handleExportHtml = () =>
    downloadText("assessment_items.html", toHtml(results), "text/html");

  const segBtn = (label, active, onClick) => (
    <button onClick={onClick} style={{
      padding: "4px 12px", border: "none",
      background: active ? DS.ink : DS.paper,
      color: active ? DS.paper : DS.ink2,
      fontFamily: FM, fontSize: 10.5, fontWeight: 600, letterSpacing: "0.04em",
      cursor: "pointer",
    }}>{label}</button>
  );

  return (
    <div style={{ display: "flex", height: "100%", width: "100%", fontFamily: FN, background: DS.paper2, color: DS.ink, overflow: "hidden", position: "relative" }}>

      {/* ── Config sidebar ── */}
      <aside style={{ width: 256, flexShrink: 0, background: DS.paper, borderRight: `1px solid ${DS.rule}`, display: "flex", flexDirection: "column", overflowY: "auto", padding: "18px 16px", gap: 18 }}>
        <div style={{ borderBottom: `1px solid ${DS.rule}`, paddingBottom: 14, display: "flex", alignItems: "baseline", gap: 10 }}>
          <span style={{ fontFamily: FS, fontSize: 17, fontWeight: 500, color: DS.ink, letterSpacing: "-0.01em" }}>
            Assessment <em style={{ fontStyle: "italic", color: DS.accentInk }}>Copilot</em>
          </span>
          <div style={{ flex: 1 }} />
          <button onClick={() => setShowKeyModal(true)}
            title={hasApiKey === false ? "No Claude API key set — click to add one" : "Update the Claude API key"}
            style={{ background: "none", border: "none", cursor: "pointer", fontFamily: FM, fontSize: 9.5, fontWeight: 600, letterSpacing: "0.06em", textTransform: "uppercase", color: hasApiKey === false ? DS.mismatchFg : DS.inkMuted, display: "flex", alignItems: "center", gap: 4 }}>
            <span style={{ fontSize: 11 }}>🔑</span>{hasApiKey === false ? "Set key" : "Key"}
          </button>
        </div>
        <div style={{ fontSize: 10.5, fontFamily: FM, color: DS.inkMuted, letterSpacing: "0.06em", textTransform: "uppercase", marginTop: -10 }}>{FACET_MAP.course}</div>

        <div>
          <MonoLabel>Topic</MonoLabel>
          <div style={{ padding: "6px 9px", borderRadius: DS.r, border: `1px solid ${DS.ruleStrong}`, background: DS.paper2, fontSize: 13, color: DS.ink2, fontFamily: FS, fontStyle: "italic" }}>
            Confidence Intervals
          </div>
        </div>

        {/* Facet selection mode */}
        <div>
          <MonoLabel action={
            <button onClick={() => setShowFacetMap(true)} style={{ fontSize: 10.5, color: DS.accentInk, background: "none", border: "none", cursor: "pointer", fontFamily: FM, fontWeight: 600, letterSpacing: "0.04em", textTransform: "uppercase" }}>Map</button>
          }>Target Facets</MonoLabel>

          {/* Auto toggle */}
          <div
            onClick={() => setAutoSelect(a => !a)}
            style={{
              display: "flex", alignItems: "center", gap: 8, marginBottom: 10,
              padding: "7px 10px", borderRadius: DS.rlg,
              background: autoSelect ? DS.accentSoft : DS.paper2,
              border: `1px solid ${autoSelect ? DS.accent : DS.ruleStrong}`,
              cursor: "pointer", transition: "all 0.15s",
            }}>
            <div style={{
              width: 32, height: 16, borderRadius: 8, position: "relative",
              background: autoSelect ? DS.accent : DS.ruleStrong,
              transition: "background 0.15s",
            }}>
              <div style={{
                width: 12, height: 12, borderRadius: 6, background: "#fff",
                position: "absolute", top: 2,
                left: autoSelect ? 18 : 2,
                transition: "left 0.15s",
              }} />
            </div>
            <span style={{ fontSize: 11.5, fontWeight: 500, color: autoSelect ? DS.accentInk : DS.ink2, fontFamily: FN }}>
              Auto-select facets
            </span>
          </div>

          {autoSelect ? (
            <div style={{ padding: "8px 10px", borderRadius: DS.rlg, background: DS.paper2, border: `1px solid ${DS.rule}` }}>
              <p style={{ margin: 0, fontSize: 11.5, color: DS.ink3, fontFamily: FS, fontStyle: "italic", lineHeight: 1.6 }}>
                The model will automatically choose diverse facet combinations for each item, avoiding repetition across the batch.
              </p>
            </div>
          ) : (
            <>
              <div style={{ marginBottom: 5, fontSize: 10, color: DS.inkMuted, fontFamily: FM, letterSpacing: "0.08em", textTransform: "uppercase" }}>Goal (A)</div>
              <div style={{ display: "flex", flexWrap: "wrap", gap: 4, marginBottom: 9 }}>
                {allGoalIds.map(id => <FacetTag key={id} id={id} selected={selectedFacets.includes(id)} onClick={() => toggleFacet(id)} />)}
              </div>
              <div style={{ marginBottom: 5, fontSize: 10, color: DS.inkMuted, fontFamily: FM, letterSpacing: "0.08em", textTransform: "uppercase" }}>Problematic (B)</div>
              <div style={{ display: "flex", flexWrap: "wrap", gap: 4 }}>
                {allBadIds.map(id => <FacetTag key={id} id={id} selected={selectedFacets.includes(id)} onClick={() => toggleFacet(id)} />)}
              </div>
            </>
          )}
        </div>

        <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
          <FormField label="Response Format">
            <Select value={format} onChange={setFormat} options={[
              { value: "single_select", label: "Single select" },
              { value: "multi_select", label: "Multi select" },
              { value: "true_false_per_option", label: "True / False per option" },
            ]} />
          </FormField>
          <FormField label="Book Context">
            <Select value={bookMode} onChange={setBookMode} options={[
              { value: "none", label: "None" },
              { value: "full_tex", label: "Full chapter (LaTeX)" },
              { value: "rag", label: "RAG (not available)" },
            ]} />
          </FormField>
          <FormField label="Options">
            <Select value={String(numOptions)} onChange={v => setNumOptions(Number(v))} options={[3,4,5,6].map(n => ({ value: String(n), label: String(n) }))} />
          </FormField>
          <FormField label={`Items — ${nItems}`}>
            <input type="range" min={1} max={50} step={1} value={nItems}
              onChange={e => setNItems(Number(e.target.value))}
              style={{ width: "100%", accentColor: DS.accent, cursor: "pointer" }} />
          </FormField>
          <FormField label={`Min. with figures — ${Math.round(nItems * figFrac)} of ${nItems}`}>
            <Select value={String(figFrac)} onChange={v => setFigFrac(Number(v))} options={[
              { value: "0", label: "None" },
              { value: "0.25", label: "25%" },
              { value: "0.33", label: "33%" },
              { value: "0.5", label: "50%" },
              { value: "0.75", label: "75%" },
              { value: "1", label: "All" },
            ]} />
          </FormField>
        </div>

        {/* Run evaluation toggle */}
        <div
          onClick={() => !generating && setRunEval(v => !v)}
          style={{
            display: "flex", alignItems: "center", gap: 8, marginTop: -6,
            padding: "7px 10px", borderRadius: DS.rlg,
            background: runEval ? DS.accentSoft : DS.paper2,
            border: `1px solid ${runEval ? DS.accent : DS.ruleStrong}`,
            cursor: generating ? "not-allowed" : "pointer", transition: "all 0.15s",
            opacity: generating ? 0.5 : 1,
          }}>
          <div style={{ width: 32, height: 16, borderRadius: 8, position: "relative", background: runEval ? DS.accent : DS.ruleStrong, transition: "background 0.15s" }}>
            <div style={{ width: 12, height: 12, borderRadius: 6, background: "#fff", position: "absolute", top: 2, left: runEval ? 18 : 2, transition: "left 0.15s" }} />
          </div>
          <span style={{ fontSize: 11.5, fontWeight: 500, color: runEval ? DS.accentInk : DS.ink2, fontFamily: FN }}>
            Run evaluation rubrics
          </span>
        </div>

        {/* Skip judge toggle (auto-forced on for large batches) */}
        <div
          onClick={() => { if (!generating && !judgeForced) setSkipJudge(v => !v); }}
          title={judgeForced ? "Judging is skipped automatically for batches over 10 items" : "Skip the independent judge pass (faster; no agreement/confidence scores)"}
          style={{
            display: "flex", alignItems: "center", gap: 8, marginTop: -6,
            padding: "7px 10px", borderRadius: DS.rlg,
            background: skipJudgeEffective ? DS.accentSoft : DS.paper2,
            border: `1px solid ${skipJudgeEffective ? DS.accent : DS.ruleStrong}`,
            cursor: (generating || judgeForced) ? "not-allowed" : "pointer", transition: "all 0.15s",
            opacity: generating ? 0.5 : judgeForced ? 0.85 : 1,
          }}>
          <div style={{ width: 32, height: 16, borderRadius: 8, position: "relative", background: skipJudgeEffective ? DS.accent : DS.ruleStrong, transition: "background 0.15s" }}>
            <div style={{ width: 12, height: 12, borderRadius: 6, background: "#fff", position: "absolute", top: 2, left: skipJudgeEffective ? 18 : 2, transition: "left 0.15s" }} />
          </div>
          <span style={{ fontSize: 11.5, fontWeight: 500, color: skipJudgeEffective ? DS.accentInk : DS.ink2, fontFamily: FN }}>
            Skip judge{judgeForced ? " (auto, >10 items)" : ""}
          </span>
        </div>

        {/* Model selection */}
        <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
          <FormField label="Generator">
            <Select value={genModel || ""} onChange={setGenModel}
              options={modelOptions} />
          </FormField>
          <FormField label="Judge">
            <Select value={judgeModel || ""} onChange={setJudgeModel}
              options={modelOptions} />
          </FormField>
          <div style={{ fontSize: 9.5, fontFamily: FM, color: DS.inkMuted, letterSpacing: "0.03em", lineHeight: 1.6 }}>
            eval &amp; simulator · {modelLabel(models.eval_model)}
          </div>
        </div>

        <button onClick={canRun ? handleGenerate : undefined} disabled={!canRun} style={{
          padding: "8px 0", borderRadius: DS.r,
          background: canRun ? DS.ink : DS.paper3,
          color: canRun ? DS.paper : DS.inkMuted,
          border: `1px solid ${canRun ? DS.ink : DS.ruleStrong}`,
          fontSize: 12.5, fontWeight: 500, cursor: canRun ? "pointer" : "not-allowed",
          fontFamily: FN, transition: "all 0.15s",
        }}>
          {generating
            ? `Generating ${genProgress.done}/${genProgress.total}…`
            : `Generate ${nItems} Item${nItems > 1 ? "s" : ""}`}
        </button>

        {hasApiKey === false && (
          <div style={{ fontSize: 10.5, color: DS.partialFg, fontFamily: FM, letterSpacing: "0.02em", lineHeight: 1.6, padding: "6px 8px", background: DS.partialBg, borderRadius: DS.r, border: `1px solid ${DS.partialFg}`, marginTop: -4 }}>
            No Claude API key detected — generation will fail.{" "}
            <span onClick={() => setShowKeyModal(true)} style={{ textDecoration: "underline", cursor: "pointer", fontWeight: 600 }}>
              Add key
            </span>
          </div>
        )}
        {keyNotice && (
          <div style={{ fontSize: 10.5, color: DS.matchFg, fontFamily: FM, letterSpacing: "0.02em", lineHeight: 1.6, padding: "6px 8px", background: DS.matchBg, borderRadius: DS.r, border: `1px solid ${DS.matchBorder}`, marginTop: -4 }}>
            {keyNotice}
          </div>
        )}

        {genError && (
          <div style={{ fontSize: 10.5, color: DS.mismatchFg, fontFamily: FM, letterSpacing: "0.02em", lineHeight: 1.6, padding: "6px 8px", background: DS.mismatchBg, borderRadius: DS.r, border: `1px solid ${DS.mismatchFg}` }}>
            {genError}
          </div>
        )}

        {/* Load / Export results */}
        <div style={{ borderTop: `1px solid ${DS.rule}`, paddingTop: 14, display: "flex", flexDirection: "column", gap: 6 }}>
          <MonoLabel>Results</MonoLabel>
          <input ref={fileInputRef} type="file" accept=".json" multiple style={{ display: "none" }}
            onChange={e => { if (e.target.files.length) handleFilesSelected(e.target.files, `${e.target.files.length} file(s)`); e.target.value = ""; }} />
          <input ref={dirInputRef} type="file" webkitdirectory="" style={{ display: "none" }}
            onChange={e => {
              if (e.target.files.length) {
                const parts = e.target.files[0].webkitRelativePath.split("/");
                handleFilesSelected(e.target.files, parts[0] || "directory");
              }
              e.target.value = "";
            }} />
          <div style={{ display: "flex", gap: 6 }}>
            <Btn onClick={() => fileInputRef.current?.click()} small style={{ flex: 1 }}>Load Files</Btn>
            <Btn onClick={() => dirInputRef.current?.click()} small style={{ flex: 1 }}>Load Folder</Btn>
          </div>
          {loadedPath && (
            <div style={{ fontSize: 10.5, color: DS.matchFg, fontFamily: FM, letterSpacing: "0.04em", padding: "4px 0" }}>
              Loaded: {loadedPath} ({results.length} items)
            </div>
          )}
          {loadError && (
            <div style={{ fontSize: 10.5, color: DS.mismatchFg, fontFamily: FM, letterSpacing: "0.04em", padding: "4px 0" }}>
              {loadError}
            </div>
          )}
          {results.length > 0 && (
            <>
              <div style={{ fontSize: 10, fontFamily: FM, color: DS.inkMuted, letterSpacing: "0.06em", textTransform: "uppercase", marginTop: 2 }}>Download</div>
              <div style={{ display: "flex", gap: 6 }}>
                <Btn onClick={handleExport} small>JSON</Btn>
                <Btn onClick={handleExportHtml} small>HTML</Btn>
                <Btn onClick={handleExportTex} small>{hasFigures ? "LaTeX (zip)" : "LaTeX"}</Btn>
              </div>
            </>
          )}
        </div>
      </aside>

      {/* ── Main area ── */}
      <main style={{ flex: 1, display: "flex", flexDirection: "column", overflow: "hidden", background: DS.paper2 }}>
        {results.length === 0 && generating && (
          <div style={{ flex: 1, display: "flex", alignItems: "center", justifyContent: "center" }}>
            <div style={{ maxWidth: 420, textAlign: "center" }}>
              <div style={{ fontFamily: FS, fontSize: 20, fontWeight: 500, color: DS.ink2, marginBottom: 10, fontStyle: "italic", letterSpacing: "-0.01em" }}>
                Generating {genProgress.total} item{genProgress.total > 1 ? "s" : ""}…
              </div>
              <div style={{ fontSize: 12.5, color: DS.ink3, lineHeight: 1.7, fontFamily: FS, marginBottom: 18 }}>
                Drafting with <strong>{modelLabel(genModel || models.generator_model) || "the generator"}</strong> and verifying with <strong>{modelLabel(judgeModel || models.judge_model) || "the judge"}</strong>. Items appear here as each one finishes.
              </div>
              <div style={{ width: 220, height: 4, borderRadius: 2, background: DS.paper3, margin: "0 auto", overflow: "hidden" }}>
                <div style={{ height: "100%", borderRadius: 2, background: DS.accent, animation: "ds-prog 1.4s ease-in-out infinite" }} />
              </div>
            </div>
          </div>
        )}
        {results.length === 0 && !generating && (
          <div style={{ flex: 1, display: "flex", alignItems: "center", justifyContent: "center" }}>
            <div style={{ maxWidth: 400, textAlign: "center" }}>
              <div style={{ fontFamily: FS, fontSize: 20, fontWeight: 500, color: DS.ink2, marginBottom: 8, fontStyle: "italic", letterSpacing: "-0.01em" }}>Load assessment results</div>
              <div style={{ fontSize: 13, color: DS.ink3, lineHeight: 1.7, fontFamily: FS, marginBottom: 20 }}>
                Load pipeline output JSON files or select the <code style={{ fontFamily: FM, fontSize: 11.5, background: DS.paper3, padding: "1px 4px", borderRadius: 2 }}>outputs/</code> directory to view generated items and judge reports.
              </div>
              <div
                onClick={() => dirInputRef.current?.click()}
                onDragOver={e => { e.preventDefault(); e.currentTarget.style.borderColor = DS.accent; e.currentTarget.style.background = DS.accentSoft; }}
                onDragLeave={e => { e.currentTarget.style.borderColor = DS.ruleStrong; e.currentTarget.style.background = DS.paper; }}
                onDrop={e => {
                  e.preventDefault();
                  e.currentTarget.style.borderColor = DS.ruleStrong;
                  e.currentTarget.style.background = DS.paper;
                  if (e.dataTransfer.files.length) handleFilesSelected(e.dataTransfer.files, "dropped files");
                }}
                style={{
                  border: `2px dashed ${DS.ruleStrong}`, borderRadius: DS.rlg + 2,
                  padding: "32px 24px", cursor: "pointer", background: DS.paper,
                  transition: "all 0.15s",
                }}>
                <div style={{ fontSize: 28, marginBottom: 8, color: DS.inkMuted }}>&#128194;</div>
                <div style={{ fontSize: 13, fontWeight: 500, color: DS.ink2, fontFamily: FN, marginBottom: 6 }}>
                  Click to select folder or drag files here
                </div>
                <div style={{ fontSize: 11, color: DS.inkMuted, fontFamily: FM, letterSpacing: "0.04em" }}>
                  Accepts pipeline JSON artifacts
                </div>
              </div>
              <div style={{ marginTop: 12 }}>
                <Btn onClick={() => fileInputRef.current?.click()}>Or select individual files</Btn>
              </div>
              {loadError && (
                <div style={{ fontSize: 11, color: DS.mismatchFg, fontFamily: FM, marginTop: 10 }}>{loadError}</div>
              )}
            </div>
          </div>
        )}

        {results.length > 0 && (
          <div style={{ flex: 1, display: "flex", flexDirection: "column", overflow: "hidden" }}>
            {/* Top bar */}
            <div style={{ display: "flex", alignItems: "center", gap: 12, padding: "8px 16px", background: DS.paper, borderBottom: `1px solid ${DS.rule}`, flexShrink: 0 }}>
              <div style={{ display: "flex", border: `1px solid ${DS.ruleStrong}`, borderRadius: DS.r, overflow: "hidden" }}>
                {segBtn("Item List", view === "list", () => setView("list"))}
                {segBtn("Aggregate", view === "aggregate", () => setView("aggregate"))}
              </div>
              <div style={{ fontSize: 10.5, color: DS.inkMuted, fontFamily: FM, letterSpacing: "0.04em" }}>
                {results.length} item{results.length > 1 ? "s" : ""}
              </div>
              <div style={{ flex: 1 }} />
              {evalError && (
                <span style={{ fontSize: 10.5, color: DS.mismatchFg, fontFamily: FM, letterSpacing: "0.02em", maxWidth: 420, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }} title={evalError}>
                  {evalError}
                </span>
              )}
              {simError && (
                <span style={{ fontSize: 10.5, color: DS.mismatchFg, fontFamily: FM, letterSpacing: "0.02em", maxWidth: 360, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }} title={simError}>
                  {simError}
                </span>
              )}
              {simulating && simStatus && (
                <span style={{ fontSize: 10.5, color: DS.accentInk, fontFamily: FM, letterSpacing: "0.02em", maxWidth: 320, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }} title={simStatus}>
                  {simStatus}
                </span>
              )}
              <Btn small onClick={simulating ? undefined : () => handleSimulate(null)} disabled={simulating || generating || evaluating}
                title="Run the student simulator on every item: a control student plus one student per keyed misconception">
                {simulating ? "Simulating…" : "Simulate Students"}
              </Btn>
              <Btn small variant="accent" onClick={evaluating ? undefined : handleEvaluate} disabled={evaluating || generating || simulating}>
                {evaluating ? `Evaluating ${evalProgress.done}/${evalProgress.total}…` : "Evaluate"}
              </Btn>
            </div>

            {/* Aggregate */}
            {view === "aggregate" && (
              <div style={{ flex: 1, minHeight: 0, overflowY: "auto", padding: "20px 22px", display: "flex", flexDirection: "column", gap: 14 }}>
                <AggregateBar items={results} />
                {simStats && <SimAggregate stats={simStats} />}
                {corpusEval && <CorpusEval corpus={corpusEval} />}
                <FacetCoverage items={results} />
                <div style={{ background: DS.paper, border: `1px solid ${DS.ruleStrong}`, borderRadius: DS.rlg, overflow: "hidden" }}>
                  <div style={{ padding: "12px 18px", borderBottom: `1px solid ${DS.rule}` }}>
                    <MonoLabel style={{ marginBottom: 0 }}>Per-item breakdown</MonoLabel>
                  </div>
                  {results.map((r, i) => {
                    const ev = r.eval_scores;
                    const bucketColor = b => b === "highly_latent" ? DS.matchFg : b === "latent" ? DS.goalFg : b === "surface" ? DS.partialFg : DS.mismatchFg;
                    return (
                    <React.Fragment key={r.id || i}>
                      {i > 0 && <Rule />}
                      <div style={{ padding: "11px 18px", display: "flex", gap: 12, alignItems: "center" }}>
                        <span style={{ width: 18, height: 18, borderRadius: 2, flexShrink: 0, background: DS.paper3, color: DS.inkMuted, display: "flex", alignItems: "center", justifyContent: "center", fontSize: 10, fontWeight: 600, fontFamily: FM, letterSpacing: "0.04em" }}>{i + 1}</span>
                        <div style={{ flex: 1, minWidth: 0 }}>
                          <RichText as="div" text={truncatePreview(r.item.stem, 90)} style={{ fontSize: 12.5, color: DS.ink2, fontFamily: FS, fontStyle: "italic", marginBottom: 6, whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }} />
                          <div style={{ display: "flex", gap: 16, alignItems: "center", flexWrap: "wrap" }}>
                            {r.judge_report && <div style={{ minWidth: 110 }}><div style={{ fontSize: 10.5, color: DS.inkMuted, fontFamily: FM, letterSpacing: "0.04em", textTransform: "uppercase", marginBottom: 3 }}>Agreement</div><ScoreBar value={r.judge_report.overall_agreement} color={DS.matchFg} /></div>}
                            {r.judge_report && <div style={{ minWidth: 110 }}><div style={{ fontSize: 10.5, color: DS.inkMuted, fontFamily: FM, letterSpacing: "0.04em", textTransform: "uppercase", marginBottom: 3 }}>Confidence</div><ScoreBar value={r.judge_report.overall_confidence} color={DS.goalFg} /></div>}
                            {ev && (
                              <>
                                <div style={{ minWidth: 50 }}>
                                  <div style={{ fontSize: 10.5, color: DS.inkMuted, fontFamily: FM, letterSpacing: "0.04em", textTransform: "uppercase", marginBottom: 3 }}>Correct</div>
                                  <span style={{ fontSize: 11, fontFamily: FM, fontWeight: 600, color: ev.correctness_pass ? DS.matchFg : DS.mismatchFg }}>{ev.correctness_pass ? "Pass" : "Fail"}</span>
                                </div>
                                {ev.naturalness_overall != null && (
                                <div style={{ minWidth: 50 }}>
                                  <div style={{ fontSize: 10.5, color: DS.inkMuted, fontFamily: FM, letterSpacing: "0.04em", textTransform: "uppercase", marginBottom: 3 }}>Natural</div>
                                  <span style={{ fontSize: 11, fontFamily: FM, fontWeight: 600, color: DS.goalFg }}>{ev.naturalness_overall}/5</span>
                                </div>
                                )}
                                <div style={{ minWidth: 50 }}>
                                  <div style={{ fontSize: 10.5, color: DS.inkMuted, fontFamily: FM, letterSpacing: "0.04em", textTransform: "uppercase", marginBottom: 3 }}>Latency</div>
                                  <span style={{ fontSize: 11, fontFamily: FM, fontWeight: 600, color: bucketColor(ev.latency_bucket) }}>{ev.latency_score}/4</span>
                                </div>
                              </>
                            )}
                            {simStats?.perItem[i] && (() => {
                              const s = simStats.perItem[i];
                              const gapColor = s.gap == null ? DS.inkMuted : s.gap >= 0.5 ? DS.matchFg : s.gap > 0 ? DS.partialFg : DS.mismatchFg;
                              return (
                                <>
                                  <div style={{ minWidth: 55 }}>
                                    <div style={{ fontSize: 10.5, color: DS.inkMuted, fontFamily: FM, letterSpacing: "0.04em", textTransform: "uppercase", marginBottom: 3 }}>Sim Gap</div>
                                    <span style={{ fontSize: 11, fontFamily: FM, fontWeight: 600, color: gapColor }}>
                                      {s.gap == null ? "—" : `${s.gap > 0 ? "+" : ""}${Math.round(s.gap * 100)}%`}
                                    </span>
                                  </div>
                                  <div style={{ minWidth: 55 }}>
                                    <div style={{ fontSize: 10.5, color: DS.inkMuted, fontFamily: FM, letterSpacing: "0.04em", textTransform: "uppercase", marginBottom: 3 }}>Control</div>
                                    <span style={{ fontSize: 11, fontFamily: FM, fontWeight: 600, color: s.controlOk == null ? DS.inkMuted : s.controlOk ? DS.matchFg : DS.mismatchFg }}>
                                      {s.controlOk == null ? "—" : s.controlOk ? "OK" : "Missed"}
                                    </span>
                                  </div>
                                </>
                              );
                            })()}
                            <div style={{ flex: 1 }}><TagRow tags={r.item.target_facets} small /></div>
                          </div>
                        </div>
                        <Btn small onClick={() => { setSelected(i); setView("list"); }}>View</Btn>
                      </div>
                    </React.Fragment>
                    );
                  })}
                </div>
              </div>
            )}

            {/* List + detail */}
            {view === "list" && (
              <div style={{ flex: 1, display: "flex", overflow: "hidden" }}>
                <div style={{ width: 280, flexShrink: 0, borderRight: `1px solid ${DS.rule}`, background: DS.paper, overflowY: "auto", display: "flex", flexDirection: "column" }}>
                  {results.map((r, i) => (
                    <React.Fragment key={r.id || i}>
                      {i > 0 && <Rule />}
                      <ItemRow result={r} index={i} selected={selected === i} onClick={() => setSelected(i)} />
                    </React.Fragment>
                  ))}
                </div>
                <div style={{ flex: 1, overflow: "hidden", display: "flex", flexDirection: "column" }}>
                  {selected !== null && results[selected] && (
                    <ItemDetail result={results[selected]}
                      onSimulate={() => handleSimulate([selected])}
                      simulating={simulating} />
                  )}
                </div>
              </div>
            )}
          </div>
        )}
      </main>

      {showFacetMap && <FacetMapModal onClose={() => setShowFacetMap(false)} />}
      {showKeyModal && <ApiKeyModal onClose={() => setShowKeyModal(false)} onSaved={handleKeySaved} />}

      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Source+Serif+4:ital,opsz,wght@0,8..60,400;0,8..60,500;0,8..60,600;1,8..60,400;1,8..60,500&family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400;600&display=swap');
        @keyframes ds-prog { 0%{width:0%;margin-left:0} 50%{width:60%;margin-left:20%} 100%{width:0%;margin-left:100%} }
      `}</style>
    </div>
  );
}

Object.assign(window, { VariationA });
