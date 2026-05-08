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
  const avgAgreement  = items.reduce((s, r) => s + r.judge_report.overall_agreement, 0)  / items.length;
  const avgConfidence = items.reduce((s, r) => s + r.judge_report.overall_confidence, 0) / items.length;
  const issueCount    = items.reduce((s, r) => s + r.judge_report.issues.length, 0);

  return (
    <div style={{ background: DS.paper, border: `1px solid ${DS.ruleStrong}`, borderRadius: DS.rlg, overflow: "hidden" }}>
      <div style={{ padding: "14px 20px", display: "flex", gap: 32, flexWrap: "wrap" }}>
        {[
          { label: "Items",          value: items.length,                                  color: DS.ink },
          { label: "Avg. Agreement", value: `${Math.round(avgAgreement * 100)}%`,           color: DS.matchFg },
          { label: "Avg. Confidence",value: `${Math.round(avgConfidence * 100)}%`,          color: DS.goalFg },
          { label: "Issues",         value: issueCount === 0 ? "None" : issueCount,         color: issueCount > 0 ? DS.mismatchFg : DS.matchFg },
        ].map(s => (
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
  const agree = judge_report.overall_agreement;
  const agreeColor = agree >= 0.9 ? DS.matchFg : agree >= 0.7 ? DS.partialFg : DS.mismatchFg;
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
          {item.stem.slice(0, 85)}…
        </div>
        {isAuto && (
          <span style={{ fontSize: 9, fontFamily: FM, fontWeight: 600, letterSpacing: "0.06em", textTransform: "uppercase", color: DS.accent, background: DS.accentSoft, padding: "1px 5px", borderRadius: DS.r, flexShrink: 0 }}>auto</span>
        )}
      </div>
      <div style={{ display: "flex", gap: 10, alignItems: "center", paddingLeft: 26 }}>
        <span style={{ fontSize: 10.5, fontFamily: FM, color: agreeColor, fontWeight: 600, letterSpacing: "0.04em" }}>{Math.round(agree * 100)}% agree</span>
        <span style={{ fontSize: 10.5, fontFamily: FM, color: DS.inkMuted, letterSpacing: "0.04em" }}>{Math.round(judge_report.overall_confidence * 100)}% conf</span>
        {judge_report.issues.length > 0 && <span style={{ fontSize: 10.5, fontFamily: FM, color: DS.mismatchFg, fontWeight: 600, letterSpacing: "0.04em" }}>{judge_report.issues.length} issue{judge_report.issues.length > 1 ? "s" : ""}</span>}
        <div style={{ flex: 1 }} />
        <TagRow tags={item.target_facets.slice(0, 3)} small />
      </div>
    </div>
  );
}

/* ── Item detail ──────────────────────────────────────────────────── */

function ItemDetail({ result }) {
  const [tab, setTab] = React.useState("item");
  React.useEffect(() => { setTab("item"); }, [result]);

  const item = result.item;
  const jr   = result.judge_report;
  const isAuto = !!result.facet_selection_reasoning;

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
        <button style={tabStyle(tab === "judge")} onClick={() => setTab("judge")}>Judge Report</button>
        <div style={{ flex: 1 }} />
        <div style={{ display: "flex", alignItems: "center", gap: 10, paddingRight: 4 }}>
          <span style={{ fontSize: 10.5, fontFamily: FM, color: DS.inkMuted, letterSpacing: "0.04em" }}>
            agree <strong style={{ color: DS.matchFg }}>{Math.round(jr.overall_agreement * 100)}%</strong>
          </span>
          <span style={{ fontSize: 10.5, fontFamily: FM, color: DS.inkMuted, letterSpacing: "0.04em" }}>
            conf <strong style={{ color: DS.ink }}>{Math.round(jr.overall_confidence * 100)}%</strong>
          </span>
        </div>
      </div>

      <div style={{ flex: 1, overflowY: "auto", padding: "20px 22px", display: "flex", flexDirection: "column", gap: 14, background: DS.paper2 }}>
        {tab === "item" && (
          <>
            {/* Facet selection reasoning (auto mode) */}
            {isAuto && (
              <div style={{ background: DS.accentSoft, border: `1px solid ${DS.accent}`, borderRadius: DS.rlg, padding: "12px 16px", display: "flex", gap: 10, alignItems: "flex-start" }}>
                <span style={{ fontSize: 9, fontFamily: FM, fontWeight: 600, letterSpacing: "0.06em", textTransform: "uppercase", color: "#fff", background: DS.accent, padding: "2px 6px", borderRadius: DS.r, flexShrink: 0, marginTop: 2 }}>auto-selected</span>
                <p style={{ margin: 0, fontSize: 12.5, lineHeight: 1.6, color: DS.accentInk, fontFamily: FS, fontStyle: "italic" }}>
                  {result.facet_selection_reasoning}
                </p>
              </div>
            )}

            {/* Stem */}
            <div style={{ background: DS.paper, border: `1px solid ${DS.ruleStrong}`, borderRadius: DS.rlg, padding: "18px 20px" }}>
              <MonoLabel action={<TagRow tags={item.target_facets} />}>Stem</MonoLabel>
              <p style={{ fontSize: 16, lineHeight: 1.7, color: DS.ink, fontFamily: FS, margin: 0 }}>{item.stem}</p>
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
                      <span style={{ fontSize: 14, lineHeight: 1.65, color: DS.ink, fontFamily: FS }}>{opt.text}</span>
                    </div>
                    <div style={{ paddingLeft: 30, display: "flex", gap: 6, flexWrap: "wrap", alignItems: "flex-start" }}>
                      <TagRow tags={opt.facet_tags} />
                      <span style={{ fontSize: 11.5, color: DS.ink3, fontFamily: FS, fontStyle: "italic", lineHeight: 1.5 }}>— {opt.rationale}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div style={{ background: DS.paper, border: `1px solid ${DS.ruleStrong}`, borderRadius: DS.rlg, padding: "14px 20px" }}>
              <MonoLabel>Explanation</MonoLabel>
              <p style={{ margin: 0, fontSize: 13.5, lineHeight: 1.75, color: DS.ink2, fontFamily: FS, fontStyle: "italic" }}>{item.explanation}</p>
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
              <div style={{ flex: 1, minWidth: 160 }}>
                <MonoLabel>Issues</MonoLabel>
                {jr.issues.length === 0
                  ? <span style={{ fontSize: 12.5, color: DS.matchFg, fontFamily: FS, fontStyle: "italic" }}>No issues</span>
                  : jr.issues.map((iss, i) => <div key={i} style={{ fontSize: 12.5, color: DS.mismatchFg, fontFamily: FN, lineHeight: 1.5 }}>{iss}</div>)}
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
                        <p style={{ margin: 0, fontSize: 13.5, color: DS.ink2, fontFamily: FS, fontStyle: "italic", lineHeight: 1.5 }}>{opt?.text}</p>
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
      .filter(item => item.item && item.judge_report)
      .sort((a, b) => (a.created_at || "").localeCompare(b.created_at || ""))
  );
}

/* ── Main app ────────────────────────────────────────────────────── */

function VariationA() {
  const allGoalIds = FACET_MAP.facets.filter(f => f.type === "goal").map(f => f.id);
  const allBadIds  = FACET_MAP.facets.filter(f => f.type === "problematic").map(f => f.id);

  const [autoSelect,  setAutoSelect]  = React.useState(false);
  const [selectedFacets, setSelectedFacets] = React.useState([]);
  const [format,     setFormat]     = React.useState("single_select");
  const [bookMode,   setBookMode]   = React.useState("none");
  const [numOptions, setNumOptions] = React.useState(4);
  const [nItems,     setNItems]     = React.useState(4);

  const [results,     setResults]     = React.useState([]);
  const [loadedPath,  setLoadedPath]  = React.useState(null);
  const [loadError,   setLoadError]   = React.useState(null);
  const [selected,    setSelected]    = React.useState(0);
  const [view,        setView]        = React.useState("list");
  const [showFacetMap, setShowFacetMap] = React.useState(false);

  const fileInputRef = React.useRef(null);
  const dirInputRef  = React.useRef(null);

  const handleFilesSelected = (fileList, label) => {
    setLoadError(null);
    loadJsonFiles(fileList).then(items => {
      if (items.length === 0) {
        setLoadError("No valid artifact JSON files found.");
        return;
      }
      setResults(items);
      setSelected(0);
      setView("list");
      setLoadedPath(label || `${items.length} file(s)`);
    }).catch(() => setLoadError("Failed to parse JSON files."));
  };

  const toggleFacet = id =>
    setSelectedFacets(prev => prev.includes(id) ? prev.filter(f => f !== id) : [...prev, id]);

  const canRun = autoSelect || selectedFacets.length > 0;

  const handleExport = () => {
    const blob = new Blob([JSON.stringify(results, null, 2)], { type: "application/json" });
    const a = document.createElement("a"); a.href = URL.createObjectURL(blob); a.download = "assessment_items.json"; a.click();
  };

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
          <div style={{ display: "flex", gap: 8 }}>
            <div style={{ flex: 1 }}>
              <FormField label="Options">
                <Select value={String(numOptions)} onChange={v => setNumOptions(Number(v))} options={[3,4,5,6].map(n => ({ value: String(n), label: String(n) }))} />
              </FormField>
            </div>
            <div style={{ flex: 1 }}>
              <FormField label="Items">
                <Select value={String(nItems)} onChange={v => setNItems(Number(v))} options={[1,2,3,4,5,6,8,10].map(n => ({ value: String(n), label: String(n) }))} />
              </FormField>
            </div>
          </div>
        </div>

        <button disabled={!canRun} style={{
          padding: "8px 0", borderRadius: DS.r,
          background: canRun ? DS.ink : DS.paper3,
          color: canRun ? DS.paper : DS.inkMuted,
          border: `1px solid ${canRun ? DS.ink : DS.ruleStrong}`,
          fontSize: 12.5, fontWeight: 500, cursor: canRun ? "pointer" : "not-allowed",
          fontFamily: FN, transition: "all 0.15s",
        }}>
          Generate {nItems} Item{nItems > 1 ? "s" : ""}
        </button>

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
            <Btn onClick={handleExport} small>Download JSON</Btn>
          )}
        </div>
      </aside>

      {/* ── Main area ── */}
      <main style={{ flex: 1, display: "flex", flexDirection: "column", overflow: "hidden", background: DS.paper2 }}>
        {results.length === 0 && (
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
            </div>

            {/* Aggregate */}
            {view === "aggregate" && (
              <div style={{ flex: 1, minHeight: 0, overflowY: "auto", padding: "20px 22px", display: "flex", flexDirection: "column", gap: 14 }}>
                <AggregateBar items={results} />
                <FacetCoverage items={results} />
                <div style={{ background: DS.paper, border: `1px solid ${DS.ruleStrong}`, borderRadius: DS.rlg, overflow: "hidden" }}>
                  <div style={{ padding: "12px 18px", borderBottom: `1px solid ${DS.rule}` }}>
                    <MonoLabel style={{ marginBottom: 0 }}>Per-item breakdown</MonoLabel>
                  </div>
                  {results.map((r, i) => (
                    <React.Fragment key={r.id || i}>
                      {i > 0 && <Rule />}
                      <div style={{ padding: "11px 18px", display: "flex", gap: 12, alignItems: "center" }}>
                        <span style={{ width: 18, height: 18, borderRadius: 2, flexShrink: 0, background: DS.paper3, color: DS.inkMuted, display: "flex", alignItems: "center", justifyContent: "center", fontSize: 10, fontWeight: 600, fontFamily: FM, letterSpacing: "0.04em" }}>{i + 1}</span>
                        <div style={{ flex: 1, minWidth: 0 }}>
                          <div style={{ fontSize: 12.5, color: DS.ink2, fontFamily: FS, fontStyle: "italic", marginBottom: 6, whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>{r.item.stem.slice(0, 90)}…</div>
                          <div style={{ display: "flex", gap: 16, alignItems: "center" }}>
                            <div style={{ minWidth: 110 }}><div style={{ fontSize: 10.5, color: DS.inkMuted, fontFamily: FM, letterSpacing: "0.04em", textTransform: "uppercase", marginBottom: 3 }}>Agreement</div><ScoreBar value={r.judge_report.overall_agreement} color={DS.matchFg} /></div>
                            <div style={{ minWidth: 110 }}><div style={{ fontSize: 10.5, color: DS.inkMuted, fontFamily: FM, letterSpacing: "0.04em", textTransform: "uppercase", marginBottom: 3 }}>Confidence</div><ScoreBar value={r.judge_report.overall_confidence} color={DS.goalFg} /></div>
                            <div style={{ flex: 1 }}><TagRow tags={r.item.target_facets} small /></div>
                          </div>
                        </div>
                        <Btn small onClick={() => { setSelected(i); setView("list"); }}>View</Btn>
                      </div>
                    </React.Fragment>
                  ))}
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
                  {selected !== null && results[selected] && <ItemDetail result={results[selected]} />}
                </div>
              </div>
            )}
          </div>
        )}
      </main>

      {showFacetMap && <FacetMapModal onClose={() => setShowFacetMap(false)} />}

      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Source+Serif+4:ital,opsz,wght@0,8..60,400;0,8..60,500;0,8..60,600;1,8..60,400;1,8..60,500&family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400;600&display=swap');
        @keyframes ds-prog { 0%{width:0%;margin-left:0} 50%{width:60%;margin-left:20%} 100%{width:0%;margin-left:100%} }
      `}</style>
    </div>
  );
}

Object.assign(window, { VariationA });
