import { useState } from "react"
import API from "../services/api"

const CONTENT_TYPES = [
  "Blog Post",
  "Email Campaign",
  "Social Media Post",
  "Product Description",
  "Newsletter",
  "Landing Page Copy",
]

const TONES = [
  "Professional",
  "Casual & Conversational",
  "Academic",
  "Technical",
  "Persuasive",
  "Inspirational",
]

function Field({ label, hint, children }) {
  return (
    <div>
      <div className="flex items-baseline justify-between mb-1.5">
        <label className="block text-sm font-medium text-gray-700">{label}</label>
        {hint && <span className="text-xs text-gray-400">{hint}</span>}
      </div>
      {children}
    </div>
  )
}

function ContentGenerator() {
  const [contentType, setContentType] = useState("")
  const [topic, setTopic] = useState("")
  const [audience, setAudience] = useState("")
  const [tone, setTone] = useState("")
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState("")
  const [copied, setCopied] = useState(false)

  const selectClass =
    "w-full px-3 py-2.5 border border-gray-300 rounded-lg bg-white text-sm text-gray-900 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
  const inputClass =
    "w-full px-3 py-2.5 border border-gray-300 rounded-lg text-sm text-gray-900 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent placeholder:text-gray-400"

  const generateContent = async () => {
    setError("")
    if (!contentType || !topic || !audience || !tone) {
      setError("Please fill in all fields before generating.")
      return
    }
    try {
      setLoading(true)
      setResult(null)
      const res = await API.post("/generate-content", { contentType, topic, audience, tone })
      setResult(res.data)
    } catch (err) {
      const detail = err?.response?.data?.detail
      setError(detail || "Content generation failed. Check that the backend is running and try again.")
    } finally {
      setLoading(false)
    }
  }

  const reset = () => {
    setResult(null)
    setError("")
    setTopic("")
    setAudience("")
    setCopied(false)
  }

  const copyToClipboard = () => {
    if (!result) return
    const text = `${result.title}\n\n${result.content}`
    navigator.clipboard.writeText(text).then(() => {
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    })
  }

  return (
    <div>
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Content Generator</h1>
        <p className="text-sm text-gray-500 mt-1">
          Generate audience-targeted content in seconds — blog posts, emails, case studies, and more.
        </p>
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-5 gap-6">

        {/* Form */}
        <div className="xl:col-span-2">
          <div className="bg-white rounded-xl border border-gray-200 p-5">
            <h2 className="text-sm font-semibold text-gray-900 mb-4">Content Settings</h2>

            <div className="space-y-4">

              <Field label="Content Type">
                <select value={contentType} onChange={(e) => setContentType(e.target.value)} className={selectClass}>
                  <option value="">Select a content type…</option>
                  {CONTENT_TYPES.map((t) => (
                    <option key={t} value={t}>{t}</option>
                  ))}
                </select>
              </Field>

              <Field label="Topic" hint="Be specific for better results">
                <input
                  type="text"
                  placeholder="e.g., Machine Learning in Healthcare Diagnostics"
                  value={topic}
                  onChange={(e) => setTopic(e.target.value)}
                  className={inputClass}
                />
              </Field>

              <Field label="Target Audience">
                <input
                  type="text"
                  placeholder="e.g., Healthcare professionals, age 30–50"
                  value={audience}
                  onChange={(e) => setAudience(e.target.value)}
                  className={inputClass}
                />
              </Field>

              <Field label="Tone of Voice">
                <select value={tone} onChange={(e) => setTone(e.target.value)} className={selectClass}>
                  <option value="">Select a tone…</option>
                  {TONES.map((t) => (
                    <option key={t} value={t}>{t}</option>
                  ))}
                </select>
              </Field>

              {error && (
                <div className="flex items-start gap-2 p-3 bg-red-50 border border-red-200 rounded-lg">
                  <svg className="w-4 h-4 text-red-500 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  <p className="text-xs text-red-700">{error}</p>
                </div>
              )}

              <button
                onClick={generateContent}
                disabled={loading}
                className="w-full flex items-center justify-center gap-2 bg-blue-600 hover:bg-blue-700 disabled:bg-blue-300 text-white text-sm font-semibold py-2.5 px-4 rounded-lg transition-colors"
              >
                {loading ? (
                  <>
                    <svg className="animate-spin w-4 h-4" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z" />
                    </svg>
                    Generating…
                  </>
                ) : (
                  <>
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                    </svg>
                    Generate Content
                  </>
                )}
              </button>
            </div>
          </div>

          {/* Tips */}
          <div className="mt-4 bg-blue-50 rounded-xl border border-blue-100 p-4">
            <h3 className="text-xs font-semibold text-blue-900 mb-2">Tips for better results</h3>
            <ul className="space-y-1.5">
              {[
                "Include keywords or phrases you want to rank for",
                "Specify pain points your audience faces",
                "Mention the desired content length or format",
              ].map((tip) => (
                <li key={tip} className="flex items-start gap-2 text-xs text-blue-700">
                  <svg className="w-3.5 h-3.5 flex-shrink-0 mt-0.5 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                  {tip}
                </li>
              ))}
            </ul>
          </div>
        </div>

        {/* Result */}
        <div className="xl:col-span-3">
          {!result && !loading && (
            <div className="h-full min-h-64 bg-white rounded-xl border border-dashed border-gray-300 flex flex-col items-center justify-center text-center p-8">
              <div className="w-12 h-12 bg-gray-100 rounded-xl flex items-center justify-center mb-3">
                <svg className="w-6 h-6 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                </svg>
              </div>
              <p className="text-sm font-medium text-gray-500">Your generated content will appear here</p>
              <p className="text-xs text-gray-400 mt-1">Fill in the settings on the left and click Generate</p>
            </div>
          )}

          {loading && (
            <div className="h-full min-h-64 bg-white rounded-xl border border-gray-200 flex flex-col items-center justify-center text-center p-8">
              <svg className="animate-spin w-8 h-8 text-blue-500 mb-3" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z" />
              </svg>
              <p className="text-sm font-medium text-gray-600">Generating your content…</p>
              <p className="text-xs text-gray-400 mt-1">This usually takes 5–10 seconds</p>
            </div>
          )}

          {result && (
            <div className="bg-white rounded-xl border border-gray-200 p-5">
              <div className="flex flex-wrap items-start justify-between gap-3 mb-4">
                <div>
                  <div className="flex items-center gap-2 mb-1">
                    <span className="px-2 py-0.5 bg-blue-100 text-blue-700 text-xs font-medium rounded-full">
                      {contentType}
                    </span>
                    <span className="px-2 py-0.5 bg-gray-100 text-gray-600 text-xs font-medium rounded-full">
                      {tone}
                    </span>
                  </div>
                  <h2 className="text-lg font-bold text-gray-900">{result.title}</h2>
                  {result.summary && (
                    <p className="text-sm text-gray-500 mt-1">{result.summary}</p>
                  )}
                </div>
                <button
                  onClick={reset}
                  className="flex items-center gap-1.5 text-xs text-gray-500 hover:text-gray-700 border border-gray-200 rounded-lg px-3 py-1.5 hover:bg-gray-50 transition-colors flex-shrink-0"
                >
                  <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                  </svg>
                  New
                </button>
              </div>

              <div className="bg-gray-50 rounded-lg p-4 mb-4 max-h-96 overflow-y-auto">
                <p className="text-sm text-gray-700 whitespace-pre-wrap leading-relaxed">{result.content}</p>
              </div>

              <div className="border-t border-gray-100 pt-4">
                <p className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-2">Metadata</p>
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                  {[
                    { label: "Topic", value: result.metadata?.topic || topic },
                    { label: "Audience", value: result.metadata?.audience || audience },
                    { label: "Tone", value: result.metadata?.tone || tone },
                  ].map(({ label, value }) => (
                    <div key={label} className="bg-gray-50 rounded-lg px-3 py-2">
                      <p className="text-xs text-gray-400">{label}</p>
                      <p className="text-sm font-medium text-gray-800 mt-0.5">{value}</p>
                    </div>
                  ))}
                </div>
              </div>

              <div className="flex gap-2 mt-4">
                <button
                  onClick={copyToClipboard}
                  className="flex items-center gap-1.5 text-sm font-medium text-gray-600 border border-gray-200 hover:bg-gray-50 px-4 py-2 rounded-lg transition-colors"
                >
                  {copied ? (
                    <>
                      <svg className="w-4 h-4 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                      </svg>
                      <span className="text-green-600">Copied!</span>
                    </>
                  ) : (
                    <>
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                      </svg>
                      Copy
                    </>
                  )}
                </button>
              </div>
            </div>
          )}
        </div>

      </div>
    </div>
  )
}

export default ContentGenerator
