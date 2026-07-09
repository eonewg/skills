# Hermes OpenAI Codex credential pools

Use this when the user wants multiple ChatGPT/OpenAI Codex accounts routed behind Hermes so one account's quota exhaustion can fall through to another.

## Core commands

Check current pool:

```bash
hermes auth list openai-codex
hermes auth status openai-codex
```

Add another Codex OAuth credential:

```bash
hermes auth add openai-codex --type oauth --label codex-backup
```

For WSL/remote/headless flows where the browser should not auto-open:

```bash
hermes auth add openai-codex --type oauth --label codex-backup --no-browser
```

Hermes prints:

```text
Open this URL in your browser:
https://auth.openai.com/codex/device

Enter this code:
XXXX-XXXX
```

The person who owns the quota opens the URL, signs into their own OpenAI/ChatGPT account, and enters the code. After they authorize, Hermes stores the OAuth credential in `~/.hermes/auth.json` under the `openai-codex` credential pool.

## Friend/teammate account handoff

It is technically possible to send the device URL and code to another person. Be explicit about the security boundary:

- They are authorizing this Hermes installation to use their Codex/ChatGPT quota until the token expires, is removed, or is revoked.
- They should never send passwords, cookies, email codes, or 2FA codes.
- Only the device URL/code is needed; if a manual callback URL is involved, treat it as sensitive because it can contain an authorization code.

If the environment requires manual callback paste, use:

```bash
hermes auth add openai-codex --type oauth --label friend-codex --manual-paste
```

## Rotation policy

For "use one account until quota is exhausted, then switch", set fill-first:

```bash
hermes config set credential_pool_strategies.openai-codex fill_first
```

Other strategies exist (`round_robin`, `least_used`, `random`), but `fill_first` is usually the right default for subscription/quota accounts.

Hermes handles usage-limit / rate-limit style failures by rotating credentials inside the same provider before falling through to cross-provider `fallback_providers`.

## Manual operations

Reset cooldown/exhaustion state after quotas recover:

```bash
hermes auth reset openai-codex
```

Remove a credential by list index:

```bash
hermes auth list openai-codex
hermes auth remove openai-codex <index>
```

### Quick manual switching between two Codex accounts

Hermes does not currently expose a dedicated `hermes auth select openai-codex <index>` command. With `fill_first`, the practical manual-switch mechanism is to move the desired credential to the first pool entry (`priority: 0`) in `~/.hermes/auth.json`; `hermes auth list openai-codex` marks that entry with `←`.

Use the packaged helper when the user wants command-style switching:

```bash
cp ~/.hermes/skills/autonomous-ai-agents/model-routing-and-provider-config/scripts/codex-use.py ~/.local/bin/codex-use
chmod +x ~/.local/bin/codex-use
codex-use list
codex-use me          # alias for the original device_code entry
codex-use zuo         # alias for the second credential labeled friend-codex
codex-use zuo --reset # select it and clear stale exhausted/cooldown status
```

If a target credential was previously marked exhausted but the user explicitly wants to force it back into use, include `--reset` on the same selection command:

```bash
codex-use zuo --reset
```

Caveat: a currently running Hermes request/session may already have resolved a token; a new request/session sees the new priority more reliably. Restart the gateway if the user needs immediate certainty.

After auth/config changes in a gateway session, restart the gateway:

```bash
hermes gateway restart
```

## Troubleshooting pattern

During device-code polling, a transient network/proxy TLS error such as:

```text
httpx.ConnectError: [SSL: UNEXPECTED_EOF_WHILE_READING]
```

can terminate the `hermes auth add` process. Do not encode this as "Codex auth is broken". Verify connectivity to the OpenAI auth endpoints if needed, then re-run `hermes auth add ... --no-browser` to generate a fresh device code. Old device codes should be discarded after a failed run.
