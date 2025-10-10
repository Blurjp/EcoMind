# Privacy Policy – Ecomind

**Last Updated**: 2025-09-30

## Overview

Ecomind is designed with **privacy-first** principles. We do not log, store, or transmit AI prompts or model completions.

## Data We Collect

### Metadata Only

When you use Ecomind (via browser extension, SDK, or API), we collect:

- **Timestamps** (when API calls occurred)
- **Provider** (e.g., OpenAI, Anthropic)
- **Model name** (extracted from URL when possible, e.g., `gpt-4o`)
- **Token counts** (if available in response headers)
- **Region** (optional, for carbon intensity calculations)
- **Organization ID** and **User ID** (for aggregation)

### What We DO NOT Collect

- ❌ Prompt text
- ❌ Model responses/completions
- ❌ Conversation history
- ❌ Personal data beyond user/org identifiers
- ❌ IP addresses (not stored beyond request logs)

## Data Usage

Collected metadata is used to:

- Calculate environmental footprint (kWh, water, CO₂)
- Aggregate usage statistics for dashboards
- Generate ESG reports
- Trigger usage alerts

## Data Retention

- **Events**: Configurable per organization (default: 90 days)
- **Aggregates**: Retained indefinitely (no PII)
- **Audit logs**: Retained for 1 year

## Data Sharing

Ecomind does **not sell or share** your data with third parties.

Exception: If you configure webhooks (Slack, Teams), alerts are sent to those services.

## Local-Only Mode

The browser extension supports **local-only mode**, where all tracking stays on your device and nothing is sent to Ecomind servers.

## GDPR/CCPA Compliance

- **Right to Access**: Request your data via support@ecomind.biz
- **Right to Deletion**: Request deletion of your organization's data
- **Data Portability**: Export via API or CSV reports

## Security

- All data encrypted in transit (TLS 1.3)
- Data encrypted at rest (AES-256)
- SOC 2 Type II certified (coming soon)

## Changes to This Policy

We will notify you of material changes via email or in-app notification.

## Contact

support@ecomind.biz