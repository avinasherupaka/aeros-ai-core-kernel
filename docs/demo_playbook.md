# Aeros — Product Enablement & Demo Playbook

**Audience:** Sales engineers, solution consultants, and account executives running
live demonstrations of the Aeros System of Assurance for pharmaceutical
manufacturing.

**Purpose:** Turn the product's technical capabilities into a compelling,
value-driven story that a non-technical buyer (Head of Quality, VP Manufacturing,
QA Director, CIO) can follow, believe, and champion internally.

---

## Table of Contents

1. [The 30-Second Pitch](#1-the-30-second-pitch)
2. [The Problem We Solve](#2-the-problem-we-solve)
3. [The Value Chain (What Aeros Actually Does)](#3-the-value-chain)
4. [The Canonical Demo Story — "The Humidity Excursion"](#4-the-canonical-demo-story)
5. [Screen-by-Screen Demo Script](#5-screen-by-screen-demo-script)
6. [Value Realization — Explaining Each Component to Non-Technical Buyers](#6-value-realization)
7. [ROI & Business Case](#7-roi--business-case)
8. [Q&A Framework](#8-qa-framework)
   - [Anticipated Customer FAQs](#81-anticipated-customer-faqs)
   - [Strategic Follow-Up Questions (to drive engagement)](#82-strategic-follow-up-questions)
   - [Curveball Questions & Pivot Scripts](#83-curveball-questions--pivot-scripts)
9. [Objection-Handling Cheat Sheet](#9-objection-handling-cheat-sheet)
10. [Demo Do's and Don'ts + Pre-Demo Checklist](#10-demo-dos-and-donts--pre-demo-checklist)
11. [Glossary (Plain-Language)](#11-glossary)
12. [Appendix — Feature-to-Value Map](#12-appendix--feature-to-value-map)

---

## 1. The 30-Second Pitch

> "Every pharma plant already has the data to prove a batch is safe — it's just
> scattered across a dozen systems that don't talk to each other. When something
> goes wrong, your best people spend **days** manually assembling the evidence to
> decide whether to release or reject a batch.
>
> **Aeros is the System of Assurance.** It continuously watches your process,
> and the moment a parameter drifts out of its validated range, it *automatically*
> assembles the complete, audit-ready evidence package — the causal story, the
> impact on quality, and the exact GMP documentation a reviewer needs — in
> **minutes, not days**. It doesn't replace your QA experts; it hands them a
> finished case file so they can make the release decision with confidence."

**One-liner:** *Aeros turns scattered plant data into an audit-ready release
decision, automatically.*

---

## 2. The Problem We Solve

Pharmaceutical manufacturing runs on a paradox: it is one of the most heavily
instrumented industries on earth, yet answering the single most important
question — **"Is this batch safe to release?"** — is still a slow, manual,
error-prone scramble.

**Why it's painful today:**

- **Data is siloed.** Temperature and humidity live in the historian. Batch
  context lives in the MES. Lab results live in the LIMS. Deviations live in the
  QMS. Equipment history lives in the CMMS. No single system sees the whole
  picture.
- **Investigations are manual.** When an excursion happens, a QA investigator
  opens 6–8 applications, exports spreadsheets, cross-references timestamps, and
  hand-writes a deviation report. This takes **days to weeks**.
- **Release is delayed.** Batches sit in quarantine — tying up working capital and
  delaying revenue — because the *evidence* isn't ready, not because the product
  is bad.
- **Audit risk is real.** Regulators (FDA, EMA) expect complete, contemporaneous,
  ALCOA+ compliant records. Gaps or reconstructed-after-the-fact records are a
  finding waiting to happen.

**The cost:** Right-first-time delays, deviation backlogs, over-conservative
rejections, and inspection exposure — measured in millions per site per year.

---

## 3. The Value Chain

Aeros is not a dashboard. It is a pipeline that converts raw signals into a
defensible decision. Every layer adds assurance:

```
  Plant Signals        Data Backbone           Assurance Engine        Decision
  ────────────         ─────────────           ────────────────        ────────
  Sensors, PLCs   ►    Lakehouse (bronze/  ►   Evidence Graph      ►   GMP Dossier
  SCADA, MES,          silver/gold) +          (causal reasoning)      Readiness +
  Historian,           Property Graph          + Impact + Risk         Release
  LIMS, QMS, ERP       (lineage)               scoring                 recommendation
```

1. **Ingest** — Live feeds from OT/IT/edge systems via Aeros connectors (OPC-UA,
   MQTT/Sparkplug, historian APIs, MES/LIMS/QMS/ERP REST).
2. **Store & structure** — A medallion **lakehouse** (bronze → silver → gold)
   plus a **property graph** that captures relationships and full lineage.
3. **Reason** — Deterministic engines detect the state-of-control breach, build
   the **Evidence Graph** (the causal chain), score **quality impact** and
   **risk**, and identify what evidence is present vs. missing.
4. **Decide** — A **GMP Dossier** is assembled and a **release-readiness**
   recommendation is surfaced for a human to approve. Humans stay in the loop.

> **Talk track:** "Notice that every layer is about *assurance*, not just
> visualization. By the time a human looks at it, the work is done — they're
> reviewing a conclusion, not doing an investigation."

---

## 4. The Canonical Demo Story

**Setup (say this out loud to frame the demo):**

> "Let's walk through a real scenario. It's 02:14 on the night shift at the
> Hyderabad plant. We're compressing a batch of a moisture-sensitive tablet.
> The HVAC unit serving Compression Room 1 starts to struggle, and relative
> humidity begins to climb past its validated limit. In most plants, nobody
> notices until the morning — and then the investigation begins. Watch what
> happens with Aeros."

**The narrative arc (five beats):**

1. **The signal.** An RH sensor on AHU-03 reports humidity crossing the **alert
   limit**, then the **action limit**. This is a *state-of-control violation* —
   the process has left its validated envelope.
2. **The detection.** Aeros confirms the **breach** (not a sensor glitch — the
   trend is sustained and corroborated by the dew-point sensor on the CDA header).
3. **The causal story.** The Evidence Graph assembles left-to-right: the *Event*
   → the *Room/Equipment* (AHU-03) → the *Batch* and *Product* affected → the
   *Risks* (moisture uptake, content uniformity) → the *Evidence* required → the
   *Deviation/CAPA* and the *Human Review* needed to close it.
4. **The impact.** Aeros scores it: **GxP impact = Yes**, **risk = High**,
   **CAPA required**. It explains *why*, with a confidence score.
5. **The decision.** The **GMP Dossier Readiness** shows exactly which evidence is
   already gathered (control chart, batch record, equipment history) and what's
   still missing (e.g., a moisture content lab result). A QA reviewer opens the
   full dossier, sees the finished case, and makes the release call — in minutes.

**The punchline:**

> "The investigation that used to take three days and eight applications just
> happened in the time it took me to describe it. And every step is captured,
> time-stamped, and audit-ready."

---

## 5. Screen-by-Screen Demo Script

> Navigate top-to-bottom. Keep each screen to 60–90 seconds. Let the visuals do
> the talking; narrate the *value*, not the UI mechanics.

### 5.1 Plant Ops — Active Event (Command Center)

**What they see:** A confirmed breach with a red status header, full event
context on the left (parameter, asset, room, batch, product, limits), the control
chart, and — front and center — the landscape **Evidence Graph**. Above the graph
sit **Required Actions** and **GMP Dossier Readiness**.

**Say:**
> "This is the single pane of assurance for an active event. On the left is the
> *what and where*. The control chart shows the excursion against the validated
> alert and action limits — you can see the exact moment we left the safe zone,
> and how long we stayed out. Up here are the required actions and how complete
> our evidence package is. And this graph is the heart of it — the causal story."

**Do:**
- Point to the alert vs. action limit lines on the chart: "These aren't arbitrary
  — they're your validated ranges."
- Click a node in the Evidence Graph → the detail panel opens. "Every node is
  backed by real data with full lineage."
- Click **Expand** on the graph → the full-screen zoom modal. "For a complex
  investigation, reviewers can pan and zoom the entire causal chain." Scroll to
  zoom, drag to pan, press Esc.
- Click **View Full Dossier** → transitions to the dossier.

**Value line:** *"Nobody assembled this. Aeros did — the instant the breach was
confirmed."*

### 5.2 The Evidence Graph (deep dive)

**What they see:** A left-to-right causal flow organized in lanes/stages: Event →
Context (Batch/Product/Room) → Risk → Evidence → Disposition (Deviation/CAPA/
Human Review/Approval). Color coding: **red** = the problem and its risks,
**amber** = actions/human steps pending, **green** = evidence that's in hand.

**Say:**
> "Read it like a sentence, left to right. *This event*, on *this equipment*,
> affected *this batch of this product*, which creates *these quality risks*,
> which require *this evidence*, and must be dispositioned through *this review*.
> The colors tell a reviewer instantly where the gaps are."

**Value line:** *"This is the difference between a data lake and an assurance
system — the data lake has the facts; Aeros has the argument."*

### 5.3 Live Floor Map

**What they see:** The ISA-95 automation pyramid (L0 field sensing → L4
enterprise/cloud) with every IT, OT, and edge system in its proper layer —
sensors, PLCs, OPC-UA, SCADA/BMS/MES/Historian, Greengrass/UNS/IoT Core, and
LIMS/QMS/ERP/CMMS/Aeros cloud. Animated dotted lines show live data movement;
color-coded status LEDs and Aeros connector chips show health.

**Say:**
> "This is your actual plant topology, config-driven — not a picture. Green means
> a live feed; amber means degraded or replayed; red means broken. The moving
> lines are real data flowing through the Aeros connectors. If a historian feed
> drops at 3 a.m., you see it here — and so does the assurance engine."

**Do:** Click a node to inspect its vendor, protocol, and connector status.

**Value line:** *"Onboarding a new site is a config file, not a re-build. Same
screen, any facility."*

### 5.4 Connector Pulse

**What they see:** Connector health grid with the **UNS Topic Explorer** promoted
to the top.

**Say:**
> "This is the nervous system. The Unified Namespace topic explorer shows every
> live signal streaming in. Assurance is only as good as the data feeding it —
> here's proof the data is flowing and trustworthy."

### 5.5 QA Release Board / Deviation Board

**What they see:** The batch release queue with dossier status and workflow state.

**Say:**
> "This is where the value lands for Quality. Every batch, its evidence status,
> and its release recommendation — in one prioritized queue. No more chasing
> paperwork across systems."

### 5.6 Dossier Review

**What they see:** A split-screen GMP document viewer with structured sections —
the audit-ready release package.

**Say:**
> "This is the deliverable a regulator would want to see: a complete,
> contemporaneous, GMP-structured dossier — deviation description, impact
> assessment, evidence, CAPA, and sign-offs — generated from the live event, not
> reconstructed weeks later."

**Value line:** *"ALCOA+ by construction: Attributable, Legible, Contemporaneous,
Original, Accurate."*

### 5.7 Readiness Matrix (Leadership)

**What they see:** A heatmap of site/line readiness with red/amber/green and grey
(not-yet-evaluated) cells, each with a reason code on click.

**Say:**
> "For leadership: one glance at readiness across the operation. Red and amber
> aren't just colors — click any cell and Aeros tells you *why*, so the
> conversation moves straight to the action."

### 5.8 Dendrix Assistant (floating, every page)

**What they see:** A floating assistant available on every screen with
context-rich suggested questions.

**Say:**
> "Meet Dendrix. Ask it anything — 'What's blocking batch release?' or 'Show the
> evidence checklist' — and it answers using the *real* underlying data, on any
> screen. It's the natural-language front door to the whole system of assurance."

---

## 6. Value Realization

*How to contextualize each component for a non-technical buyer. Pair every
feature with a business outcome — never demo a feature without naming the value.*

| Component | Don't say (feature) | Do say (value) |
|-----------|---------------------|----------------|
| Control chart | "Time-series with limit lines." | "The exact proof of when and how long you were out of your validated range — the core of any deviation." |
| Evidence Graph | "A directed causal graph." | "The finished investigation — the argument for release, assembled automatically." |
| Lakehouse + graph backbone | "Medallion architecture with a property graph." | "One trustworthy source of truth with full lineage, so every number can be traced to its origin for audit." |
| Live Floor Map | "ISA-95 topology visualization." | "Live proof your plant is connected and healthy, and a config-driven way to onboard any new site." |
| GMP Dossier | "Structured document generation." | "Audit-ready paperwork by construction — days of manual assembly, eliminated." |
| Readiness Matrix | "A status heatmap." | "Operational risk at a glance for leadership, with the reason baked in." |
| Dendrix | "An LLM assistant." | "Answers from your real data in plain English, so anyone can self-serve." |
| Multi-tenant config | "Config-driven tenancy." | "Standardize once, roll out to every site with a config file — not a project." |

**The golden rule:** *Feature → "which means" → business outcome.* Example:
"Aeros builds the Evidence Graph automatically, **which means** your QA experts
review a finished case instead of spending three days assembling one, **which
means** batches release faster and your best people focus on judgment, not
data-wrangling."

---

## 7. ROI & Business Case

Frame value in four buckets. Use the customer's own numbers where possible; the
figures below are illustrative anchors.

1. **Faster release (working capital + revenue).**
   - Typical manual deviation investigation: **2–5 days**. With Aeros: **minutes
     to hours**.
   - Every day of quarantine ties up batch value and delays revenue recognition.
   - *Anchor:* "If Aeros releases a held batch even one day sooner, on a
     $2–5M batch, the carrying-cost and revenue-timing impact alone can justify
     the platform."

2. **Labor reallocation (efficiency).**
   - QA investigators reclaim the hours spent app-hopping and spreadsheet-building.
   - *Anchor:* "Reassign senior QA time from data assembly to disposition and
     continuous improvement."

3. **Reduced deviation backlog & right-first-time.**
   - Contemporaneous evidence shrinks the deviation queue and reduces
     over-conservative rejections.

4. **Audit & compliance risk reduction (avoided cost).**
   - ALCOA+ dossiers by construction reduce the risk of 483 observations and
     warning letters — whose cost (remediation, delayed approvals, reputational)
     dwarfs the platform price.

**Discovery questions to build the case live:**
- "How long does a typical humidity or temperature excursion investigation take
  today, start to finish?"
- "How many deviations does a site process per month? What's your current
  backlog?"
- "What's the average value of a batch, and how long do batches sit in
  quarantine waiting on *evidence* rather than *product*?"
- "What did your last regulatory inspection findings cost you — in time and
  remediation?"

---

## 8. Q&A Framework

### 8.1 Anticipated Customer FAQs

**Q: Does this replace my MES / LIMS / QMS / historian?**
> No — Aeros sits *on top of* them. It's the assurance layer that connects the
> systems you've already invested in. We make your existing stack more valuable,
> not obsolete.

**Q: Is this an AI black box making quality decisions?**
> No. The core reasoning is **deterministic and explainable** — the same inputs
> always produce the same evidence graph and impact assessment. AI (Dendrix)
> assists with natural-language access, but **humans make every release
> decision.** Aeros assembles the case; your qualified person approves it.

**Q: How does a new site get onboarded?**
> It's config-driven. A site is described by a standardized set of config files —
> its topology, connectors, and secret references. Fill those out, run the
> validation suite, and the platform configures itself. No custom code per site.

**Q: What data does it need, and what if a feed goes down?**
> It connects to your existing OT/IT sources via standard protocols (OPC-UA,
> MQTT/Sparkplug, historian and enterprise APIs). If a feed degrades or drops,
> the Live Floor Map and Connector Pulse show it immediately, and the assurance
> engine flags evidence as unavailable rather than guessing.

**Q: How long to first value?**
> Because it overlays existing systems and is config-driven, a first site can be
> stood up quickly against your real feeds — you see live assurance on your own
> data, not a canned demo, early in the engagement.

**Q: On-prem, cloud, or hybrid?**
> All three. The core runs identically locally, in your cloud, or hybrid at the
> edge. The architecture is environment-agnostic; only configuration changes.

**Q: What about validation (CSV / GxP)?**
> The deterministic engines are designed to be validatable — reproducible outputs,
> versioned config, and full lineage. We support your CSV approach with
> traceability from raw signal to dossier statement.

### 8.2 Strategic Follow-Up Questions (to drive engagement)

Ask these to deepen the conversation and expand the opportunity:

- "If your team could trust that the evidence package is *always* ready, how would
  that change your release SLAs?"
- "Which single deviation type costs you the most time today? Let's make that our
  first proof point."
- "Who owns the pain when a batch is delayed by paperwork rather than product —
  and how is that measured?"
- "How many sites would you want on a common assurance standard, and what's
  stopping that standardization today?"
- "When your next inspection comes, what would it be worth to hand the inspector a
  complete, contemporaneous dossier on demand?"
- "Where does your current data actually live, and how much of your team's week
  goes to moving it between systems?"

### 8.3 Curveball Questions & Pivot Scripts

*Tough technical/compliance questions and how to pivot to strength — calmly,
never defensively.*

**Curveball: "How do I know your AI isn't hallucinating the evidence?"**
> **Pivot:** "Great question — and it's exactly why our assurance core is
> **deterministic, not generative.** The evidence graph and impact scores come
> from rules and real data with full lineage; every node traces back to a source
> record. The AI assistant only helps you *query* that verified data in plain
> English — it never invents the evidence. You can audit any statement to its
> origin."

**Curveball: "This is GxP — how can I validate a system that uses AI?"**
> **Pivot:** "We separate the two concerns. The GxP-critical reasoning is
> deterministic and reproducible — the same inputs always yield the same output,
> which is validatable under your CSV process. Configuration is versioned, and we
> provide traceability from raw signal to dossier line. The AI assistant is a
> non-GxP convenience layer that reads verified data; it isn't in the decision
> path."

**Curveball: "What about data integrity and ALCOA+?"**
> **Pivot:** "Aeros is ALCOA+ by construction. Records are **Attributable**
> (tied to source and user), **Legible**, **Contemporaneous** (captured live, not
> reconstructed), **Original** (with full lineage back to the raw signal), and
> **Accurate** (deterministic transforms). That's stronger than the manual
> process it replaces, where records are often assembled after the fact."

**Curveball: "Where does our data go? Is it multi-tenant / shared?"**
> **Pivot:** "Your data stays isolated. In the cloud, **each tenant runs in its
> own VPC** — no shared network, no shared database, no shared secret scope.
> Secrets are referenced from your secure store and resolved at runtime with
> least privilege. We designed for strict data tenancy from the ground up; I can
> walk your security team through the isolation model."

**Curveball: "We already spent millions on a data lake / historian. Why do I need
this?"**
> **Pivot:** "You've done the hard part — you have the data. But a lake stores
> facts; it doesn't build the *argument* for release or generate the *dossier*.
> Aeros turns that existing investment into decisions. We make your lake pay off."

**Curveball: "What happens when a sensor is wrong or a feed is bad?"**
> **Pivot:** "Aeros corroborates. A single sensor doesn't confirm a breach — the
> engine cross-checks related signals, and if a feed is degraded, it's flagged
> red on the Floor Map and the evidence is marked unavailable rather than assumed.
> Bad data becomes visible, not silently trusted."

**Curveball: "Isn't this just a nicer dashboard?"**
> **Pivot:** "A dashboard shows you a problem. Aeros hands you the finished
> investigation and the release-ready dossier for it. The dashboard is the least
> valuable thing on the screen — the assembled evidence and decision are the
> product."

**Curveball: "How much does it cost / what's the TCO?"**
> **Pivot:** "Let's ground it in your numbers. If we take one batch out of
> unnecessary quarantine and give your QA team back the days per investigation,
> the platform typically pays for itself well inside a year. Let's quantify your
> deviation volume and batch value and I'll build the model with you." *(Then use
> §7 discovery questions.)*

---

## 9. Objection-Handling Cheat Sheet

| Objection | One-line reframe |
|-----------|------------------|
| "Too risky to change our validated process." | "Aeros augments — humans still approve. It strengthens your evidence trail, not replaces your controls." |
| "We don't have clean data." | "Aeros surfaces exactly where data is missing or degraded — it turns your data gaps into a visible, fixable list." |
| "Our IT/OT is locked down." | "We use standard protocols and can run at the edge, in your VPC. Nothing leaves your boundary unless you choose." |
| "We tried a data project; it stalled." | "Those projects stall because they end at 'we have the data.' Aeros starts where they stop — at the decision." |
| "Our team is already stretched." | "That's the point — Aeros removes the manual assembly work that's stretching them today." |
| "Show me it works on *our* data." | "Absolutely — it's config-driven; we point it at your feeds and you see live assurance on your own plant." |

---

## 10. Demo Do's and Don'ts + Pre-Demo Checklist

**Do:**
- Lead with the story (§4), not the navigation.
- Say the value line after every screen ("which means…").
- Use *their* vocabulary: deviation, disposition, quarantine, release, CAPA,
  ALCOA+, state of control.
- Let silences land after the punchline — let them realize the time saved.
- Tie everything back to *faster, safer release*.

**Don't:**
- Don't narrate the UI ("now I'll click this button"). Narrate the outcome.
- Don't oversell the AI. Lead with *deterministic assurance*; AI is the assistant.
- Don't get pulled into a feature-by-feature tour with no story.
- Don't guess on compliance specifics — pivot to the isolation/validation model
  and offer a follow-up with their security/QA team.
- Don't dodge a curveball — use the pivot scripts; they turn hard questions into
  proof points.

**Pre-demo checklist:**
- [ ] Backend healthy — `/cp/backbone/status` returns green; all `/cp/*`
      endpoints reachable (no yellow connectivity banner in the UI).
- [ ] An active event is present so the Command Center shows a confirmed breach.
- [ ] Floor Map shows live/animated flows (not all grey).
- [ ] Evidence Graph **Expand** modal opens, zooms, and pans smoothly.
- [ ] "View Full Dossier" navigates to a populated dossier.
- [ ] Dendrix assistant responds on at least two screens.
- [ ] If demoing multi-tenancy: both `pharma_co_a` and `pharma_co_b` stacks up;
      Floor Map shows the correct site label per tenant.
- [ ] Know the customer's deviation volume and batch value for the ROI moment.

---

## 11. Glossary

*Plain-language definitions to keep everyone in the room aligned.*

- **State of control** — The process operating inside its validated ranges. Leaving
  those ranges is a *state-of-control violation* (a breach).
- **Alert limit / Action limit** — Two thresholds: alert = "pay attention," action =
  "you're now out of the validated range and must act."
- **Deviation** — A documented departure from an approved process; must be
  investigated and dispositioned.
- **CAPA** — Corrective And Preventive Action: fixing the issue and preventing
  recurrence.
- **Disposition** — The decision on a batch: release, reject, or hold.
- **Dossier** — The complete evidence package supporting a batch's disposition.
- **Evidence Graph** — Aeros's causal map connecting an event to its context,
  risks, evidence, and required actions.
- **Lakehouse (bronze/silver/gold)** — Layered data storage: raw → cleaned →
  business-ready.
- **Lineage** — The traceable path from a dossier statement back to the raw signal.
- **ISA-95 (L0–L4)** — The standard model of plant automation layers, from field
  sensors (L0) to enterprise/cloud (L4).
- **UNS** — Unified Namespace: a single, organized real-time view of all plant data.
- **ALCOA+** — Data-integrity principles regulators expect: Attributable, Legible,
  Contemporaneous, Original, Accurate (+ Complete, Consistent, Enduring,
  Available).
- **GxP** — "Good practice" regulations (GMP, GLP, etc.) governing regulated
  manufacturing.
- **Connector** — An Aeros integration to a source system (historian, MES, LIMS…).
- **Tenant** — One customer/facility, isolated in its own network/VPC and config.

---

## 12. Appendix — Feature-to-Value Map

| Screen / Feature | Primary persona | Core value | Proof point in demo |
|------------------|-----------------|------------|---------------------|
| Command Center (Active Event) | Plant Ops / QA | Investigation done automatically | Breach + auto-assembled evidence graph |
| Control Chart | QA / Engineering | Objective breach proof vs. validated limits | Alert/action lines + excursion duration |
| Evidence Graph + Zoom | QA | The release *argument*, readable at a glance | Click node → lineage; Expand → pan/zoom |
| GMP Dossier Readiness | QA / Regulatory | Days of paperwork eliminated | Present vs. missing evidence + full dossier |
| Live Floor Map | Engineering / IT-OT | Live connectivity + config-driven onboarding | Animated flows, connector status, node detail |
| Connector Pulse / UNS Explorer | IT / OT | Trustworthy, flowing data | Live topics streaming |
| QA Release Board | QA management | Prioritized, evidence-backed release queue | Batch queue with recommendations |
| Dossier Review | Regulatory / QA | Audit-ready, ALCOA+ by construction | Structured GMP document |
| Readiness Matrix | Leadership | Operational risk at a glance, with reasons | Red/amber/grey cells + reason codes |
| Dendrix Assistant | All | Self-serve answers from real data | Ask on any screen, get grounded answers |
| Multi-tenant config | CIO / Program | Standardize once, roll out everywhere | Two sites, same UI, config-only difference |

---

*This playbook is a living document. Update the ROI anchors and proof points with
each new reference customer and win story.*
