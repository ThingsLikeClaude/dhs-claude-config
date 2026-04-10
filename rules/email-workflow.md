---
paths:
  - "**/gmail*"
  - "**/email*"
  - "**/gws-gmail*"
---

# Email Workflow

## Triage (메일 정리)

Trigger: "메일 정리", "메일 확인", "이메일 정리"

### Flow

```
1. Search today's emails
   gmail_search_messages: after:YYYY/MM/DD before:YYYY/MM/DD+1

2. Search all unread+inbox emails
   gmail_search_messages: is:unread in:inbox (maxResults: 50)

3. Output summary table
   | # | From | Subject | Category | Date |

4. Batch read + archive
   gws gmail users threads modify:
     removeLabelIds: ["UNREAD", "INBOX"]

5. Verify
   Re-search is:unread in:inbox → confirm 0 results
```

### Rules

- Do NOT ask "아카이브 할까요?" — process immediately
- Include older unprocessed emails, not just today
- Mark important emails (security alerts, work-related) with ⚠️ in table
- Output result table after processing

## Sending

Use gws-gmail-send skill.

### Self-send ("나에게 보내기") — CRITICAL

`gws gmail +send --to me` does NOT work. `me` is a Gmail REST API alias, not recognized by gws CLI's `--to` flag.

**When user requests "send to myself":**
1. Call `gmail_get_profile` MCP tool to get the actual email address
2. Use the resolved address in `--to`

```bash
# BAD — causes "Invalid To header" error
gws gmail +send --to me --subject '...' --body '...'

# GOOD
gws gmail +send --to oovbeats@gmail.com --subject '...' --body '...'
```

## Reply

Use gws-gmail-reply / gws-gmail-reply-all skill.

## Forward

Use gws-gmail-forward skill.
