"""
Seed the database with realistic content and engagement data.

Run from the backend directory:
    python -m app.seed
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import Base, engine, SessionLocal
from app.models.content_model import Content
from app.models.engagement_model import Engagement
from app.models.experiment_model import Experiment, ExperimentEvent

CONTENT_ITEMS = [
    {
        "title": "Rethinking SaaS Onboarding: Why Your Day-1 Email Sets the Tone for Churn",
        "summary": "Most SaaS teams spend 90% of their content budget on acquisition and nearly nothing on activation. Your first onboarding email is your highest-leverage touchpoint—here's how to rewrite it.",
        "content": """## The Email Nobody Reads (That Determines Whether They Stay)

Most SaaS companies send the same day-1 email: a wall of links, a generic welcome, and instructions for features the user hasn't asked about yet. Open rates hover around 28%. Click rates are worse.

The problem isn't the email. It's the assumption behind it—that a new user needs a product tour when what they actually need is a reason to come back tomorrow.

## What High-Retention Companies Do Differently

Intercom's onboarding team ran an experiment in 2023: they replaced their feature-walkthrough email with a single question—"What's the one thing you're hoping to accomplish this week?" Responses drove a 34% lift in day-7 activation.

The lesson: users don't churn because they don't know where the settings panel is. They churn because they never had a moment where the product felt necessary.

## The 3-Part Framework

**1. Acknowledge their specific goal, not a generic use case.**
If you collected job title or use case at signup, use it. "As a content marketer, you'll probably want to start with..." outperforms "Welcome to the platform" by 2–3x on every metric that matters.

**2. Show one win, not ten features.**
Pick the single action that correlates most strongly with retention in your cohort data. For most SaaS products, it's one specific action taken in the first session. Guide them to that action only.

**3. Remove friction from the reply.**
End with a question. Not "Let us know if you need help" (passive), but "What were you hoping to get done today?" (specific). Replies are signals. They're also relationship-starters.

## The Rewrite That Moved the Needle

One B2B analytics company rewrote their day-1 email using this framework. The old email: 6 links, a GIF walkthrough, and a calendar link for an onboarding call. The new email: 3 sentences, one task, one question.

Day-7 activation went from 19% to 31%. Trial-to-paid conversion improved by 8 percentage points over the following quarter.

The best onboarding email isn't the one with the most information. It's the one that makes a user feel like the product was built specifically for them.""",
        "topic": "Customer Retention",
        "audience": "SaaS founders and marketing teams",
        "tone": "Professional",
        "category": "Blog Post",
        "engagement_score": 0.74,
        "click_rate": 0.062,
        "response_consistency": 0.91,
    },
    {
        "title": "Re-engagement Email: 'You've been quiet lately…'",
        "summary": "A win-back campaign for users inactive 30+ days. Curiosity framing + one low-friction CTA recovered 11.4% of lapsed accounts within 72 hours.",
        "content": """Subject: You've been quiet lately, {first_name}

Preview text: We noticed. Here's what you missed.

---

Hey {first_name},

It's been a while since we've seen you in [Product]. We get it—things get busy.

But while you were away, your competitors weren't.

Three things that changed since your last login:

• **Batch generation** — create up to 50 pieces at once (saves ~4 hours per week for teams your size)
• **Custom tone presets** — save your brand voice once, use it forever
• **HubSpot sync** — your content metadata now flows directly into your CRM

We've also fixed the export bug you might have hit last time.

One ask: come back for 10 minutes.

Not to explore everything—just to run one generation with your saved tone preset. If it doesn't save you time, we'll leave you alone.

[→ Generate something in 10 minutes]

If the timing still isn't right, no hard feelings. You can pause your account instead of cancelling—your data stays intact for 90 days.

— The [Product] team

P.S. Your last draft, "{last_draft_title}", is still waiting for you.""",
        "topic": "Re-engagement",
        "audience": "Lapsed trial users",
        "tone": "Casual & Conversational",
        "category": "Email Campaign",
        "engagement_score": 0.61,
        "click_rate": 0.114,
        "response_consistency": 0.88,
    },
    {
        "title": "How Meridian Logistics Cut Content Production Time by 63%",
        "summary": "Meridian's 3-person marketing team went from 4 pieces a month to 18—without adding headcount. Here's the exact workflow they built.",
        "content": """## The Problem: Great Ideas, No Time to Execute

In January 2026, Meridian Logistics' marketing team had a backlog of 47 content ideas and the bandwidth to execute maybe 4 of them per month. The team—a content manager, a designer, and a part-time SEO specialist—was spending 60% of their writing time on first drafts and structural editing.

"We knew what we wanted to say," says Marcus Webb, Meridian's Head of Marketing. "We just couldn't get it out fast enough."

## The Approach: AI-Assisted, Human-Edited

Meridian's team spent two weeks building a workflow around AI-assisted content generation. The process they landed on:

**Step 1 — Brief creation (10 min)**
Each piece starts with a structured brief: topic, audience, tone, key claims, and one mandatory real-world example. The brief gets fed directly into the generation tool.

**Step 2 — AI first draft (3-5 min)**
The tool generates a complete draft. The team reviews for factual accuracy, brand voice, and narrative flow—not grammar.

**Step 3 — Human edit pass (25-35 min)**
Writers focus entirely on quality, not structure. They add proprietary data, customer quotes, and Meridian-specific context. "The AI gives us something to react to instead of a blank page," Webb notes.

**Step 4 — Design + publish (1 hour)**
Unchanged from before.

## The Results: 6 Months Later

| Metric | Before | After |
|---|---|---|
| Monthly output | 4 pieces | 18 pieces |
| Avg. time per piece | 6.5 hours | 2.4 hours |
| Engagement rate | 52% | 71% |
| Pipeline influenced | $140K/quarter | $380K/quarter |

The team didn't grow. The tools changed.

## What Made It Work

The critical factor wasn't the AI—it was the brief quality. Teams that front-load 10 minutes of structured thinking produce dramatically better outputs than teams that type vague prompts and hope for the best.

Meridian now runs a weekly "brief clinic" where the team reviews upcoming topics and tightens the briefs together before anything goes to generation.""",
        "topic": "Customer Story",
        "audience": "B2B marketing teams",
        "tone": "Professional",
        "category": "Case Study",
        "engagement_score": 0.84,
        "click_rate": 0.091,
        "response_consistency": 0.95,
    },
    {
        "title": "The Engagement Paradox: Why Your Best Content Gets the Fewest Clicks",
        "summary": "We analyzed 2,400 content pieces and found a consistent pattern: the highest-value content underperforms in clicks but overperforms in pipeline. Here's what to do about it.",
        "content": """## The Data That Confused Our Clients

Across 2,400 pieces of B2B content analyzed over 18 months, we found a pattern that initially confused every client we showed it to.

The pieces with the lowest click-through rates—sometimes under 2%—were generating the most qualified pipeline. The high-CTR pieces (4–8%) were driving traffic, but virtually no revenue.

This is the engagement paradox.

## Why It Happens

High-CTR content is usually:
- Listicles and "X things you should know" posts
- Contrarian takes designed to trigger a reaction
- News commentary with a quick opinion

These formats earn clicks because they're designed to. But they attract everyone, which means they attract no one in particular. The visitor who clicks "7 signs your content strategy is broken" is a marketer, a student, a competitor, or a curious person—not necessarily your buyer.

High-value content is usually:
- Specific to a narrow audience with a named problem
- Longer and more technical
- Less shareable but more referenceable

The CFO doesn't share your blog post. But they do forward the 2,000-word breakdown of unit economics in SaaS content to their VP of Marketing with a note: "This is what we should be tracking."

## The Fix: Separate Your Metrics by Goal

Stop measuring all content by the same KPIs. Assign one of three goals to every piece before you publish:

**Awareness content** — optimize for CTR, reach, and shares. Accept lower quality scores.

**Consideration content** — optimize for time on page, return visits, and email signups. CTR is irrelevant.

**Decision content** — optimize for demo requests, trial signups, and sales conversations influenced. Don't even publish CTR data to stakeholders—it will mislead them.

When Clearwave, a healthcare SaaS company, separated their content metrics this way, they stopped killing their highest-value pieces based on traffic data. Pipeline-influenced revenue from content grew 44% in the following two quarters.""",
        "topic": "Content Strategy",
        "audience": "Content marketers and marketing leaders",
        "tone": "Professional",
        "category": "Blog Post",
        "engagement_score": 0.78,
        "click_rate": 0.048,
        "response_consistency": 0.92,
    },
    {
        "title": "Product Update — May 2026: Batch Generation, Tone Presets & CRM Sync",
        "summary": "Three features shipped this month that our customers have been requesting since launch: batch generation (up to 50 pieces), saveable tone presets, and direct HubSpot/Salesforce sync.",
        "content": """## What We Shipped This Month

May was one of our biggest release months since launch. Here's exactly what changed and why.

---

### Batch Generation — Up to 50 Pieces at Once

**The problem:** Teams were running the generator one piece at a time, then manually compiling results. For anyone producing 20+ pieces a week, this was the main bottleneck.

**What changed:** You can now submit a batch of up to 50 briefs in one job. Upload a CSV with your topics, audiences, and tone, or build the batch in-app. Results arrive in your library when the job completes—usually under 4 minutes for a full batch.

**Who it's for:** Content teams managing multiple clients, brands, or product lines simultaneously.

---

### Custom Tone Presets

**The problem:** Re-specifying brand voice every generation was friction. Teams described their tone differently each time, which led to inconsistent output.

**What changed:** You can now save named tone presets (e.g., "Meridian — Technical, Direct", "Blog — Conversational"). Presets persist across sessions and can be shared with your team.

**Who it's for:** Anyone who generates content for the same brand repeatedly.

---

### HubSpot & Salesforce Sync

**The problem:** Content metadata (topic, audience, performance) lived in our platform but not in the CRMs where sales teams work.

**What changed:** Connect your HubSpot or Salesforce account in Settings → Integrations. Published content metadata syncs automatically. Sales reps can now filter accounts by which content they've engaged with.

**Who it's for:** Teams using content for pipeline generation, not just awareness.

---

## What's Coming in June

- Content scoring (AI-rated quality before you publish)
- A/B variant generation (produce two versions of any piece in one click)
- Slack notifications for completed batch jobs

Questions or feedback? Reply to this email or book a call with your account manager.""",
        "topic": "Product Announcements",
        "audience": "Existing customers and power users",
        "tone": "Professional",
        "category": "Product Update",
        "engagement_score": 0.56,
        "click_rate": 0.031,
        "response_consistency": 0.94,
    },
    {
        "title": "We replaced our content calendar spreadsheet. Here's what happened.",
        "summary": "Switched from a 47-tab spreadsheet to AI-assisted content planning. The honest breakdown of what got better, what got worse, and what surprised us.",
        "content": """We ran our content calendar on a spreadsheet for three years.

It had 47 tabs, 12 conditional formatting rules, and a color-coding system that only one person on the team fully understood.

Last quarter we replaced it. Here's the honest breakdown.

**What got immediately better:**
→ Brief creation dropped from 45 minutes to 12
→ First drafts stopped looking like first drafts
→ We stopped losing good ideas because they didn't fit the template

**What got harder:**
→ The approval workflow took 3 weeks to rebuild in the new system
→ Two team members had a legitimate adjustment period
→ We over-generated for the first month and had to build a quality filter

**The thing that surprised us most:**
We thought the time savings would come from faster writing. They didn't. They came from fewer revision cycles. When the structure is right from the start, editors spend time on ideas—not on reorganizing paragraphs.

Three months in: we're publishing 4x as much, our engagement is up, and the spreadsheet is archived (not deleted—we're not monsters).

The tool doesn't replace judgment. It just removes the part of the job that wasn't judgment to begin with.

#ContentMarketing #MarketingOps #B2BMarketing #ContentStrategy #AITools""",
        "topic": "Brand Story",
        "audience": "Marketing professionals on LinkedIn",
        "tone": "Casual & Conversational",
        "category": "Social Post",
        "engagement_score": 0.48,
        "click_rate": 0.142,
        "response_consistency": 0.87,
    },
    {
        "title": "Measuring Content ROI: A Framework That Actually Works for B2B",
        "summary": "Most content ROI frameworks fail because they try to attribute revenue to individual pieces. This model measures what content actually influences—and gives you numbers you can defend in a board meeting.",
        "content": """## Why Standard Content ROI Models Break

Ask most marketing leaders how they measure content ROI and you'll hear one of three answers:

1. "We track traffic and leads"
2. "We use last-touch attribution"
3. "We honestly don't have a great answer"

The first two are measuring the wrong things. The third is at least honest.

The problem with last-touch attribution in B2B content is structural: buyers read 7-13 pieces of content before talking to sales. Crediting the last piece ignores 12 touchpoints that built the trust that made the conversation possible.

## A Better Model: Content Influence Scoring

Instead of attributing revenue to content, measure content's influence on the buyer journey. The framework has three layers:

**Layer 1 — Awareness Contribution**
Did this content introduce your brand to someone who later became a customer? Track new contacts generated per piece. Goal: 15+ net-new contacts per blog post per quarter.

**Layer 2 — Consideration Acceleration**
Did deals with content-engaged contacts close faster? Compare average sales cycle length for contacts who consumed 3+ pieces vs. those who consumed none. A 15-20% cycle reduction is common for content-mature programs.

**Layer 3 — Pipeline Influence**
Of the deals that closed this quarter, what percentage had contact with your content? This is your "content-influenced pipeline" number—the one that belongs in board decks.

## How to Implement This in 30 Days

**Week 1:** Tag all content with a UTM structure that ties to your CRM.
**Week 2:** Build a "content engagement" field in your CRM that tracks piece count per contact.
**Week 3:** Pull a cohort report comparing sales cycles by content engagement level.
**Week 4:** Calculate content-influenced pipeline for the trailing quarter.

This won't give you a perfect attribution model. Nothing will. But it gives you a defensible story about what content does for the business—which is what your CFO is actually asking for.""",
        "topic": "Thought Leadership",
        "audience": "Marketing leaders and CMOs",
        "tone": "Professional",
        "category": "Blog Post",
        "engagement_score": 0.71,
        "click_rate": 0.055,
        "response_consistency": 0.89,
    },
    {
        "title": "The Content Intelligence Digest — June 2026",
        "summary": "This month: AI content tools that are actually shipping useful features, the death of the generic blog post, and one framework for deciding what to never automate.",
        "content": """**The Content Intelligence Digest** · June 2026

---

Good morning,

Three things worth your attention this month.

---

**1. The generic blog post is officially dead.**

Google's March 2026 algorithm update quietly de-ranked a massive segment of AI-generated content—specifically content that covers a topic broadly without a specific point of view or original data.

The shift is already showing up in search console data for dozens of companies. The sites holding position are the ones with authored content, proprietary research, and named perspectives.

The takeaway: AI is great for execution speed. It is not a substitute for having something worth saying.

---

**2. The feature that changed how we think about content operations.**

Batch generation shipped last month, and the use case we didn't anticipate is the one getting the most traction: competitive analysis at scale.

One customer is generating 50 response pieces per week—one per competitor claim—and staging them for rapid deployment when those claims come up in sales conversations. Their sales team calls it "the objection library." Win rate on competitive deals is up 18% since implementation.

---

**3. One thing to never automate.**

Customer interviews.

No matter how good the tooling gets, the signal you get from a 45-minute conversation with a churned customer cannot be replicated by any model. It's the highest-quality input to any content strategy, and it's the one task where automation creates the most risk.

Everything else is negotiable.

---

That's it for June.

If you have something worth sharing with this community—data, a framework, an honest post-mortem—hit reply. The best issues of this newsletter come from you.

— The Content Intelligence team""",
        "topic": "Curated Insights",
        "audience": "Marketing leaders and content strategists",
        "tone": "Professional",
        "category": "Newsletter",
        "engagement_score": 0.63,
        "click_rate": 0.042,
        "response_consistency": 0.91,
    },
]


EXPERIMENTS = [
    {
        "name": "Homepage Hero — Outcome vs. Process Messaging",
        "hypothesis": "Outcome-focused copy ('save 18 minutes per piece') will convert better than feature-focused copy because visitors care more about results than how we deliver them.",
        "status": "Active",
        "variant_a_name": "Process messaging",
        "variant_a_copy": "The only content platform that writes, tests, and learns for you",
        "variant_b_name": "Outcome messaging",
        "variant_b_copy": "Go from 2 hours to 18 minutes per content piece",
        "metric_label": "Trial Signup Rate",
        "traffic_split": 50,
        "start_date": "May 20, 2026",
        "end_date": "Jun 20, 2026",
        # ~3.8% rate A, ~5.2% rate B out of ~2000 impressions each
        "events": (
            [("A", "impression")] * 2000 +
            [("A", "conversion")] * 76 +
            [("B", "impression")] * 1847 +
            [("B", "conversion")] * 96
        ),
    },
    {
        "name": "Onboarding Email #2 — Tutorial vs. Social Proof",
        "hypothesis": "Showing a real customer story on day 3 will drive higher day-7 activation than a step-by-step tutorial, because new users are still in trust-building mode.",
        "status": "Completed",
        "variant_a_name": "Step-by-step tutorial",
        "variant_a_copy": "How to generate your first piece in under 10 minutes",
        "variant_b_name": "Customer story",
        "variant_b_copy": "See how Meridian went from 4 to 18 pieces a month",
        "metric_label": "Day-7 Activation",
        "traffic_split": 50,
        "start_date": "Apr 8, 2026",
        "end_date": "May 8, 2026",
        # ~41.2% rate A, ~54.7% rate B out of ~600 each
        "events": (
            [("A", "impression")] * 600 +
            [("A", "conversion")] * 247 +
            [("B", "impression")] * 604 +
            [("B", "conversion")] * 330
        ),
    },
    {
        "name": "LinkedIn Post Format — Question Hook vs. Bold Claim",
        "hypothesis": "Posts opening with a counter-intuitive bold statement will get higher reach than question-based hooks because the algorithm favors early engagement.",
        "status": "Draft",
        "variant_a_name": "Question hook",
        "variant_a_copy": "Why do your best content pieces get the fewest clicks?",
        "variant_b_name": "Bold claim",
        "variant_b_copy": "Your highest-traffic blog post is probably your worst business investment.",
        "metric_label": "Engagement Rate",
        "traffic_split": 50,
        "start_date": "Jun 15, 2026",
        "end_date": "Jul 15, 2026",
        "events": [],
    },
]


def seed():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        existing = db.query(Content).count()
        if existing > 0:
            print(f"Database already has {existing} content items. Skipping seed.")
            print("To reseed, delete content.db and run again.")
            return

        print("Seeding database with sample content and engagement data...")
        for i, item in enumerate(CONTENT_ITEMS, 1):
            content = Content(
                title=item["title"],
                summary=item["summary"],
                content=item["content"],
                topic=item["topic"],
                audience=item["audience"],
                tone=item["tone"],
                category=item["category"],
            )
            db.add(content)
            db.flush()

            engagement = Engagement(
                content_id=content.id,
                click_rate=item["click_rate"],
                engagement_score=item["engagement_score"],
                response_consistency=item["response_consistency"],
            )
            db.add(engagement)
            print(f"  [{i}/{len(CONTENT_ITEMS)}] {item['title'][:60]}...")

        db.commit()
        print(f"\n[1/2] Seeded {len(CONTENT_ITEMS)} content items with engagement data.")

        # Seed experiments
        exp_existing = db.query(Experiment).count()
        if exp_existing > 0:
            print(f"[2/2] Experiments already seeded ({exp_existing} found). Skipping.")
        else:
            print("[2/2] Seeding experiments...")
            for item in EXPERIMENTS:
                exp = Experiment(
                    name=item["name"],
                    hypothesis=item["hypothesis"],
                    status=item["status"],
                    variant_a_name=item["variant_a_name"],
                    variant_a_copy=item["variant_a_copy"],
                    variant_b_name=item["variant_b_name"],
                    variant_b_copy=item["variant_b_copy"],
                    metric_label=item["metric_label"],
                    traffic_split=item["traffic_split"],
                    start_date=item["start_date"],
                    end_date=item["end_date"],
                )
                db.add(exp)
                db.flush()

                for variant, event_type in item["events"]:
                    db.add(ExperimentEvent(
                        experiment_id=exp.id,
                        variant=variant,
                        event_type=event_type,
                    ))

                print(f"     {item['name'][:60]}… ({len(item['events'])} events)")

            db.commit()
            print(f"     Done. Seeded {len(EXPERIMENTS)} experiments.")

        print("\nSeed complete.")
    except Exception as e:
        db.rollback()
        print(f"Error during seed: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed()
