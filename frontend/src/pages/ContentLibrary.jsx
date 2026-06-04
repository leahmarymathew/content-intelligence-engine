import { useEffect, useState } from "react"
import { Link } from "react-router-dom"
import API from "../services/api"

const SAMPLE_CONTENT = [
  {
    id: "c1",
    title: "Rethinking SaaS Onboarding: Why Your Day-1 Email Sets the Tone for Churn",
    summary: "Most SaaS teams spend 90% of their content budget on acquisition and nearly nothing on activation. This breaks down why your first onboarding email is your single highest-leverage asset—and how to rewrite it.",
    category: "Blog Post",
    topic: "Customer Retention",
    readTime: "6 min read",
    status: "Published",
  },
  {
    id: "c2",
    title: "Re-engagement Email — 'You've been quiet lately…'",
    summary: "A win-back campaign targeting users who hadn't logged in for 30+ days. Uses curiosity framing and a single, low-friction CTA. Recovered 11.4% of lapsed accounts in the first 72 hours.",
    category: "Email Campaign",
    topic: "Re-engagement",
    readTime: "Email · 180 words",
    status: "Published",
  },
  {
    id: "c3",
    title: "How Meridian Logistics Cut Their Content Production Time by 63%",
    summary: "Meridian's 3-person marketing team was publishing 4 pieces a month, mostly blogs written by the founder. After adopting AI-assisted workflows, they're now at 18 pieces—with measurably higher engagement across the board.",
    category: "Case Study",
    topic: "Customer Story",
    readTime: "8 min read",
    status: "Published",
  },
  {
    id: "c4",
    title: "The Engagement Paradox: Why Your Best Content Gets the Fewest Clicks",
    summary: "High-value content often underperforms in CTR but overperforms in pipeline influence. We analyzed 2,400 content pieces and found a consistent pattern—and a counter-intuitive fix.",
    category: "Blog Post",
    topic: "Content Strategy",
    readTime: "9 min read",
    status: "Published",
  },
  {
    id: "c5",
    title: "Product Update — May 2026: Batch Generation, Tone Presets & CRM Sync",
    summary: "This month we shipped three features our customers have been requesting for months: generate up to 50 pieces in a single batch job, save and reuse custom tone presets, and sync content metadata directly to HubSpot or Salesforce.",
    category: "Product Update",
    topic: "Product Announcements",
    readTime: "3 min read",
    status: "Published",
  },
  {
    id: "c6",
    title: "LinkedIn: We replaced our content calendar spreadsheet. Here's what happened.",
    summary: "A behind-the-scenes look at switching from manual content planning to AI-assisted scheduling—written as a first-person narrative for the brand LinkedIn account. Reached 14.2K impressions organically.",
    category: "Social Post",
    topic: "Brand Story",
    readTime: "LinkedIn · 220 words",
    status: "Published",
  },
  {
    id: "c7",
    title: "The ROI of AI Content Tools: A Framework for Marketing Leaders",
    summary: "Calculating ROI on content tooling is notoriously murky. This framework gives marketing leaders a practical model covering three dimensions: time saved per piece, quality delta, and attributed pipeline—with a worked example.",
    category: "Blog Post",
    topic: "Thought Leadership",
    readTime: "11 min read",
    status: "Draft",
  },
  {
    id: "c8",
    title: "June Newsletter — AI in Marketing: What's Real, What's Hype",
    summary: "Our monthly newsletter separating AI marketing trends that have real substance from the ones that are mostly noise—curated for busy marketing leaders who don't have time to read everything.",
    category: "Newsletter",
    topic: "Curated Insights",
    readTime: "Newsletter · 5 min read",
    status: "Draft",
  },
]

const CATEGORIES = ["All", "Blog Post", "Email Campaign", "Case Study", "Social Post", "Product Update", "Newsletter"]

const CATEGORY_COLORS = {
  "Blog Post":      "bg-blue-50 text-blue-700",
  "Email Campaign": "bg-orange-50 text-orange-700",
  "Case Study":     "bg-purple-50 text-purple-700",
  "Social Post":    "bg-pink-50 text-pink-700",
  "Product Update": "bg-teal-50 text-teal-700",
  "Newsletter":     "bg-green-50 text-green-700",
}

const STATUS_COLORS = {
  Published: "bg-green-100 text-green-700",
  Draft:     "bg-gray-100 text-gray-500",
}

function ContentModal({ item, onClose }) {
  if (!item) return null
  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50"
      onClick={onClose}
    >
      <div
        className="bg-white rounded-xl w-full max-w-xl max-h-[85vh] overflow-y-auto shadow-xl"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="p-6">
          {/* Modal header */}
          <div className="flex items-start justify-between gap-4 mb-4">
            <div className="flex flex-wrap gap-2">
              <span className={`text-xs px-2.5 py-1 rounded-full font-medium ${CATEGORY_COLORS[item.category] || "bg-gray-100 text-gray-600"}`}>
                {item.category}
              </span>
              {item.status && (
                <span className={`text-xs px-2 py-1 rounded-full font-medium ${STATUS_COLORS[item.status] || ""}`}>
                  {item.status}
                </span>
              )}
            </div>
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-600 flex-shrink-0 p-1 rounded-lg hover:bg-gray-100 transition-colors"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          <h2 className="text-base font-bold text-gray-900 leading-snug mb-3">{item.title}</h2>

          <div className="flex items-center gap-3 mb-4 text-xs text-gray-400">
            {item.readTime && <span>{item.readTime}</span>}
            {item.topic && (
              <>
                <span>·</span>
                <span>Topic: {item.topic}</span>
              </>
            )}
          </div>

          <div className="bg-gray-50 rounded-lg p-4 mb-4">
            <p className="text-sm text-gray-700 leading-relaxed">{item.summary}</p>
          </div>

          <div className="flex gap-2">
            <button
              onClick={() => {
                navigator.clipboard.writeText(`${item.title}\n\n${item.summary}`)
                onClose()
              }}
              className="flex items-center gap-1.5 text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 px-4 py-2 rounded-lg transition-colors"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
              </svg>
              Copy content
            </button>
            <button
              onClick={onClose}
              className="text-sm font-medium text-gray-500 border border-gray-200 hover:bg-gray-50 px-4 py-2 rounded-lg transition-colors"
            >
              Close
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

function ContentLibrary() {
  const [data, setData] = useState(SAMPLE_CONTENT)
  const [loading, setLoading] = useState(true)
  const [searchTerm, setSearchTerm] = useState("")
  const [activeCategory, setActiveCategory] = useState("All")
  const [selected, setSelected] = useState(null)

  useEffect(() => {
    API.get("/content-library")
      .then((res) => {
        if (res.data?.length > 0) {
          // Normalize API items to match the shape the UI expects
          const normalized = res.data.map((item) => ({
            ...item,
            category: item.category || item.metadata?.category || "Blog Post",
            topic: item.metadata?.topic || item.topic || "",
            status: "Published",
            readTime: item.content
              ? `${Math.max(1, Math.round(item.content.split(" ").length / 200))} min read`
              : null,
          }))
          setData(normalized)
        }
      })
      .catch(() => {})
      .finally(() => setLoading(false))
  }, [])

  const filtered = data.filter((item) => {
    const q = searchTerm.toLowerCase()
    const matchesSearch = !q ||
      item.title?.toLowerCase().includes(q) ||
      item.category?.toLowerCase().includes(q) ||
      item.topic?.toLowerCase().includes(q) ||
      item.summary?.toLowerCase().includes(q)
    const matchesCategory = activeCategory === "All" || item.category === activeCategory
    return matchesSearch && matchesCategory
  })

  return (
    <div>
      <ContentModal item={selected} onClose={() => setSelected(null)} />

      {/* Header */}
      <div className="flex flex-wrap items-start justify-between gap-4 mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Content Library</h1>
          <p className="text-sm text-gray-400 mt-0.5">
            {data.filter(i => i.status === "Published").length} published · {data.filter(i => i.status === "Draft").length} drafts
          </p>
        </div>
        <Link
          to="/generator"
          className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white text-sm font-semibold px-4 py-2.5 rounded-lg transition-colors flex-shrink-0"
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
          </svg>
          Generate content
        </Link>
      </div>

      {/* Search */}
      <div className="relative mb-4">
        <svg className="w-4 h-4 text-gray-400 absolute left-3.5 top-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
        </svg>
        <input
          type="text"
          placeholder="Search by title, topic, or summary…"
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="w-full pl-10 pr-4 py-2.5 border border-gray-200 rounded-lg text-sm bg-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent placeholder:text-gray-400"
        />
      </div>

      {/* Filters */}
      <div className="flex gap-2 mb-5 flex-wrap">
        {CATEGORIES.map((cat) => (
          <button
            key={cat}
            onClick={() => setActiveCategory(cat)}
            className={`px-3 py-1.5 rounded-full text-xs font-medium transition-colors whitespace-nowrap ${
              activeCategory === cat
                ? "bg-gray-900 text-white"
                : "bg-gray-100 text-gray-500 hover:bg-gray-200 hover:text-gray-700"
            }`}
          >
            {cat}
          </button>
        ))}
      </div>

      {loading && (
        <div className="flex justify-center py-12">
          <div className="animate-spin rounded-full h-7 w-7 border-b-2 border-blue-500" />
        </div>
      )}

      {!loading && filtered.length === 0 && (
        <div className="text-center py-16 bg-white rounded-xl border border-dashed border-gray-200">
          <svg className="mx-auto h-10 w-10 text-gray-200 mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 13h6m-3-3v6m5 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
          <p className="text-sm font-medium text-gray-600">
            {searchTerm ? `No results for "${searchTerm}"` : "No content in this category yet."}
          </p>
          {!searchTerm && (
            <Link to="/generator" className="text-xs text-blue-600 hover:underline mt-2 inline-block">
              Generate your first piece →
            </Link>
          )}
        </div>
      )}

      {!loading && filtered.length > 0 && (
        <>
          <p className="text-xs text-gray-400 mb-3">{filtered.length} item{filtered.length !== 1 ? "s" : ""}</p>
          <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 gap-4">
            {filtered.map((item) => (
              <div
                key={item.id}
                onClick={() => setSelected(item)}
                className="bg-white rounded-xl border border-gray-200 p-5 hover:shadow-md hover:border-gray-300 transition-all cursor-pointer flex flex-col"
              >
                <div className="flex items-center justify-between gap-2 mb-3">
                  <span className={`text-xs px-2.5 py-1 rounded-full font-medium ${CATEGORY_COLORS[item.category] || "bg-gray-100 text-gray-600"}`}>
                    {item.category}
                  </span>
                  {item.status && (
                    <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${STATUS_COLORS[item.status] || ""}`}>
                      {item.status}
                    </span>
                  )}
                </div>

                <h3 className="text-sm font-semibold text-gray-900 mb-2 line-clamp-2 leading-snug">
                  {item.title}
                </h3>

                <p className="text-xs text-gray-500 leading-relaxed line-clamp-3 flex-1 mb-3">
                  {item.summary}
                </p>

                <div className="flex items-center justify-between pt-3 border-t border-gray-100 mt-auto">
                  {item.readTime && (
                    <span className="text-xs text-gray-400">{item.readTime}</span>
                  )}
                  <span className="text-xs font-medium text-blue-600 ml-auto">Open →</span>
                </div>
              </div>
            ))}
          </div>
        </>
      )}
    </div>
  )
}

export default ContentLibrary
