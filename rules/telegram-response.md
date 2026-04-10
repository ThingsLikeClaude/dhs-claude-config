# Telegram Response Protocol

## Rule: 3-Step Response Pattern

When a message arrives from Telegram (`<channel source="plugin:telegram:telegram">`), ALWAYS follow this exact sequence:

### Step 1: Instant Acknowledgement (React)
- Call `telegram__react` with emoji `👀` on the incoming message
- This tells the sender "I saw your message"

### Step 2: Short First Reply
- Call `telegram__reply` with a brief 1-line acknowledgement
- Examples: "확인했어요, 처리 중이에요!", "잠시만요, 확인 중!", "네, 바로 볼게요!"
- Do NOT include the full answer here

### Step 3: Detailed Response
- Process the actual request
- Send the full answer as a separate `telegram__reply`

## Execution Order

```
Message received
  → react(👀)          # immediate
  → reply("짧은 확인")   # immediate
  → [processing...]     # actual work
  → reply("상세 응답")   # when done
```

## Exceptions

- Simple greetings (hi, 안녕) → Step 1 + Step 2 only (no Step 3 needed)
- If the answer is genuinely 1 sentence → Step 1 + combine Step 2 & 3 into one reply

## Why

User reported that sometimes responses feel delayed or uncertain whether the bot received the message. The emoji reaction provides instant visual feedback before processing begins, improving perceived responsiveness.
