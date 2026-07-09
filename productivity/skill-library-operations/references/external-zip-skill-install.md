# External ZIP Skill Installation

Use when a user provides a direct `.zip` URL containing a skill directory.

## Workflow

1. Download to a temporary directory, not directly into `~/.hermes/skills`.
2. Compute and record SHA256 of the archive.
3. Extract with a safe library/tool and inspect the file tree before installing.
4. Vet contents separately from quality:
   - Security: look for executable scripts, shell commands, network endpoints, secret handling, destructive operations.
   - Quality: frontmatter shape, name validity, description clarity, linked files, version.
5. Normalize the local skill name if the upstream name is not Hermes-friendly, e.g. Chinese or space-containing names. Preserve the upstream name in local installation notes.
6. Install under an existing class-level category when possible. Put supporting Markdown files under `references/` and rewrite SKILL.md pointers from `foo.md` to `references/foo.md`.
7. Add local provenance to SKILL.md: source URL, SHA256, upstream name, environment variables required, and any external endpoints called.
8. Validate frontmatter with YAML parsing and `skill_view(<normalized-name>)` after install.
9. If the skill requires an API key, verify presence without printing it; run a harmless smoke test only if credentials exist.
10. **Report the install destination**: After installing, tell the user where the skill landed (full path to SKILL.md and scripts/ dir). the user expects "搞定了要汇报一下归到哪儿了" — don't leave them wondering where it went.

## Example pattern

```bash
WORK=$(mktemp -d)
curl -fL --retry 3 -o "$WORK/skill.zip" 'https://example.com/skill.zip'
sha256sum "$WORK/skill.zip"
python3 - <<'PY'
import zipfile, pathlib
z = zipfile.ZipFile('/tmp/path/skill.zip')
z.extractall('/tmp/path/extracted')
PY
find "$WORK/extracted" -maxdepth 4 -type f
```

Then transform/install with a short script rather than copying blindly.

## Pitfalls

- Do not use an upstream non-ASCII `name` directly if it makes loading awkward; normalize and document the original.
- Do not mirror bundled demos/assets unless the skill needs them.
- Do not hardcode API keys found in docs or environment; mention required env vars only.
- If `unzip` is unavailable, use Python `zipfile`.
- **Do not skip step 10**: The user wants to know where the files landed. Show the absolute path to the installed skill directory and SKILL.md after install.