import { useEffect, useState } from "react"
import { Link } from "react-router-dom"
import API from "../services/api"
import {
  LineChart, Line, XAxis, YAxis, Tooltip, CartesianGrid, ResponsiveContainer, Legend
} from "recharts"

const RECENT_ITEMS = [
  {
    id: 1,
    title: "Rethinking SaaS Onboarding: Why Your Day-1 Email Sets the Tone for Churn",
    type: "Blog Post",
    ago: "2 hours ago",
  },
  {
    id: 2,
    title: "How Meridian Logistics Cut Content Production Time by 63%",
    type: "Case Study",
    ago: "Yesterday",
  },
  {
    id: 3,
    title: "Re-engagement Email — 'You've been quiet lately…'",
    type: "Email Campaign",
    ago: "2 days ago",
  },
]

const chartData = [
  { week: "Wk 1", engagement: 57, consistency: 68 },
  { week: "Wk 2", engagement: 63, consistency: 71 },
  { week: "Wk 3", engagement: 69, consistency: 76 },
  { week: "Wk 4", engagement: 66, consistency: 79 },
  { week: "Wk 5", engagement: 74, consistency: 83 },
]

const TYPE_COLORS = {
  "Blog Post": "bg-blue-50 text-blue-700",
  "Case Study": "bg-purple-50 text-purple-700",
  "Email Campaign": "bg-orange-50 text-orange-700",
  "Social Post": "bg-pink-50 text-pink-700",
  "Product Update": "bg-teal-50 text-teal-700",
  "Newsletter": "bg-green-50 text-green-700",
}

function StatCard({ label, value, sub, subColor = "text-gray-400" }) {
  return (
    <div className="bg-white rounded-xl border border-gray-200 p-5 flex flex-col">
      <p className="text-xs font-medium text-gray-400 uppercase tracking-wide">{label}</p>
      <p className="text-2xl font-bold text-gray-900 mt-2 mb-1">{value}</p>
      {sub && <p className={`text-xs ${subColor}`}>{sub}</p>}
    </div>
  )
}

function Dashboard() {
  const [recentContent, setRecentContent] = useState(RECENT_ITEMS)

  useEffect(() => {
    API.get("/content-library")
      .then((res) => {
        const items = res.data?.slice(0, 3)
        if (items?.length > 0) setRecentContent(items)
      })
      .catch(() => {})
  }, [])

  return (
    <div>
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Good morning, Alex</h1>
        <p className="text-sm text-gray-400 mt-0.5">Wednesday, June 4 · Your content team published 3 pieces this week.</p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        <StatCard
          label="Published This Month"
          value="47"
          sub="↑ 12 vs. May"
          subColor="text-green-600"
        />
        <StatCard
          label="Avg. Engagement Rate"
          value="68.4%"
          sub="↓ 1.3% vs. last month"
          subColor="text-red-500"
        />
        <StatCard
          label="Best Performing Type"
          value="Case Studies"
          sub="84% avg. engagement"
          subColor="text-gray-400"
        />
        <StatCard
          label="AI Accuracy Score"
          value="91.7%"
          sub="↑ 2.1% vs. last month"
          subColor="text-green-600"
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
              <LineChart data={chartData} margin={{ top: 4, right: 4, left: -20, bottom: 0 }}>
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
                <Line type="monotone" dataKey="engagement" stroke="#3b82f6" strokeWidth={2} dot={false} />
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
              <Link key={item.id} to="/library" className="flex items-start gap-3 px-3 py-2.5 rounded-lg hover:bg-gray-50 transition-colors">
                <div className="w-8 h-8 bg-gray-100 rounded-lg flex items-center justify-center flex-shrink-0 mt-0.5">
                  <svg className="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-gray-800 line-clamp-2 leading-snug">{item.title}</p>
                  <div className="flex items-center gap-2 mt-1">
                    <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${TYPE_COLORS[item.type] || "bg-gray-100 text-gray-600"}`}>
                      {item.type || item.category || "Content"}
                    </span>
                    <span className="text-xs text-gray-400">{item.ago || ""}</span>
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

      {/* Active A/B test */}
      <div className="bg-white rounded-xl border border-gray-200 p-5">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="text-sm font-semibold text-gray-900">Active Experiment Snapshot</h3>
            <p className="text-xs text-gray-400 mt-0.5">Homepage Hero — Outcome vs. Process Messaging</p>
          </div>
          <Link to="/experiments" className="text-xs text-blue-600 hover:text-blue-700 font-medium">
            View all →
          </Link>
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          <div className="bg-gray-50 rounded-lg p-4 border border-gray-200">
            <p className="text-xs text-gray-500 mb-2">Variant A</p>
            <p className="text-xs italic text-gray-600 mb-3 leading-relaxed">
              "The only content platform that writes, tests, and learns for you"
            </p>
            <p className="text-xl font-bold text-gray-900">3.8%</p>
            <p className="text-xs text-gray-400">Trial signup rate</p>
          </div>
          <div className="bg-green-50 rounded-lg p-4 border border-green-200">
            <p className="text-xs text-gray-500 mb-2">Variant B · Leading</p>
            <p className="text-xs italic text-gray-600 mb-3 leading-relaxed">
              "Go from 2 hours to 18 minutes per content piece"
            </p>
            <p className="text-xl font-bold text-green-700">5.2%</p>
            <p className="text-xs text-gray-400">Trial signup rate</p>
          </div>
        </div>
        <p className="text-xs text-gray-400 mt-3">
          3,847 participants · Running since May 20 ·
          <span className="text-green-600 font-medium"> Variant B outperforming by +36.8%</span>
        </p>
      </div>

    </div>
  )
}

export default Dashboard
