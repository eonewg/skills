# Lark CLI calendar reminders

Use this when the user asks for a reminder / 提醒 and indicates it should be on Feishu, or when he corrects a cron/chat reminder to “用飞书日程”.

## Preference

For the user, reminder-like requests should default to Feishu Calendar events, not cron jobs, unless he explicitly asks for a chat-only reminder or exact scheduler behavior. If a cron reminder was already created and the user says to use Feishu Calendar instead, remove the cron job first, then create the calendar event.

## Workflow

1. Check current Asia/Shanghai time before resolving relative time:

```bash
TZ=Asia/Shanghai date '+%Y-%m-%d %H:%M:%S %Z %z'
```

2. Resolve the requested time to an explicit timestamp. For short reminders, create a 5-minute event and set `reminders: [{"minutes": 0}]` so Feishu reminds at the start time.

3. Create the event on the primary calendar. Example:

```bash
START=$(TZ=Asia/Shanghai date -d '2026-05-17 14:55:00' +%s)
END=$(TZ=Asia/Shanghai date -d '2026-05-17 15:00:00' +%s)
lark-cli calendar events create \
  --params '{"calendar_id":"primary"}' \
  --data "{\"summary\":\"抢瑞幸\",\"description\":\"提醒：抢瑞幸\",\"start_time\":{\"timestamp\":\"$START\",\"timezone\":\"Asia/Shanghai\"},\"end_time\":{\"timestamp\":\"$END\",\"timezone\":\"Asia/Shanghai\"},\"reminders\":[{\"minutes\":0}],\"free_busy_status\":\"free\",\"visibility\":\"private\"}" \
  --format json
```

4. Verify by reading the event back. Use the returned `organizer_calendar_id` and `event_id`:

```bash
lark-cli calendar events get \
  --params '{"calendar_id":"<organizer_calendar_id>","event_id":"<event_id>"}' \
  --format json
```

For this CLI/API shape, create/get/patch responses may nest the actual event under `data.event`, not directly under `data`. If extracting IDs programmatically, read `data.event.organizer_calendar_id` and `data.event.event_id`; otherwise a parser can incorrectly produce `None` even though creation succeeded.

### Reschedule an existing reminder event

When the user asks to move an existing Feishu Calendar reminder (e.g. “把这个日程挪到明天中午十一点半”), do not delete/recreate if you already know the original `organizer_calendar_id` and `event_id`. Patch the existing event, then read it back:

```bash
START=$(TZ=Asia/Shanghai date -d '2026-06-10 11:30:00' +%s)
END=$(TZ=Asia/Shanghai date -d '2026-06-10 11:35:00' +%s)
lark-cli calendar events patch \
  --params '{"calendar_id":"<organizer_calendar_id>","event_id":"<event_id>"}' \
  --data "{\"start_time\":{\"timestamp\":\"$START\",\"timezone\":\"Asia/Shanghai\"},\"end_time\":{\"timestamp\":\"$END\",\"timezone\":\"Asia/Shanghai\"},\"reminders\":[{\"minutes\":0}],\"free_busy_status\":\"free\",\"visibility\":\"private\"}" \
  --format json
lark-cli calendar events get \
  --params '{"calendar_id":"<organizer_calendar_id>","event_id":"<event_id>"}' \
  --format json
```

5. Reply with the title, explicit date/time, reminder timing, and whether it is private/free-busy. Keep it short.

## Deleting events

When the user asks to delete calendar events by keyword (e.g. "把腰的日程都删了"):

1. Search for matching events using `search_event` with a keyword query. Feishu searches summary AND description:

```bash
lark-cli calendar events search_event \
  --params '{"calendar_id":"primary"}' \
  --data '{"query":"腰","page_size":100}' \
  --format json
```

2. Extract instance event_ids. Recurring events produce individual instances with `_timestamp` suffixes (e.g. `80cab3c8-..._1781530200`). The base event_id without `_timestamp` is NOT a valid delete target — you MUST delete each instance individually.

3. Collect all instance event_ids from the search results. Check for pagination via `has_more` — if true, re-search with the returned `page_token`:

```bash
lark-cli calendar events search_event \
  --params '{"calendar_id":"primary"}' \
  --data '{"query":"腰","page_size":100,"page_token":"<token>"}' \
  --format json
```

4. Delete each instance. There is no bulk-delete API, so iterate in a shell loop:

```bash
for eid in <instance_id_1> <instance_id_2> ...; do
  lark-cli calendar events delete \
    --params '{"calendar_id":"<organizer_calendar_id>","event_id":"'$eid'"}' \
    --format json
done
```

5. Verify by re-running the search with the same query and confirming zero results (or fewer results). Search may return cached results — re-run to confirm.

### Pitfalls for deletion

- The base event_id (without `_timestamp` suffix) is **not** a valid delete target for instances of recurring events. Delete each `_timestamp`-suffixed instance individually.
- Multiple recurring event series may match the same keyword — each belongs to a different base event_id and must be collected separately.
- Pagination: if `has_more` is `true`, you must re-request with the `page_token` to get remaining instances. A single search call may only return a subset.
- After deletion, search results may briefly show stale cached data — re-run the query to get current state.

## Pitfalls

- Do not leave duplicate reminders in both cron and Feishu after the user corrects the destination.
- Do not use Feishu Tasks for pure time reminders; use Calendar events.
- Set `free_busy_status: free` for lightweight personal reminders so they do not block the calendar.
- Use `visibility: private` for personal errands by default.
- A Feishu Calendar create response may return a numeric `calendarId` in `app_link` but `events get` should use the returned `organizer_calendar_id`.