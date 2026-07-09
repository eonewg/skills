# Publishing a Local Hermes Skill to a New GitHub Repository

Use this pattern when the user asks to publish a local Hermes skill as its own GitHub repo.

## Packaging shape

Create a clean staging repo instead of publishing directly from `~/.hermes/skills/...`:

```text
README.md
LICENSE
.gitignore
skill/SKILL.md
skill/references/...
scripts/...           # companion scripts the skill refers to
```

Copy only intentional public files. Do not copy local secrets, generated caches, OCR outputs, `.env` files, or the entire Hermes profile.

## README expectations

The public README should explain:

- what the skill does
- repository layout
- dependency installation
- basic usage
- token handling policy, with placeholder examples only
- Hermes installation instructions
- license

For the user-facing reusable skill repositories, default to a bilingual README unless the user asks for a single language. Use a clear switch such as `[English](#english) | [中文](#中文)` and keep both sections equivalent enough that Chinese users can install/use the skill without reading the English section. After pushing, fetch or view the remote README and verify both anchors/sections are present; do not just assume the local file made it upstream.

## Verification before publishing

Run syntax checks for included scripts, then remove generated caches before commit:

```bash
python3 -m py_compile scripts/*.py
bash -n scripts/*.sh
find . -type d -name __pycache__ -prune -exec rm -rf {} +
```

Run a secret scan before `git add`. Search for real token patterns, not just the word `TOKEN`:

```bash
grep -RInE 'ghp_[A-Za-z0-9_]{20,}|github_pat_[A-Za-z0-9_]{20,}|sk-[A-Za-z0-9_-]{12,}|Bearer[[:space:]]+[A-Za-z0-9._-]{20,}|(API_KEY|TOKEN)[[:space:]]*=[[:space:]]*[^[:space:]]+' . \
  --exclude-dir=.git --exclude-dir=.venv --exclude='*.pyc'
```

Placeholder examples such as `PADDLEOCR_TOKEN=***`, `your_token`, or `<TOKEN>` are acceptable, but prefer examples that avoid assignment-looking fake secrets when possible.

## Creating and pushing with GitHub device login

If `gh auth login --web` is hard to drive through a non-interactive/PTY tool, use GitHub's device flow directly, then feed the resulting token to `gh auth login --with-token` without printing it. Start by requesting a device code from `https://github.com/login/device/code` using the GitHub CLI OAuth client id (`178c6fc778ccc68e1d6a`) and scopes such as `repo read:org gist`; send the user the returned `verification_uri` and `user_code`; poll `https://github.com/login/oauth/access_token` until it returns `access_token`; then run:

```bash
printf '%s\n' "$GITHUB_DEVICE_TOKEN" | gh auth login --hostname github.com --with-token
gh auth setup-git --hostname github.com
```

Never print or persist the returned access token. After login, create/push with normal `gh repo create` and `git push`, then verify with `git ls-remote`.

## Creating and pushing without `gh`

If `gh` is unavailable but the user provides a GitHub token, avoid writing it to disk. Use it only in process environment for API calls and push:

```bash
python3 - <<'PY'
import json, os, subprocess, urllib.request

token = os.environ['GH_PAT']  # set only in the current process/session
headers = {'Authorization': 'Bearer ' + token, 'Accept': 'application/vnd.github+json'}

req = urllib.request.Request('https://api.github.com/user', headers=headers)
with urllib.request.urlopen(req, timeout=20) as r:
    owner = json.load(r)['login']

repo = 'pdf-ocr-searchable'
body = json.dumps({
    'name': repo,
    'description': 'Hermes skill and scripts for searchable PDF OCR',
    'private': False,
    'auto_init': False,
}).encode()
req = urllib.request.Request('https://api.github.com/user/repos', data=body, headers=headers, method='POST')
try:
    urllib.request.urlopen(req, timeout=20).read()
except Exception as e:
    # If the repo already exists, continue to push; otherwise inspect the error.
    print(f'repo create returned: {e}')

subprocess.run(['git', 'remote', 'add', 'origin', f'https://{owner}:{token}@github.com/{owner}/{repo}.git'], check=True)
subprocess.run(['git', 'push', '-u', 'origin', 'main'], check=True)
subprocess.run(['git', 'remote', 'set-url', 'origin', f'https://github.com/{owner}/{repo}.git'], check=True)
PY

git remote add origin "https://$OWNER:$user@example.com/$OWNER/$REPO.git"
git push -u origin main
git remote set-url origin "https://github.com/$OWNER/$REPO.git"
unset GITHUB_TOKEN
```

After push, verify with a tokenless public URL if the repo is public:

```bash
git ls-remote "https://github.com/$OWNER/$REPO.git" HEAD
```

If the repository is private, verify via authenticated API instead, but do not print the token.

## Device-code auth from a headless or remote agent session

When the user asks the agent to handle GitHub login and `gh auth login --web` times out or blocks in a remote/headless session, keep the actual authorization in the user's browser and automate only the polling/push side. Do not ask for a long-lived token unless this route fails.

Pattern:

```bash
# Start a GitHub OAuth device flow for the GitHub CLI OAuth app.
python3 - <<'PY'
import json, urllib.parse, urllib.request
client_id = '178c6fc778ccc68e1d6a'  # GitHub CLI OAuth app
scope = 'repo read:org gist'
data = urllib.parse.urlencode({'client_id': client_id, 'scope': scope}).encode()
req = urllib.request.Request('https://github.com/login/device/code', data=data, headers={'Accept': 'application/json'})
with urllib.request.urlopen(req, timeout=20) as r:
    print(json.dumps(json.load(r), indent=2))
PY
```

Send the user only the `verification_uri` and `user_code`. In a background process, poll `https://github.com/login/oauth/access_token` with `grant_type=urn:ietf:params:oauth:grant-type:device_code` until `access_token` is returned, then feed it to `gh auth login --with-token` via stdin. From there, use normal `gh repo create`, `git push`, and remote verification.

Safety notes:

- Never print the returned `access_token`.
- Avoid storing the token in repo files, git remotes, logs, or README examples.
- If a temporary token must be embedded in an HTTPS remote for a push, immediately reset the remote URL to the clean `https://github.com/OWNER/REPO.git` form.
- Treat `authorization_pending` and `slow_down` as normal polling states, not errors; respect the returned interval.

## Pitfalls

- `py_compile` creates `__pycache__`; delete it before committing.
- Do not publish profile-specific absolute secret paths as required user setup unless clearly documented as optional/local defaults.
- Before the first public push, scan for user names, local usernames, absolute home paths, private email addresses, generated OCR outputs, local dotenv paths, and assignment-looking token examples. Replace machine-specific paths with repository-relative paths such as `scripts/...` or configurable variables.
- If private information was already pushed in an earlier commit, a normal follow-up commit is not enough: amend/squash the public branch and `git push --force-with-lease`, then verify a fresh shallow clone of the public URL scans clean. Mention that hosting providers may retain caches even after branch history is rewritten.
- Missing `gh` or unconfigured credentials is setup state, not a blocker to packaging. Prepare and commit locally first, then ask for a token only when remote creation/push is needed.
- Do not paste a token into git config, `.git-credentials`, README, scripts, or skill files. If a token must appear in a remote URL for push, immediately reset the remote URL afterward.
