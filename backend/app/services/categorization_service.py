def categorize_content(title: str, content: str) -> str:
    text = (title + " " + content).lower()

    if any(w in text for w in ["subject line", "open rate", "drip", "re-engagement", "unsubscribe", "email campaign", "cold email", "inbox"]):
        return "Email Campaign"

    if any(w in text for w in ["case study", "how they", "how we", "results:", "challenge:", "customer story", "client story", "cut their", "reduced", "increased their"]):
        return "Case Study"

    if any(w in text for w in ["linkedin", "instagram", "twitter", "tiktok", "social post", "hashtag", "impressions", "reach", "viral"]):
        return "Social Post"

    if any(w in text for w in ["product update", "we shipped", "new feature", "changelog", "release notes", "now available", "just launched"]):
        return "Product Update"

    if any(w in text for w in ["newsletter", "digest", "this week in", "weekly roundup", "curated", "edition"]):
        return "Newsletter"

    if any(w in text for w in ["landing page", "above the fold", "hero section", "conversion rate", "cta", "sign up now", "get started free"]):
        return "Landing Page Copy"

    return "Blog Post"
