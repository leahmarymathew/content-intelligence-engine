import { useState } from "react"

const INITIAL_WORKFLOWS = [
  {
    id: 1,
    name: "Publish → Push to CMS",
    description: 'When a piece is marked "Approved" in the library, automatically push the content and metadata to WordPress via the REST API and schedule it.',
    trigger: "Status change → Approved",
    triggerDetail: "Fires immediately on status update",
    action: "POST to WordPress REST API",
    actionDetail: "Sets post status to 'scheduled', attaches SEO metadata",
    status: "Active",
    audience: "Content Team",
    lastRun: "2 hours ago",
    runsTotal: 94,
    successRate: 98.9,
  },
  {
    id: 2,
    name: "Monday Morning Content Digest",
    description: "Every Monday at 8 AM, compile the previous week's published pieces into a digest email and send it to the internal marketing channel.",
    trigger: "Scheduled — Monday at 8:00 AM",
    triggerDetail: "Cron: 0 8 * * MON",
    action: "Compile digest → Send via SendGrid",
    actionDetail: "Delivered to marketing@team.internal",
    status: "Active",
    audience: "Marketing Team",
    lastRun: "2 days ago",
    runsTotal: 22,
    successRate: 100,
  },
  {
    id: 3,
    name: "Low Engagement Alert",
    description: "If a published piece drops below 40% engagement for 48 hours straight, notify the assigned editor in Slack so they can decide whether to revise or boost it.",
    trigger: "Metric threshold — Engagement < 40% for 48h",
    triggerDetail: "Checked every 6 hours",
    action: "Post alert to #content-alerts in Slack",
    actionDetail: "Includes piece title, current score, and direct link",
    status: "Active",
    audience: "Editorial Team",
    lastRun: "4 days ago",
    runsTotal: 7,
    successRate: 100,
  },
  {
    id: 4,
    name: "Trial Signup → Personalized Onboarding Email",
    description: "When a new user signs up for a trial, use their role and industry data from the signup form to generate a personalized first email via the AI engine.",
    trigger: "Event — New trial user created",
    triggerDetail: "Via webhook from auth service",
    action: "Generate personalized email → Queue in SendGrid",
    actionDetail: "Sent within 5 minutes of signup",
    status: "Inactive",
    audience: "All Trial Users",
    lastRun: "Never",
    runsTotal: 0,
    successRate: null,
  },
]

const STATUS_STYLES = {
  Active:   { badge: "bg-green-100 text-green-800", dot: "bg-green-500" },
  Inactive: { badge: "bg-gray-100 text-gray-500",   dot: "bg-gray-300" },
}

function WorkflowCard({ workflow, onToggle }) {
  const style = STATUS_STYLES[workflow.status] || STATUS_STYLES.Inactive

  return (
    <div className="bg-white rounded-xl border border-gray-200 p-5 flex flex-col">
      {/* Header */}
      <div className="flex items-start justify-between gap-3 mb-2">
        <div className="flex items-start gap-3 min-w-0">
          <div className="w-9 h-9 bg-blue-50 rounded-lg flex items-center justify-center flex-shrink-0">
            <svg className="w-5 h-5 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
            </svg>
          </div>
          <div className="min-w-0">
            <h3 className="text-sm font-semibold text-gray-900">{workflow.name}</h3>
            <p className="text-xs text-gray-400 mt-0.5">{workflow.audience}</p>
          </div>
        </div>
        <div className="flex items-center gap-1.5 flex-shrink-0">
          <div className={`w-1.5 h-1.5 rounded-full ${style.dot}`} />
          <span className={`text-xs px-2.5 py-1 rounded-full font-medium ${style.badge}`}>
            {workflow.status}
          </span>
        </div>
      </div>

      <p className="text-xs text-gray-500 leading-relaxed mb-4 ml-12">{workflow.description}</p>

      {/* Steps */}
      <div className="ml-12 mb-4 space-y-0">
        <div className="flex items-start gap-3">
          <div className="flex flex-col items-center">
            <div className="w-6 h-6 bg-purple-100 rounded-full flex items-center justify-center flex-shrink-0">
              <span className="text-purple-700 text-xs font-bold">1</span>
            </div>
            <div className="w-px flex-1 bg-gray-200 min-h-[18px] mt-1" />
          </div>
          <div className="pb-3 min-w-0">
            <p className="text-xs font-semibold text-gray-600">Trigger</p>
            <p className="text-xs text-gray-600">{workflow.trigger}</p>
            <p className="text-xs text-gray-400 font-mono">{workflow.triggerDetail}</p>
          </div>
        </div>
        <div className="flex items-start gap-3">
          <div className="w-6 h-6 bg-blue-100 rounded-full flex items-center justify-center flex-shrink-0">
            <span className="text-blue-700 text-xs font-bold">2</span>
          </div>
          <div className="min-w-0">
            <p className="text-xs font-semibold text-gray-600">Action</p>
            <p className="text-xs text-gray-600">{workflow.action}</p>
            <p className="text-xs text-gray-400">{workflow.actionDetail}</p>
          </div>
        </div>
      </div>

      {/* Stats */}
      <div className="ml-12 flex items-center gap-6 py-3 border-t border-gray-100 mb-3">
        <div>
          <p className="text-sm font-bold text-gray-900">{workflow.runsTotal}</p>
          <p className="text-xs text-gray-400">Total runs</p>
        </div>
        <div>
          <p className={`text-sm font-bold ${
            workflow.successRate === null ? "text-gray-400" :
            workflow.successRate >= 99  ? "text-green-600" :
            workflow.successRate >= 95  ? "text-blue-600"  : "text-orange-500"
          }`}>
            {workflow.successRate !== null ? `${workflow.successRate}%` : "—"}
          </p>
          <p className="text-xs text-gray-400">Success rate</p>
        </div>
        <div>
          <p className="text-sm font-bold text-gray-900">{workflow.lastRun}</p>
          <p className="text-xs text-gray-400">Last run</p>
        </div>
      </div>

      {/* Action */}
      <div className="ml-12">
        <button
          onClick={() => onToggle(workflow.id)}
          className={`text-xs font-semibold px-4 py-2 rounded-lg border transition-colors ${
            workflow.status === "Active"
              ? "text-orange-600 border-orange-200 hover:bg-orange-50"
              : "text-green-700 border-green-200 hover:bg-green-50"
          }`}
        >
          {workflow.status === "Active" ? "Pause workflow" : "Enable workflow"}
        </button>
      </div>
    </div>
  )
}

function Automation() {
  const [workflows, setWorkflows] = useState(INITIAL_WORKFLOWS)

  const toggleWorkflow = (id) => {
    setWorkflows((prev) =>
      prev.map((w) =>
        w.id === id
          ? { ...w, status: w.status === "Active" ? "Inactive" : "Active" }
          : w
      )
    )
  }

  const active = workflows.filter((w) => w.status === "Active").length
  const totalRuns = workflows.reduce((s, w) => s + w.runsTotal, 0)
  const rated = workflows.filter((w) => w.successRate !== null)
  const avgSuccess = rated.length
    ? (rated.reduce((s, w) => s + w.successRate, 0) / rated.length).toFixed(1)
    : "—"

  return (
    <div>
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Automation</h1>
        <p className="text-sm text-gray-400 mt-0.5">
          Event-driven and scheduled workflows that run your content operations hands-free.
        </p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        {[
          { label: "Total Workflows",    value: workflows.length, color: "text-gray-900" },
          { label: "Active",             value: active,           color: "text-green-600" },
          { label: "Total Runs",         value: totalRuns,        color: "text-blue-600" },
          { label: "Avg. Success Rate",  value: `${avgSuccess}%`, color: "text-gray-900" },
        ].map(({ label, value, color }) => (
          <div key={label} className="bg-white rounded-xl border border-gray-200 p-4 text-center">
            <p className={`text-2xl font-bold ${color}`}>{value}</p>
            <p className="text-xs text-gray-400 mt-0.5">{label}</p>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {workflows.map((w) => (
          <WorkflowCard key={w.id} workflow={w} onToggle={toggleWorkflow} />
        ))}
      </div>
    </div>
  )
}

export default Automation
