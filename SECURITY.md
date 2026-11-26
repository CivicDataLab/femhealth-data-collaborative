# Security and data protection policy

This repository holds public datasets, the scripts that process them, and documentation. It runs no service and stores no user accounts, so the main risks are a secret committed by mistake, personal data published by mistake, and unsafe code or binaries in the scripts. This policy covers how to report those and how we respond.

## What to report privately

Please report these by email rather than in a public issue:

- **Personal data** in any file: names, phone numbers, addresses, ID numbers or survey records that identify private individuals and were not already published by an official source.
- **Secrets**: credentials, API keys, tokens or private keys anywhere in the repository or its history.
- **Unsafe code or binaries**: a script or committed executable (for example the scraper's `chromedriver`) that could harm someone who runs it.
- **Vulnerable dependencies** that put people running the scripts at risk, if Dependabot has not already raised them.

Ordinary data errors, such as a wrong value or a mis-tagged record, are not security issues; please [report them as a data problem](https://github.com/CivicDataLab/femhealth-data-collaborative/issues/new/choose) instead.

## How to report

Email **tech@civicdatalab.in** with the subject `[SECURITY] femhealth-data-collaborative: <short description>`. Include:

- the file path and, where relevant, the commit or line
- what the problem is and who could be affected
- for personal data: which records, without copying the personal data into the email

We aim to acknowledge reports within 48 hours and will keep you informed until the issue is resolved.

## How we respond

1. **Confirm** the problem and how far it reaches (which files, which commits).
2. **Contain** it. For personal data or secrets, remove the content from the current files immediately. A committed secret is treated as compromised and rotated, because removing it from the files does not remove it from Git history or from forks.
3. **Clean history** where the risk warrants it, for example by rewriting history to purge personal data, and ask anyone with a fork or copy to update.
4. **Prevent recurrence**: add a check, adjust the SOP or the pre-commit hooks, and note the change in the affected dataset's README changelog.
5. **Credit** the reporter if they wish.

## Supported versions

Only the `main` branch is maintained. There are no releases.

## Guidelines for contributors

- Never commit credentials, tokens or `.env` files. `.gitignore` excludes `.env` files, and the `detect-private-key` pre-commit hook blocks private keys; run `pre-commit install` to turn the hooks on.
- Do not commit personal data, and publish aggregates rather than individual records (see [RESPONSIBLE_DATA_USE.md](RESPONSIBLE_DATA_USE.md)).
- Prefer downloading tools such as browser drivers from their official source over committing binaries; if a binary must be committed, record where it came from and its version.
- Read a script before running it, especially notebooks and scrapers that make network requests.
- Keep dependencies current by reviewing Dependabot pull requests.

## Applicable law

Handling of personal data must comply with India's Digital Personal Data Protection Act, 2023, and with each source's terms of use.
