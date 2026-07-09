# Third-party sources and attribution for `github-repo-management`

This file is generated during public packaging to keep upstream references visible. Verify upstream licenses before redistributing modified scripts or templates.

## URLs

- https://github.com/$GH_USER/my-new-project.git
- https://github.com/$GH_USER/repo-name.git
- https://github.com/$OWNER/$REPO.git
- https://github.com/OWNER/REPO.git`
- https://github.com/login/device/code
- https://github.com/login/device/code`
- https://github.com/login/oauth/access_token`
- https://github.com/o/r.git`
- https://github.com/owner/repo-name.git
- https://github.com/{owner}/{repo}.git

## Source/license lines found in the skill files

- `license: MIT`
- `elif grep -q "github.com" ~/.git-credentials 2>/dev/null; then`
- `GITHUB_TOKEN=$(grep "github.com" ~/.git-credentials 2>/dev/null | head -1 | sed 's|https://[^:]*:\([^@]*\)@.*|\1|')`
- `GH_USER=$(curl -s -H "Authorization: token $GITHUB_TOKEN" https://api.github.com/user | python3 -c "import sys,json; print(json.load(sys.stdin)['login'])")`
- `git clone https://github.com/owner/repo-name.git`
- `git clone https://github.com/owner/repo-name.git ./my-local-dir`
- `git clone --depth 1 https://github.com/owner/repo-name.git`
- `git clone --branch develop https://github.com/owner/repo-name.git`
- `https://api.github.com/user/repos \`
- `git clone https://github.com/$GH_USER/my-new-project.git`
- `git remote add origin https://github.com/$GH_USER/my-new-project.git`
- `https://api.github.com/orgs/my-org/repos \`
- `https://api.github.com/repos/owner/template-repo/generate \`
- `https://api.github.com/repos/owner/repo-name/forks`
- `git clone https://github.com/$GH_USER/repo-name.git`
- `git remote add upstream https://github.com/owner/repo-name.git`
- `https://api.github.com/repos/$OWNER/$REPO \`
- `"https://api.github.com/user/repos?per_page=20&sort=updated" \`
- `"https://api.github.com/search/repositories?q=machine+learning+language:python&sort=stars&per_page=10" \`
- `https://api.github.com/repos/$OWNER/$REPO/topics \`
- `https://api.github.com/repos/$OWNER/$REPO/branches/main/protection`
- `https://api.github.com/repos/$OWNER/$REPO/branches/main/protection \`
- `https://api.github.com/repos/$OWNER/$REPO/actions/secrets/public-key`
- `https://api.github.com/repos/$OWNER/$REPO/actions/secrets/API_KEY \`
- `https://api.github.com/repos/$OWNER/$REPO/actions/secrets \`
- `https://api.github.com/repos/$OWNER/$REPO/releases \`
- `"https://uploads.github.com/repos/$OWNER/$REPO/releases/$RELEASE_ID/assets?name=binary-amd64" \`
- `https://api.github.com/repos/$OWNER/$REPO/actions/workflows \`
- `"https://api.github.com/repos/$OWNER/$REPO/actions/runs?per_page=10" \`
- `https://api.github.com/repos/$OWNER/$REPO/actions/runs/$RUN_ID/logs \`
- `https://api.github.com/repos/$OWNER/$REPO/actions/runs/$RUN_ID/rerun`
- `https://api.github.com/repos/$OWNER/$REPO/actions/runs/$RUN_ID/rerun-failed-jobs`
- `https://api.github.com/repos/$OWNER/$REPO/actions/workflows/$WORKFLOW_ID/dispatches \`
- `https://api.github.com/gists \`
- `Move the old single-skill repository contents into the relevant category folder, preserve `SKILL.md`, scripts, references, and attribution, then create/push the new library repo. Before publishing, scan for real tokens and local paths (`/home/<user>`, `C:\\Users`, secret env files), run syntax checks for included scripts, and validate each `SKILL.md` frontmatter. If retiring the old repository with `gh repo delete`, remember GitHub requires the `delete_repo` OAuth scope; if the existing `gh` token lacks it, run `gh auth refresh -h github.com -s delete_repo`, send the user the device-code URL/code, then retry deletion and verify the old repo is gone.`
- `| Clone | `gh repo clone o/r` | `git clone https://github.com/o/r.git` |`
- `Base URL: `https://api.github.com``
- `| Upload asset | POST | `https://uploads.github.com/repos/{owner}/{repo}/releases/{id}/assets?name={filename}` |`
- `- Check remaining: `curl -s -H "Authorization: token $GITHUB_TOKEN" https://api.github.com/rate_limit``
- `https://api.github.com/repos/$GH_OWNER/$GH_REPO`
- `https://api.github.com/repos/$GH_OWNER/$GH_REPO/issues \`
- `https://api.github.com/repos/$GH_OWNER/$GH_REPO/issues/42 \`
- `https://api.github.com/repos/$GH_OWNER/$GH_REPO/issues/42/labels/bug`
- `https://api.github.com/repos/$OWNER/$REPO/pulls \`
- `https://api.github.com/repos/$OWNER/$REPO/commits/$SHA/status \`
- `https://api.github.com/repos/$OWNER/$REPO/commits/$SHA/check-runs \`
- `"https://api.github.com/repos/$OWNER/$REPO/actions/runs?branch=$BRANCH&per_page=5" \`
- `https://api.github.com/repos/$OWNER/$REPO/pulls/$PR_NUMBER/merge \`
- `https://api.github.com/repos/$OWNER/$REPO/pulls/$PR_NUMBER \`
- `https://api.github.com/graphql \`
- `| List my PRs | `gh pr list --author @me` | `curl -s -H "Authorization: token $GITHUB_TOKEN" "https://api.github.com/repos/$OWNER/$REPO/pulls?state=open"` |`
- `https://api.github.com/repos/$GH_OWNER/$GH_REPO/actions/runs/<RUN_ID>/logs \`
- `fatal: could not read Username for 'https://github.com': No such device or address`
- `echo "Poll with: curl -s -H 'Authorization: token ...' https://api.github.com/repos/.../commits/$(git rev-parse HEAD)/status"`
- `If `gh auth login --web` is hard to drive through a non-interactive/PTY tool, use GitHub's device flow directly, then feed the resulting token to `gh auth login --with-token` without printing it. Start by requesting a device code from `https://github.com/login/device/code` using the GitHub CLI OAuth client id (`178c6fc778ccc68e1d6a`) and scopes such as `repo read:org gist`; send the user the returned `verification_uri` and `user_code`; poll `https://github.com/login/oauth/access_token` until it returns `access_token`; then run:`
- `printf '%s\n' "$GITHUB_DEVICE_TOKEN" | gh auth login --hostname github.com --with-token`
- `gh auth setup-git --hostname github.com`
- `req = urllib.request.Request('https://api.github.com/user', headers=headers)`
- `req = urllib.request.Request('https://api.github.com/user/repos', data=body, headers=headers, method='POST')`
- `subprocess.run(['git', 'remote', 'add', 'origin', f'https://{owner}:{token}@github.com/{owner}/{repo}.git'], check=True)`
- `subprocess.run(['git', 'remote', 'set-url', 'origin', f'https://github.com/{owner}/{repo}.git'], check=True)`
- `git remote set-url origin "https://github.com/$OWNER/$REPO.git"`
- `git ls-remote "https://github.com/$OWNER/$REPO.git" HEAD`
- `req = urllib.request.Request('https://github.com/login/device/code', data=data, headers={'Accept': 'application/json'})`
- `Send the user only the `verification_uri` and `user_code`. In a background process, poll `https://github.com/login/oauth/access_token` with `grant_type=urn:ietf:params:oauth:grant-type:device_code` until `access_token` is returned, then feed it to `gh auth login --with-token` via stdin. From there, use normal `gh repo create`, `git push`, and remote verification.`
- `- If a temporary token must be embedded in an HTTPS remote for a push, immediately reset the remote URL to the clean `https://github.com/OWNER/REPO.git` form.`

## License signals

- `license: MIT`
