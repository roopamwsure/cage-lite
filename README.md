<p align="center">
  <img
    src="cage_lite/ui/assets/cage_logo.png"
    alt="CAGE logo"
    width="170"
  >
</p>

<h1 align="center">CAGE-lite</h1>

<p align="center">
  Prebind assurance for AI-agent actions at the business consequence boundary.
</p>

> Agent platforms govern how agents run. CAGE governs whether agent actions are allowed to become business consequences.

CAGE-lite is my open-source implementation of the CAGE framework: **Control Assurance Governance Evaluation**.

The project started with a simple question:

**An AI agent can propose an action, but what should happen before that action becomes real?**

Before an agent releases a payment, grants access, approves a transaction, updates a system of record, or discloses protected information, an organization should be able to verify that the action is authorized and supported by the required evidence.

CAGE adds that final assurance step before the action becomes a binding business consequence.

CAGE-lite is currently a **v1 product preview**. The Python package version is `0.1.0`, and the current CAGE Warrant schema is version `0.4`.

## Where CAGE fits

CAGE does not replace agent runtimes, IAM, policy engines, guardrails, gateways, approval systems, or observability tools.

Those systems produce important signals. CAGE consumes those signals and evaluates whether the proposed action should be allowed to cross the business consequence boundary.

<p align="center">
  <img
    src="docs/images/cage-architecture.png"
    alt="CAGE prebind assurance architecture"
    width="100%"
  >
</p>

The diagram above shows the broader CAGE framework. CAGE-lite is the open-source implementation used to make this assurance model visible, testable, and easier to evaluate.

## The basic idea

A simplified CAGE flow looks like this:

```text
Agent proposes an action
        |
        v
Identity, standing, policy, and approval signals
        |
        v
CAGE prebind boundary
        |
        +---- HELD ----> NO_BIND ----> Business effect blocked
        |
        +---- ADMITTED -> BOUND ------> Business effect executed
        |
        v
CAGE Warrant and effect proof