# PlainSight

Privacy Intelligence Extension
Real-time analysis of cookie consent mechanisms and privacy policies

📌 Overview

Modern websites ask users to accept cookies and privacy policies that are complex, vague, and often designed to nudge acceptance rather than enable understanding. As a result, consent is frequently given without real awareness of tracking behavior or data usage.

This project builds a privacy intelligence system consisting of:

a browser extension that observes consent interfaces and policy links,

deterministic and semantic analysis pipelines that evaluate cookie usage and privacy disclosures,

a side panel that presents clear, user-friendly summaries and flagged risks,

optional storage and change detection for long-term transparency.

The system focuses on explainability, transparency, and ethical data access.

🧩 System Architecture (High Level)
Webpage
├── Cookie banner / consent modal
├── Privacy & cookie policy links
└── Browser cookies (metadata only)
↓
Chrome Extension (Observer)
├── Content Script (DOM inspection)
├── Cookie Metadata Reader
└── Message Router
↓
Backend Pipelines
├── Cookie Analyzer (deterministic + optional ML)
└── Policy NLP Analyzer (semantic analysis)
↓
Side Panel (Results)
├── Cookie summary + flags
├── Policy summary + flags
└── Risk indicators
↓
Database (optional)
├── Cached analyses
└── Change detection over time

1️⃣ Extension: What is Extracted & How

The extension does not modify webpages and does not collect personal data.
It only observes user-visible content and browser-exposed metadata.

A. Visible Text Extraction (DOM-based)

The content script reads only what is rendered on the page:

Cookie banner text

Consent modal text

Short consent descriptions

Category labels and explanations

No full-page scraping is performed.

B. Policy Link Detection

The extension detects relevant hyperlinks by inspecting <a> tags where:

Anchor text contains:

privacy

cookie

terms

OR href contains:

/privacy

/cookies

/policy

From this, it extracts:

Privacy policy URL

Cookie policy URL (if separate)

The extension does not click links — it only reads what is visible.

C. Cookie Metadata Extraction (All Legitimate Methods)

The extension never reads cookie values.

1. Chrome Cookies API (Primary)

Using the browser’s cookie API, it retrieves:

Cookie name

Domain

Path

Expiry time

Secure / HttpOnly / SameSite flags

This allows inference of:

Third-party cookies

Long-lived identifiers

Session vs persistent cookies

2. Consent Management Platform (CMP) APIs (When Available)

Many sites expose structured consent data via JavaScript objects such as:

window.OneTrust

window.Cookiebot

window.\_\_tcfapi

From these, the extension can extract:

Cookie categories

Default consent states

Purpose descriptions

Vendor information

This is first-class, compliance-oriented metadata.

3. DOM Inspection of Preference Modals (Fallback)

When CMP APIs are unavailable:

Toggle labels

Default checked state

Category descriptions

Button hierarchy (Accept / Reject / Manage)

This enables detection of:

Pre-checked non-essential cookies

Hidden preferences

Asymmetric consent flows

2️⃣ Cookie Pipeline: Deterministic Core + Optional ML
Why Deterministic First

Cookie behavior is structural

Compliance logic must be explainable

ML alone is brittle for consent analysis

Judges and reviewers trust rule-based findings

Therefore, deterministic rules are the source of truth.

Inputs to Cookie Pipeline

Cookie metadata (browser API)

Consent structure (DOM + CMP)

Category labels and descriptions (text)

Deterministic Checks (Must-Have)
Structural Signals

Accept = 1 click, Reject = N clicks

Non-essential categories pre-checked

Consent required to proceed

“Manage preferences” hidden or deprioritized

Cookie Behavior

Third-party cookie domains

Expiry > 6 months

Cookies set before consent

Ads / analytics enabled by default

These checks are objective and binary.

Detecting Misleading or Wrong Usage

The pipeline cross-checks claims vs behavior, for example:

“Only essential cookies” but marketing enabled

“Analytics only” but ad trackers present

Consent labeled optional but cookies set pre-consent

These cases are flagged as misleading consent.

Optional ML Layer (Thin, Non-Authoritative)

ML is used only for language interpretation, never for decisions.

Valid ML uses:

Classifying vague descriptions
(“Improve experience” → analytics / ads)

Detecting euphemistic phrasing

Mapping descriptions to risk intent

Approaches:

Zero-shot classification

Sentence embeddings + similarity

ML cannot override deterministic flags.

3️⃣ Policy NLP Pipeline: Semantic Analysis

This pipeline analyzes linked privacy and cookie policies, not for length but for meaning and risk.

Inputs

Policy URL(s)

Public HTML content

Processing Steps

Fetch policy page

Remove boilerplate (nav, footer)

Chunk text into paragraphs

Convert chunks to embeddings

Classify clauses into:

Data collection

Data sharing

Retention

User rights

Flag risky clauses

Generate concise summary

What Gets Flagged

Third-party data sharing

Indefinite retention

Vague purpose limitation

Lack of opt-out

Cross-service tracking

The output is explainable and user-friendly, not legal advice.

4️⃣ Tools / APIs / Tech Stack
Extension

JavaScript

Chrome Extension (Manifest V3)

Content Scripts

Chrome Cookies API

Chrome Side Panel API

Cookie Analyzer Pipeline

Python (rule engine)

JavaScript (DOM + CMP parsing)

Optional: spaCy / Sentence-Transformers

Policy NLP Pipeline

Python

BeautifulSoup

Sentence-Transformers

spaCy

FastAPI (lightweight wrapper)

Dashboard

Streamlit (fast, hackathon-friendly)

Databases

SQLite: local caching, pipeline outputs

MongoDB Atlas (optional): user-saved summaries, cross-device sync

5️⃣ Database & Periodic Updates
What is Stored

Policy URL

Content hash

Analysis results

Timestamp

No personal data is stored by default.

Change Detection Strategy

Store hash of policy content

Periodically refetch (daily / weekly)

Re-hash content

Re-run analysis only if content changes

This avoids unnecessary scraping and respects resources.

Is This Web Scraping?

Yes — but limited, ethical, and public:

Only public policy pages

Low frequency

No authentication

No personal data

This is acceptable for academic and product use.

🔐 Transparency & Ethics

Only user-visible data is analyzed

Cookie metadata, not values

No tracking of browsing behavior

No storage without explicit user action

Deterministic logic drives decisions

AI is used only for summarization

🚀 Status

This repository implements:

Cookie consent analysis

Privacy policy semantic analysis

Side-panel-ready summaries

Optional persistence and change tracking

Future work includes:

Personal risk profiles

Cross-site comparisons

Regulatory mapping (GDPR / DPDP)
