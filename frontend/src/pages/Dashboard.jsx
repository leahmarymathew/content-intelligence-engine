import { useEffect, useState } from "react"
import { Link } from "react-router-dom"
import API from "../services/api"
import {
  LineChart, Line, XAxis, YAxis, Tooltip, CartesianGrid, ResponsiveContainer, Legend
} from "recharts"

const FALLBACK_CONTENT = [
  { id: 1, title: "Rethinking SaaS Onboarding: Why Your Day-1 Email Sets the Tone for Churn", category: "Blog Post" },
  { id: 2, title: "How Meridian Logistics Cut Content Production Time by 63%", category: "Case Study" },
  { id: 3, title: "Re-engagement Email — 'You've been quiet lately…'", category: "Email Campaign" },
]

const CHART_DATA = [
  { week: "Wk 1", engagement: 57, consistency: 68 },
  { week: "Wk 2", engagement: 63, consistency: 71 },
  { week: "Wk 3", engagement: 69, consistency: 76 },
  { week: "Wk 4", engagement: 66, consistency: 79 },
  { week: "Wk 5", engagement: 74, consistency: 83 },
]

const TYPE_COLORS = {
  "Blog Post":      "bg-blue-50 text-blue-700",
  "Case Study":     "bg-purple-50 text-purple-700",
  "Email Campaign": "bg-orange-50 text-orange-700",
  "Social Post":    "bg-pink-50 text-pink-700",
  "Product Update": "bg-teal-50 text-teal-700",
  "Newsletter":     "bg-green-50 text-green-700",
}

function greeting() {
  const h = new Date().getHours()
  if (h < 12) return "Good morning"
  if (h < 17) return "Good afternoon"
  return "Good evening"
}

function todayStr() {
  return new Date().toLocaleDateString("en-US", {
    weekday: "long", month: "long", day: "numeric"
  })
}

function StatCard({ label, value, sub, subColor = "text-gray-400", loading }) {
  return (
    <div className="bg-white rounded-xl border border-gray-200 p-5 flex flex-col">
      <p className="text-xs font-medium text-gray-400 uppercase tracking-wide">{label}</p>
      {loading
        ? <div className="h-8 w-20 bg-gray-100 animate-pulse rounded mt-2 mb-1" />
        : <p className="text-2xl font-bold text-gray-900 mt-2 mb-1">{value}</p>
      }
      {sub && <p className={`text-xs ${subColor}`}>{sub}</p>}
    </div>
  )
}

function Dashboard() {
  const [recentContent, setRecentContent]     = useState(FALLBACK_CONTENT)
  const [stats, setStats]                     = useState(null)
  const [activeExp, setActiveExp]             = useState(null)
  const [loadingStats, setLoadingStats]       = useState(true)

  useEffect(() => {
    // Fetch stats from the same analytics endpoint Analytics page uses
    API.get("/analytics")
      .then((res) => {
        const d = res.data
        const cats = d.category_breakdown || []
        const best = cats.length
          ? cats.reduce((a, b) => (a.engagement > b.engagement ? a : b))
          : null

        setStats({
          total:       d.total_content || 0,
          engagement:  ((d.average_engagement   || 0.684) * 100).toFixed(1),
          accuracy:    ((d.response_consistency  || 0.917) * 100).toFixed(1),
          bestType:    best?.category || "Case Studies",
          bestPct:     best?.engagement || 84,
        })
      })
      .catch(() => {
        // Fallback so stats still show something
        setStats({ total: "—", engagement: "—", accuracy: "—", bestType: "Case Studies", bestPct: 84 })
      })
      .finally(() => setLoadingStats(false))

    // Load first active experiment for the snapshot
    API.get("/experiments")
      .then((res) => {
        const active = res.data?.find((e) => e.status === "Active")
        if (active) setActiveExp(active)
      })
      .catch(() => {})

    // Load recent content
    API.get("/content-library")
      .then((res) => {
        const items = res.data?.slice(0, 3)
        if (items?.length > 0) setRecentContent(items)
      })
      .catch(() => {})
  }, [])

  return (
    <div>
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900">{greeting()}, Leah</h1>
        <p className="text-sm text-gray-400 mt-0.5">
          {todayStr()}
          {stats && stats.total > 0 && ` · ${stats.total} pieces in your library`}
        </p>
      </div>

      {/* Stats — all from /analytics API */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        <StatCard
          label="Total Published"
          value={stats?.total ?? "—"}
          sub="All time"
          loading={loadingStats}
        />
        <StatCard
          label="Avg. Engagement Rate"
          value={stats ? `${stats.engagement}%` : "—"}
          sub="From engagement records"
          subColor="text-blue-600"
          loading={loadingStats}
        />
        <StatCard
          label="Best Performing Type"
          value={stats?.bestType ?? "—"}
          sub={stats ? `${stats.bestPct}% avg. engagement` : ""}
          loading={loadingStats}
        />
        <StatCard
          label="AI Accuracy Score"
          value={stats ? `${stats.accuracy}%` : "—"}
          sub="Quality & consistency"
          subColor="text-green-600"
          loading={loadingStats}
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">

        {/* Chart */}
        <div className="bg-white rounded-xl border border-gray-200 p-5">
          <div className="flex items-start justify-between mb-4">
            <div>
              <h3 className="text-sm font-semibold text-gray-900">Engagement & Consistency</h3>
              <p className="text-xs text-gray-400 mt-0.5">Last 5 weeks</p>
            </div>
          </div>
          <div className="h-52">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={CHART_DATA} margin={{ top: 4, right: 4, left: -20, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f3f4f6" />
                <XAxis dataKey="week" tick={{ fontSize: 11, fill: "#9ca3af" }} axisLine={false} tickLine={false} />
                <YAxis tick={{ fontSize: 11, fill: "#9ca3af" }} domain={[40, 100]} unit="%" axisLine={false} tickLine={false} />
                <Tooltip
                  formatter={(v, name) => [`${v}%`, name === "engagement" ? "Engagement" : "AI Accuracy"]}
                  contentStyle={{ fontSize: 12, borderRadius: 8, border: "1px solid #e5e7eb" }}
                />
                <Legend
                  formatter={(v) => v === "engagement" ? "Engagement" : "AI Accuracy"}
                  iconType="circle"
                  wrapperStyle={{ fontSize: 12 }}
                />
                <Line type="monotone" dataKey="engagement"  stroke="#3b82f6" strokeWidth={2} dot={false} />
                <Line type="monotone" dataKey="consistency" stroke="#10b981" strokeWidth={2} dot={false} strokeDasharray="4 2" />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Recent Content */}
        <div className="bg-white rounded-xl border border-gray-200 p-5">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-sm font-semibold text-gray-900">Recently Published</h3>
            <Link to="/library" className="text-xs text-blue-600 hover:text-blue-700 font-medium">
              View library →
            </Link>
          </div>
          <div className="space-y-1">
            {recentContent.map((item) => (
              <Link
                key={item.id}
                to="/library"
                className="flex items-start gap-3 px-3 py-2.5 rounded-lg hover:bg-gray-50 transition-colors"
              >
                <div className="w-8 h-8 bg-gray-100 rounded-lg flex items-center justify-center flex-shrink-0 mt-0.5">
                  <svg className="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-gray-800 line-clamp-2 leading-snug">{item.title}</p>
                  <div className="flex items-center gap-2 mt-1">
                    <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${TYPE_COLORS[item.category] || "bg-gray-100 text-gray-600"}`}>
                      {item.category || "Content"}
                    </span>
                  </div>
                </div>
              </Link>
            ))}
          </div>
          <div className="mt-3 pt-3 border-t border-gray-100">
            <Link
              to="/generator"
              className="flex items-center justify-center gap-2 w-full py-2 text-sm font-medium text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
              </svg>
              Generate new content
            </Link>
          </div>
        </div>

      </div>

      {/* Active experiment — live from /experiments API */}
      <div className="bg-white rounded-xl border border-gray-200 p-5">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="text-sm font-semibold text-gray-900">Active Experiment</h3>
            <p className="text-xs text-gray-400 mt-0.5">
              {activeExp ? activeExp.name : "No active experiments"}
            </p>
          </div>
          <Link to="/experiments" className="text-xs text-blue-600 hover:text-blue-700 font-medium">
            View all →
          </Link>
        </div>

        {activeExp ? (
          <>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <div className={`rounded-lg p-4 border ${
                activeExp.variant_a.metric !== null && activeExp.variant_b.metric !== null && activeExp.variant_a.metric >= activeExp.variant_b.metric
                  ? "bg-green-50 border-green-200" : "bg-gray-50 border-gray-200"
              }`}>
                <p className="text-xs text-gray-500 mb-1">Variant A · {activeExp.variant_a.name}</p>
                {activeExp.variant_a.copy && (
                  <p className="text-xs italic text-gray-400 mb-2 line-clamp-2">{activeExp.variant_a.copy}</p>
                )}
                {activeExp.variant_a.metric !== null
                  ? <><p className="text-xl font-bold text-gray-900">{activeExp.variant_a.metric}%</p><p className="text-xs text-gray-400">{activeExp.variant_a.label}</p></>
                  : <div className="flex items-center gap-1.5 mt-1"><div className="w-1.5 h-1.5 bg-green-400 rounded-full animate-pulse" /><p className="text-xs text-gray-400">Collecting data…</p></div>
                }
              </div>
              <div className={`rounded-lg p-4 border ${
                activeExp.variant_a.metric !== null && activeExp.variant_b.metric !== null && activeExp.variant_b.metric > activeExp.variant_a.metric
                  ? "bg-green-50 border-green-200" : "bg-gray-50 border-gray-200"
              }`}>
                <p className="text-xs text-gray-500 mb-1">Variant B · {activeExp.variant_b.name}</p>
                {activeExp.variant_b.copy && (
                  <p className="text-xs italic text-gray-400 mb-2 line-clamp-2">{activeExp.variant_b.copy}</p>
                )}
                {activeExp.variant_b.metric !== null
                  ? <><p className={`text-xl font-bold ${activeExp.variant_b.metric > activeExp.variant_a.metric ? "text-green-700" : "text-gray-900"}`}>{activeExp.variant_b.metric}%</p><p className="text-xs text-gray-400">{activeExp.variant_b.label}</p></>
                  : <div className="flex items-center gap-1.5 mt-1"><div className="w-1.5 h-1.5 bg-green-400 rounded-full animate-pulse" /><p className="text-xs text-gray-400">Collecting data…</p></div>
                }
              </div>
            </div>
            {activeExp.improvement !== null && (
              <p className="text-xs text-gray-400 mt-3">
                {activeExp.participants.toLocaleString()} participants ·
                <span className="text-green-600 font-medium"> {activeExp.variant_b.name} outperforming by +{activeExp.improvement}%</span>
              </p>
            )}
          </>
        ) : (
          <div className="text-center py-6 bg-gray-50 rounded-lg border border-dashed border-gray-200">
            <p className="text-xs text-gray-400">No active experiments.</p>
            <Link to="/experiments" className="text-xs text-blue-600 hover:underline mt-1 inline-block">
              Start an experiment →
            </Link>
          </div>
        )}
      </div>

    </div>
  )
}

export default Dashboard
