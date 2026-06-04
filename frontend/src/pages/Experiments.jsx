import { useEffect, useRef, useState } from "react"
import API from "../services/api"

const EMPTY_FORM = {
  name: "", hypothesis: "",
  variantAName: "", variantACopy: "",
  variantBName: "", variantBCopy: "",
  metricLabel: "", trafficSplit: "50",
  startDate: "", endDate: "",
}

const SPLITS = ["50 / 50", "60 / 40", "70 / 30", "80 / 20"]

const STATUS_STYLES = {
  Active:    "bg-green-100 text-green-800",
  Completed: "bg-blue-100 text-blue-800",
  Paused:    "bg-yellow-100 text-yellow-800",
  Draft:     "bg-gray-100 text-gray-500",
}

function exportExperiment(exp) {
  const blob = new Blob([JSON.stringify(exp, null, 2)], { type: "application/json" })
  const url  = URL.createObjectURL(blob)
  const a    = document.createElement("a")
  a.href     = url
  a.download = `experiment-${exp.id}.json`
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
  URL.revokeObjectURL(url)
}

// ─── New Experiment Modal ────────────────────────────────────────────────────

function NewExperimentModal({ onClose, onSave }) {
  const [form, setForm]     = useState(EMPTY_FORM)
  const [errors, setErrors] = useState({})
  const [saving, setSaving] = useState(false)

  const set = (field) => (e) => setForm((f) => ({ ...f, [field]: e.target.value }))

  const validate = () => {
    const e = {}
    if (!form.name.trim())         e.name         = "Required"
    if (!form.hypothesis.trim())   e.hypothesis   = "Required"
    if (!form.variantAName.trim()) e.variantAName = "Required"
    if (!form.variantBName.trim()) e.variantBName = "Required"
    if (!form.metricLabel.trim())  e.metricLabel  = "Required"
    if (!form.startDate)           e.startDate    = "Required"
    if (!form.endDate)             e.endDate      = "Required"
    setErrors(e)
    return Object.keys(e).length === 0
  }

  const handleSave = async () => {
    if (!validate()) return
    setSaving(true)
    try {
      await onSave({
        name:           form.name,
        hypothesis:     form.hypothesis,
        variant_a_name: form.variantAName,
        variant_a_copy: form.variantACopy || null,
        variant_b_name: form.variantBName,
        variant_b_copy: form.variantBCopy || null,
        metric_label:   form.metricLabel,
        traffic_split:  parseInt(form.trafficSplit) || 50,
        start_date: new Date(form.startDate).toLocaleDateString("en-US", { month: "short", day: "numeric", year: "numeric" }),
        end_date:   new Date(form.endDate).toLocaleDateString("en-US", { month: "short", day: "numeric", year: "numeric" }),
      })
    } finally {
      setSaving(false)
    }
  }

  const cls = (f) =>
    `w-full px-3 py-2 border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 ${
      errors[f] ? "border-red-300 bg-red-50" : "border-gray-200"
    }`

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50" onClick={onClose}>
      <div className="bg-white rounded-xl w-full max-w-xl max-h-[90vh] overflow-y-auto shadow-xl" onClick={(e) => e.stopPropagation()}>
        <div className="p-6">
          <div className="flex items-center justify-between mb-5">
            <h2 className="text-base font-bold text-gray-900">New Experiment</h2>
            <button onClick={onClose} className="text-gray-400 hover:text-gray-600 p-1 rounded-lg hover:bg-gray-100">
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          <div className="space-y-4">
            <div>
              <label className="block text-xs font-semibold text-gray-600 mb-1">Experiment name <span className="text-red-400">*</span></label>
              <input placeholder="e.g. Homepage CTA — Benefit vs. Action" value={form.name} onChange={set("name")} className={cls("name")} />
              {errors.name && <p className="text-xs text-red-500 mt-1">{errors.name}</p>}
            </div>

            <div>
              <label className="block text-xs font-semibold text-gray-600 mb-1">Hypothesis <span className="text-red-400">*</span></label>
              <textarea placeholder="We believe [variant B] will outperform [variant A] because [reason]." value={form.hypothesis} onChange={set("hypothesis")} rows={2} className={`${cls("hypothesis")} resize-none`} />
              {errors.hypothesis && <p className="text-xs text-red-500 mt-1">{errors.hypothesis}</p>}
            </div>

            <div>
              <label className="block text-xs font-semibold text-gray-600 mb-1">Metric being tested <span className="text-red-400">*</span></label>
              <input placeholder="e.g. Trial Signup Rate, Open Rate, Day-7 Activation" value={form.metricLabel} onChange={set("metricLabel")} className={cls("metricLabel")} />
              {errors.metricLabel && <p className="text-xs text-red-500 mt-1">{errors.metricLabel}</p>}
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <div className="bg-blue-50 rounded-lg p-3 border border-blue-100">
                <p className="text-xs font-bold text-blue-700 mb-2">Variant A</p>
                <input placeholder="Name *" value={form.variantAName} onChange={set("variantAName")} className={`${cls("variantAName")} mb-2`} />
                {errors.variantAName && <p className="text-xs text-red-500 mb-1">{errors.variantAName}</p>}
                <textarea placeholder="Copy / content (optional)" value={form.variantACopy} onChange={set("variantACopy")} rows={2} className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm resize-none focus:outline-none focus:ring-2 focus:ring-blue-500" />
              </div>
              <div className="bg-green-50 rounded-lg p-3 border border-green-100">
                <p className="text-xs font-bold text-green-700 mb-2">Variant B</p>
                <input placeholder="Name *" value={form.variantBName} onChange={set("variantBName")} className={`${cls("variantBName")} mb-2`} />
                {errors.variantBName && <p className="text-xs text-red-500 mb-1">{errors.variantBName}</p>}
                <textarea placeholder="Copy / content (optional)" value={form.variantBCopy} onChange={set("variantBCopy")} rows={2} className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm resize-none focus:outline-none focus:ring-2 focus:ring-blue-500" />
              </div>
            </div>

            <div>
              <label className="block text-xs font-semibold text-gray-600 mb-1">Traffic split (A / B)</label>
              <div className="flex gap-2">
                {["50", "40", "30", "20"].map((a) => {
                  const label = `${a} / ${100 - parseInt(a)}`
                  return (
                    <button key={a} type="button" onClick={() => setForm((f) => ({ ...f, trafficSplit: a }))}
                      className={`text-xs px-3 py-1.5 rounded-lg border font-medium transition-colors ${
                        form.trafficSplit === a ? "bg-blue-600 text-white border-blue-600" : "bg-white text-gray-600 border-gray-200 hover:border-blue-300"
                      }`}>
                      {label}
                    </button>
                  )
                })}
              </div>
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block text-xs font-semibold text-gray-600 mb-1">Start date <span className="text-red-400">*</span></label>
                <input type="date" value={form.startDate} onChange={set("startDate")} className={cls("startDate")} />
                {errors.startDate && <p className="text-xs text-red-500 mt-1">{errors.startDate}</p>}
              </div>
              <div>
                <label className="block text-xs font-semibold text-gray-600 mb-1">End date <span className="text-red-400">*</span></label>
                <input type="date" value={form.endDate} onChange={set("endDate")} className={cls("endDate")} />
                {errors.endDate && <p className="text-xs text-red-500 mt-1">{errors.endDate}</p>}
              </div>
            </div>
          </div>

          <div className="flex gap-2 mt-6 pt-4 border-t border-gray-100">
            <button onClick={handleSave} disabled={saving}
              className="flex-1 bg-blue-600 hover:bg-blue-700 disabled:bg-blue-300 text-white text-sm font-semibold py-2.5 rounded-lg transition-colors">
              {saving ? "Saving…" : "Create as Draft"}
            </button>
            <button onClick={onClose} className="text-sm font-medium text-gray-500 border border-gray-200 hover:bg-gray-50 px-4 py-2 rounded-lg transition-colors">
              Cancel
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

// ─── Experiment Card ─────────────────────────────────────────────────────────

function ExperimentCard({ exp, onStatusChange }) {
  const { variant_a: vA, variant_b: vB, status } = exp
  const hasResults = (status === "Active" || status === "Completed") && vA.metric !== null
  const bWins      = hasResults && vB.metric > vA.metric
  const [split, setSplit] = useState("50 / 50")

  const fmtCopy = (c) => c ? `"${c}"` : null

  return (
    <div className="bg-white rounded-xl border border-gray-200 p-5">
      <div className="flex flex-wrap items-start justify-between gap-3 mb-1">
        <h3 className="text-base font-semibold text-gray-900 leading-snug">{exp.name}</h3>
        <span className={`text-xs px-2.5 py-1 rounded-full font-medium flex-shrink-0 ${STATUS_STYLES[status] || STATUS_STYLES.Draft}`}>
          {status}
        </span>
      </div>

      <p className="text-xs text-gray-400 italic mb-1 leading-relaxed">Hypothesis: {exp.hypothesis}</p>
      <p className="text-xs text-gray-400 mb-4">
        {exp.start_date} → {exp.end_date}
        {exp.participants > 0 && <span className="ml-2">· {exp.participants.toLocaleString()} participants</span>}
      </p>

      {/* Variants */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 mb-4">
        {[
          { v: vA, letter: "A", wins: hasResults && !bWins, color: "blue" },
          { v: vB, letter: "B", wins: bWins,                color: "green" },
        ].map(({ v, letter, wins, color }) => (
          <div key={letter} className={`rounded-lg p-4 border-2 transition-colors ${
            wins ? `border-${color}-300 bg-${color}-50` : "border-transparent bg-gray-50"
          }`}>
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs font-semibold text-gray-400 uppercase tracking-wide">Variant {letter}</span>
              <div className={`w-6 h-6 bg-${color}-100 rounded-full flex items-center justify-center`}>
                <span className={`text-${color}-600 text-xs font-bold`}>{letter}</span>
              </div>
            </div>
            <p className="text-xs font-medium text-gray-700 mb-1">{v.name}</p>
            {fmtCopy(v.copy) && <p className="text-xs text-gray-400 italic mb-3 leading-relaxed line-clamp-2">{fmtCopy(v.copy)}</p>}
            {v.metric !== null
              ? <><p className={`text-2xl font-bold ${wins ? `text-${color}-700` : "text-gray-900"}`}>{v.metric}%</p><p className="text-xs text-gray-400 mt-0.5">{v.label}</p></>
              : status === "Draft"
                ? <p className="text-xs text-gray-300 mt-2">No data · not launched yet</p>
                : <div className="flex items-center gap-1.5 mt-2"><div className="w-1.5 h-1.5 bg-green-400 rounded-full animate-pulse" /><p className="text-xs text-gray-400">Collecting data…</p></div>
            }
          </div>
        ))}
      </div>

      {/* Winner banner */}
      {hasResults && (
        <div className="flex items-center justify-between bg-green-50 border border-green-200 rounded-lg px-4 py-2.5 mb-4">
          <div className="flex items-center gap-2">
            <svg className="w-4 h-4 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <span className="text-xs font-semibold text-gray-800">{bWins ? vB.name : vA.name} wins</span>
          </div>
          {exp.improvement !== null && <span className="text-sm font-bold text-green-700">+{exp.improvement}%</span>}
        </div>
      )}

      {/* Draft: traffic split picker */}
      {status === "Draft" && (
        <div className="bg-gray-50 border border-gray-200 rounded-lg px-4 py-3 mb-4">
          <p className="text-xs font-semibold text-gray-600 mb-2">Traffic split (A / B)</p>
          <div className="flex flex-wrap gap-2">
            {SPLITS.map((s) => (
              <button key={s} onClick={() => setSplit(s)}
                className={`text-xs px-3 py-1.5 rounded-lg border font-medium transition-colors ${
                  split === s ? "bg-blue-600 text-white border-blue-600" : "bg-white text-gray-600 border-gray-200 hover:border-blue-300"
                }`}>
                {s}
              </button>
            ))}
          </div>
          <p className="text-xs text-gray-400 mt-2">
            Variant A gets {split.split("/")[0].trim()}% · Variant B gets {split.split("/")[1].trim()}%
          </p>
        </div>
      )}

      {/* Actions */}
      <div className="flex flex-wrap gap-2 pt-4 border-t border-gray-100">
        <button onClick={() => exportExperiment(exp)} className="text-sm font-medium text-gray-500 hover:bg-gray-50 border border-gray-200 px-3 py-2 rounded-lg transition-colors">
          Export JSON
        </button>
        {(status === "Active" || status === "Paused") && (
          <button onClick={() => onStatusChange(exp.id, status === "Active" ? "Paused" : "Active")}
            className={`text-sm font-medium px-3 py-2 rounded-lg border transition-colors ${
              status === "Active" ? "text-orange-600 border-orange-200 hover:bg-orange-50" : "text-green-700 border-green-200 hover:bg-green-50"
            }`}>
            {status === "Active" ? "Pause test" : "Resume test"}
          </button>
        )}
        {status === "Draft" && (
          <button onClick={() => onStatusChange(exp.id, "Active")}
            className="text-sm font-medium text-green-700 hover:bg-green-50 border border-green-200 px-3 py-2 rounded-lg transition-colors">
            Launch
          </button>
        )}
        {status === "Active" && (
          <button onClick={() => onStatusChange(exp.id, "Completed")}
            className="text-sm font-medium text-blue-600 hover:bg-blue-50 border border-blue-200 px-3 py-2 rounded-lg transition-colors">
            Mark Complete
          </button>
        )}
      </div>
    </div>
  )
}

// ─── Page ────────────────────────────────────────────────────────────────────

function Experiments() {
  const [experiments, setExperiments] = useState([])
  const [loading, setLoading]         = useState(true)
  const [showModal, setShowModal]     = useState(false)
  const pollRef = useRef(null)

  const load = () =>
    API.get("/experiments")
      .then((r) => setExperiments(r.data))
      .catch(() => {})
      .finally(() => setLoading(false))

  useEffect(() => {
    load()
    // Poll every 15 s to pick up new tracking events
    pollRef.current = setInterval(load, 15000)
    return () => clearInterval(pollRef.current)
  }, [])

  const handleStatusChange = async (id, status) => {
    await API.patch(`/experiments/${id}/status`, { status })
    load()
  }

  const handleCreate = async (data) => {
    await API.post("/experiments", data)
    setShowModal(false)
    load()
  }

  const active    = experiments.filter((e) => e.status === "Active").length
  const completed = experiments.filter((e) => e.status === "Completed").length
  const withLift  = experiments.filter((e) => e.improvement !== null)
  const avgLift   = withLift.length
    ? (withLift.reduce((s, e) => s + e.improvement, 0) / withLift.length).toFixed(1)
    : "—"

  return (
    <div>
      {showModal && <NewExperimentModal onClose={() => setShowModal(false)} onSave={handleCreate} />}

      <div className="flex flex-wrap items-start justify-between gap-4 mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">A/B Experiments</h1>
          <p className="text-sm text-gray-400 mt-0.5">Test hypotheses about your content to find what actually moves the needle.</p>
        </div>
        <button onClick={() => setShowModal(true)}
          className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white text-sm font-semibold px-4 py-2.5 rounded-lg transition-colors flex-shrink-0">
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
          </svg>
          New Experiment
        </button>
      </div>

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        {[
          { label: "Total",     value: experiments.length, color: "text-gray-900" },
          { label: "Active",    value: active,             color: "text-green-600" },
          { label: "Completed", value: completed,          color: "text-blue-600"  },
          { label: "Avg. Lift", value: `${avgLift}%`,      color: "text-gray-900"  },
        ].map(({ label, value, color }) => (
          <div key={label} className="bg-white rounded-xl border border-gray-200 p-4 text-center">
            <p className={`text-2xl font-bold ${color}`}>{value}</p>
            <p className="text-xs text-gray-400 mt-0.5">{label}</p>
          </div>
        ))}
      </div>

      {loading && (
        <div className="flex justify-center py-12">
          <div className="animate-spin rounded-full h-7 w-7 border-b-2 border-blue-500" />
        </div>
      )}

      {!loading && experiments.length === 0 && (
        <div className="text-center py-16 bg-white rounded-xl border border-dashed border-gray-200">
          <p className="text-sm font-medium text-gray-500">No experiments yet.</p>
          <button onClick={() => setShowModal(true)} className="text-xs text-blue-600 hover:underline mt-2 inline-block">
            Create your first experiment →
          </button>
        </div>
      )}

      <div className="space-y-4">
        {experiments.map((exp) => (
          <ExperimentCard key={exp.id} exp={exp} onStatusChange={handleStatusChange} />
        ))}
      </div>
    </div>
  )
}

export default Experiments
