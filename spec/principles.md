# LMF Design Principles

These are the tiebreakers — design values that guide every architecture decision in the Local Mind Foundation. They sit alongside the Covenant (non-negotiable terms) as the second load-bearing document.

The Covenant says *what must be true*. The principles say *how we decide when it's not obvious*.

---

## Scaffold the Gap, Don't Replace Cognition

The cognition is already there. The operator can do the thing — but a barrier blocks access. Remove the barrier. The prosthetic fills the gap between the operator's capability and the environment's demand. It does not substitute for the operator.

**Test:** Does this feature do something the operator can't do, or does it remove something that stops them from doing what they already can?

---

## Discrete Problem First, Broader Integration Second

No one adopts a system — they adopt a solution to a specific problem. Every feature should solve one discrete cognitive gap before it reaches for integration. Integration across features is the natural next step, not the entry condition.

**Test:** Can this feature be described as "helps me [specific action]" without mentioning other features?

---

## All Data Is Intentional, Not Automatic

The inbox is a buffer, not a pipeline. Raw input and permanent record are distinct lifecycle stages. The system never assumes capture implies enrichment, and never promotes buffer content to permanent status without operator review.

**Test:** Does any data flow from capture to storage without an explicit operator action?

---

## The System Finds the Operator

Barrier to access is a first sentence, not a demonstrated capability. The prosthetic must surface to the operator — notifications, ambient presence, zero-navigation activation. The operator should never have to seek the system out.

**Test:** How many steps does it take to go from "I need my system" to "the system is in front of me"? If more than zero, the design is wrong.

---

## The Assistant Is Nonpartisan Support, Not Judgment

The assistant serves the operator's declared intent. It does not evaluate, rank, or triage the operator's priorities against an external standard. When the operator says what they want to do, the assistant helps. When the operator changes their mind, the assistant helps with that too.

**Test:** Does this flow ever make the operator justify their choice to the assistant?

---

## Mode Is Operator-Declared, Never Inferred

The operator declares their context state. The system never infers it from time, location, calendar, or behavior. Inference would be wrong often enough to break trust, and the trust cost of a wrong inference exceeds any convenience gain from a correct one.

**Test:** Does this feature ever change behavior based on observed data about the operator without their declaration?

---

## Build for the Specific Population; Generalization Is Downstream

The people most harmed by illegible systems are least positioned to instrument them. Build for the specific neurological profile, the specific access need, the specific cognitive gap. General purpose is a side effect of solving specific problems well, not a design goal.

**Test:** Is this feature built for a named cognitive gap with a known operator? If not, what specific gap is it for?

---

## Trust Is an Architecture Constraint, Not a UI Property

Behavioral trust is load-bearing. A feature that works 90% of the time may be net negative if the uncertainty cost exceeds the offload benefit. Trust bugs ship before features. A broken flow the operator depends on is P0 regardless of what else is queued.

**Test:** Can the operator depend on this feature being available and correct every time they reach for it?
