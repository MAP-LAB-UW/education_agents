// Evaluation Comparison Dashboard
// Loads eval result JSONs + artifact directories, shows side-by-side metrics

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
  matchFg:     "oklch(0.38 0.09 150)",
  matchBg:     "oklch(0.96 0.02 150)",
  partialFg:   "oklch(0.45 0.12 70)",
  mismatchFg:  "oklch(0.55 0.12 25)",
  goalFg:      "oklch(0.38 0.09 245)",
  goalBg:      "oklch(0.96 0.02 240)",
  badFg:       "oklch(0.42 0.10 335)",
  r:           3,
  rlg:         6,
};

const FS = "'Source Serif 4', 'Source Serif Pro', Georgia, serif";
const FN = "'Inter', -apple-system, BlinkMacSystemFont, sans-serif";
const FM = "'JetBrains Mono', ui-monospace, Menlo, monospace";

const PALETTE = [
  "oklch(0.55 0.15 250)",
  "oklch(0.58 0.14 150)",
  "oklch(0.55 0.14 30)",
  "oklch(0.55 0.14 330)",
  "oklch(0.58 0.12 70)",
  "oklch(0.55 0.12 200)",
];

/* ── Helpers ──────────────────────────────────────────────────────── */

function summarizeDataset(ds) {
  const items = ds.item_evaluations || [];
  const arts = ds._artifacts || [];
  const n = items.length || arts.length || ds.n_items || 0;

  const hasItemEval = items.length > 0;
  const hasCorpus = !!ds.corpus_evaluation;

  // Judge data: prefer per-item judge fields in eval JSONs, fall back to artifacts
  let judge = null;
  const hasJudgeInItems = items.length > 0 && items.some(it => it.judge);
  const hasJudgeInArts = arts.length > 0 && arts[0]?.judge_report;

  if (hasJudgeInItems) {
    const judgeItems = items.filter(it => it.judge);
    const agreements = judgeItems.map(it => it.judge.overall_agreement);
    const confidences = judgeItems.map(it => it.judge.overall_confidence);
    const issues = judgeItems.reduce((s, it) => s + (it.judge.issues?.length || 0), 0);
    judge = {
      mean_agreement: agreements.reduce((a, b) => a + b, 0) / agreements.length,
      mean_confidence: confidences.reduce((a, b) => a + b, 0) / confidences.length,
      total_issues: issues,
    };
  } else if (hasJudgeInArts) {
    const agreements = arts.map(a => a.judge_report.overall_agreement);
    const confidences = arts.map(a => a.judge_report.overall_confidence);
    const issues = arts.reduce((s, a) => s + a.judge_report.issues.length, 0);
    judge = {
      mean_agreement: agreements.reduce((a, b) => a + b, 0) / agreements.length,
      mean_confidence: confidences.reduce((a, b) => a + b, 0) / confidences.length,
      total_issues: issues,
    };
  }
  const hasJudge = !!judge;

  let itemMetrics = null;
  if (hasItemEval) {
    const correctCount = items.filter(r => r.correctness.is_correct).length;
    const hasLLM = items[0].naturalness.stem_score > 0;
    const figItems = items.filter(r => r.figure_necessity != null);
    itemMetrics = {
      correctness_pct: correctCount / items.length,
      correctness_count: correctCount,
      flagged_distractors: items.reduce((s, r) => s + r.correctness.flagged_distractors.length, 0),
      naturalness_stem: hasLLM ? items.reduce((s, r) => s + r.naturalness.stem_score, 0) / items.length : null,
      naturalness_options: hasLLM ? items.reduce((s, r) => s + r.naturalness.options_score, 0) / items.length : null,
      naturalness_overall: hasLLM ? items.reduce((s, r) => s + r.naturalness.overall_score, 0) / items.length : null,
      latency_score: items.reduce((s, r) => s + (r.facet_latency.score || 0), 0) / items.length,
      latency_similarity: items.reduce((s, r) => s + (r.facet_latency.mean_similarity || 0), 0) / items.length,
      figure_items: figItems.length,
      figure_necessity_avg: figItems.length > 0 ? figItems.reduce((s, r) => s + r.figure_necessity, 0) / figItems.length : null,
    };
  }

  return { n, hasItemEval, hasCorpus, hasJudge, judge, itemMetrics, corpus: ds.corpus_evaluation };
}

/* ── Primitives ───────────────────────────────────────────────────── */

function Bar({ value, max, color, width = 120, height = 14 }) {
  const pct = max > 0 ? Math.min(value / max, 1) : 0;
  return (
    <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
      <div style={{ width, height, borderRadius: 2, background: DS.paper3, overflow: "hidden", flexShrink: 0 }}>
        <div style={{ width: `${pct * 100}%`, height: "100%", borderRadius: 2, background: color, transition: "width 0.4s" }} />
      </div>
    </div>
  );
}

function MetricCell({ value, fmt, color, subtext }) {
  return (
    <div style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 2 }}>
      <span style={{ fontSize: 16, fontWeight: 600, fontFamily: FN, color: color || DS.ink, lineHeight: 1 }}>{fmt || value}</span>
      {subtext && <span style={{ fontSize: 9.5, fontFamily: FM, color: DS.inkMuted, letterSpacing: "0.04em" }}>{subtext}</span>}
    </div>
  );
}

function SectionHeader({ children }) {
  return (
    <div style={{ padding: "14px 0 8px", borderBottom: `1px solid ${DS.rule}`, marginBottom: 12, marginTop: 16 }}>
      <span style={{ fontSize: 11, fontWeight: 600, letterSpacing: "0.12em", textTransform: "uppercase", color: DS.ink3, fontFamily: FM }}>{children}</span>
    </div>
  );
}

function ComparisonTable({ rows, datasets, summaries }) {
  const minCol = 140;
  const metricW = 200;
  const tableMinW = metricW + datasets.length * minCol;

  return (
    <div style={{ background: DS.paper, border: `1px solid ${DS.ruleStrong}`, borderRadius: DS.rlg, overflowX: "auto" }}>
      <div style={{ minWidth: tableMinW }}>
        {/* Header */}
        <div style={{ display: "flex", borderBottom: `2px solid ${DS.rule}`, background: DS.paper }}>
          <div style={{ width: metricW, flexShrink: 0, padding: "12px 16px", fontSize: 10.5, fontFamily: FM, fontWeight: 600, letterSpacing: "0.1em", textTransform: "uppercase", color: DS.ink3 }}>Metric</div>
          {datasets.map((ds, i) => (
            <div key={i} style={{ flex: 1, minWidth: minCol, padding: "12px 10px", textAlign: "center", borderLeft: `1px solid ${DS.rule}` }}>
              <div style={{ display: "flex", alignItems: "center", justifyContent: "center", gap: 6 }}>
                <span style={{ width: 8, height: 8, borderRadius: 4, background: PALETTE[i % PALETTE.length], flexShrink: 0 }} />
                <span style={{ fontSize: 11.5, fontWeight: 600, fontFamily: FN, color: DS.ink, letterSpacing: "-0.01em", wordBreak: "break-word" }}>{ds._label}</span>
              </div>
              <div style={{ fontSize: 10, fontFamily: FM, color: DS.inkMuted, marginTop: 2 }}>{summaries[i].n} items</div>
            </div>
          ))}
        </div>
        {/* Rows */}
        {rows.map((row, ri) => {
          if (row.type === "header") {
            return (
              <div key={ri} style={{ padding: "10px 16px", background: DS.paper3, borderTop: ri > 0 ? `1px solid ${DS.rule}` : "none" }}>
                <span style={{ fontSize: 10, fontWeight: 600, letterSpacing: "0.12em", textTransform: "uppercase", color: DS.ink3, fontFamily: FM }}>{row.label}</span>
              </div>
            );
          }
          return (
            <div key={ri} style={{ display: "flex", borderTop: `1px solid ${DS.rule}`, alignItems: "center" }}>
              <div style={{ width: metricW, flexShrink: 0, padding: "10px 16px" }}>
                <div style={{ fontSize: 12, fontFamily: FN, color: DS.ink2, fontWeight: 500 }}>{row.label}</div>
                {row.sublabel && <div style={{ fontSize: 10, fontFamily: FM, color: DS.inkMuted, marginTop: 1 }}>{row.sublabel}</div>}
              </div>
              {datasets.map((ds, i) => {
                const val = row.getValue(summaries[i], i);
                return (
                  <div key={i} style={{ flex: 1, minWidth: minCol, padding: "10px", textAlign: "center", borderLeft: `1px solid ${DS.rule}`, display: "flex", flexDirection: "column", alignItems: "center", gap: 4 }}>
                    {val !== null && val !== undefined ? (
                      <>
                        <span style={{ fontSize: 15, fontWeight: 600, fontFamily: FN, color: val.color || DS.ink }}>{val.display}</span>
                        {val.bar && <Bar value={val.bar.value} max={val.bar.max} color={PALETTE[i % PALETTE.length]} width={90} />}
                        {val.sub && <span style={{ fontSize: 9.5, fontFamily: FM, color: DS.inkMuted }}>{val.sub}</span>}
                      </>
                    ) : (
                      <span style={{ fontSize: 11, fontFamily: FM, color: DS.inkMuted }}>—</span>
                    )}
                  </div>
                );
              })}
            </div>
          );
        })}
      </div>
    </div>
  );
}

/* ── Per-item detail table ─────────────────────────────────────────── */

function ItemDetailTable({ datasets, summaries }) {
  const hasAny = datasets.some(ds => (ds.item_evaluations || []).length > 0);
  if (!hasAny) return null;

  const maxItems = Math.max(...datasets.map(ds => (ds.item_evaluations || []).length));
  const hasJudgeData = datasets.some(ds => {
    const items = ds.item_evaluations || [];
    return items.some(it => it.judge) || (ds._artifacts || []).some(a => a.judge_report);
  });
  const hasFigNec = datasets.some(ds => (ds.item_evaluations || []).some(it => it.figure_necessity != null));
  const colSpan = (hasJudgeData ? 6 : 4) + (hasFigNec ? 1 : 0);

  const getJudge = (ds, idx) => {
    const items = ds.item_evaluations || [];
    if (items[idx]?.judge) return items[idx].judge;
    const arts = ds._artifacts || [];
    if (arts[idx]?.judge_report) return arts[idx].judge_report;
    return null;
  };

  return (
    <div style={{ background: DS.paper, border: `1px solid ${DS.ruleStrong}`, borderRadius: DS.rlg, overflow: "hidden" }}>
      <div style={{ padding: "12px 16px", borderBottom: `1px solid ${DS.rule}`, background: DS.paper }}>
        <span style={{ fontSize: 10.5, fontWeight: 600, letterSpacing: "0.12em", textTransform: "uppercase", color: DS.ink3, fontFamily: FM }}>Per-Item Scores</span>
      </div>
      <div style={{ overflowX: "auto" }}>
        <table style={{ width: "100%", borderCollapse: "collapse", fontSize: 12, fontFamily: FN }}>
          <thead>
            <tr style={{ borderBottom: `2px solid ${DS.rule}` }}>
              <th style={thStyle}>#</th>
              {datasets.map((ds, i) => (
                <React.Fragment key={i}>
                  <th style={{ ...thStyle, borderLeft: `2px solid ${DS.ruleStrong}`, color: PALETTE[i % PALETTE.length] }} colSpan={colSpan}>{ds._label}</th>
                </React.Fragment>
              ))}
            </tr>
            <tr style={{ borderBottom: `1px solid ${DS.rule}` }}>
              <th style={thStyle}></th>
              {datasets.map((ds, i) => (
                <React.Fragment key={i}>
                  <th style={{ ...thStyle, borderLeft: i === 0 ? `2px solid ${DS.ruleStrong}` : `1px solid ${DS.rule}`, fontSize: 9 }}>Correct</th>
                  <th style={{ ...thStyle, fontSize: 9 }}>Natural</th>
                  <th style={{ ...thStyle, fontSize: 9 }}>Latency</th>
                  <th style={{ ...thStyle, fontSize: 9 }}>Sim</th>
                  {hasFigNec && <th style={{ ...thStyle, fontSize: 9 }}>Fig</th>}
                  {hasJudgeData && <th style={{ ...thStyle, fontSize: 9 }}>Agree</th>}
                  {hasJudgeData && <th style={{ ...thStyle, fontSize: 9 }}>Conf</th>}
                </React.Fragment>
              ))}
            </tr>
          </thead>
          <tbody>
            {Array.from({ length: maxItems }, (_, idx) => (
              <tr key={idx} style={{ borderTop: `1px solid ${DS.rule}` }}>
                <td style={tdStyle}>{idx + 1}</td>
                {datasets.map((ds, i) => {
                  const items = ds.item_evaluations || [];
                  const item = items[idx];
                  if (!item) return (
                    <React.Fragment key={i}>
                      <td style={{ ...tdStyle, borderLeft: i === 0 ? `2px solid ${DS.ruleStrong}` : `1px solid ${DS.rule}` }} colSpan={colSpan}>
                        <span style={{ color: DS.inkMuted }}>—</span>
                      </td>
                    </React.Fragment>
                  );
                  const hasLLM = item.naturalness.stem_score > 0;
                  const jd = getJudge(ds, idx);
                  const agr = jd?.overall_agreement;
                  const conf = jd?.overall_confidence;
                  return (
                    <React.Fragment key={i}>
                      <td style={{ ...tdStyle, borderLeft: i === 0 ? `2px solid ${DS.ruleStrong}` : `1px solid ${DS.rule}`, color: item.correctness.is_correct ? DS.matchFg : DS.mismatchFg, fontWeight: 600 }}>
                        {item.correctness.is_correct ? "Pass" : "Fail"}
                      </td>
                      <td style={tdStyle}>{hasLLM ? `${item.naturalness.overall_score}/5` : "—"}</td>
                      <td style={{ ...tdStyle, color: item.facet_latency.score >= 3 ? DS.matchFg : item.facet_latency.score >= 2 ? DS.partialFg : DS.mismatchFg }}>
                        {item.facet_latency.score}/4
                      </td>
                      <td style={{ ...tdStyle, color: DS.inkMuted, fontSize: 10.5, fontFamily: FM }}>{item.facet_latency.mean_similarity.toFixed(3)}</td>
                      {hasFigNec && (
                        <td style={{ ...tdStyle, fontWeight: 600, fontSize: 10.5, fontFamily: FM, color: item.figure_necessity != null ? (item.figure_necessity === 1 ? DS.matchFg : DS.mismatchFg) : DS.inkMuted }}>
                          {item.figure_necessity != null ? item.figure_necessity : "—"}
                        </td>
                      )}
                      {hasJudgeData && (
                        <td style={{ ...tdStyle, color: agr != null ? (agr >= 0.8 ? DS.matchFg : agr >= 0.5 ? DS.partialFg : DS.mismatchFg) : DS.inkMuted, fontWeight: 600, fontSize: 10.5, fontFamily: FM }}>
                          {agr != null ? `${Math.round(agr * 100)}%` : "—"}
                        </td>
                      )}
                      {hasJudgeData && (
                        <td style={{ ...tdStyle, color: DS.ink2, fontSize: 10.5, fontFamily: FM }}>
                          {conf != null ? `${Math.round(conf * 100)}%` : "—"}
                        </td>
                      )}
                    </React.Fragment>
                  );
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

const thStyle = { padding: "8px 8px", fontSize: 10, fontFamily: FM, fontWeight: 600, letterSpacing: "0.06em", textTransform: "uppercase", color: DS.ink3, textAlign: "center" };
const tdStyle = { padding: "7px 8px", textAlign: "center", fontSize: 12 };

const btnStyle = {
  padding: "7px 14px", borderRadius: DS.r,
  background: DS.paper, color: DS.ink,
  border: `1px solid ${DS.ruleStrong}`,
  fontSize: 12, fontWeight: 500, cursor: "pointer",
  fontFamily: FN,
};

/* ── Facet coverage heatmap ────────────────────────────────────────── */

function FacetHeatmap({ datasets, summaries }) {
  const hasCoverage = summaries.some(s => s.corpus && s.corpus.facet_coverage);
  if (!hasCoverage) return null;

  const allFacets = [];
  summaries.forEach(s => {
    if (s.corpus && s.corpus.facet_coverage) {
      Object.keys(s.corpus.facet_coverage.facet_counts).forEach(fid => {
        if (!allFacets.includes(fid)) allFacets.push(fid);
      });
    }
  });
  allFacets.sort();

  const goalFacets = allFacets.filter(f => f.startsWith("A"));
  const badFacets = allFacets.filter(f => f.startsWith("B"));

  const maxCount = Math.max(1, ...summaries.flatMap(s =>
    s.corpus && s.corpus.facet_coverage ? Object.values(s.corpus.facet_coverage.facet_counts) : [0]
  ));

  const renderRow = (facets, label, fg) => (
    <>
      <tr>
        <td colSpan={datasets.length + 1} style={{ padding: "8px 12px", fontSize: 10, fontFamily: FM, fontWeight: 600, letterSpacing: "0.1em", textTransform: "uppercase", color: fg, background: DS.paper3 }}>
          {label}
        </td>
      </tr>
      {facets.map(fid => (
        <tr key={fid} style={{ borderTop: `1px solid ${DS.rule}` }}>
          <td style={{ padding: "5px 12px", fontSize: 11, fontFamily: FM, fontWeight: 600, color: fg }}>{fid}</td>
          {summaries.map((s, i) => {
            const count = s.corpus?.facet_coverage?.facet_counts?.[fid] || 0;
            const intensity = count / maxCount;
            return (
              <td key={i} style={{ padding: "5px 8px", textAlign: "center", borderLeft: `1px solid ${DS.rule}` }}>
                <div style={{ display: "flex", alignItems: "center", justifyContent: "center", gap: 4 }}>
                  <div style={{ width: 40, height: 10, borderRadius: 2, background: DS.paper3, overflow: "hidden" }}>
                    <div style={{ width: `${intensity * 100}%`, height: "100%", background: PALETTE[i % PALETTE.length], opacity: 0.7 }} />
                  </div>
                  <span style={{ fontSize: 10, fontFamily: FM, color: count > 0 ? DS.ink2 : DS.inkMuted }}>{count}</span>
                </div>
              </td>
            );
          })}
        </tr>
      ))}
    </>
  );

  return (
    <div style={{ background: DS.paper, border: `1px solid ${DS.ruleStrong}`, borderRadius: DS.rlg, overflow: "hidden" }}>
      <div style={{ padding: "12px 16px", borderBottom: `1px solid ${DS.rule}` }}>
        <span style={{ fontSize: 10.5, fontWeight: 600, letterSpacing: "0.12em", textTransform: "uppercase", color: DS.ink3, fontFamily: FM }}>Facet Coverage Heatmap</span>
      </div>
      <table style={{ width: "100%", borderCollapse: "collapse" }}>
        <thead>
          <tr style={{ borderBottom: `2px solid ${DS.rule}` }}>
            <th style={{ padding: "8px 12px", fontSize: 10, fontFamily: FM, fontWeight: 600, color: DS.ink3, textAlign: "left", width: 60 }}>Facet</th>
            {datasets.map((ds, i) => (
              <th key={i} style={{ padding: "8px 8px", fontSize: 10, fontFamily: FM, fontWeight: 600, color: PALETTE[i % PALETTE.length], textAlign: "center", borderLeft: `1px solid ${DS.rule}` }}>{ds._label}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {renderRow(goalFacets, "Goal (A)", DS.goalFg)}
          {renderRow(badFacets, "Problematic (B)", DS.badFg)}
        </tbody>
      </table>
    </div>
  );
}

/* ── Radar-style summary (simple bar comparison) ───────────────────── */

function MetricBars({ label, datasets, values, max, unit }) {
  return (
    <div style={{ marginBottom: 12 }}>
      <div style={{ fontSize: 11, fontFamily: FN, fontWeight: 500, color: DS.ink2, marginBottom: 5 }}>{label}</div>
      {datasets.map((ds, i) => {
        const v = values[i];
        if (v === null || v === undefined) return null;
        return (
          <div key={i} style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 3 }}>
            <span style={{ width: 8, height: 8, borderRadius: 4, background: PALETTE[i % PALETTE.length], flexShrink: 0 }} />
            <Bar value={v} max={max} color={PALETTE[i % PALETTE.length]} width={140} />
            <span style={{ fontSize: 12, fontFamily: FM, fontWeight: 600, color: DS.ink, minWidth: 50 }}>
              {typeof v === "number" ? (v % 1 === 0 ? v : v.toFixed(v < 1 ? 3 : 1)) : v}{unit || ""}
            </span>
          </div>
        );
      })}
    </div>
  );
}

/* ── File loading ──────────────────────────────────────────────────── */

function loadFiles(fileList) {
  return Promise.all(
    Array.from(fileList)
      .filter(f => f.name.endsWith(".json"))
      .map(f => new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = () => {
          try { resolve({ name: f.name, path: f.webkitRelativePath || f.name, data: JSON.parse(reader.result) }); }
          catch (e) { reject(e); }
        };
        reader.onerror = reject;
        reader.readAsText(f);
      }))
  );
}

function classifyFile(parsed) {
  const d = parsed.data;
  if (d.item_evaluations || d.corpus_evaluation) return "eval_result";
  if (d.item && d.judge_report) return "artifact";
  return "unknown";
}

/* ── Main app ──────────────────────────────────────────────────────── */

function CompareApp() {
  const [datasets, setDatasets] = React.useState([]);
  const [tab, setTab] = React.useState("overview");

  const evalInputRef = React.useRef(null);
  const artifactDirRef = React.useRef(null);

  const addEvalFiles = (fileList) => {
    loadFiles(fileList).then(parsed => {
      const newSets = [];
      // Group: if files are artifacts from a dir, combine them; if eval result, use directly
      const evalResults = parsed.filter(p => classifyFile(p) === "eval_result");
      const artifacts = parsed.filter(p => classifyFile(p) === "artifact");

      evalResults.forEach(p => {
        const label = p.data.source || p.data.input_dir?.replace(/.*\//, "") || p.name.replace(".json", "");
        newSets.push({ ...p.data, _label: label, _type: "eval" });
      });

      if (artifacts.length > 0) {
        const dirParts = artifacts[0].path.split("/");
        const dirName = dirParts.length > 1 ? dirParts[dirParts.length - 2] : "artifacts";
        const sorted = artifacts.map(a => a.data).sort((a, b) => (a.created_at || "").localeCompare(b.created_at || ""));

        // Build judge-only dataset from artifacts
        const judgeAgg = {
          _label: dirName,
          _type: "artifacts",
          _artifacts: sorted,
          n_items: sorted.length,
        };

        // If artifacts have eval_scores, convert to item_evaluations
        if (sorted.some(a => a.eval_scores)) {
          judgeAgg.item_evaluations = sorted.filter(a => a.eval_scores).map((a, i) => ({
            source: a.created_at?.slice(0, 19) || `item_${i+1}`,
            correctness: {
              selected_answer: "",
              correct_answer_ids: a.item.correct_option_ids,
              is_correct: a.eval_scores.correctness_pass,
              flagged_distractors: a.eval_scores.correctness_flagged_distractors || [],
              reasoning: "",
            },
            naturalness: {
              stem_score: a.eval_scores.naturalness_stem,
              stem_reasoning: "",
              options_score: a.eval_scores.naturalness_options,
              options_reasoning: "",
              overall_score: a.eval_scores.naturalness_overall,
            },
            facet_latency: {
              mean_similarity: a.eval_scores.latency_similarity,
              score: a.eval_scores.latency_score,
              bucket: a.eval_scores.latency_bucket,
              option_details: a.eval_scores.latency_option_details || [],
            },
            figure_necessity: a.eval_scores.figure_necessity,
          }));
        }

        newSets.push(judgeAgg);
      }

      setDatasets(prev => [...prev, ...newSets]);
    });
  };

  const removeDataset = (idx) => {
    setDatasets(prev => prev.filter((_, i) => i !== idx));
  };

  const summaries = datasets.map(summarizeDataset);

  const rows = buildComparisonRows(summaries);

  const tabStyle = active => ({
    padding: "9px 18px", border: "none", background: "transparent",
    borderBottom: `2px solid ${active ? DS.accent : "transparent"}`,
    color: active ? DS.accentInk : DS.inkMuted,
    fontFamily: FM, fontSize: 10.5, fontWeight: 600, letterSpacing: "0.06em",
    textTransform: "uppercase", cursor: "pointer", marginBottom: -1,
  });

  return (
    <div style={{ maxWidth: 1100, margin: "0 auto", padding: "24px 28px", fontFamily: FN }}>
      {/* Header */}
      <div style={{ display: "flex", alignItems: "baseline", gap: 14, marginBottom: 20 }}>
        <span style={{ fontFamily: FS, fontSize: 22, fontWeight: 500, color: DS.ink, letterSpacing: "-0.01em" }}>
          Evaluation <em style={{ fontStyle: "italic", color: DS.accentInk }}>Comparison</em>
        </span>
        <span style={{ fontSize: 10.5, fontFamily: FM, color: DS.inkMuted, letterSpacing: "0.06em", textTransform: "uppercase" }}>Assessment Copilot</span>
      </div>

      {/* Load controls */}
      <div style={{ display: "flex", gap: 10, marginBottom: 20, flexWrap: "wrap", alignItems: "center" }}>
        <input ref={evalInputRef} type="file" accept=".json" multiple style={{ display: "none" }}
          onChange={e => { if (e.target.files.length) addEvalFiles(e.target.files); e.target.value = ""; }} />
        <input ref={artifactDirRef} type="file" webkitdirectory="" style={{ display: "none" }}
          onChange={e => { if (e.target.files.length) addEvalFiles(e.target.files); e.target.value = ""; }} />
        <button onClick={() => evalInputRef.current?.click()} style={btnStyle}>Load Eval JSONs</button>
        <button onClick={() => artifactDirRef.current?.click()} style={btnStyle}>Load Artifact Folder</button>
        {datasets.length > 0 && (
          <button onClick={() => setDatasets([])} style={{ ...btnStyle, color: DS.mismatchFg, borderColor: DS.mismatchFg }}>Clear All</button>
        )}
      </div>

      {/* Loaded datasets */}
      {datasets.length > 0 && (
        <div style={{ display: "flex", gap: 8, flexWrap: "wrap", marginBottom: 20 }}>
          {datasets.map((ds, i) => (
            <div key={i} style={{
              display: "flex", alignItems: "center", gap: 8,
              padding: "6px 12px", borderRadius: DS.rlg,
              background: DS.paper, border: `1px solid ${DS.ruleStrong}`,
            }}>
              <span style={{ width: 8, height: 8, borderRadius: 4, background: PALETTE[i % PALETTE.length] }} />
              <span style={{ fontSize: 12, fontFamily: FN, fontWeight: 500, color: DS.ink }}>{ds._label}</span>
              <span style={{ fontSize: 10, fontFamily: FM, color: DS.inkMuted }}>{summaries[i].n} items</span>
              <button onClick={() => removeDataset(i)} style={{
                background: "none", border: "none", cursor: "pointer", color: DS.inkMuted, fontSize: 14, lineHeight: 1, padding: "0 2px",
              }}>×</button>
            </div>
          ))}
        </div>
      )}

      {/* Empty state */}
      {datasets.length === 0 && (
        <div style={{ textAlign: "center", padding: "60px 20px" }}>
          <div style={{ fontFamily: FS, fontSize: 18, color: DS.ink2, fontStyle: "italic", marginBottom: 8 }}>Load evaluation results to compare</div>
          <div style={{ fontSize: 13, color: DS.ink3, fontFamily: FS, lineHeight: 1.7, maxWidth: 500, margin: "0 auto" }}>
            Load eval result JSONs (from <code style={{ fontFamily: FM, fontSize: 11, background: DS.paper3, padding: "1px 4px", borderRadius: 2 }}>run_evaluation.py</code> or <code style={{ fontFamily: FM, fontSize: 11, background: DS.paper3, padding: "1px 4px", borderRadius: 2 }}>eval_experts.py</code>) or artifact folders to compare metrics side-by-side.
          </div>
        </div>
      )}

      {/* Tabs + content */}
      {datasets.length > 0 && (
        <>
          <div style={{ display: "flex", borderBottom: `1px solid ${DS.rule}`, marginBottom: 18 }}>
            <button style={tabStyle(tab === "overview")} onClick={() => setTab("overview")}>Overview</button>
            <button style={tabStyle(tab === "items")} onClick={() => setTab("items")}>Per-Item</button>
            <button style={tabStyle(tab === "coverage")} onClick={() => setTab("coverage")}>Facet Coverage</button>
          </div>

          {tab === "overview" && (
            <div style={{ display: "flex", flexDirection: "column", gap: 18 }}>
              <ComparisonTable rows={rows} datasets={datasets} summaries={summaries} />

              {/* Visual comparison bars */}
              <div style={{ background: DS.paper, border: `1px solid ${DS.ruleStrong}`, borderRadius: DS.rlg, padding: "18px 22px" }}>
                <div style={{ fontSize: 10.5, fontWeight: 600, letterSpacing: "0.12em", textTransform: "uppercase", color: DS.ink3, fontFamily: FM, marginBottom: 14 }}>Visual Comparison</div>
                <div style={{ display: "flex", gap: 32, flexWrap: "wrap" }}>
                  <div style={{ flex: 1, minWidth: 200 }}>
                    {summaries.some(s => s.judge) && (
                      <MetricBars label="Judge Agreement" datasets={datasets} values={summaries.map(s => s.judge?.mean_agreement)} max={1} unit="" />
                    )}
                    {summaries.some(s => s.itemMetrics) && (
                      <>
                        <MetricBars label="Correctness %" datasets={datasets} values={summaries.map(s => s.itemMetrics?.correctness_pct)} max={1} unit="" />
                        <MetricBars label="Facet Latency Score" datasets={datasets} values={summaries.map(s => s.itemMetrics?.latency_score)} max={4} unit="/4" />
                      </>
                    )}
                  </div>
                  <div style={{ flex: 1, minWidth: 200 }}>
                    {summaries.some(s => s.itemMetrics?.naturalness_overall !== null) && (
                      <MetricBars label="Naturalness" datasets={datasets} values={summaries.map(s => s.itemMetrics?.naturalness_overall)} max={5} unit="/5" />
                    )}
                    {summaries.some(s => s.itemMetrics) && (
                      <MetricBars label="Mean Embedding Similarity" datasets={datasets} values={summaries.map(s => s.itemMetrics?.latency_similarity)} max={1} unit="" />
                    )}
                    {summaries.some(s => s.itemMetrics?.figure_necessity_avg != null) && (
                      <MetricBars label="Figure Necessity" datasets={datasets} values={summaries.map(s => s.itemMetrics?.figure_necessity_avg)} max={1} unit="" />
                    )}
                    {summaries.some(s => s.corpus) && (
                      <MetricBars label="Facet Uniformity" datasets={datasets} values={summaries.map(s => s.corpus?.facet_coverage?.uniformity)} max={1} unit="" />
                    )}
                  </div>
                </div>
              </div>
            </div>
          )}

          {tab === "items" && (
            <ItemDetailTable datasets={datasets} summaries={summaries} />
          )}

          {tab === "coverage" && (
            <FacetHeatmap datasets={datasets} summaries={summaries} />
          )}
        </>
      )}
    </div>
  );
}

/* ── Build comparison rows ─────────────────────────────────────────── */

function buildComparisonRows(summaries) {
  const rows = [];

  // Item-level section (includes judge metrics when available)
  if (summaries.some(s => s.hasItemEval || s.hasJudge)) {
    rows.push({ type: "header", label: "Item-Level Rubrics" });

    if (summaries.some(s => s.hasJudge)) {
      rows.push({
        label: "Judge Agreement", sublabel: "avg",
        getValue: s => s.judge ? { display: `${Math.round(s.judge.mean_agreement * 100)}%`, color: s.judge.mean_agreement >= 0.8 ? DS.matchFg : s.judge.mean_agreement >= 0.5 ? DS.partialFg : DS.mismatchFg, bar: { value: s.judge.mean_agreement, max: 1 } } : null,
      });
      rows.push({
        label: "Judge Confidence", sublabel: "avg",
        getValue: s => s.judge ? { display: `${Math.round(s.judge.mean_confidence * 100)}%`, color: DS.goalFg, bar: { value: s.judge.mean_confidence, max: 1 } } : null,
      });
      rows.push({
        label: "Judge Issues", sublabel: "total",
        getValue: s => s.judge ? { display: s.judge.total_issues, color: s.judge.total_issues > 0 ? DS.mismatchFg : DS.matchFg } : null,
      });
    }
    rows.push({
      label: "Correctness", sublabel: "pass rate",
      getValue: s => s.itemMetrics ? {
        display: `${Math.round(s.itemMetrics.correctness_pct * 100)}%`,
        color: s.itemMetrics.correctness_pct === 1 ? DS.matchFg : DS.mismatchFg,
        sub: `${s.itemMetrics.correctness_count}/${s.n}`,
      } : null,
    });
    rows.push({
      label: "Flagged Distractors", sublabel: "total",
      getValue: s => s.itemMetrics ? { display: s.itemMetrics.flagged_distractors, color: s.itemMetrics.flagged_distractors > 0 ? DS.partialFg : DS.matchFg } : null,
    });
    rows.push({
      label: "Naturalness", sublabel: "overall avg",
      getValue: s => s.itemMetrics?.naturalness_overall !== null ? {
        display: `${s.itemMetrics.naturalness_overall.toFixed(1)}/5`,
        color: DS.goalFg,
        bar: { value: s.itemMetrics.naturalness_overall, max: 5 },
      } : null,
    });
    rows.push({
      label: "Naturalness (Stem)", sublabel: "avg",
      getValue: s => s.itemMetrics?.naturalness_stem !== null ? { display: `${s.itemMetrics.naturalness_stem.toFixed(1)}/5`, color: DS.ink2 } : null,
    });
    rows.push({
      label: "Naturalness (Options)", sublabel: "avg",
      getValue: s => s.itemMetrics?.naturalness_options !== null ? { display: `${s.itemMetrics.naturalness_options.toFixed(1)}/5`, color: DS.ink2 } : null,
    });
    rows.push({
      label: "Facet Latency", sublabel: "score avg",
      getValue: s => s.itemMetrics ? {
        display: `${s.itemMetrics.latency_score.toFixed(1)}/4`,
        color: s.itemMetrics.latency_score >= 3 ? DS.matchFg : s.itemMetrics.latency_score >= 2 ? DS.partialFg : DS.mismatchFg,
        bar: { value: s.itemMetrics.latency_score, max: 4 },
      } : null,
    });
    rows.push({
      label: "Embedding Similarity", sublabel: "mean",
      getValue: s => s.itemMetrics ? { display: s.itemMetrics.latency_similarity.toFixed(3), color: DS.ink2 } : null,
    });
    if (summaries.some(s => s.itemMetrics?.figure_items > 0)) {
      rows.push({
        label: "Figure Necessity", sublabel: "avg (1=essential, 0=decorative)",
        getValue: s => {
          if (!s.itemMetrics || s.itemMetrics.figure_items === 0) return null;
          const avg = s.itemMetrics.figure_necessity_avg;
          return {
            display: avg.toFixed(2),
            color: avg >= 0.5 ? DS.matchFg : DS.mismatchFg,
            bar: { value: avg, max: 1 },
            sub: `${s.itemMetrics.figure_items} items with figures`,
          };
        },
      });
    }
  }

  // Corpus-level section
  if (summaries.some(s => s.hasCorpus)) {
    rows.push({ type: "header", label: "Corpus-Level Rubrics" });
    rows.push({
      label: "Facet Coverage", sublabel: "covered / total",
      getValue: s => s.corpus ? {
        display: `${s.corpus.facet_coverage.covered_facets}/${s.corpus.facet_coverage.total_facets_in_map}`,
        color: s.corpus.facet_coverage.covered_facets === s.corpus.facet_coverage.total_facets_in_map ? DS.matchFg : DS.partialFg,
      } : null,
    });
    rows.push({
      label: "Facet Uniformity", sublabel: "entropy (1.0=uniform)",
      getValue: s => s.corpus ? {
        display: s.corpus.facet_coverage.uniformity.toFixed(3),
        color: DS.ink,
        bar: { value: s.corpus.facet_coverage.uniformity, max: 1 },
      } : null,
    });
    rows.push({
      label: "Combination Diversity", sublabel: "unique / total",
      getValue: s => s.corpus ? {
        display: `${s.corpus.facet_combination_diversity.unique_combinations}/${s.corpus.facet_combination_diversity.total_items}`,
        sub: `${Math.round(s.corpus.facet_combination_diversity.combination_ratio * 100)}%`,
      } : null,
    });
    rows.push({
      label: "Jaccard Distance", sublabel: "mean pairwise",
      getValue: s => s.corpus ? {
        display: s.corpus.facet_combination_diversity.mean_pairwise_jaccard_distance.toFixed(3),
        bar: { value: s.corpus.facet_combination_diversity.mean_pairwise_jaccard_distance, max: 1 },
      } : null,
    });
    rows.push({
      label: "Format Entropy", sublabel: "structural diversity",
      getValue: s => s.corpus?.problem_diversity ? {
        display: s.corpus.problem_diversity.structural.format_entropy.toFixed(3),
        sub: Object.entries(s.corpus.problem_diversity.structural.format_distribution).map(([k,v]) => `${k.replace("_select","sel")}:${v}`).join(" "),
      } : null,
    });
    rows.push({
      label: "Style Entropy", sublabel: "question variety",
      getValue: s => s.corpus?.problem_diversity ? {
        display: s.corpus.problem_diversity.structural.style_entropy.toFixed(3),
        sub: Object.entries(s.corpus.problem_diversity.structural.style_distribution).map(([k,v]) => `${k.slice(0,6)}:${v}`).join(" "),
      } : null,
    });
    rows.push({
      label: "Semantic Similarity", sublabel: "mean pairwise stem",
      getValue: s => s.corpus?.problem_diversity ? {
        display: s.corpus.problem_diversity.semantic.mean_pairwise_similarity.toFixed(3),
        color: s.corpus.problem_diversity.semantic.mean_pairwise_similarity > 0.85 ? DS.mismatchFg : DS.ink,
      } : null,
    });
    rows.push({
      label: "Max Stem Similarity", sublabel: "most similar pair",
      getValue: s => s.corpus?.problem_diversity ? {
        display: s.corpus.problem_diversity.semantic.max_pairwise_similarity.toFixed(3),
        color: s.corpus.problem_diversity.semantic.max_pairwise_similarity > 0.9 ? DS.mismatchFg : DS.ink2,
      } : null,
    });
    if (summaries.some(s => s.corpus?.figure_fraction != null)) {
      rows.push({
        label: "Figure Fraction", sublabel: "items with figures",
        getValue: s => s.corpus?.figure_fraction != null ? {
          display: `${Math.round(s.corpus.figure_fraction * 100)}%`,
          color: DS.ink,
          bar: { value: s.corpus.figure_fraction, max: 1 },
        } : null,
      });
    }
  }

  return rows;
}
