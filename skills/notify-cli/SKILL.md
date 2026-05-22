---
name: notify-cli
description: CLI tools for sending notifications through the Hermes bus ecosystem — notify-hermes (bus messages) and notify-agent (tmux session messages).
version: 1.0.0
metadata:
  hermes:
    tags: [cli, notify-hermes, notify-agent, bus, notification, channel]
---

# Notify CLI

> **Purpose:** This skill is designed for **Hermes agents** to learn correct CLI syntax, then teach non-Hermes agents (Claude Code, OpenCode, etc.) by embedding examples in task messages. Non-Hermes agents don't load skills — they learn from what you tell them.
>
> For the receive side (how bus-plugin routes messages with channel), see the `notification-protocol` skill (hermes-bus-plugin).

Two CLI commands for sending notifications in the Hermes bus ecosystem.

## notify-hermes

Send a message through the bus to any endpoint:

```bash
notify-hermes --to <endpoint> --type <type> [--channel <platform:chat_id>] [--from <sender>] "message"
```

| Arg | Required | Description |
|-----|----------|-------------|
| `--to` | yes | Target bus endpoint name |
| `--type` | no | Message type: `ack`, `task_start`, `progress`, `task_done`, `plan_ready`, `task_error`, `need_decision`, `directive` |
| `--channel` | no | Reply routing token: `platform:chat_id` (e.g. `feishu:oc_abc123`) |
| `--from` | no | Sender name override (auto-detected from tmux session) |
| `--body` | no | Full JSON body dict instead of positional message |
| `message` | * | Plain text (positional, last arg) |

Examples:

```bash
notify-hermes --to lead-agent --type ack "Received, starting work"
notify-hermes --to lead-agent --type task_done --channel feishu:oc_abc123 "Complete"
```

## notify-agent

Send text directly to a tmux session (not through the bus):

```bash
notify-agent [--from SENDER] <tmux-session-name> "message"
```

The first argument is a **tmux session name** (the name passed to `tmux new-session -s`). This is NOT a bus endpoint or agent name.

```bash
tmux new-session -d -s lead-agent   'claude'
tmux new-session -d -s worker-alpha 'claude'
notify-agent --from worker-alpha lead-agent "Build complete"
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
