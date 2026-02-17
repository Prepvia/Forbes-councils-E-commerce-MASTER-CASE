# Security Policy

## Supported Versions

This project is currently maintained as a single active branch (`main`).

| Version | Supported |
| ------- | --------- |
| main    | Yes       |
| older commits/tags | No |

## Reporting a Vulnerability

If you discover a security issue, please report it privately.

Preferred channel:
- Use GitHub's private vulnerability reporting for this repository (Security Advisories).

If private reporting is not available:
- Contact the repository owner directly via GitHub profile and request a private channel for disclosure.

Please include:
- A clear description of the issue
- Steps to reproduce
- Impact assessment (what data/process could be affected)
- Suggested fix, if available

## Response Expectations

- Acknowledgement target: within 48 hours
- Initial triage target: within 7 days
- Fix timeline: based on severity and complexity

## Disclosure Policy

- Do not publish proof-of-concept details publicly before a fix is available.
- Once resolved, maintainers may publish a summary in release notes or a security advisory.

## Scope

In scope:
- Vulnerabilities in `optimizer_engine.py`, `master_case_optimizer.html`, and local server behavior
- Input handling and unsafe server behavior
- Dependency-related vulnerabilities that affect this repository

Out of scope:
- Local machine misconfiguration
- Third-party service outages
- Social engineering
