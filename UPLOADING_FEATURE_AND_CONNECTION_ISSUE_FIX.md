### Uploading feature and connection issue fix

#### Problem
- Connections to Facebook/Instagram appear "lost" after navigation/refresh because the app kept connection state in frontend memory only.
- Using the FB JS SDK causes HTTPS and global access token side-effects; we should post via backend using per-request tokens.

#### Goal
- Persist FB/IG connections per user in our database, hydrate UI on load, and post via backend without exposing tokens to the frontend.

---

### Proposed architecture
- **Persistence**: Store connection records in `social_media_accounts` (already added) keyed by `user_id` + `platform`.
- **Backend-only tokens**: Access/refresh tokens live in DB (encrypted at rest by Supabase + optional app-level encryption) and are never returned to the browser.
- **Per-request token usage**: Backend passes `access_token` as a query/body param to Graph APIs; never sets any global token in SDKs.
- **Hydration on mount**: Frontend requests `GET /social-media/connected-accounts` on page load and renders real username + profile picture; Zustand/React state is only a cache, not the source of truth.
- **Fallback**: If no per-user record exists but an env `FACEBOOK_ACCESS_TOKEN` is configured, backend exposes a read-only "env-sourced" account so UI still shows as connected.

---

### Data model (already present, add fields if missing)
- `social_media_accounts`
  - `id` (uuid)
  - `user_id` (uuid)
  - `platform` (enum: facebook, instagram, ...)
  - `account_id` (text) — FB Page ID or IG Business ID
  - `account_name` (text)
  - `username` (text)
  - `profile_picture_url` (text)
  - `access_token` (text) — stored server-side only; never sent to client
  - `refresh_token` (text, nullable)
  - `scopes` (text[])
  - `expires_at` (timestamptz, nullable)
  - `is_active` (bool, default true)
  - `created_at`, `updated_at`

Notes:
- If we prefer, encrypt `access_token` with an app-managed key before storing.
- Add RLS policies to ensure users can only read their own rows; backend uses service key.

---

### Backend API
- `POST /social-media/accounts` — save or update a connection (after OAuth or manual token). Body: platform, account_id, account_name, username, profile_picture_url, access_token, refresh_token, scopes, expires_at.
- `GET /social-media/connected-accounts` — returns a sanitized list: platform, accountId, accountName, username, profilePicture, isConnected. No tokens.
- `GET /social-media/account-info/{platform}` — pulls real name + avatar from Graph API using the stored/env token; returns sanitized info only.
- `DELETE /social-media/accounts/{id}` — deactivate/remove a connection.
- Posting endpoints (`/uploads`, `/uploads/{id}/post`) already call provider APIs with the token passed per request.

Security:
- Authenticate with Clerk; pass `X-User-ID` header; validate ownership on all mutating routes.
- Never return tokens to the browser. Use them only inside backend calls to Meta/LinkedIn/Twitter/etc.

---

### Frontend flow
- On settings and uploader mount:
  1. Call `GET /social-media/connected-accounts`.
  2. Populate a global store (Zustand) for cross-page persistence.
  3. Render real `username` + `profilePicture` in UI and previews.
- On connect/disconnect:
  - Submit to backend; on success, refresh the connected accounts list.

Why this persists:
- State is sourced from DB via backend each time, not only from ephemeral component state.

---

### Migration plan
1. Ensure `social_media_accounts` has fields listed above; add columns if missing via migration.
2. Implement/verify endpoints listed under Backend API (most exist; adjust to return sanitized data only).
3. Replace FB SDK usage on the frontend with backend-driven state.
4. In settings/uploader pages, hydrate from `GET /social-media/connected-accounts` and cache in Zustand.
5. Add RLS and test with multiple users.

---

### Testing plan
- Unit: Validate serializers and per-request token calls (no global token set). 
- Integration: 
  - Save a connection, navigate across pages, reload — UI remains connected.
  - Verify that tokens never appear in network responses.
  - Post a test item via backend with token passed in request params; confirm success or clear error.
- Manual: Try HTTPS locally (Next.js dev https or proxy) to avoid SDK warnings if any SDK remains.

---

### Rollout & fallback
- If a user's row is missing, but env `FACEBOOK_ACCESS_TOKEN` exists, backend returns an env-based connected account (read-only). This preserves current behavior while we migrate users to per-user connections.

---

### Summary of benefits
- Connection state persists across navigation and refresh.
- Tokens remain server-side and are used per request only.
- Real account data (name/avatar) shown reliably.
- No FB SDK HTTPS or global token pitfalls.


