# Changelog

This file records notable user-facing changes to CAGE-lite.

CAGE-lite uses separate version labels for the product, Python package, and CAGE Warrant schema:

- product: CAGE-lite v1 product preview;
- Python package: `0.1.1`;
- CAGE Warrant schema: `0.4`.

These versions serve different purposes and should not be treated as interchangeable.

## Unreleased

## 0.1.1 — 2026-07-21 — PyPI presentation and release hardening

### Fixed

- Corrected README image rendering on PyPI by using absolute HTTPS image URLs.

### Changed

- Added a direct PyPI installation path to the Quick Start.
- Reworked the release workflow to build and verify immutable tagged distributions, publish through TestPyPI first, and use Trusted Publishing attestations.

## 0.1.0 — 2026-07-20 — CAGE-lite v1 product preview

### Added

- Modular Streamlit application with Overview, Boundary Runs, Warrants, Replay, and Architecture views.
- USD 75,000 vendor-payment demonstration covering both a held attempt and an admitted replay after approval.
- Durable effect, evidence, and CAGE Warrant artifacts.
- CAGE Warrant schema `0.4`, including boundary outcome, effect proof, timestamps, and replay linkage.
- Independent Warrant digest verification and integrity status in the user interface.
- Boundary-run history showing held, admitted, and narrowed outcomes.
- Public payment examples for no-bind, approval, and narrowed-action scenarios.
- Integration tests covering examples, replay behavior, Warrant generation, digest verification, artifact loading, and the modular UI.
- Package metadata, project links, Apache-2.0 license metadata, and packaged UI assets.
- Continuous integration on Python 3.10 and Python 3.13.
- Contribution guidelines, code of conduct, and security-reporting policy.
- Product screenshots and verified Quick Start instructions.

### Changed

- Adopted **CAGE Warrant** as the public name for the final assurance record.
- Clarified that CAGE provides prebind assurance at the business consequence boundary and does not replace runtimes, IAM, policy engines, guardrails, gateways, observability, or agent evaluation platforms.
- Updated effect-executing examples to persist durable effect proof through `FileLedger`.
- Improved first-run routing, artifact-loading diagnostics, timestamp handling, and Boundary Runs presentation.
- Updated packaging so the Streamlit application, logo, license, and notice are included in built distributions.

### Removed

- Removed the obsolete sidebar-based `receipt_viewer.py` application after confirming that the modular v1 application no longer imported or used it.
- Removed outdated public demo labels and misleading example terminology.
