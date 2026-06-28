---
name: notify-cli
description: CLI senders for the Hermes ecosystem — notify-hermes (non-Hermes agents → Hermes agent via bus) and notify-agent (Hermes agent → other tmux agents directly).
version: 0.8.1
metadata:
  hermes:
    tags: [cli, notify-hermes, notify-agent, bus, notification, channel]
---

# Notify CLI

> **Direction matters — pick by who sends to whom:**
> - **`notify-hermes`** — used by **non-Hermes agents** (Claude Code, OpenCode, etc.) to send messages **to a Hermes agent** through the bus. The sender is outside Hermes and wants to reach an endpoint on the bus.
> - **`notify-agent`** — used by a **Hermes agent** to send messages **to other tmux agents directly** (same-machine, no bus). The sender is Hermes-side and wants to reach another tmux pane.
>
> **Purpose:** This skill is for **Hermes agents** to learn correct CLI syntax, then teach non-Hermes agents by embedding examples in task messages. Non-Hermes agents don't load skills — they learn from what you tell them.
>
> For the receive side (how bus-plugin routes messages with channel), see the `notification-protocol` skill (hermes-bus-plugin).

Two CLI commands for sending notifications in the Hermes bus ecosystem.

## notify-hermes — non-Hermes → Hermes (via bus)

Used by **non-Hermes agents** to send a message **to a Hermes agent** through the bus. The sender is outside Hermes (Claude Code, OpenCode, CI pipeline, etc.) and targets a bus endpoint.

```bash
notify-hermes --to <endpoint> --type <type> [--channel <platform:chat_id>] [--from <sender>] "message"
```

| Arg | Required | Description |
|-----|----------|-------------|
| `--to` | yes | Target Hermes endpoint name (e.g. `lead-agent`, `hermes-bus`) |
| `--type` | no | Message type: `ack`, `task_start`, `progress`, `task_done`, `plan_ready`, `task_error`, `need_decision`, `directive` |
| `--channel` | no | Reply routing token: `platform:chat_id` (e.g. `feishu:oc_abc123`) |
| `--from` | no | Sender name override (auto-detected from tmux session via `role_map`) |
| `--body` | no | Full JSON body dict instead of positional message |
| `message` | * | Plain text (positional, last arg) |

Examples (non-Hermes agent sending to Hermes):

```bash
# Claude Code → Hermes lead-agent
notify-hermes --to lead-agent --type ack "Received, starting work"

# CI pipeline → Hermes with reply channel
notify-hermes --to lead-agent --type task_done --channel feishu:oc_abc123 "Build #142 passed"
```

## notify-agent — Hermes → other tmux agents (direct)

Used by a **Hermes agent** to send text **directly to other tmux agents** on the same machine. Does NOT go through the bus. The sender is Hermes-side; the target is a tmux session name.

```bash
notify-agent [--from SENDER] [--to SESSION] <session> "message"
```

- All flags (`--from`, `--to`, `--config`) can appear in **any order**.
- `--to` is an alias for positional `<session>` (either works).
- `--from` omitted → **no sender prefix** (pure message). Provided → `role_map` lookup; unmatched → use `--from` value as-is.
- Message format with `--from`: `⚕ [{sender}]: {text}`.

The first positional arg (or `--to`) is a **tmux session name** (the `-s` of `tmux new-session`). NOT a bus endpoint.

```bash
# Hermes agent → another tmux agent (role_map resolves worker-alpha → "Alpha")
tmux new-session -d -s lead-agent   'claude'
tmux new-session -d -s worker-alpha 'claude'
notify-agent --from worker-alpha --to lead-agent "Build complete"
# → ⚕ [Alpha]: Build complete

# Sender not in role_map → use as-is
notify-agent --from MyBot lead-agent "Deploy done"
# → ⚕ [MyBot]: Deploy done

# No --from → pure message
notify-agent lead-agent "Status check"
# → Status check
```

## Channel Routing

The `--channel` parameter enables reply routing across chat platforms. The channel token is preserved through the entire notification chain — agents echo it, the bus-plugin delivers it to the correct platform adapter at the final step.

### `notify-agent` channel tag

When using `notify-agent`, append the channel tag to the message text:

```text
[channel:<platform>:<chat_id>]
```

The tag tells every agent in the chain: this task came from Hermes, preserve the tag, the last agent with bus access reports via `notify-hermes --channel`.

```bash
notify-agent worker-alpha "Fix parser [channel:feishu:oc_abc123]"
```

No tag → normal agent-to-agent conversation, reply via `notify-agent`.
