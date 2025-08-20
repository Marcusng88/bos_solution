## Facebook/Instagram OAuth, Account Linking, Preview Enhancements, and Insights Ingestion – Implementation Plan

### Objectives
- Rename the combined FB/IG UI to separate entries: Facebook and Instagram.
- Trigger a unified OAuth/connect flow so pressing either Facebook or Instagram connect results in writing two rows in `social_media_accounts` when a linked IG Business Account exists: one for `facebook`, one for `instagram`.
- Handle edge cases where only one account connects; visually “shine” only the successful platform and guide users to complete the missing link.
- Persist connections to `social_media_accounts` (already partially implemented) and surface username and profile pictures for Facebook Page and IG Business account.
- Display connected account info under `dashboard -> publishing -> preview`.
- Add an hourly insights ingestion pipeline for Facebook and Instagram, with a new database table, API endpoints, and a scheduler to keep metrics updated.

---

## Current State (Summary)

- Backend (FastAPI):
  - `app/api/v1/endpoints/social_media.py` already supports:
    - `POST /social-media/connect/{platform}` that stores connections in `social_media_accounts` (Facebook path also fetches permissions and persists them; Instagram path looks up IG Business account through Graph API).
    - `GET /social-media/connected-accounts` that returns sanitized account info and persists env-based fallback if needed.
  - `app/core/supabase_client.py` performs CRUD via Supabase REST for `social_media_accounts`, `content_uploads`, `content_templates`.
  - `app/core/auth_utils.py` enforces `X-User-ID` header.

- Database:
  - `social_media_accounts` exists with fields: `user_id`, `platform`, `account_name`, `username`, `profile_picture_url`, `account_id`, `access_token`, `refresh_token`, `token_expires_at`, `is_active`, `is_test_account`, `permissions`, timestamps, and uniqueness constraint `(user_id, platform, account_name)`.

- Frontend:
  - API client (`frontend/lib/api-client.ts`) exposes `connectPlatform(userId, platform)`, `getConnectedAccounts(userId)`, etc.
  - Settings area contains Facebook/Instagram UI; preview area under `dashboard -> publishing -> preview` exists.

---

## Scope of Changes

### 1) UI: Rename FB/IG to Facebook; separate Instagram item
- Update any settings UI that shows “FB/IG” to instead show two separate sections:
  - “Facebook”
  - “Instagram”
- Each section shows its own Connect/Disconnect button and account status indicators.
- On connect click (Facebook or Instagram): call the same backend flow (`POST /social-media/connect/{platform}`) but ensure the backend attempts to persist both Facebook and the linked Instagram Business account in one go when possible.

Implementation notes:
- Files to update (examples; actual names may differ):
  - `frontend/components/settings/connected-accounts.tsx`
  - `frontend/app/dashboard/settings/page.tsx`
  - Any shared connect UI in `frontend/components/settings`.

UI copy and states:
- States per platform: Not Connected, Connecting…, Connected, Error (with details).
- Badges/colors: Gray (not connected), Blue (connecting), Green (connected), Red (error).
- “Shine” effect: only highlight platforms that are actually connected; do not suggest that both are connected unless both writes exist in `social_media_accounts`.

### 2) Unified connect flow with dual writes
- Requirement: whenever user triggers the OAuth/connect for either Facebook or Instagram, attempt to write two rows in `social_media_accounts`:
  - Facebook page account row (platform = `facebook`)
  - Instagram business account row (platform = `instagram`) IF linked to the Facebook Page via Graph API

Backend adjustments:
- `POST /social-media/connect/{platform}` already:
  - Facebook path validates token, fetches `me`, computes permissions, persists the FB account.
  - Instagram path looks up the IG business account via `me/accounts` → `instagram_business_account`, and persists.
- Enhancement:
  - When platform = `facebook`, after saving the FB account, immediately call Graph API to fetch the linked IG Business account. If present, persist the IG account entry too (if not already present), using the same access token. Handle duplicate unique constraint by updating existing row.
  - When platform = `instagram`, perform the same lookup for FB page context as needed. If the IG account is found, also ensure a corresponding FB Page entry is present or created if possible (optional, guarded by permissions).

Edge cases to handle:
- Facebook connected, Instagram not found → return success for FB, and a partial status for IG with guidance.
- Instagram connect attempted but no IG business account linked to any page → return guidance.
- Token present but missing permissions (e.g., `pages_show_list`, `instagram_basic`, `pages_read_engagement`) → show missing permission hints.
- Duplicate records → update instead of insert.

Response contract (proposal):
```json
{
  "success": true,
  "facebook": { "connected": true, "accountId": "...", "accountName": "..." },
  "instagram": { "connected": false, "reason": "No business account linked" }
}
```

### 3) Display connected account info in Publishing → Preview
- Under `dashboard -> publishing -> preview`, fetch and render connected account info using existing endpoint:
  - `GET /social-media/connected-accounts` → returns array with `platform`, `accountId`, `accountName`, `username`, `profilePicture`, `isConnected`.
- Render:
  - Facebook: Page name, page username (if available), page profile picture.
  - Instagram: IG username and profile picture.
- Hide/disable posting controls for platforms that are not connected.

Frontend tasks:
- Update `frontend/components/publishing/post-preview.tsx` (or `frontend/components/publishing/publishing-interface.tsx`) to call `apiClient.getConnectedAccounts(userId)` on mount and display the avatars/usernames inline.

### 4) Guidance UI when FB succeeds but IG fails
- New modal flow for the “Facebook connected, Instagram not connected” scenario:
  - Modal 1: Explain that to connect Instagram, the IG account must be a Business/Creator account linked to the Facebook Page.
  - Modal 2: Steps:
    - In Instagram app: Settings → Account → Switch to Professional → Business.
    - In Facebook Page settings: Link Instagram account to your Page.
    - Re-run connect.
  - Modal 3: Troubleshoot (permissions: ensure `instagram_basic`, `pages_show_list`, `pages_read_engagement` are granted; ensure Page admin access).
  - Provide a “Re-check now” button, which calls `connect/instagram` again and re-queries `connected-accounts` to refresh status.

Frontend tasks:
- Add a reusable modal in `frontend/components/ui/dialog.tsx` or use existing dialog component.
- Wire the modal to the connect results from the backend response contract.

### 5) Persist connections to `social_media_accounts`
- This is already implemented. Verify the following fields are populated on connect:
  - `platform`, `user_id`, `account_id`, `account_name`, `username`, `profile_picture_url`, `access_token`, `is_active`, `permissions`.
- Acceptance criteria: After connect, querying `social_media_accounts` shows both a `facebook` row and (if linked) an `instagram` row for the same user.

---

## Insights Ingestion (Facebook + Instagram)

### Goals
- Pull insights hourly for connected accounts and store time-bucketed metrics for analytics.
- Support queries like “last hour”, “last 24 hours” per platform/account.
- Provide an API to fetch recent insights and aggregates; surface in UI dashboards.

### Facebook Graph API endpoints (examples)
- Page-level insights (Page ID required):
  - `GET /{page-id}/insights` with metrics such as `page_impressions`, `page_engaged_users`, `page_fans`, etc.
  - Use `period` parameter: `day`, `week`, `days_28`, or lifetime (documented by Meta).

### Instagram Graph API endpoints (IG Business account ID required)
- User-level insights: `GET /{ig-user-id}/insights` with metrics `impressions`, `reach`, `profile_views`, `follower_count` (periods: `day`, `week`, `days_28`).
- Media-level insights: `GET /{ig-media-id}/insights` for content analytics (optional for phase 1).

### Proposed database schema

Add a new table to store time-bucketed insights. We will keep raw-ish metrics in JSONB for flexibility and add common aggregates for fast queries.

```sql
-- social_media_insights
CREATE TABLE social_media_insights (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id VARCHAR(255) NOT NULL, -- Clerk user ID
    platform social_media_platform NOT NULL, -- 'facebook' | 'instagram'
    account_id VARCHAR(255) NOT NULL, -- FB Page ID or IG Business User ID
    period VARCHAR(16) NOT NULL, -- 'hour' | 'day'
    window_start TIMESTAMP WITH TIME ZONE NOT NULL,
    window_end   TIMESTAMP WITH TIME ZONE NOT NULL,
    metrics JSONB NOT NULL, -- Raw metrics keyed by metric name
    derived JSONB, -- Optional pre-computed fields
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    CONSTRAINT smi_unique UNIQUE (user_id, platform, account_id, period, window_start)
);

CREATE INDEX idx_smi_user_platform ON social_media_insights(user_id, platform);
CREATE INDEX idx_smi_account_period ON social_media_insights(account_id, period);
CREATE INDEX idx_smi_window_start ON social_media_insights(window_start);

CREATE TRIGGER update_smi_updated_at BEFORE UPDATE ON social_media_insights
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
```

Notes:
- `period='hour'` rows contain last-hour windows; `period='day'` contain day-level windows.
- We store `metrics` JSONB with keys like `impressions`, `reach`, `engagement`, etc.
- Optional `derived` can cache calculated rates (engagement_rate, followers_delta, etc.).

### Ingestion architecture

Option A – In-process scheduler (APScheduler):
- Add APScheduler to FastAPI app startup to run hourly jobs that:
  1) Query `social_media_accounts` for active FB and IG accounts (via Supabase REST).
  2) For each account, fetch insights from Graph API using stored `access_token`.
  3) Upsert an hourly `social_media_insights` row for each account.
- Pros: Simple; Cons: Process-bound and less reliable if horizontally scaled without leader election.

Option B – External scheduler calling an endpoint:
- Add `POST /social-media/insights/sync` that performs the same logic; trigger hourly via external scheduler (GitHub Actions, cron, Vercel Cron, or Supabase Scheduled Functions hitting the endpoint).
- Pros: Works in serverless; Cons: Requires external scheduling.

Recommended: Start with Option B for portability. We can still provide Option A code if you prefer self-managed scheduling.

### Backend additions

New endpoints (in `social_media.py`):
- `POST /social-media/insights/sync` (admin/scheduled): Sync latest hourly insights for all users or a single `user_id` (optional query) and persist.
- `GET /social-media/insights` (user-scoped):
  - Query by `platform`, `period` (`hour` or `day`), `range` (e.g., last 24h, last 7d), returns time series and aggregates.

Pseudocode for sync handler:
```python
# 1) List active accounts
accounts = await supabase_client.get_user_social_accounts(user_id)  # or for all users, iterate by user

# 2) For each account
for acc in accounts:
    if acc["platform"] == "facebook":
        # fetch FB page insights via Graph API using acc["access_token"], acc["account_id"]
        metrics = await fetch_facebook_page_insights(acc)
    elif acc["platform"] == "instagram":
        # fetch IG insights via Graph API using acc["access_token"], acc["account_id"]
        metrics = await fetch_instagram_user_insights(acc)

    # 3) Determine window (hourly): window_start = floor(now to hour)
    # 4) Upsert social_media_insights row with unique key
    await supabase_client.upsert_insights_row({ ... })
```

Graph API examples (hourly collection suggestions):
- Facebook: `/{page-id}/insights?metric=page_impressions,page_engaged_users&since=...&until=...`
- Instagram: `/{ig-user-id}/insights?metric=impressions,reach,profile_views,website_clicks&period=day` (IG supports certain periods; for “hourly”, aggregate ourselves by capturing deltas).

Delta strategy (when hourly metrics aren’t natively provided):
- Store cumulative counts or day metrics and compute deltas between consecutive snapshots for “last hour” derived numbers.
- Keep `derived` JSON with computed deltas and rates for quick read.

### Supabase client additions
- Add methods in `supabase_client.py`:
  - `list_all_social_accounts()` (admin use) or paginated per user.
  - `upsert_insights_row(payload)` to insert or update `social_media_insights`.
  - `get_insights(user_id, platform, period, since, until)` to retrieve for UI.

### Frontend dashboards
- Settings: show last sync time per platform; button “Sync Now” for manual refresh (calls `POST /social-media/insights/sync?user_id=...`).
- Monitoring/Analytics pages: render charts for last hour/24h metrics for each platform.

---

## Detailed Task List

### Backend
- [ ] `social_media.py`: Enhance `connect_platform` (facebook path) to also persist IG Business account if present (dual write). Handle duplicates via update.
- [ ] `social_media.py`: Extend response to include per-platform connection status payload to drive UI modals.
- [ ] Add endpoints:
  - [ ] `POST /social-media/insights/sync` (with `user_id` optional filter, non-interactive flag).
  - [ ] `GET /social-media/insights` (params: `platform`, `period`, `hours` or `days`).
- [ ] `supabase_client.py`: Add `upsert_insights_row`, `get_insights` (and helpers) for `social_media_insights`.
- [ ] Add Graph API helpers for insights:
  - [ ] `fetch_facebook_page_insights(page_id, access_token, window)`
  - [ ] `fetch_instagram_user_insights(ig_user_id, access_token, window)`

### Database
- [ ] Append `social_media_insights` table SQL to `database_schema.sql` (or create migration) per schema above.
- [ ] Ensure indexes/triggers created.

### Frontend
- [ ] Settings UI: rename “FB/IG” to “Facebook”; add separate “Instagram”.
- [ ] Separate Connect buttons; wire both to `apiClient.connectPlatform(userId, 'facebook'|'instagram')`.
- [ ] After connect, parse response and show:
  - [ ] Success highlight for each platform connected.
  - [ ] If FB connected but IG missing, launch multi-step guidance modal.
- [ ] Publishing preview: show connected accounts’ avatar and username, hide controls for unconnected platforms.
- [ ] Insights views: add small cards showing last hour and last 24 hours metrics (after backend endpoints are ready).

### UX Content (Guidance modal)
- Page 1: Why Instagram failed
  - “We found your Facebook Page, but no Instagram Business account is linked.”
  - “To connect Instagram, you must convert your account to a Business account and link it to your Facebook Page.”
- Page 2: How to link
  - “In Instagram: Settings → Account → Switch to Professional → Business.”
  - “In Facebook Page settings: Link your Instagram account to this Page.”
  - “Return here and press Connect again.”
- Page 3: Permissions check
  - “Ensure permissions: instagram_basic, pages_show_list, pages_read_engagement.”
  - Button: “Re-check now” → re-run `connect/instagram` and refresh `connected-accounts`.

---

## API Contracts (Proposed)

### Connect platform (response enhancement)
`POST /api/v1/social-media/connect/{platform}`

Response 200:
```json
{
  "success": true,
  "facebook": {
    "connected": true,
    "accountId": "PAGE_ID",
    "accountName": "My Page",
    "username": "My Page",
    "profilePicture": "https://..."
  },
  "instagram": {
    "connected": false,
    "reason": "No Instagram business account linked"
  }
}
```

### Connected accounts (unchanged)
`GET /api/v1/social-media/connected-accounts`

Response 200:
```json
{
  "accounts": [
    {"platform": "facebook", "accountId": "...", "accountName": "...", "username": "...", "profilePicture": "...", "isConnected": true},
    {"platform": "instagram", "accountId": "...", "accountName": "...", "username": "...", "profilePicture": "...", "isConnected": true}
  ],
  "total": 2
}
```

### Insights sync
`POST /api/v1/social-media/insights/sync?user_id={optional}`

Response 200:
```json
{
  "success": true,
  "synced": {
    "facebook": 1,
    "instagram": 1
  },
  "window": {
    "period": "hour",
    "window_start": "2025-08-20T10:00:00Z",
    "window_end": "2025-08-20T11:00:00Z"
  }
}
```

### Insights read
`GET /api/v1/social-media/insights?platform=facebook&period=hour&hours=24`

Response 200:
```json
{
  "platform": "facebook",
  "period": "hour",
  "series": [
    {"window_start": "...", "metrics": {"impressions": 123, "engaged": 4}},
    {"window_start": "...", "metrics": {"impressions": 98,  "engaged": 6}}
  ],
  "aggregates": {
    "sum_impressions": 221,
    "sum_engaged": 10
  }
}
```

---

## Security & Tokens
- Dev mode may use `FACEBOOK_ACCESS_TOKEN` as a page access token (env). For production, prefer proper OAuth to obtain page-scoped tokens per user session.
- Tokens are persisted only in the backend (`social_media_accounts.access_token`) and are never returned to the client.
- Ensure scopes include: `pages_show_list`, `pages_read_engagement`, `instagram_basic`, and for publishing `pages_manage_posts`, `instagram_content_publish` (future).

---

## Testing Plan

Unit/Integration:
- Connect flow (facebook):
  - Mocks Graph API to return `me`, permissions, and `me/accounts` with IG business account → expect two inserts.
  - Without IG BA → expect FB insert only and response shows IG guidance.
- Connected accounts: ensure returns saved rows without leaking tokens.
- Insights sync: mock Graph API responses and verify rows in `social_media_insights` with correct unique key and window.

E2E manual:
- Click Connect Facebook → FB shows as connected, IG guidance shown if missing.
- After linking IG to Page, press Connect Instagram → both show connected.
- Preview shows avatars/usernames for connected platforms.
- After 1–2 hours, insights charts show last hour and last 24 hours values.

---

## Rollout Steps
1) Backend
   - Implement dual-write in `connect_platform` and enhanced responses.
   - Add insights endpoints and Supabase client helpers.
   - Append `social_media_insights` schema and run migration.
2) Frontend
   - Rename UI labels and split sections.
   - Implement guidance modal.
   - Update preview to show avatars/usernames.
   - Add lightweight insights cards.
3) Configure scheduler
   - External cron hitting `/social-media/insights/sync` hourly (recommended) or integrate APScheduler.
4) QA and iterate.

---

## Acceptance Criteria Checklist
- [ ] UI shows separate Facebook and Instagram sections (no “FB/IG”).
- [ ] Pressing Connect on either platform triggers the same backend logic; Facebook connect attempts IG dual-write when applicable.
- [ ] `social_media_accounts` contains FB row and (if linked) IG row after connect.
- [ ] Preview shows profile picture and username for each connected platform.
- [ ] Partial connection states are correctly highlighted; guidance modal appears when IG is missing.
- [ ] Insights table created; hourly sync populates records; API serves last hour/24h metrics.
- [ ] No tokens are exposed to the client.


