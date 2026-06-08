#!/usr/bin/env python3
"""Generate static deep-dive reader pages for the Bezos concepts hub."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = ROOT / "analysis"
SUMMARY_PATH = Path(__file__).resolve().parent / "simple_summaries.json"


def summary_key(year: int, title: str, line_ranges: list[list[int]]) -> str:
    ranges = ",".join(f"{start}-{end}" for start, end in line_ranges)
    return f"{year}|{ranges}|{title}"


def load_simple_summaries() -> dict[str, dict[str, str]]:
    if not SUMMARY_PATH.exists():
        return {}
    raw = json.loads(SUMMARY_PATH.read_text(encoding="utf-8"))
    return {
        key: value
        for key, value in raw.items()
        if not key.startswith("_") and isinstance(value, dict)
    }


SIMPLE_SUMMARIES = load_simple_summaries()


def simple_fallback(why: str) -> dict[str, str]:
    return {"summary": why}


def card(
    year: int,
    pillar: str,
    title: str,
    quote: str,
    why: str,
    support: str,
    takeaway: str,
    line_ranges: list[list[int]],
    tags: list[str],
) -> dict:
    range_text = " and ".join(f"{start}-{end}" for start, end in line_ranges)
    simple = {
        **simple_fallback(why),
        **SIMPLE_SUMMARIES.get(summary_key(year, title, line_ranges), {}),
    }
    simple = {"summary": simple["summary"]}
    return {
        "year": year,
        "pillar": pillar,
        "title": title,
        "source": f"../data/extracted/{year}.md",
        "range": f"lines {range_text}",
        "lineRanges": line_ranges,
        "quote": quote,
        "why": why,
        "support": support,
        "takeaway": takeaway,
        "simple": simple,
        "tags": tags,
    }


IDEAS = [
    {
        "file": 'long_term_thinking_reader.html',
        "title": 'Long-Term Thinking',
        "kicker": 'Personal operating system',
        "thesis": 'Long-term thinking is a decision system: prefer what compounds customer trust and future cash flow, even when it makes the current quarter look worse.',
        "life": 'Use it for career, investing, health, and relationships: optimize for the future value of a choice, not how it looks right now.',
        "business": 'Use it to justify patient investment, durable customer trust, and free-cash-flow discipline over short-term earnings optics.',
        "children": ['Long-term thinking', 'Ownership vs tenancy', 'Enduring franchise', 'Market leadership logic'],
        "cards": [
            card(1997, 'foundation', 'The original operating philosophy', "It's All About the Long Term", 'This is the root text. Bezos tells shareholders that Amazon will prioritize market leadership, customer growth, brand strength, analytical investment, bold bets, and future cash flow over short-term optics.', 'Read the full bullet list after the heading. It is effectively the constitution for how Amazon wants to make tradeoffs.', 'This is the base layer. Long-term thinking is not patience by itself. It is a specific operating contract with shareholders.', [[45, 130]], ['market leadership', 'customer focus', 'cash flow', 'bold bets', 'shareholder alignment']),
            card(1998, 'foundation', 'Forward investment as the less risky path', 'least risky long-term value creation approach', 'Bezos explains why heavy investment in distribution, systems, brand promise, product expansion, and people/processes can be rational even when it looks expensive.', 'The surrounding material shows the operational burden of scaling, not just a slogan about growth.', 'Forward investment is justified only when it builds the customer experience and the infrastructure needed for a much larger business.', [[219, 305]], ['infrastructure', 'scaling', 'brand promise', 'investment risk']),
            card(1999, 'foundation', 'Long-term franchise, not just near-term growth', 'long-term franchise', 'The 1999 letter connects profitability, return on capital, partnerships, platform leverage, and customer service to the long-term franchise idea.', 'This is useful as a bridge between the 1997 philosophy and the later free-cash-flow language.', 'A long-term franchise is not just a big company. It is a company whose platform makes future opportunities easier and more profitable.', [[269, 305]], ['franchise', 'profitability', 'return on capital', 'platform']),
            card(2000, 'foundation', 'Stock price voting versus business weighing', 'build a heavier and heavier company', 'During the dot-com collapse, Bezos separates market opinion from business substance. The goal is to improve the company that will eventually be weighed.', 'Read this with 2012, where he repeats the same Benjamin Graham idea after positive stock movement.', 'Long-term thinking means asking whether the company is getting stronger, not whether the stock market is currently approving.', [[71, 81], [169, 173]], ['stock noise', 'business substance', 'Benjamin Graham']),
            card(2001, 'finance', 'Future cash flow is the financial target', 'future cash flows', 'This converts long-term thinking into valuation language. A share is valuable because of future cash flows and future share count, not because earnings look nice today.', 'The surrounding section connects customer repeat purchases to more cash flow and more long-term shareholder value.', 'The financial version of long-term thinking is future free cash flow per share, not current accounting polish.', [[153, 215]], ['valuation', 'free cash flow', 'share count', 'customers']),
            card(2003, 'owner', 'Owner mindset, not tenant mindset', 'Owners are different from tenants.', 'This is the cleanest definition of long-term thinking as behavior. Owners protect the asset. Tenants optimize the moment.', 'The examples around negative reviews, Instant Order Update, free shipping, and price cuts show the idea becoming concrete.', 'If 1997 is the philosophy, 2003 is the behavior test. A long-term owner willingly gives up bad short-term revenue to build trust.', [[11, 95]], ['ownership', 'tenant mindset', 'negative reviews', 'free shipping', 'price-cost loop']),
            card(2004, 'finance', 'Free cash flow per share beats accounting appearance', 'free cash flow per share', 'Bezos explains why earnings growth can destroy value if it requires too much capital. Long-term thinking requires knowing the right scorecard.', 'The later section explains operating cycle, inventory turns, capital efficiency, and share dilution.', 'Good long-term thinking needs the right metric. Otherwise you can grow the wrong number and destroy value.', [[11, 29], [345, 385]], ['earnings quality', 'capital efficiency', 'inventory', 'dilution']),
            card(2005, 'customer', 'Judgment when short-term math is incomplete', 'start with the customer and work backwards', 'The short-term math says lower prices hurt. Bezos argues that the five-to-ten-year trust effect cannot be fully measured, so leadership judgment matters.', 'Read this with Prime and Free Super Saver Shipping in mind. Both were expensive before their long-term logic was obvious.', 'Long-term thinking often requires judgment where the measurable short-term number is pointing the other way.', [[49, 101], [123, 165]], ['pricing', 'judgment', 'Prime', 'shipping', 'working backwards']),
            card(2006, 'invention', 'Planting small seeds with discipline', 'discipline, a bit of patience', 'This shows that patience is not random experimentation. New businesses need return potential, large scale, differentiation, and customer relevance.', 'The small-seed section is useful because it explains why a big company must protect ideas that are not yet big.', 'Protecting saplings is not charity. It is a disciplined way to let future large businesses survive their small early stage.', [[9, 31], [75, 125]], ['seed planting', 'return bar', 'differentiation', 'culture']),
            card(2008, 'customer', 'Long-term thinking plus working backwards', 'work patiently for multiple years', 'This is one of the best supporting passages. Long-term orientation lets Amazon learn new capabilities because the customer need is durable.', 'Kindle, stable customer needs, pricing, Prime, FBA, and AWS all appear in the same surrounding section.', 'Long-term thinking lets you build new muscles when the customer need is durable enough to justify the learning curve.', [[11, 131]], ['working backwards', 'Kindle', 'durable needs', 'Prime', 'AWS']),
            card(2009, 'customer', 'Controllable inputs over financial outputs', 'controllable inputs', 'Amazon manages what teams can directly improve: customer experience goals, owners, deliverables, invention, and urgency.', 'The surrounding section is useful because Bezos shows the annual planning process, not just the principle.', 'If you want long-term financial results, manage the inputs that can compound those results.', [[109, 157]], ['inputs', 'goals', 'owners', 'customer experience']),
            card(2010, 'customer', 'Customer and owner interests align', 'aligned with the interests of customers', 'This is a short confirmation of the recurring bridge: serve customers well enough and the owner outcome follows.', 'Read after 2001 and 2003. It is the same argument, now made with more years of execution behind it.', "The customer is not outside the financial model. In Amazon's model, customer trust is the route to owner value.", [[145, 153]], ['alignment', 'customers', 'owners', 'invention']),
            card(2012, 'customer', 'Proactive customer delight earns trust', 'long-term thinking squares the circle', 'This is the clearest statement of the customer-shareholder bridge. Improvements can look too generous now, but trust compounds into future business.', 'The stock-market passage nearby reinforces the difference between celebrating stock price and improving customer experience.', 'Proactive improvement builds trust before competitors or customers force the issue, and trust opens future business.', [[21, 31], [125, 159]], ['trust', 'Prime', 'AWS', 'Kindle', 'weighing machine']),
            card(2013, 'culture', 'Taking the long view in everyday invention', 'taking the long view', 'This letter shows long-term thinking as daily behavior: patient refinement, asking how to make things better, accepting messy invention, and preferring substance over optics.', 'Amazon Fresh, Prime, Mayday, Kindle, and decentralized invention appear as examples of patient improvement around customers.', 'Long-term thinking shows up in everyday improvement, patient trials, and willingness to learn through messy invention.', [[11, 25], [203, 217], [547, 573]], ['patient culture', 'Amazon Fresh', 'invention', 'substance over optics']),
            card(2014, 'invention', 'Dreamy businesses last for decades', 'durable in time', 'Marketplace, Prime, and AWS are framed as durable offerings that took bold bets, risk, and nurture before becoming obvious.', 'The closing section says Amazon will continue searching for a fourth big idea while keeping the 1997 approach.', 'The best long-term bets are not just big. They are loved by customers, economically strong, and durable.', [[11, 35], [435, 447]], ['Marketplace', 'Prime', 'AWS', 'durability', 'bold bets']),
            card(2015, 'culture', 'Culture is how the philosophy survives scale', 'patience to think long-term', 'By this point, long-term thinking is described as a cultural trait, not just a CEO preference.', 'The AWS passage shows the same approach working in a business far from online retail.', 'A philosophy survives scale only when it becomes culture, ownership, and operating practice.', [[29, 34], [295, 307], [519, 523]], ['culture', 'AWS', 'single-threaded owners', 'operational excellence']),
            card(2016, 'culture', 'Day 1 protects against slow decline', 'experiment patiently', 'This links long-term thinking to anti-complacency. Day 2 may harvest for years, but decline still arrives if invention stops.', 'The supporting line about planting seeds and protecting saplings is the operator version of patience.', 'Long-term thinking is not comfort. It is the discipline that keeps a successful company from becoming passive.', [[13, 23], [53, 56]], ['Day 1', 'Day 2', 'experiments', 'saplings', 'customer delight']),
            card(2020, 'foundation', 'Looking back: the bets were not preordained', 'create more than you consume', 'In his final CEO letter, Bezos looks back at Prime, Marketplace, Alexa, and AWS as risky work, then widens the principle to value creation in business and life.', 'The nearby future-cash-flow reminder connects the moral language of value creation back to investor economics.', 'The final CEO letter closes the loop: long-term thinking created value because Amazon kept making non-obvious bets that increased future usefulness.', [[11, 33], [55, 65]], ['Prime', 'Marketplace', 'Alexa', 'AWS', 'value creation']),
        ],
    },
    {
        "file": "day_1_anti_complacency_reader.html",
        "title": "Day 1 Anti-Complacency",
        "kicker": "Culture and scale",
        "thesis": "Day 1 is the habit of staying urgent, curious, customer-close, and allergic to institutional drift after success arrives.",
        "life": "Use it when a good routine has quietly turned into autopilot. Ask what reality, customer, or external trend you are no longer seeing.",
        "business": "Use it to diagnose whether a team is defending yesterday's process or still learning from customers, trends, and fast decisions.",
        "children": ["Day 1 mentality", "Day 2 decline", "Embrace external trends", "Keep a company non-typical", "Differentiation is survival"],
        "cards": [
            card(1997, "origin", "Day 1 starts as opportunity, not nostalgia", "this is Day 1 for the Internet", "The original Day 1 language is about the size and freshness of the opportunity. It is a warning to execute while the terrain is still being formed.", "Read the surrounding paragraphs with the long-term section. Day 1 begins as a market and customer opportunity, then becomes an operating posture.", "Day 1 is not a slogan about energy. It is a demand to keep acting as if the opportunity is still being created.", [[11, 43]], ["origin", "internet", "execution"]),
            card(1998, "origin", "Still Day 1 after early success", "it remains Day 1 for Amazon.com", "After explosive growth, Bezos repeats the Day 1 frame to resist premature satisfaction. Growth does not remove the need for execution.", "The nearby customer and infrastructure sections show that Day 1 means scaling without losing customer focus.", "The first danger after success is believing the hard part is over.", [[21, 31]], ["success", "execution", "humility"]),
            card(1999, "origin", "Day 1 during category formation", "this remains Day 1 for e-commerce", "Bezos repeats the Day 1 frame while describing customer relationship formation. The opportunity is still early, so Amazon must keep earning first-time customer trust.", "This fills an important missing bridge between the early Internet Day 1 language and the later Day 2 defense.", "Day 1 means behaving as if customer relationships are still being formed, not already owned.", [[177, 185]], ["category formation", "customer relationships", "early days"]),
            card(2016, "diagnosis", "Day 2 is the slow death pattern", "Day 2 is stasis", "This is the clearest anti-complacency passage. Bezos names the sequence from stasis to irrelevance to decline to death.", "The question is not whether decline starts visibly. The passage says Day 2 can last for decades before the end state appears.", "Complacency is dangerous because it is usually comfortable before it is fatal.", [[9, 33]], ["day 2", "decline", "stasis"]),
            card(2016, "defense", "Customer obsession is protective", "customers are always beautifully, wonderfully dissatisfied", "Customer dissatisfaction keeps a company from coasting. Even happy customers want something better, so customer obsession creates useful restlessness.", "The Prime example matters because no customer asked for it directly, yet customer desire pulled the invention forward.", "The best anti-complacency force is not fear of competitors. It is active empathy for customers.", [[35, 57]], ["customer obsession", "prime", "restlessness"]),
            card(2016, "defense", "Proxies create fake progress", "process as proxy", "Day 2 starts when the symbol of progress replaces the result. Teams can follow a process and stop looking at whether customers are better served.", "The survey discussion extends the idea: averages and process outputs can hide the lived customer experience.", "A process is useful only while it keeps you closer to the result.", [[59, 101]], ["proxies", "process", "surveys"]),
            card(2016, "defense", "External trends are tailwinds or threats", "embrace powerful trends quickly", "A successful company can still be pushed into Day 2 if it refuses an external trend. The issue is not trend-chasing. It is trend denial.", "Machine learning is the example in the letter. Bezos frames it as a powerful trend that can quietly improve many parts of the business.", "If a major trend is real, ignoring it does not make you disciplined. It makes you exposed.", [[103, 151]], ["external trends", "machine learning", "tailwinds"]),
            card(2016, "defense", "Decision velocity keeps Day 1 alive", "high-quality, high-velocity decisions", "Slow decisions are a large-company disease. Bezos argues that big organizations must preserve decision speed without abandoning quality.", "The section gives practical mechanisms: two-way doors, 70 percent information, disagree and commit, and quick escalation.", "Day 1 requires decisions that are good enough, fast enough, and cleanly committed.", [[153, 233]], ["decision speed", "70 percent", "commitment"]),
            card(2014, "renewal", "Keep searching for the fourth idea", "we won't stop trying", "Marketplace, Prime, and AWS are celebrated, but Bezos immediately turns the attention back to improving them and searching for another big idea.", "This is Day 1 anti-complacency in a positive form: even three major wins do not justify stopping the search.", "Day 1 treats existing winners as responsibilities to improve, not trophies to admire.", [[435, 447]], ["bold bets", "renewal", "customer invention"]),
            card(2018, "renewal", "Listening and wandering keep Day 1 alive", "listening to customers and wandering on their behalf", "The 2018 close ties Day 1 to customer listening, wandering, and pioneering spirit.", "This line matters because it shows Day 1 as a company-wide practice, not only a CEO phrase or early-stage company mood.", "A large company stays Day 1 by keeping curiosity and customer listening distributed across teams.", [[389, 395]], ["wandering", "customer listening", "pioneering spirit"]),
            card(2020, "life", "Originality is part of survival", "be kind, be original", "In the final CEO letter, the Day 1 close is linked to the personal fight against being made normal. Differentiation is a survival issue.", "The surrounding passage makes the idea more general than business: distinctiveness takes continuous energy.", "Day 1 at the personal level means protecting your useful originality from slow conformity.", [[449, 545]], ["originality", "differentiation", "personal operating system"]),
        ],
    },
    {
        "file": "customer_backed_empathy_reader.html",
        "title": "Customer-Backed Empathy",
        "kicker": "Customer and service mindset",
        "thesis": "Start from the person served, not from the org chart, competitor, spreadsheet, or current skill set.",
        "life": "Use it by asking who is actually affected, what they experience, and what would make their life meaningfully easier.",
        "business": "Use it to turn customer needs into product choices, operating priorities, and investments that compound trust.",
        "children": ["Customer obsession as empathy", "Working backwards", "Be proactive before pressure", "Proactive customer delight", "Stable customer needs", "Customer experience pillars"],
        "cards": [
            card(1997, "foundation", "Compelling value before scale", "offering our customers compelling value", "The earliest customer section is concrete: selection, useful browsing, 1-Click, reviews, recommendations, lower prices, and trust.", "This makes customer obsession operational before the later language becomes famous.", "Empathy starts by making the customer's job easier in visible ways.", [[155, 181]], ["customer value", "selection", "trust"]),
            card(1998, "foundation", "Brand follows reality", "brand image follows reality", "Bezos treats customers as perceptive. You cannot brand your way around a weak experience.", "The passage names selection, ease of use, low prices, and service as the reasons customers choose and recommend Amazon.", "Empathy starts by respecting that customers eventually know the truth.", [[123, 157]], ["brand", "service", "customer reality"]),
            card(2001, "pillars", "Three customer-experience pillars", "selection and convenience", "Amazon adds relentlessly lowering prices to selection and convenience as a core customer-experience pillar.", "The surrounding examples show self-service, Look Inside the Book, and error elimination as customer-backed operating choices.", "A customer-backed system names the few experience pillars it will keep improving.", [[83, 135]], ["selection", "convenience", "lower prices"]),
            card(2002, "mechanism", "Turn experience into fixed cost", "world-leading customer experience and the lowest possible prices", "Amazon tries to escape the traditional tradeoff between high-touch experience and low price by using technology as fixed cost.", "The surrounding section is useful because it explains why scale can improve both price and service.", "A good system can make empathy cheaper to deliver over time.", [[11, 57]], ["fixed cost", "technology", "low prices"]),
            card(2003, "behavior", "Customer experience is every touchpoint", "every customer-facing aspect of our business", "This passage defines customer experience broadly: price, selection, interface, packaging, and shipping.", "The negative review and order-update examples show empathy even when it reduces a short-term transaction.", "Customer empathy is not sentiment. It is visible in the tradeoffs you make when money is on the table.", [[21, 59]], ["touchpoints", "reviews", "short-term sales"]),
            card(2008, "method", "Working backwards from durable needs", "work patiently for multiple years", "If a customer need is meaningful and durable, Amazon lets that need pull it into new capabilities.", "Kindle is the example: customer need required hardware, software, service, and new muscles.", "Work backwards means the need chooses the learning curve.", [[11, 35]], ["working backwards", "kindle", "durable needs"]),
            card(2008, "pillars", "Stable needs justify patient investment", "higher prices, less selection, or slower delivery", "Bezos names retail needs that are unlikely to reverse: low prices, broad selection, and fast convenient delivery.", "Because the needs are stable, Amazon can keep investing behind them even when the payback is long.", "When a customer need will not go away, the investment can compound for years.", [[63, 87]], ["stable needs", "price", "selection", "delivery"]),
            card(2012, "proactive", "Improve before pressure forces you", "We lower prices and increase value for customers before we have to.", "Customer-backed empathy is proactive. Amazon tries to delight customers before a competitor or complaint makes it necessary.", "The refund examples make this concrete: Amazon finds bad experiences and returns value without requiring customers to ask.", "The highest-trust service fixes problems before the customer has to carry the burden.", [[21, 79]], ["proactive", "refunds", "trust"]),
            card(2016, "depth", "Surveys are not enough", "heart, intuition, curiosity, play, guts, taste", "Bezos warns that market research can become a proxy for customers. Good builders study anecdotes and understand customers deeply.", "The passage is not anti-data. It says surveys and beta tests cannot replace ownership-level customer understanding.", "Empathy needs data, but it also needs taste, attention, and direct human understanding.", [[35, 101]], ["surveys", "intuition", "customer understanding"]),
            card(2017, "expectations", "Customers are divinely discontent", "Customers won't have it.", "The 2017 letter reframes customer empathy around rising expectations. Yesterday's wow becomes ordinary.", "The passage explains why customer-backed thinking has to keep moving even after high satisfaction scores.", "Customer empathy is dynamic because expectations rise as soon as the old delight becomes normal.", [[35, 53]], ["expectations", "discontent", "continuous improvement"]),
        ],
    },
    {
        "file": "high_standards_and_craft_reader.html",
        "title": "High Standards and Craft",
        "kicker": "Standards and craft",
        "thesis": "High standards mean knowing what good looks like, knowing the true scope of the work, and caring about invisible quality.",
        "life": "Use it for writing, health, school, work, and relationships by asking whether you understand the real standard and the effort required.",
        "business": "Use it to build teams where quality is teachable, visible, and protected even when the work is behind the scenes.",
        "children": ["High standards are teachable", "High standards are domain-specific", "Recognition and scope", "Hidden work matters"],
        "cards": [
            card(2017, "teachable", "High standards can be learned", "high standards are teachable", "Bezos rejects the idea that high standards are only innate. Exposure to a high-standards team changes what people recognize.", "The section also explains why articulating principles can accelerate the learning.", "Raise standards by making quality visible and contagious.", [[55, 79]], ["teachable", "culture", "exposure"]),
            card(2017, "domain", "Standards do not transfer automatically", "high standards are domain specific", "A person can have excellent standards in one domain and weak standards in another. Each craft has to be learned.", "Bezos uses his own operational-process learning as the example.", "Do not assume competence in one area means standards in another.", [[81, 101]], ["domain specific", "learning", "operations"]),
            card(2017, "scope", "Recognition plus realistic scope", "recognize what good looks like", "The framework is simple: recognize quality and understand how hard the work should be.", "The handstand story shows how wrong expectations about time can destroy high standards even when motivation is high.", "Low standards often come from underestimating the real scope.", [[107, 139]], ["recognition", "scope", "handstand"]),
            card(2017, "writing", "Six-page memos reveal hidden scope", "great memos are written and re-written", "The memo example translates the handstand idea into business craft. A good memo is not produced in a few spare hours.", "This is useful because it shows invisible work in a knowledge-work setting.", "If you want excellent output, budget the real work behind it.", [[145, 177]], ["memos", "writing", "hidden work"]),
            card(2017, "leadership", "You can hold standards without doing every craft", "recognize high standards for those things", "A leader does not need to perform every role personally, but they must recognize quality and teach realistic scope.", "The passage protects teams from vague taste and unrealistic demands by tying leadership to standards and scope.", "Leadership requires knowing enough to judge quality and coach the work.", [[183, 199]], ["leadership", "coaching", "quality"]),
            card(2017, "culture", "Invisible work needs protection", "work that no one sees", "High standards protect work no customer sees directly, such as defect prevention and unseen service operations.", "The passage also connects high standards to recruiting, retention, and pride in professionalism.", "A high-standards culture makes invisible excellence worth doing.", [[201, 219]], ["invisible work", "professionalism", "retention"]),
            card(2017, "principle", "Leadership standard as explicit expectation", "unreasonably high", "The leadership principle makes high standards a role expectation, not just an aesthetic preference.", "This short passage is useful as the operating version of the 2017 framework.", "High standards become real when leaders are expected to raise the bar repeatedly.", [[223, 229]], ["leadership principle", "bar raising", "expectation"]),
        ],
    },
    {
        "file": "decision_quality_and_speed_reader.html",
        "title": "Decision Quality and Speed",
        "kicker": "Decision quality",
        "thesis": "Match the decision process to reversibility, move before certainty when appropriate, and commit cleanly after debate.",
        "life": "Use it to stop treating every choice like a permanent life decision. Separate reversible experiments from true one-way doors.",
        "business": "Use it to keep large teams from slowing down every decision with one heavyweight process.",
        "children": ["Type 1 decisions", "Type 2 decisions", "70% information rule", "Disagree and commit", "Escalate true misalignment", "One-size-fits-all decision trap"],
        "cards": [
            card(2005, "judgment", "Judgment decisions invite debate", "judgment-based decisions are rightly debated", "Not every important decision has clean data. Bezos frames debate as natural when judgment is the main ingredient.", "The passage closes by returning to customer-backwards reasoning as the best decision compass.", "Healthy debate is a feature of judgment decisions, not a failure of alignment.", [[123, 165]], ["judgment", "debate", "customer backwards"]),
            card(2015, "type", "One-way doors need heavyweight care", "consequential and irreversible or nearly irreversible", "Type 1 decisions are serious because their consequences are hard to reverse. They need methodical process.", "The contrast with Type 2 decisions is the key. The problem is not rigor, but misapplying rigor everywhere.", "Use heavy process only where the decision is truly hard to reverse.", [[417, 425]], ["type 1", "irreversible", "risk"]),
            card(2015, "type", "Two-way doors should move quickly", "changeable, reversible", "Most decisions are two-way doors. If they go wrong, you can reopen the door and correct course.", "Bezos warns that large organizations tend to treat Type 2 decisions as Type 1, creating slowness and risk aversion.", "Speed improves when you recognize that many choices are reversible experiments.", [[427, 443]], ["type 2", "reversible", "speed"]),
            card(2016, "velocity", "Day 1 needs high-velocity decisions", "high-quality, high-velocity decisions", "The 2016 letter makes speed part of Day 1 defense. Slow high-quality decisions are not enough.", "The passage stresses that large companies can still preserve decision velocity if they are intentional.", "A good decision system optimizes both quality and tempo.", [[153, 169]], ["velocity", "large company", "day 1"]),
            card(2016, "information", "The 70 percent rule", "70% of the information", "Waiting for almost complete information is often too slow. Bezos argues that many decisions should happen around 70 percent information.", "The key caveat is correction. The cost of being wrong is lower if you are good at noticing and correcting bad calls.", "Do not wait for certainty when fast correction is available.", [[171, 181]], ["70 percent", "uncertainty", "correction"]),
            card(2016, "commitment", "Disagree and commit preserves speed", "disagree and commit", "This phrase lets teams move after sincere disagreement without pretending everyone agrees.", "The example of Amazon Studios shows even the boss can disagree and still commit to the team's judgment.", "Commitment after debate is how disagreement stops becoming drag.", [[183, 207]], ["disagree and commit", "commitment", "team speed"]),
            card(2016, "alignment", "Escalate real misalignment quickly", "recognize true misalignment issues early", "Sometimes teams have different objectives and cannot resolve the issue by wearing each other down. Bezos says escalate quickly.", "The passage frames exhaustion as a bad alignment strategy.", "When goals conflict, escalation is faster and healthier than grinding people down.", [[213, 233]], ["misalignment", "escalation", "exhaustion"]),
        ],
    },
    {
        "file": "judgment_beyond_proxies_reader.html",
        "title": "Judgment Beyond Proxies",
        "kicker": "Decision quality",
        "thesis": "Use data and process, but do not let measurements, surveys, or short-term math replace judgment.",
        "life": "Use it when a metric is convenient but incomplete. Ask what the metric cannot see.",
        "business": "Use it to protect customer trust, invention, and long-term economics from false precision.",
        "children": ["Resist proxies", "Data plus judgment", "Long-term judgment against short-term math", "Heart, intuition, curiosity, taste"],
        "cards": [
            card(2005, "math", "Some decisions are math-based", "math-based", "Bezos first gives data its due. Many operational decisions can be improved by models, forecasts, and quantitative analysis.", "This matters because the proxy argument is not anti-analytics. It is about knowing where analytics stop.", "Respect math where the system can be modeled.", [[11, 55]], ["math", "operations", "forecasting"]),
            card(2005, "judgment", "Long-term price trust beats short-term math", "we go against the math", "Price cuts can look wrong in short-term elasticity math because the five-to-ten-year trust effect cannot be measured cleanly.", "Free Super Saver Shipping and Prime appear as similar judgment calls.", "When the long-term trust effect is real but unmeasurable, judgment must carry the decision.", [[57, 101]], ["pricing", "trust", "long term"]),
            card(2016, "proxy", "Process can become the goal", "process as proxy", "A good process helps serve customers. A bad process becomes the thing people manage instead of the customer result.", "The key diagnostic is whether the team is asking if the process or the outcome deserves credit.", "Do not mistake doing the process for achieving the result.", [[59, 77]], ["process", "proxy", "outcomes"]),
            card(2016, "customer", "Surveys can hide the customer", "market research and customer surveys can become proxies", "Surveys can be useful, but they can also replace deeper customer understanding.", "Bezos says good inventors study anecdotes and use heart, intuition, curiosity, play, guts, and taste.", "Customer understanding is richer than the average response in a survey.", [[79, 101]], ["surveys", "anecdotes", "taste"]),
            card(2018, "wandering", "Nonlinear problems need more than efficiency", "wandering in business is not efficient", "Some inventions cannot be found by a straight-line plan. They require guided wandering.", "This passage gives judgment a role in ambiguous work: hunch, gut, intuition, curiosity, and conviction about customer value.", "Efficiency is not the right proxy when the path itself is unknown.", [[141, 163]], ["wandering", "intuition", "nonlinear"]),
            card(2018, "invention", "Customers cannot always ask for the future", "customers don't know to ask for", "Bezos says the biggest needle movers may be things customers do not know to request.", "AWS is the example of inventing on behalf of customers even without a direct ask.", "Listening is necessary, but invention sometimes requires seeing beyond stated requests.", [[179, 187]], ["AWS", "inventing on behalf", "unstated needs"]),
        ],
    },
    {
        "file": "invention_portfolio_reader.html",
        "title": "Invention Portfolio",
        "kicker": "Innovation and experimentation",
        "thesis": "Protect small seeds, run many experiments, accept failure, wander intelligently, and let rare big winners pay for the misses.",
        "life": "Use it by treating learning projects as a portfolio: many small tries, a few promising saplings, and patience for compounding.",
        "business": "Use it to design an innovation system where failure is expected, bounded when possible, and large enough to matter at scale.",
        "children": ["Plant seeds and protect saplings", "Failure is part of invention", "Failure and invention are inseparable", "Big winners pay for many losers", "Wandering", "Builder's mentality", "Beginner's mind"],
        "cards": [
            card(1997, "origin", "Learn from successes and failures", "successes and our failures", "The original shareholder framework already includes both successes and failures.", "This early line is brief, but it shows that Amazon expected experimentation from the start.", "A serious invention system assumes some bets will not work.", [[87, 97]], ["origin", "learning", "failure"]),
            card(2008, "permission", "Long-term thinking permits failure and iteration", "failure and iteration required for invention", "The 2008 letter connects long-term thinking directly to the failure and iteration that invention needs.", "This passage was missing from the first-pass reader even though it is a compact statement of the invention portfolio logic.", "Without a long enough horizon, experimentation gets starved before it can teach you.", [[11, 17]], ["long term", "failure", "iteration"]),
            card(2006, "seeds", "New businesses need patience and culture", "discipline, a bit of patience, and a nurturing culture", "Bezos describes new businesses as seeds that need more than capital. They need discipline, patience, and culture.", "The same section defines selection criteria: large potential, strong returns, customer-facing differentiation.", "Do not protect every idea. Protect ideas that meet a disciplined bar and need time.", [[11, 31]], ["seeds", "patience", "discipline"]),
            card(2006, "culture", "Small seeds need protection inside a big company", "tiny seeds", "A new business can look tiny beside established businesses, so culture must keep it from being dismissed too early.", "Bezos says meaningful new businesses may take three to seven years before they matter to company economics.", "Without cultural protection, today's tiny idea never gets the chance to become tomorrow's engine.", [[75, 125]], ["saplings", "culture", "time horizon"]),
            card(2013, "experiments", "Weblab makes experimentation routine", "1,976 Weblabs worldwide", "The Weblab section shows experimentation as operating infrastructure, not a special event.", "The numbers matter because they show experiments happening at scale across websites and products.", "A portfolio works better when experimentation is easy and normal.", [[371, 381]], ["weblab", "experiments", "infrastructure"]),
            card(2013, "failure", "Failure is part and parcel", "Failure comes part and parcel with invention.", "Bezos says failure is not optional if you want invention. The trick is failing early and iterating.", "The passage adds the portfolio logic: most experiments start small, and when one works for customers, Amazon doubles down.", "You cannot demand invention and also demand zero failure.", [[547, 565]], ["failure", "iteration", "doubling down"]),
            card(2015, "failure", "Failure and invention are inseparable", "inseparable twins", "The 2015 letter makes the failure principle explicit. Companies that cannot tolerate failed experiments also limit invention.", "The surrounding section explains why Amazon's scale allows large enough experiments to matter.", "The price of meaningful invention is a string of experiments that may fail.", [[57, 79]], ["failure", "experiments", "scale"]),
            card(2016, "saplings", "Protect saplings and double down", "plant seeds, protect saplings", "The Day 1 defense compresses the invention portfolio into one operating sequence: experiment, accept failures, plant, protect, then double down on customer delight.", "This connects the invention page back to Day 1 and customer obsession.", "The portfolio is not just starting ideas. It is protecting and scaling the right ones.", [[41, 57]], ["saplings", "day 1", "customer delight"]),
            card(2018, "wandering", "Builders keep beginner's mind", "culture of builders", "Builders stay curious even when they are experts. They keep a beginner's mind and keep reinventing.", "The passage links builder culture with wandering, iteration, and big hard-to-solve opportunities.", "A builder's mentality keeps expertise from becoming rigidity.", [[141, 163]], ["builders", "beginner mind", "wandering"]),
            card(2018, "scale", "Failure needs to scale too", "Failure needs to scale too", "As Amazon becomes larger, tiny failures cannot produce meaningful learning for the whole company.", "The Fire Phone and Echo comparison shows how one failed bet and one big winner can emerge from adjacent wandering.", "At scale, the experiment portfolio must be large enough for wins to move the needle.", [[281, 311]], ["big failures", "echo", "fire phone"]),
            card(2020, "retrospective", "The big bets were not preordained", "none was preordained", "Looking back, Bezos emphasizes that Prime, Marketplace, Alexa, and AWS were not obvious or inevitable.", "This passage gives the retrospective proof of the portfolio: risk, sweat, ingenuity, and non-obvious bets created the later pillars.", "A portfolio only looks obvious after the winners have compounded.", [[11, 33]], ["prime", "marketplace", "alexa", "AWS"]),
        ],
    },
    {
        "file": "missionary_value_creation_reader.html",
        "title": "Missionary Value Creation",
        "kicker": "Stakeholder and society",
        "thesis": "Create more value than you consume, care about the mission, and resist becoming generic.",
        "life": "Use it as a moral test: are you adding real value to the people around you, or mainly extracting from the system?",
        "business": "Use it to distinguish missionary builders from mercenary operators and to evaluate whether a model creates non-zero-sum value.",
        "children": ["Missionary mindset", "Create more than you consume", "Value is not zero-sum", "Be kind, be original"],
        "cards": [
            card(2007, "mission", "Missionaries build better products", "missionaries build better products", "The Kindle section explains why passion for the mission matters. Bezos believes missionaries make better products than mercenaries.", "The passage is rooted in reading, but the idea applies to any product where deep care affects decisions.", "Mission is useful when it improves the work, not when it becomes branding language.", [[41, 131]], ["kindle", "missionaries", "product"]),
            card(2011, "platform", "Platforms create non-zero-sum value", "not zero-sum", "AWS, FBA, and KDP are framed as self-service platforms that let others do what was previously impossible or impractical.", "The value creation spans developers, entrepreneurs, customers, authors, and readers.", "A missionary business widens opportunity instead of only shifting value from one pocket to another.", [[145, 157]], ["self-service", "non-zero-sum", "platforms"]),
            card(2012, "team", "Missionaries value customers daily", "missionaries who value our customers", "This short close shows missionary language applied to the team, not only to Kindle.", "It connects mission to repeated daily behavior toward customers.", "Mission has to show up in how people serve customers every day.", [[161, 163]], ["team", "customers", "daily behavior"]),
            card(2013, "reading", "Missionaries for reading", "missionaries for reading", "The reading stories give the missionary idea emotional grounding. The mission is not abstract; it comes from seeing customer lives changed.", "The line sits near Kindle examples where invention is tied to reader benefit.", "Mission gets stronger when builders stay close to the human story.", [[63, 71]], ["reading", "kindle", "human story"]),
            card(2020, "value", "Create more than you consume", "create more than you consume", "In the final CEO letter, Bezos turns value creation into a business and life principle.", "The passage immediately links success to creating value for everyone you interact with.", "A life or company succeeds by being a net creator of value.", [[55, 65]], ["life", "value creation", "net positive"]),
            card(2020, "society", "Real value creation is not zero-sum", "not a zero-sum game", "Bezos widens the lens from Amazon to society and says invention is the root of real value creation.", "This passage ties employees, sellers, customers, and shareholders into one value-creation frame.", "The best business models make the total pie larger.", [[167, 173]], ["society", "invention", "stakeholders"]),
            card(2020, "originality", "Be kind and original", "be kind, be original", "The closing passage makes originality an ethical and practical requirement.", "It is a personal version of the same differentiation logic: do not let the world smooth away what makes you useful.", "Missionary value creation needs kindness plus distinctiveness.", [[509, 545]], ["originality", "kindness", "personal"]),
        ],
    },
    {
        "file": "trust_flywheel_reader.html",
        "title": "Trust Flywheel",
        "kicker": "Customer and service mindset",
        "thesis": "Earn trust through reality: lower prices, better service, honest information, speed, selection, and proactive improvement.",
        "life": "Use it by noticing that trust compounds from repeated small proofs, not big promises.",
        "business": "Use it to connect customer trust with durable economics: lower costs, lower prices, more volume, more scale, and more trust.",
        "children": ["Customer trust as asset", "Everyday low prices", "Price-cost flywheel", "Advanced technology should feel simple", "Better and faster beats cheaper alone"],
        "cards": [
            card(2001, "loop", "The price-cost flywheel", "Please expect us to repeat this loop.", "The 2001 letter gives the clearest early flywheel mechanics: cost improvement allows lower prices, lower prices drive growth, growth spreads fixed costs, and that enables more price reductions.", "This was a missing foundational card for trust because it ties customer liking to shareholder economics.", "Trust compounds when better economics are returned to customers repeatedly.", [[11, 33]], ["price-cost loop", "fixed costs", "growth"]),
            card(2002, "tradeoff", "Low price plus better experience", "what's good for customers is good for shareholders", "Amazon argues it can lower prices and improve experience by turning parts of customer experience into fixed cost.", "The section connects customer satisfaction, price reductions, and shareholder value.", "Trust compounds when the system keeps giving customers more value.", [[101, 167]], ["low prices", "experience", "shareholders"]),
            card(2003, "honesty", "Negative reviews build trust", "negative reviews cost us some sales", "Showing negative reviews can reduce a short-term sale, but it helps customers make better decisions.", "This is a clean example of giving up bad revenue to build better trust.", "Honest information is a trust asset even when it costs a transaction.", [[37, 59]], ["reviews", "honesty", "short term"]),
            card(2003, "loop", "Price-cost loop", "price-cost structure loop", "Bezos explains the loop from efficient scale to lower prices to more value for customers and a larger bottom line over time.", "The passage is important because it makes trust economic, not merely emotional.", "A flywheel works when customer value and business efficiency reinforce each other.", [[61, 91]], ["price-cost loop", "scale", "economics"]),
            card(2005, "judgment", "Low prices need long-term judgment", "relentlessly returning efficiency improvements", "Price cuts may look bad in short-term math, but Bezos believes they create a long-term trust effect.", "Prime and Free Super Saver Shipping are included as judgment calls with similar logic.", "Trust often has to be built before the spreadsheet can prove it.", [[57, 101]], ["pricing", "judgment", "prime"]),
            card(2008, "trust", "Pricing objective is customer trust", "earn customer trust", "Amazon explicitly says its pricing objective is not short-term profit optimization.", "The section also explains why customers notice total cost, including shipping charges.", "Trust grows when customers believe the company is on their side repeatedly.", [[63, 87]], ["pricing objective", "total cost", "trust"]),
            card(2012, "proactive", "Proactive fixes delight customers", "surprises, delights, and earns trust", "Amazon's automated refunds and pre-order price protection show trust created by removing customer burden.", "These examples are powerful because they are expensive and voluntary.", "Trust deepens when customers do not have to fight for fairness.", [[55, 79]], ["refunds", "fairness", "delight"]),
            card(2014, "AWS", "Better and faster beats cheaper alone", "better and faster", "Bezos explains that AWS wins by making customers better and faster, with cost savings as a bonus rather than the whole offer.", "This directly supports the merged trust-flywheel child idea that low cost is not enough if the product is weaker.", "Trust is stronger when the service improves capability, speed, and cost at the same time.", [[249, 291]], ["AWS", "better and faster", "capability"]),
            card(2014, "flywheel", "FBA links Marketplace and Prime", "This is powerful for our flywheel.", "FBA creates a win for sellers and customers, while increasing Prime selection and seller sales.", "The flywheel is not metaphor only. It is a set of participant incentives reinforcing each other.", "Trust scales when the system makes multiple parties better off at once.", [[211, 245]], ["FBA", "Prime", "Marketplace"]),
        ],
    },
    {
        "file": "free_cash_flow_discipline_reader.html",
        "title": "Free Cash Flow Discipline",
        "kicker": "Business model and capital",
        "thesis": "Judge business value by future cash flow per share, capital efficiency, and dilution, not surface accounting appearance.",
        "life": "Use it as a personal-finance analogy: do not confuse looking profitable with actually producing durable surplus.",
        "business": "Use it to evaluate whether growth creates owner value after capital needs, working capital, and dilution.",
        "children": ["Free cash flow per share", "Earnings can mislead", "Capital efficiency"],
        "cards": [
            card(1997, "origin", "Cash flows over accounting appearance", "we'll take the cash flows", "The original letter tells investors Amazon will choose present value of future cash flows over GAAP accounting appearance.", "This is the root of the later free-cash-flow scorecard.", "The financial contract starts with cash value, not cosmetic accounting.", [[99, 109]], ["origin", "cash flow", "accounting"]),
            card(2001, "valuation", "A share is a claim on future cash flows", "future cash flows", "Bezos explains why cash flows and share count are central to stock value.", "The passage also covers dilution and why cash flow per share matters more than total cash flow alone.", "Owner value depends on future cash flow per share.", [[153, 215]], ["valuation", "share count", "dilution"]),
            card(2004, "scorecard", "The ultimate financial measure", "free cash flow per share", "This is the clearest statement of Amazon's primary financial measure.", "Bezos explains why earnings, EPS, and earnings growth can miss working capital, capex, and dilution.", "Free cash flow per share is the scorecard because it tracks owner economics more directly.", [[11, 29]], ["scorecard", "EPS", "capex"]),
            card(2004, "warning", "Earnings growth can destroy value", "cumulative negative free cash flow", "The transportation-business example shows how strong earnings growth can coexist with terrible cash economics.", "This is the anti-surface-metric passage for investors.", "Growth is not valuable if it consumes more capital than it creates.", [[163, 171]], ["earnings", "negative FCF", "capital intensity"]),
            card(2004, "warning", "EBITDA is not cash flow", "EBITDA isn't cash flow", "Bezos warns that excluding capital expenditures gives only part of the story.", "The passage is useful because it attacks a common shortcut used in business analysis.", "If the assets must be replaced or expanded, the cash outflow matters.", [[251, 265]], ["EBITDA", "capex", "cash reality"]),
            card(2004, "mechanism", "Inventory turns and dilution matter", "cash generative operating cycle", "Amazon's model benefits from fast inventory turns, supplier payment timing, modest fixed assets, and attention to share count.", "This is the operating explanation behind free cash flow per share.", "The best scorecard connects finance to operating mechanics.", [[345, 385]], ["operating cycle", "inventory", "dilution"]),
            card(2008, "capital", "Free cash flow with high returns", "maximizing long-term free cash flow", "The 2008 letter links free cash flow with high rates of return on invested capital.", "The nearby muda section shows that waste removal supports the financial goal.", "Cash flow discipline is not separate from operations. Waste removal improves the economics.", [[113, 131]], ["ROIC", "waste", "operations"]),
            card(2014, "AWS", "Capital efficiency in AWS", "strong returns on capital", "AWS is capital intensive, so Bezos explicitly examines utilization and capital efficiency.", "The passage shows the same scorecard applied to a different business model.", "A great business can be capital intensive if scale and utilization create strong returns.", [[365, 377]], ["AWS", "capital efficiency", "returns"]),
            card(2020, "reminder", "Stock prices look forward", "prediction of future cash flows", "The final CEO letter restates the valuation idea: prices look forward to future cash flows.", "This closes the loop from 1997 and 2001 after Amazon has become a much larger company.", "Even after massive scale, the owner lens is still future cash flow.", [[63, 65]], ["valuation", "future", "stock price"]),
        ],
    },
    {
        "file": "operating_system_of_excellence_reader.html",
        "title": "Operating System of Excellence",
        "kicker": "Culture and scale",
        "thesis": "Translate strategy into controllable inputs, waste removal, ownership, inspection, and repeatable execution.",
        "life": "Use it by converting vague goals into inputs you can own, inspect, and improve.",
        "business": "Use it to connect customer experience, productivity, cost structure, and financial outputs through mechanisms.",
        "children": ["Operational excellence", "Muda and waste removal", "Controllable inputs over outputs"],
        "cards": [
            card(1998, "scale", "Scale requires operational excellence", "operational excellence and high efficiency", "Amazon's 1998 investment section makes operational excellence a requirement for serving tens of millions of customers.", "The passage connects distribution capacity, systems capacity, people, process, and 24x7 availability.", "Customer promise becomes real only through operational capacity.", [[219, 249]], ["scale", "systems", "capacity"]),
            card(1999, "goals", "Operational excellence as a major goal", "driving operational excellence", "Amazon names operational excellence as one of six major goals for 2000.", "The goals include growth, customer relationships, brand, expansion, operations, and financial strength.", "Excellence becomes serious when it is one of the explicit operating goals.", [[163, 175]], ["goals", "operations", "execution"]),
            card(1999, "definition", "Operational excellence defined", "continuous improvement in customer experience", "Bezos defines operational excellence as both better customer experience and better productivity, margin, efficiency, and asset velocity.", "This is a compact definition that links customer and financial outcomes.", "The best operations improve the customer and the economics together.", [[215, 233]], ["definition", "productivity", "asset velocity"]),
            card(2002, "measurement", "Cycle time and contacts per order", "contacts per order", "The 2002 letter shows operating excellence through concrete measures: fulfillment cycle time and customer contacts per order.", "These measures matter because they are close to customer experience and internal process quality.", "Choose metrics that reveal whether the system is making life easier for customers.", [[57, 67]], ["cycle time", "contacts", "customer satisfaction"]),
            card(2008, "waste", "Muda as potential", '"muda" or waste', "Bezos frames waste not only as cost but as opportunity for years of productivity gains.", "The passage directly links waste removal to free cash flow and returns on invested capital.", "Operational waste is future value waiting to be released.", [[113, 131]], ["muda", "waste", "productivity"]),
            card(2009, "inputs", "Controllable inputs over outputs", "controllable inputs", "Amazon's planning process focuses on inputs teams can control, not only final financial outputs.", "The 452 goals include owners, deliverables, dates, reviews, and a heavy emphasis on customer experience.", "Long-term outputs improve when teams own the right inputs.", [[109, 157]], ["inputs", "owners", "goals"]),
            card(2010, "technology", "Technology embedded in operations", "Technology infuses all of our teams", "The 2010 letter shows operating excellence as technology embedded in teams, processes, decisions, and innovation.", "The Whispersync example makes the point concrete: complex systems are hidden so the customer experiences magic.", "Operational excellence improves when core technology is inside the operating system, not parked beside it.", [[107, 153]], ["technology", "processes", "customer experience"]),
            card(2013, "kaizen", "Kaizen makes improvement local", "streamline processes and reduce defects and waste", "The Kaizen section shows operational excellence happening through small teams in fulfillment centers.", "The passage also includes green goals, reinforcing that operations can improve cost, quality, and environmental outcomes.", "An operating system gets stronger when improvement is distributed close to the work.", [[311, 325]], ["kaizen", "fulfillment", "defects"]),
            card(2015, "AWS", "Operational excellence travels beyond retail", "cares deeply about operational excellence", "AWS is described with the same operating traits as Amazon retail: customer obsessed, inventive, experimental, long-term oriented, and operationally intense.", "This proves the operating system is portable across very different businesses.", "A real operating system can transfer into new domains without becoming a slogan.", [[295, 307]], ["AWS", "single-threaded owners", "daily releases"]),
        ],
    },
    {
        "file": "platform_and_ecosystem_design_reader.html",
        "title": "Platform and Ecosystem Design",
        "kicker": "Business model and capital",
        "thesis": "Build platforms where customers, sellers, builders, authors, and partners make each other stronger.",
        "life": "Use it as a systems lens: build environments where other people can create value without waiting on you.",
        "business": "Use it to understand Marketplace, AWS, FBA, KDP, Prime, and the compounding logic of participant incentives.",
        "children": ["Platform as asset", "Self-service platforms", "Marketplace paradox", "Flywheel design", "Business model alignment"],
        "cards": [
            card(1999, "asset", "The e-commerce platform", "brand, customers, technology, distribution", "Bezos defines Amazon's platform as a bundle of capabilities, not just a website.", "The passage names brand, customers, technology, distribution, expertise, and team as platform assets.", "A platform is a reusable capability base for future businesses.", [[125, 155]], ["platform", "brand", "capabilities"]),
            card(1999, "extension", "New services build on the platform", "with our platform in place", "Amazon's 1999 initiatives use the existing platform to enter under-served categories and partnership programs.", "The key idea is leverage: each new product and service should build on the platform.", "Expansion is stronger when new efforts reuse and strengthen existing capabilities.", [[239, 267]], ["leverage", "partnerships", "expansion"]),
            card(2002, "marketplace", "Product detail pages become shared real estate", "we let them", "The 2002 letter makes the platform move vivid: Amazon puts used products and third-party offers next to new first-party products.", "This is a simple early expression of ecosystem design: the customer-facing surface is shared when it creates better value.", "A platform owner creates value by letting others win on the platform when customers benefit.", [[11, 23]], ["detail pages", "third-party", "used products"]),
            card(2005, "marketplace", "Let third parties compete on detail pages", "single detail page", "Putting third-party offers beside Amazon retail offers looked internally controversial, but it improved customer choice.", "The passage shows the Marketplace paradox: competing with yourself can strengthen the whole ecosystem.", "A good platform may favor the customer over internal channel protection.", [[103, 121]], ["third-party sellers", "detail pages", "choice"]),
            card(2006, "AWS", "AWS as a developer platform", "software developers", "AWS appears as a new business focused on developer needs like storage and compute capacity.", "This early AWS section shows platform design before AWS became obvious.", "A platform starts by solving a broad repeated need for builders.", [[53, 73]], ["AWS", "developers", "compute"]),
            card(2011, "self-service", "Self-service platforms remove gatekeepers", "powerful self-service platforms", "AWS, FBA, and KDP allow people to experiment without gatekeeper approval.", "The section explicitly says these platforms create win-win value for multiple participant groups.", "Self-service design increases the number of people who can try ideas.", [[145, 183]], ["self-service", "AWS", "FBA", "KDP"]),
            card(2011, "gatekeepers", "Gatekeepers slow innovation", "well-meaning gatekeepers slow innovation", "Bezos explains why self-service matters: even helpful gatekeepers create friction.", "KDP shows how removing gatekeepers changes author economics and reader access.", "A platform can unlock value by reducing permission bottlenecks.", [[183, 225]], ["gatekeepers", "authors", "innovation"]),
            card(2012, "FBA", "FBA turns seller inventory into Prime value", "game changer for our seller customers", "FBA lets sellers warehouse inventory in Amazon's network, making their items Prime eligible and increasing consumer selection.", "This passage fills a missing 2012 bridge between the self-service platform concept and the later Marketplace-Prime flywheel.", "Ecosystem design works when one participant's tool improves another participant's experience.", [[45, 53]], ["FBA", "seller customers", "Prime"]),
            card(2014, "flywheel", "Marketplace accelerates the flywheel", "accelerated the Amazon flywheel", "Marketplace adds selection, draws customers, attracts sellers, creates scale, and supports lower prices.", "This section is the clearest Marketplace flywheel description.", "Ecosystem design works when participant growth reinforces customer value.", [[37, 65]], ["marketplace", "flywheel", "selection"]),
            card(2014, "glue", "FBA links Marketplace and Prime", "FBA completes the circle", "FBA makes seller inventory Prime eligible, increasing seller sales and Prime member value.", "This is the business model alignment passage where two separate offerings become one reinforcing system.", "The best ecosystem mechanism makes each participant's win strengthen the other participants.", [[211, 245]], ["FBA", "Prime", "alignment"]),
            card(2015, "marketplace", "Marketplace, FBA, and seller growth", "that flywheel spins faster", "The 2015 letter shows Marketplace scale and how FBA accelerates the Prime and seller loop.", "It also adds seller outcomes such as entrepreneurs, jobs, and sales growth.", "A platform becomes stronger when third parties can build serious businesses on it.", [[173, 195]], ["sellers", "FBA", "jobs"]),
            card(2018, "sellers", "Independent sellers beat first party", "Third-party sellers are kicking our first party butt.", "The 2018 letter gives the strongest retrospective evidence that Marketplace became a real ecosystem, not a side channel.", "The surrounding lines explain that FBA, Prime, and seller tools helped independent sellers compete against Amazon's own first-party business.", "A strong platform can let external participants outperform the owner on the owner's own surface.", [[91, 139]], ["third-party sellers", "FBA", "Prime", "seller tools"]),
            card(2020, "stakeholders", "Third-party sellers as value recipients", "third-party seller profits", "The final CEO letter estimates seller value creation, not just Amazon value.", "This brings platform design into the stakeholder-value frame.", "A real ecosystem creates measurable value for participants outside the platform owner.", [[83, 89]], ["seller value", "stakeholders", "2020"]),
        ],
    },
    {
        "file": "dreamy_business_filter_reader.html",
        "title": "Dreamy Business Filter",
        "kicker": "Business model and capital",
        "thesis": "Look for opportunities customers love, that can become huge, earn strong returns, and last for decades.",
        "life": "Use it to evaluate career or project opportunities: loved, large, economically strong, and durable.",
        "business": "Use it as a compact screen for exceptional business models and long-term capital allocation.",
        "children": ["Dreamy business offering", "Market-size unconstrained", "Enduring franchise", "Market leadership logic"],
        "cards": [
            card(2014, "filter", "The four characteristics", "Customers love it", "Bezos gives a compact test: customers love it, it can get very large, it has strong returns on capital, and it can endure for decades.", "Marketplace, Prime, and AWS are named as the three examples.", "A dreamy business is loved, large, profitable, and durable.", [[11, 35]], ["filter", "durability", "returns"]),
            card(2014, "marketplace", "Marketplace survives early misses", "no customers", "Marketplace emerged after Auctions and zShops missed. The eventual model integrated third-party sellers into customer detail pages.", "The flywheel passage shows why Marketplace became a dreamy business rather than just another category.", "A great business may be found through failed versions before the right mechanism appears.", [[37, 65]], ["marketplace", "flywheel", "iteration"]),
            card(2014, "prime", "Prime builds from owned retail", "foundation of Prime", "Prime depends on fulfillment, inventory systems, pricing, delivery promises, and selection.", "This passage shows the operational foundation behind a beloved customer offering.", "A dreamy offering often needs deep infrastructure before it feels simple.", [[117, 155]], ["prime", "infrastructure", "fulfillment"]),
            card(2014, "flywheel", "FBA deepens Prime and Marketplace", "Prime pumps energy into Marketplace", "FBA links Prime and Marketplace so seller participation increases Prime value and Prime increases seller sales.", "This is one reason the business can remain durable: the parts make each other stronger.", "Durability improves when a business is a reinforcing system, not a standalone feature.", [[211, 245]], ["FBA", "system", "durability"]),
            card(2014, "AWS", "AWS fits the dreamy filter", "one of those dreamy business offerings", "Bezos applies the dreamy-business frame to AWS, emphasizing customer value, large market size, and capital returns.", "The passage also discusses market-size unconstrained and leadership advantages.", "A dreamy business can be technical and complex if the customer value and economics are strong.", [[333, 377]], ["AWS", "market size", "capital returns"]),
            card(2014, "search", "Keep looking for the next one", "find a fourth", "Bezos closes by saying Amazon will keep searching for a fourth big idea while nurturing the first three.", "This keeps the dreamy filter from becoming backward-looking nostalgia.", "The filter is a live search tool, not only a way to explain past winners.", [[435, 447]], ["capital allocation", "search", "day 1"]),
        ],
    },
    {
        "file": "culture_as_compounding_infrastructure_reader.html",
        "title": "Culture as Compounding Infrastructure",
        "kicker": "Culture and scale",
        "thesis": "Culture is the repeated behavior system that lets a large company keep acting like builders.",
        "life": "Use it by noticing which repeated behaviors your environment rewards, then choosing or shaping the culture deliberately.",
        "business": "Use it to preserve speed, ownership, invention, and operational excellence as the organization scales.",
        "children": ["Culture as advantage", "Culture fit and self-selection", "Single-threaded ownership", "Technology embedded in business"],
        "cards": [
            card(2000, "asset", "Culture works through capability assets", "brand, the customer relationships, the technology", "The 2000 letter describes Amazon as a unique asset made of brand, customer relationships, technology, fulfillment infrastructure, financial strength, people, and determination.", "This is a useful early culture-and-capability passage because the organization is framed as an asset base, not only a retailer.", "Culture compounds when it keeps strengthening the capabilities that make the company hard to copy.", [[145, 157]], ["capability", "technology", "customer first"]),
            card(2006, "saplings", "Culture protects new businesses", "supportive of small businesses", "Amazon's culture helps small new businesses survive beside larger existing ones.", "The passage says culture is formed by intentions and by past experience with successful new businesses.", "Culture compounds by shaping which early ideas are allowed to live.", [[75, 125]], ["culture", "saplings", "new businesses"]),
            card(2010, "technology", "Technology is embedded, not off to the side", "technology off to the side", "Bezos argues technology matters because it is integrated directly into teams and customer experiences.", "The Kindle example shows complex technology hidden behind a simple customer experience.", "A strong culture embeds the core capability into everyday work.", [[107, 131]], ["technology", "integration", "kindle"]),
            card(2015, "identity", "Culture is enduring and self-selecting", "corporate cultures", "The 2015 letter defines culture as stable, hard to change, and shaped by people self-selecting into it.", "Amazon's named principles include customer obsession, invention, willingness to fail, long-term patience, and operational excellence.", "Culture is not a poster. It is the behavior system people choose to join or leave.", [[29, 53]], ["culture", "self-selection", "principles"]),
            card(2015, "ownership", "Small teams with single-threaded owners", "single-threaded owners", "AWS operates through small teams with clear owners, enabling rapid innovation.", "The passage shows how culture becomes organizational design.", "Ownership scales better when responsibility is clear and concentrated.", [[295, 307]], ["AWS", "owners", "small teams"]),
            card(2015, "scale", "A large company that is an invention machine", "invention machine", "Bezos names the large-company challenge: combine big-company capabilities with invention and speed.", "The decision-process section follows because Type 1 and Type 2 discipline helps culture survive scale.", "Culture must counter the default slowness of size.", [[405, 443]], ["scale", "invention", "decision process"]),
            card(2017, "standards", "High standards protect invisible work", 'protective of all the "invisible"', "High standards are part of culture because they make unseen excellence rewarding.", "This supports culture as infrastructure: teams do quality work even when no one is watching.", "A compounding culture makes invisible good work normal.", [[201, 215]], ["high standards", "invisible work", "professionalism"]),
            card(2018, "builders", "Builder culture keeps beginner's mind", "culture of builders", "Amazon wants people who are curious, explorers, and fresh even when expert.", "The passage links builder culture to iteration, wandering, and hard problems.", "A builder culture keeps a scaled company from becoming a maintenance organization.", [[141, 163]], ["builders", "beginner mind", "wandering"]),
        ],
    },
    {
        "file": "responsible_scale_reader.html",
        "title": "Responsible Scale",
        "kicker": "Stakeholder and society",
        "thesis": "As scale grows, value creation must expand beyond customers and shareholders to employees, sellers, communities, and climate.",
        "life": "Use it by asking how your growing power changes your responsibilities to the people affected by you.",
        "business": "Use it to study responsibility as invention and operations, not only reputation management.",
        "children": ["Employee choice and upskilling", "Scale for good", "Stakeholder value creation", "Earth's Best Employer", "Climate as invention opportunity"],
        "cards": [
            card(2013, "employees", "Choice for employees", "The goal is to enable choice", "Career Choice and Pay to Quit show Amazon experimenting with employee agency, not only customer features.", "The programs are framed as internal inventions that can benefit employees around the world.", "Responsible scale includes giving people more options, even when those options may lead away from the company.", [[241, 265]], ["career choice", "pay to quit", "agency"]),
            card(2013, "packaging", "Packaging waste as customer and planet problem", "reducing packaging waste", "Frustration-Free Packaging reduces wrap rage and environmental waste at the same time.", "The passage is a good example of customer delight and environmental improvement reinforcing each other.", "The best responsible-scale ideas solve multiple real problems at once.", [[413, 421]], ["packaging", "waste", "customer delight"]),
            card(2014, "upskilling", "Career Choice grows globally", "pre-pay 95% of tuition", "Amazon pre-pays tuition for in-demand fields, including paths outside Amazon.", "The glass-wall classroom detail shows a deliberate effort to make the program visible and encouraging.", "Upskilling is stronger when the company reduces friction and makes participation normal.", [[385, 423]], ["career choice", "tuition", "skills"]),
            card(2015, "scale", "Inventive culture applied to social problems", "our scale provides opportunities", "Bezos groups renewable energy, packaging, Career Choice, Leave Share, and Ramp Back as scale-enabled inventions.", "The passage matters because it connects responsibility back to invention and long-term thinking.", "Responsible scale is strongest when it uses the same invention engine as the core business.", [[457, 525]], ["renewables", "leave share", "ramp back"]),
            card(2018, "wages", "Investing in employees from heart and head", "heart as the head", "The wage and upskilling sections show employee investment justified by analysis and by values.", "Career Choice and workforce training become part of retaining owner-minded talent.", "Scale raises the bar for how a company treats and develops its people.", [[335, 375]], ["wages", "upskilling", "employees"]),
            card(2017, "milestones", "Sustainability and Career Choice milestones", "100% renewable energy", "The 2017 letter adds concrete scale-era responsibility evidence: renewable energy projects, packaging waste reduction, and Career Choice classrooms.", "This fills a missing year in the responsible-scale story between the 2015 program list and the 2018 wage/upskilling discussion.", "Responsible scale becomes credible when it shows up as measurable programs, not only commitments.", [[507, 525], [571, 591]], ["renewable energy", "packaging", "career choice"]),
            card(2019, "crisis", "Safety during essential service", "focused on the safety of our employees", "The pandemic letter makes employee safety and essential services central to operations.", "The testing-lab discussion shows responsibility becoming a large-scale operational problem.", "When a company is essential, safety becomes part of the core mission.", [[37, 87]], ["COVID", "safety", "essential services"]),
            card(2019, "climate", "Scale and innovation for climate", "scale and ability to innovate quickly", "Amazon frames climate action as an area where its scale can make a positive impact.", "The passage covers the Climate Pledge, renewable energy, packaging, and AWS efficiency.", "Scale creates responsibility, but also gives tools to act.", [[231, 323]], ["climate pledge", "renewables", "AWS efficiency"]),
            card(2020, "employer", "Earth's Best Employer", "Earth's Best Employer and Earth's Safest Place to Work", "Bezos explicitly raises the standard for employee value creation and safety.", "The passage includes coaching, safety science, WorkingWell, staffing algorithms, wages, and benefits.", "The responsibility standard moves from being good enough to aiming to lead.", [[185, 333]], ["employees", "safety", "best employer"]),
            card(2020, "climate", "Climate as market signal", "signal to the marketplace", "The Climate Pledge section presents climate action as a way to create demand for new technologies.", "The Climate Pledge Fund turns responsibility into an investment and invention agenda.", "Responsible scale can shape markets by signaling demand for better solutions.", [[341, 423]], ["climate pledge", "market signal", "technology"]),
        ],
    },
]


TEMPLATE_PATH = Path(__file__).resolve().parent / "reader_template.html"


def render_page(idea: dict) -> str:
    data = {
        "idea": {key: value for key, value in idea.items() if key != "cards"},
        "passages": idea["cards"],
    }
    html = TEMPLATE_PATH.read_text(encoding="utf-8")
    replacements = {
        "%%TITLE%%": idea["title"],
        "%%KICKER%%": idea["kicker"],
        "%%THESIS%%": idea["thesis"],
        "%%LIFE%%": idea["life"],
        "%%BUSINESS%%": idea["business"],
        "%%DATA_JSON%%": json.dumps(data, ensure_ascii=True, indent=4),
    }
    for token, value in replacements.items():
        html = html.replace(token, value)
    return html


def main() -> None:
    for idea in IDEAS:
        output_path = OUTPUT_DIR / idea["file"]
        output_path.write_text(render_page(idea), encoding="utf-8")
        print(output_path)


if __name__ == "__main__":
    main()
