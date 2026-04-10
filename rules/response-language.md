# Response Language

## Rule

All responses to the user MUST be in **Korean** when oh-my-stalab-pro-max is active.

This includes:
- Interview questions (deep-interview)
- Planning summaries (ralplan)
- Status reports (status)
- Completion reports (ralph, autopilot)
- Error messages and escalation notices
- Progress indicators

## Exceptions

- Code, file paths, and technical identifiers remain in English
- Skill definitions (SKILL.md), agent definitions, rules, and documentation are written in English
- State files (JSON) use English keys
- Git commit messages follow the project's existing convention

## Examples

```
# GOOD: Korean response with English code
"인증 모듈을 구현했습니다. `src/auth/handler.ts`에 OAuth 콜백을 추가했고,
테스트 12개 모두 통과했습니다."

# BAD: English response
"I implemented the auth module. Added OAuth callback to src/auth/handler.ts,
all 12 tests passing."

# BAD: Korean in skill file
"## 목적\n이 스킬은..."  <- skill files must be English
```
