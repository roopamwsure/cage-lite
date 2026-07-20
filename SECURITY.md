# Security Policy

## Supported versions

CAGE-lite is currently released as a product preview.

| Release line | Security support |
| --- | --- |
| 0.1.x product preview | Supported |
| Earlier development versions | Not supported |

Security fixes will be applied to the latest supported version. Before reporting a vulnerability, please confirm that the issue is still present in the latest available code.

The CAGE Warrant schema version is separate from the Python package version. Warrant schema `0.4` does not represent a separate software support line.

## Reporting a vulnerability

Do not report suspected security vulnerabilities through public GitHub issues, discussions, or pull requests.

Use GitHub private vulnerability reporting:

1. Open the repository's **Security** page.
2. Select **Advisories**.
3. Select **Report a vulnerability**.
4. Submit the report using the private advisory form.

Please include as much of the following information as possible:

- the affected package version, commit, or branch;
- the affected module or component;
- steps required to reproduce the issue;
- expected and observed behavior;
- the potential security impact;
- relevant logs, traces, sample artifacts, or proof-of-concept material;
- any known mitigation or suggested correction.

Remove credentials, access tokens, personal information, confidential business information, and production data before submitting evidence.

## Response process

The maintainer will review the report and respond as soon as reasonably possible.

The review may include:

- confirming whether the issue can be reproduced;
- assessing severity and affected versions;
- requesting additional technical information;
- preparing and validating a correction;
- coordinating publication of a security advisory.

Please allow reasonable time for investigation and remediation before publicly disclosing the vulnerability.

Reports that describe feature requests, documentation gaps, or product behavior without a security impact may be redirected to the public issue tracker.

## Scope

Security reports may cover:

- CAGE-lite source code;
- Python package and distribution artifacts;
- command-line behavior;
- the Streamlit application;
- artifact loading and storage;
- CAGE Warrant generation and verification;
- evidence and digest processing;
- boundary decisions and effect records;
- demonstration and replay workflows.

CAGE-lite is an open-source reference implementation. It is not a security certification, production authorization, or replacement for an organization's own architecture review, threat modelling, access controls, secrets management, dependency management, monitoring, and deployment security practices.

Deployments that connect CAGE-lite to protected APIs, identity systems, policy engines, approval systems, ledgers, or systems of record must be independently assessed for their intended environment.
