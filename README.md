# AI Chat Compliance Risk Gate — Workflow Control Architecture

## The Premise

Current AI systems handle safety through refusal. That works today.

But refusal is a ceiling, not a floor. As AI moves from answering simple customer support queries toward draft financial education, personalized insights, advisor assistance, and portfolio nudges — the question is no longer "how do we stop AI from saying the wrong thing?" It becomes: **"how do we expand what AI can safely do, and prove it?"**

This system is the answer to that question. It is not a safer chatbot. It is the governance layer that makes expanding AI autonomy possible.

---

## 1. System Objective

This prototype introduces a **workflow control architecture** for AI-assisted customer support — a deterministic risk gate that sits between a drafting model and the user.

The core operating principle: **AI assumes responsibility for velocity. Humans retain responsibility for judgment and fiduciary duty.**

Today, that means auto-routing safe support queries while intercepting compliance-sensitive ones. Tomorrow, the same architecture governs AI-assisted advisors, drafted financial communications, and personalized nudges — wherever AI moves closer to decision support.

What this system enables that refusal alone cannot:

- **Measurable automation headroom** — a provable percentage of queries safe for full auto-send, expanding over time as the model matures
- **Deterministic routing** — generation and adjudication are functionally separated, so failure modes are not correlated
- **Accountability surfaces** — every decision, override, and final response is logged with full provenance, not just flagged or refused
- **Human leverage** — agent time is focused on edge cases with compliance concerns already identified, not spent reading from scratch

---

## 2. The Human/AI Boundary

This system does not replace human judgment. It optimizes its deployment.

**AI is responsible for:** synthesizing information, drafting procedural guidance, evaluating output against strict regulatory and demographic vectors, and autonomous self-correction on borderline drafts before escalating.

**Humans are responsible for:** resolving ambiguity, approving Medium Risk edge cases with full context surfaced, handling financial distress escalations, and owning ultimate legal liability.

**Auditability:** Every system transition — from generation to routing to human override — is logged immutably with the AI draft, the risk rationale, the human action taken, and the final response sent. This is not a log of refusals. It is a complete decision trail.

---

## 3. Architecture & Routing Logic

The architecture deliberately separates two functions that most deployed AI systems conflate: **generation** and **adjudication**. When both happen in the same model step, their failure modes are correlated — a jailbreak that manipulates the draft also manipulates the safety check. Decoupling them eliminates that surface.

The Risk Gate evaluates every drafted response across three vectors:

**1. Regulatory Boundary**
Enforces the line between procedural guidance (how to execute an action on the platform) and outcome guidance (what financial decision to make). A keyword scanner cannot do this — "buy" appears in both "you should buy this ETF" and "here is how to buy an ETF." Semantic intent requires AI.

**2. Demographic & Assumption Risk**
Flags language that embeds unwarranted assumptions about a user's financial capability, risk tolerance, age, or literacy without explicit confirmation.

**3. Urgency & Harm**
Detects indicators of fraud, account compromise, panic selling, or financial distress requiring immediate escalation.

### Routing Outputs

| Class | Trigger | Action |
|-------|---------|--------|
| **LOW** | Zero violations across all vectors | Auto-send to user |
| **MEDIUM** | Borderline risk — autonomous rewrite attempted first, re-evaluated | Queue for human review with flagged vector and highlighted text surfaced |
| **HIGH** | Explicit financial advice, fraud, or harm detected | Block transmission, auto-escalate to Tier 2 / Compliance |

---

## 4. Failure Modes & Mitigations

Systems fail. This architecture is designed to fail safely and visibly.

**Failure Mode 1: The False Positive Bottleneck**
Risk: The evaluator becomes too conservative, flagging standard educational content as outcome guidance, crushing support velocity.
Mitigation: The system defaults to the human-in-the-loop queue (MEDIUM) rather than failing closed to the user. Velocity drops; compliance holds. The escalation rate metric surfaces this problem immediately if it occurs.

**Failure Mode 2: Context-Blindness**
Risk: The AI evaluator lacks the historical timeline of a client's specific financial situation, misjudging severity.
Mitigation: The JSON explanation vector explicitly logs the rationale used for every judgment. Human reviewers see exactly what context the AI had — and can immediately spot what it was missing.

**Failure Mode 3: Prompt Injection & Jailbreaks**
Risk: Users attempt to manipulate the support bot into providing unauthorized financial recommendations.
Mitigation: The Risk Gate is isolated from the drafting model. Its sole directive is adversarial evaluation of text. A user-facing injection that manipulates the draft cannot reach the evaluator.

---

## 5. Evaluation Framework

Success is not measured by abstract safety metrics. It is measured by operational leverage and provable risk containment.

| Signal | Definition | Target |
|--------|-----------|--------|
| **Incident Leakage Rate** | % of post-hoc compliance breaches originating from LOW auto-sends | 0% |
| **Automation Rate** | % of queries auto-sent without human touch | Maximize over time |
| **Escalation Rate** | % routed to human review | Benchmark and trend |
| **Human Override Rate** | Frequency agents disagree with AI risk classification | Measures evaluator precision |
| **Review Time Reduction** | Time saved on MEDIUM tickets with pre-surfaced compliance concerns vs. reading from scratch | Quantify in pilot |

The Incident Leakage Rate is the system's primary accountability metric. If AI is taking autonomous action, the organization needs to know — with precision — when that autonomy fails.

---

## 6. Setup & Execution

1. Clone the repository

2. Install dependencies:
```
pip install -r requirements.txt
```

3. Set environment variable:
```
export OPENAI_API_KEY='your-key-here'
```

4. Run the application:
```
streamlit run app.py
```
