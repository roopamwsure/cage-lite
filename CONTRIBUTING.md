# Contributing to CAGE-lite

Thank you for considering a contribution to CAGE-lite.

CAGE-lite is an open-source reference implementation of the CAGE framework: Control Assurance Governance Evaluation. The project focuses on prebind assurance for AI-agent actions at the business consequence boundary.

## Before contributing

Please open an issue before starting a large feature, architectural change, schema change, or broad refactor.

Small bug fixes, documentation corrections, and focused tests can usually be submitted directly as a pull request.

Keep changes narrow. Avoid combining unrelated cleanup with a functional change.

## Development setup

CAGE-lite requires Python 3.10 or later.

Clone the repository, then create a virtual environment.

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

macOS or Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install the project and test dependency:

```bash
python -m pip install --upgrade pip
python -m pip install -e .
python -m pip install pytest
```

Run the test suite:

```bash
python -m pytest -q
```

Generate the payment replay demo:

```bash
python -m cage_lite.demo.payment_replay
```

Launch the Streamlit application:

```bash
streamlit run cage_lite/ui/app.py
```

## Project terminology

The public product term is **CAGE Warrant**.

Some internal modules, directories, and schema fields continue to use `receipt` terminology for implementation and compatibility reasons. Examples include:

- `receipt_id`
- `replay_of_receipt_id`
- the `receipts` artifact directory
- receipt schema classes and functions

Please do not rename these internal fields broadly without first checking the impact on schemas, tests, saved artifacts, and existing APIs.

## Contribution principles

Contributions should keep these stages distinct:

- the proposed agent action
- the prebind boundary decision
- effect execution
- effect proof
- the resulting CAGE Warrant

CAGE does not replace agent runtimes, IAM, policy engines, approval systems, gateways, guardrails, observability tools, or systems of record.

Please keep public claims grounded. CAGE-lite is a product preview and reference implementation, not a certified control, finished industry standard, or replacement for existing governance systems.

## Code changes

Please:

- keep code readable and direct
- avoid unnecessary abstractions
- preserve existing compatibility behavior unless the change is intentional and documented
- add or update tests for changed behavior
- avoid unrelated formatting or refactoring
- keep generated playground artifacts out of commits
- run the full test suite before submitting a pull request

For UI changes, also inspect the affected page visually.

## Pull requests

A pull request should explain:

1. what problem it addresses
2. what changed
3. which files are affected
4. how the change was tested
5. whether compatibility, schemas, artifacts, or screenshots are affected

Before submitting, run:

```bash
python -m pytest -q
git diff --check
git status --short
```

The working tree should contain only the files required for the contribution.

## Documentation

Update documentation when a change affects:

- installation commands
- demo behavior
- public terminology
- artifact formats
- Warrant fields
- UI behavior
- deployment requirements

Do not commit local virtual environments, caches, generated artifact histories, or editor-specific files.

## Licensing

CAGE-lite is licensed under the Apache License 2.0.

By submitting a contribution, you agree that your contribution may be distributed under the same license.
