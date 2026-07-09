# SiYuan on WSL: CLI install and S3 sync import

Use this reference when the user asks to install SiYuan in WSL, operate SiYuan as a local knowledge backend, or attach a fresh WSL workspace to an existing SiYuan S3 sync repo.

## Install pattern
- Prefer the Linux tarball for the WSL architecture from the GitHub release assets, not the desktop `.deb` path.
- Install under `~/.local/opt/siyuan-<version>` and maintain `~/.local/opt/siyuan` as a symlink.
- Create wrappers in `~/.local/bin`:
  - `siyuan-kernel` -> `~/.local/opt/siyuan/resources/kernel/SiYuan-Kernel "$@"`
  - `siyuan-serve` -> serve `~/SiYuan` on port `6806`, language `zh-CN`, blank local access auth unless user requests otherwise.
  - `siyuan` -> desktop Electron entry; in WSL it needs `$DISPLAY`, so treat it as secondary to Kernel + Web UI.
- Verify with `siyuan-kernel --version`, `siyuan-kernel workspace info -w ~/SiYuan -f json`, and `curl http://127.0.0.1:6806/api/system/version`.

## Useful CLI/API surface
- Kernel help: `siyuan-kernel --help`.
- Serve: `siyuan-kernel serve -w ~/SiYuan --port 6806 --lang zh-CN`.
- Sync status: `siyuan-kernel sync status -w ~/SiYuan -f json`.
- Pull only after importing existing cloud config: `siyuan-kernel sync pull -w ~/SiYuan -f json`.
- List notebooks after pull: `siyuan-kernel notebook list -w ~/SiYuan -f json`.

## Importing an existing S3 sync repo
When attaching a fresh WSL workspace to another device's existing SiYuan S3 sync:
1. Start the local kernel service and verify `http://127.0.0.1:6806` responds.
2. Import the Data repo key first. The key is Base64 and should decode to 32 bytes. Use the API rather than editing config by hand:
   `POST /api/repo/importRepoKey` with JSON `{"key":"<base64-key>"}`.
3. Back up the fresh workspace before changing sync state, for example `tar -czf ~/SiYuan-backup-before-s3-import-$(date +%Y%m%d%H%M%S).tar.gz -C ~ SiYuan`.
4. Import the exported cloud provider package from the other device:
   `POST /api/sync/importSyncProviderS3` as multipart form field `file=@...json.zip`.
5. Set provider to S3 with `POST /api/sync/setSyncProvider` JSON `{"provider":2}`.
6. Use manual sync mode initially. Enable conflict document generation. Enable sync only after config is present.
7. First sync must be download/pull from cloud. Do not push from the fresh/empty workspace until cloud data is visible locally.
8. Verify notebooks and workspace sizes after pull.

## Pitfalls
- Do not print or persist secret keys in logs or final replies. Redact `accessKey`, `secretKey`, and repo key values.
- `listCloudSyncDir` may return S3 `ListBuckets` 403 when the access key is limited to a single bucket. Treat that as a warning, not proof that pull cannot work.
- If `enabled` flips back to `false` and status says “数据同步尚未启用”, the kernel likely has not recognized a logged-in SiYuan account/member entitlement. Ask the user to open `http://127.0.0.1:6806` and log in, then retry enable + pull.
- Do not record transient missing-package failures such as `unzip: command not found`; use Python `zipfile` or install the tool only when needed.
- In WSL, Electron desktop launch can fail with missing `$DISPLAY`; Kernel + Web UI is the default reliable route.
