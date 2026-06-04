import { useEffect, useState } from "react"
import API from "../services/api"
import {
  LineChart, Line, BarChart, Bar,
  XAxis, YAxis, Tooltip, CartesianGrid,
  ResponsiveContainer, Legend
} from "recharts"

const DATASETS = {
  "Last 6 Weeks": [
    { period: "Wk 1", engagement: 57, accuracy: 68, ctr: 3.9 },
    { period: "Wk 2", engagement: 63, accuracy: 71, ctr: 4.1 },
    { period: "Wk 3", engagement: 69, accuracy: 76, ctr: 4.8 },
    { period: "Wk 4", engagement: 66, accuracy: 79, ctr: 4.5 },
    { period: "Wk 5", engagement: 74, accuracy: 83, ctr: 5.2 },
    { period: "Wk 6", engagement: 71, accuracy: 82, ctr: 4.9 },
  ],
  "Last 3 Months": [
    { period: "Apr", engagement: 60, accuracy: 70, ctr: 3.8 },
    { period: "May", engagement: 65, accuracy: 75, ctr: 4.3 },
    { period: "Jun", engagement: 71, accuracy: 82, ctr: 4.9 },
  ],
  "Last 6 Months": [
    { period: "Jan", engagement: 48, accuracy: 61, ctr: 3.0 },
    { period: "Feb", engagement: 52, accuracy: 65, ctr: 3.3 },
    { period: "Mar", engagement: 57, accuracy: 68, ctr: 3.6 },
    { period: "Apr", engagement: 60, accuracy: 70, ctr: 3.8 },
    { period: "May", engagement: 65, accuracy: 75, ctr: 4.3 },
    { period: "Jun", engagement: 71, accuracy: 82, ctr: 4.9 },
  ],
}

const FALLBACK_CATEGORIES = [
  { category: "Case Studies",    posts: 8,  engagement: 84 },
  { category: "Blog Posts",      posts: 38, engagement: 72 },
  { category: "Social Posts",    posts: 19, engagement: 48 },
  { category: "Email Campaigns", posts: 24, engagement: 61 },
  { category: "Product Updates", posts: 11, engagement: 56 },
]

const PERIODS = Object.keys(DATASETS)

function exportCSV(rows, filename) {
  const header = Object.keys(rows[0]).join(",")
  const body   = rows.map((r) => Object.values(r).join(",")).join("\n")
  const blob   = new Blob([`${header}\n${body}`], { type: "text/csv" })
  const url    = URL.createObjectURL(blob)
  const a      = document.createElement("a")
  a.href = url
  a.download = filename
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
  URL.revokeObjectURL(url)
}

function SortIcon({ dir }) {
  if (!dir) return <span className="text-gray-300 ml-1">↕</span>
  return <span className="ml-1">{dir === "asc" ? "↑" : "↓"}</span>
}

function KpiCard({ label, value, sub, subColor, icon, bg }) {
  return (
    <div className={`rounded-xl border p-4 ${bg}`}>
      <div className="flex items-center justify-between mb-2">
        <p className="text-xs font-semibold uppercase tracking-wide opacity-70">{label}</p>
        <span className="opacity-60">{icon}</span>
      </div>
      <p className="text-2xl font-bold">{value}</p>
      {sub && <p className={`text-xs mt-1 ${subColor}`}>{sub}</p>}
    </div>
  )
}

function Analytics() {
  const [metrics, setMetrics] = useState({
    engagement: 68.4, accuracy: 91.7, ctr: 4.6,
    total: 0, experiments: 0, categories: [],
  })
  const [loading, setLoading]   = useState(true)
  const [period, setPeriod]     = useState("Last 6 Weeks")
  const [sortCol, setSortCol]   = useState("engagement")
  const [sortDir, setSortDir]   = useState("desc")

  useEffect(() => {
    Promise.all([
      API.get("/analytics"),
      API.get("/experiments").catch(() => ({ data: [] })),
    ]).then(([analyticsRes, expRes]) => {
      const d = analyticsRes.data
      const activeExps = expRes.data.filter((e) => e.status === "Active").length
      setMetrics({
        engagement:  ((d.average_engagement   || 0.684) * 100).toFixed(1),
        accuracy:    ((d.response_consistency  || 0.917) * 100).toFixed(1),
        ctr:         ((d.average_ctr           || 0.046) * 100).toFixed(1),
        total:       d.total_content  || 0,
        experiments: activeExps,
        categories:  d.category_breakdown || [],
      })
    }).catch(() => {}).finally(() => setLoading(false))
  }, [])

  const chartData = DATASETS[period]

  const now = new Date().toLocaleDateString("en-US", { month: "long", year: "numeric" })

  // Sortable category rows
  const rawCategories = metrics.categories.length > 0 ? metrics.categories : FALLBACK_CATEGORIES
  const sortedCategories = [...rawCategories].sort((a, b) => {
    const av = a[sortCol] ?? 0
    const bv = b[sortCol] ?? 0
    return sortDir === "asc" ? av - bv : bv - av
  })

  const handleSort = (col) => {
    if (sortCol === col) setSortDir((d) => (d === "asc" ? "desc" : "asc"))
    else { setSortCol(col); setSortDir("desc") }
  }

  const thCls = (col) =>
    `pb-2 text-xs font-semibold text-gray-400 uppercase tracking-wide cursor-pointer hover:text-gray-600 select-none ${
      sortCol === col ? "text-gray-700" : ""
    }`

  return (
    <div>
      {/* Header */}
      <div className="flex flex-wrap items-start justify-between gap-4 mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Analytics</h1>
          <p className="text-sm text-gray-400 mt-0.5">
            {now}
            {metrics.total > 0 && ` · ${metrics.total} pieces in library`}
            {metrics.experiments > 0 && ` · ${metrics.experiments} active experiment${metrics.experiments !== 1 ? "s" : ""}`}
          </p>
        </div>
        <div className="flex items-center gap-2 flex-shrink-0">
          {/* Export */}
          <button
            onClick={() => exportCSV(sortedCategories, "analytics-by-type.csv")}
            className="flex items-center gap-1.5 text-xs font-medium text-gray-500 border border-gray-200 hover:bg-gray-50 px-3 py-2 rounded-lg transition-colors"
          >
            <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
            </svg>
            Export CSV
          </button>

          {/* Period picker */}
          <div className="flex gap-1 bg-gray-100 p-1 rounded-lg">
            {PERIODS.map((p) => (
              <button
                key={p}
                onClick={() => setPeriod(p)}
                className={`text-xs font-medium px-3 py-1.5 rounded-md transition-colors whitespace-nowrap ${
                  period === p ? "bg-white text-gray-900 shadow-sm" : "text-gray-400 hover:text-gray-700"
                }`}
              >
                {p}
              </button>
            ))}
          </div>
        </div>
      </div>

      {loading && (
        <div className="flex justify-center py-12">
          <div className="animate-spin rounded-full h-7 w-7 border-b-2 border-blue-500" />
        </div>
      )}

      {!loading && (
        <>
          {/* KPIs */}
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
            <KpiCard
              label="Avg. Engagement"
              value={`${metrics.engagement}%`}
              sub="↓ 1.3% vs prior period"
              subColor="text-red-500"
              bg="bg-blue-50 border-blue-200 text-blue-900"
              icon={<svg className="w-5 h-5 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" /></svg>}
            />
            <KpiCard
              label="AI Accuracy"
              value={`${metrics.accuracy}%`}
              sub="↑ 2.1% vs prior period"
              subColor="text-green-600"
              bg="bg-green-50 border-green-200 text-green-900"
              icon={<svg className="w-5 h-5 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>}
            />
            <KpiCard
              label="Avg. CTR"
              value={`${metrics.ctr}%`}
              sub="Across all published content"
              subColor="text-gray-400"
              bg="bg-purple-50 border-purple-200 text-purple-900"
              icon={<svg className="w-5 h-5 text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 15l-2 5L9 9l11 4-5 2zm0 0l5 5" /></svg>}
            />
            <KpiCard
              label="Published"
              value={metrics.total || "—"}
              sub="Total in library"
              subColor="text-gray-400"
              bg="bg-orange-50 border-orange-200 text-orange-900"
              icon={<svg className="w-5 h-5 text-orange-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" /></svg>}
            />
          </div>

          {/* Charts */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
            <div className="bg-white rounded-xl border border-gray-200 p-5">
              <h3 className="text-sm font-semibold text-gray-900 mb-1">Engagement & AI Accuracy</h3>
              <p className="text-xs text-gray-400 mb-4">{period}</p>
              <div className="h-52">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={chartData} margin={{ top: 4, right: 4, left: -20, bottom: 0 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#f3f4f6" />
                    <XAxis dataKey="period" tick={{ fontSize: 11, fill: "#9ca3af" }} axisLine={false} tickLine={false} />
                    <YAxis tick={{ fontSize: 11, fill: "#9ca3af" }} domain={[30, 100]} unit="%" axisLine={false} tickLine={false} />
                    <Tooltip
                      formatter={(v, name) => [`${v}%`, name === "engagement" ? "Engagement" : "AI Accuracy"]}
                      contentStyle={{ fontSize: 12, borderRadius: 8, border: "1px solid #e5e7eb" }}
                    />
                    <Legend formatter={(v) => v === "engagement" ? "Engagement" : "AI Accuracy"} iconType="circle" wrapperStyle={{ fontSize: 12 }} />
                    <Line type="monotone" dataKey="engagement" stroke="#3b82f6" strokeWidth={2} dot={false} />
                    <Line type="monotone" dataKey="accuracy"   stroke="#10b981" strokeWidth={2} dot={false} strokeDasharray="4 2" />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </div>

            <div className="bg-white rounded-xl border border-gray-200 p-5">
              <h3 className="text-sm font-semibold text-gray-900 mb-1">Click-Through Rate</h3>
              <p className="text-xs text-gray-400 mb-4">{period}</p>
              <div className="h-52">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={chartData} margin={{ top: 4, right: 4, left: -20, bottom: 0 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#f3f4f6" />
                    <XAxis dataKey="period" tick={{ fontSize: 11, fill: "#9ca3af" }} axisLine={false} tickLine={false} />
                    <YAxis tick={{ fontSize: 11, fill: "#9ca3af" }} unit="%" axisLine={false} tickLine={false} />
                    <Tooltip formatter={(v) => [`${v}%`, "CTR"]} contentStyle={{ fontSize: 12, borderRadius: 8, border: "1px solid #e5e7eb" }} />
                    <Bar dataKey="ctr" fill="#8b5cf6" radius={[3, 3, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>
          </div>

          {/* Category table — sortable */}
          <div className="bg-white rounded-xl border border-gray-200 p-5">
            <div className="flex items-center justify-between mb-1">
              <h3 className="text-sm font-semibold text-gray-900">Engagement by Content Type</h3>
              <p className="text-xs text-gray-400">
                {metrics.categories.length > 0 ? "Live data" : "Sample data"} · click headers to sort
              </p>
            </div>
            <div className="overflow-x-auto mt-4">
              <table className="w-full text-sm min-w-[380px]">
                <thead>
                  <tr className="text-left border-b border-gray-100">
                    <th className="pb-2 text-xs font-semibold text-gray-400 uppercase tracking-wide">Type</th>
                    <th className={thCls("posts")} onClick={() => handleSort("posts")}>
                      Pieces <SortIcon dir={sortCol === "posts" ? sortDir : null} />
                    </th>
                    <th className={thCls("engagement")} onClick={() => handleSort("engagement")}>
                      Engagement <SortIcon dir={sortCol === "engagement" ? sortDir : null} />
                    </th>
                  </tr>
                </thead>
                <tbody>
                  {sortedCategories.map((row, i) => (
                    <tr key={row.category} className={i < sortedCategories.length - 1 ? "border-b border-gray-50" : ""}>
                      <td className="py-3 font-medium text-gray-800">{row.category}</td>
                      <td className="py-3 text-gray-400">{row.posts}</td>
                      <td className="py-3">
                        <div className="flex items-center gap-2">
                          <div className="w-20 bg-gray-100 rounded-full h-1.5">
                            <div className="bg-blue-500 h-1.5 rounded-full" style={{ width: `${row.engagement}%` }} />
                          </div>
                          <span className="text-xs font-medium text-gray-700">{row.engagement}%</span>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </>
      )}
    </div>
  )
}

export default Analytics
