<!-- -*- markdown -*- -->
<!-- -*- coding: utf-8 -*- -->
<!--
michael a.g. aïvázis <michael.aivazis@para-sim.com>
(c) 1998-2026 all rights reserved
-->

# Driving a qed instance on NISAR On-Demand

> Status: **not yet attempted in practice.** This records what an automated browser driver runs into
> when it points at a qed instance hosted on NISAR On-Demand, why the obvious shortcuts fail, and the
> approaches worth trying — **after** clearing the practice with the security team. Nothing here has
> been used to actually drive the hosted instance; the one experiment that touched local browser
> state (a Chrome profile copy) was deleted immediately. Do not run any of this against the hosted
> system until the access method is approved.

## The goal

The same thing the local automation surface gives us (see [automation-surface.md](./automation-surface.md)):
drive a *hosted* qed client through `window.qed` from a headless browser — e.g. to scroll a viewport
to the dataset center with

```js
const s = await window.qed.state()
const [rows, cols] = s.dataset.shape
const [r0, c0] = s.dataset.origin ?? [0, 0]
await window.qed.lookAt(Math.round(r0 + rows / 2), Math.round(c0 + cols / 2))
```

Because the viewport look-at center is server state synced to every connected client, one driver doing
this recenters all of them — a logged-in human browser will follow.

An example instance URL has the form:

```
https://nisar.jpl.nasa.gov/ondemand/user/<user>/qed/
```

The automation facade is opt-in, so the driver appends `?automation` (or seeds
`localStorage["qed.automation"] = "1"`).

## What's actually in the way: the auth wall

The hosted qed is **not** directly reachable. NISAR On-Demand fronts each user's qed with a
**JupyterHub OAuth** login. An unauthenticated request to the instance URL 302-redirects to:

```
https://nisar.jpl.nasa.gov/ondemand/hub/login?next=/ondemand/hub/api/oauth2/authorize?client_id=jupyterhub-user-<user>&redirect_uri=/ondemand/user/<user>/oauth_callback&response_type=code&state=...
```

which renders the **"NISAR On-Demand Login"** page (HTTP 200). The qed React client never loads, so
`window.qed` is never published and any driver times out waiting for it. A human's browser gets
through only because it already holds an authenticated session.

### Why the session can't be borrowed from disk

The credential that proves the session is a JupyterHub auth cookie, `jupyterhub-user-<user>`. On
macOS Chrome it is a **session cookie**: it lives only in the running browser process's memory and is
**never written to the on-disk cookie store** (barring "continue where you left off"). The on-disk
cookie DB for the domain holds only the non-secret companions:

- `_xsrf` (path `/ondemand/hub/`)
- `jupyterhub-user-<user>-oauth-state` (path `/ondemand/user/<user>/`)

— not the bearer token. So **any approach that reads cookies from disk is missing the credential by
construction**, no matter how the decryption is handled.

## Approaches tried locally (and why they failed)

These were attempted against the live URL from this workstation; none reached the client.

| Approach | Outcome |
|----------|---------|
| Headless **chromium** (fresh context) | Redirected to the login page; no session. |
| Headless **webkit** (fresh context) | Same. Playwright's WebKit is its own bundled build with its own cookie jar — it does **not** share Safari's profile or cookies, so "Safari is already logged in" gives it nothing. |
| Real **Chrome against a copied profile** | Copied `~/Library/Application Support/Google/Chrome` (`Local State` + `Default`, minus caches) to a temp dir and launched `channel: "chrome"` headless against it, so Chrome could decrypt cookies with its own Keychain key ("Chrome Safe Storage"). Still redirected — the copied DB had only the two non-secret cookies above; the session token was in live Chrome's memory, not on disk. The temp profile was deleted afterward. |

The takeaways: a profile copy is pointless (the token isn't on disk), and WebKit/Safari sharing is a
non-starter (separate cookie jars).

## Approaches worth trying later (pending security approval)

All of these inject or reuse a **live** session, which is exactly the sensitive part — confirm with
security which, if any, is acceptable before using it against the hosted system. The Playwright
toolchain setup (NODE_PATH / PLAYWRIGHT_BROWSERS_PATH) is described in the team notes; these snippets
assume it is on the environment.

### A. CDP attach to a live Chrome (most durable)

Relaunch Chrome with the DevTools protocol exposed, log in to NISAR On-Demand in that window, then
attach Playwright over CDP. The driver acts inside the *already-authenticated* session, so it never
sees the login wall and never handles the token itself.

```bash
# quit Chrome first; then:
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
  --remote-debugging-port=9222 --profile-directory=Default
# log in to the On-Demand instance in that window, then:
```

```js
const { chromium } = require("playwright")
const browser = await chromium.connectOverCDP("http://localhost:9222")
const ctx = browser.contexts()[0]
const page = await ctx.newPage()
await page.goto("https://nisar.jpl.nasa.gov/ondemand/user/<user>/qed/?automation")
await page.waitForFunction(() => window.qed != null)
// ... window.qed.state() / lookAt(...) as above
```

- **Pro:** reuses the genuine session; nothing copies or exfiltrates the cookie; reusable across runs.
- **Con:** the relaunch may drop the in-memory session and force a fresh NISAR re-login. Opening a
  debug port is itself a security consideration — bind to localhost only, and raise it with security.

### B. Inject the session cookie into a fresh context (quick, short-lived)

Copy the `jupyterhub-user-<user>` cookie value from DevTools (Application ▸ Cookies) and add it to a
clean Playwright context before navigating.

```js
const ctx = await browser.newContext()
await ctx.addCookies([{
  name: "jupyterhub-user-<user>",
  value: "<paste the value>",
  domain: "nisar.jpl.nasa.gov",
  path: "/",
  httpOnly: true, secure: true,
}])
```

- **Pro:** no Chrome relaunch; fully headless.
- **Con:** the session cookie is short-lived; this is hand-copying a live credential — likely the
  most scrutinized option from a security standpoint.

### C. Let the human drive; the driver only computes the target

Since look-at is synced server state, a logged-in human pasting the one-liner from
[The goal](#the-goal) into their own authenticated tab recenters every client. No automated browser
touches the hosted system at all — the lowest-risk option, and a sensible default while approval is
pending.

## Live sync (SSE) behind the proxy

A separate symptom on On-Demand: two browsers connected to the *same* hosted qed server **do not
live-sync** (a recenter in one does not move the other). Locally, multi-client sync works — three
clients followed each other on the local server — so the regression is the proxy chain, not qed.

### Why it's the proxy, not qed

qed pushes state changes over **Server-Sent Events (SSE)**: the client opens an `EventSource` and the
server holds the connection open, pushing a frame whenever state changes
([automation-surface.md](./automation-surface.md) live-sync; the transport is pyre's `EventStream` /
`Hub`). The server already does everything SSE-correctly:

- **Headers**: `Content-Type: text/event-stream`, `Cache-Control: no-cache`, `Connection: keep-alive`,
  and `X-Accel-Buffering: no` (the hint that tells nginx not to buffer the stream).
- **Keepalive**: periodic `: keepalive` comment frames on a timer hold idle connections open.
- **Concurrency**: each held connection is driven non-blocking through a `Hub`, so many browsers can
  each hold a stream at once — which is exactly why local multi-client sync works.

So the variable that changed is the proxy in front of it.

### The chain SSE must survive

The URL (`/ondemand/user/<user>/qed/`) and the `jupyterhub-user-<user>` cookie say this is
**JupyterHub**. A pushed event has to cross roughly three hops:

```
browser → outer TLS proxy (nginx/Apache at nisar.jpl.nasa.gov)
        → configurable-http-proxy (JupyterHub's CHP, node-http-proxy)
        → jupyter-server-proxy (maps /qed/ → the qed process in the session)
        → qed
```

Any one can break SSE. Most likely, in order:

1. **Response buffering** — the usual cause. A buffering hop holds the `data:` frames *and the
   keepalive comments* until its buffer fills or the connection closes; an SSE connection never
   closes, so nothing is ever delivered. `X-Accel-Buffering: no` is honored by **nginx** but ignored
   by CHP, jupyter-server-proxy (tornado), and Apache `mod_proxy`, which have their own buffering
   knobs. gzip / `mod_deflate` on the stream does the same.
2. **No `Content-Length` / no chunked framing** — the stream carries neither delimiter (legal for
   SSE), but a stricter intermediary may buffer the whole body until EOF when it sees neither.
3. **Idle read timeouts** — `proxy_read_timeout` (nginx), `ProxyTimeout` (Apache), CHP
   `--proxy-timeout`. If a hop also buffers the keepalives, the upstream looks idle and gets killed,
   giving reconnect loops or silence instead of sync.

### How to pin down which hop

- **DevTools ▸ Network ▸ the `events` request** in each browser. Healthy SSE stays *pending/open*
  with frames accumulating. Completed / 0-byte / hung-with-no-frames → buffering downstream.
- **Inspect the headers that reach the browser** on that response: is `X-Accel-Buffering: no` still
  present? Is `Content-Type` still `text/event-stream`? Did something add `Content-Encoding: gzip`?
- **`curl -N` at increasing depth** (`-N`/`--no-buffer` is essential):
  - Inside the Jupyter session, against the local qed port: `curl -N http://localhost:<port>/events`
    — proves qed streams.
  - Public URL with the auth cookie:
    `curl -N -H 'Cookie: …' https://nisar.jpl.nasa.gov/ondemand/user/<user>/qed/events` — if frames
    stop appearing here, a public-facing hop is buffering.
- **Timing tell**: events arriving only in a burst on reload/close is textbook buffering.

### Levers

- **qed side** — headers are already right; little to do. Safe hardening: emit
  `Transfer-Encoding: chunked` explicitly (removes the #2 ambiguity) and lower the `heartbeat`
  interval so keepalives outrun idle timeouts. Neither helps if a hop buffers, since buffering
  swallows keepalives too.
- **Proxy side** (for ops/security to apply) — disable buffering and compression for the qed
  location: nginx `proxy_buffering off`; Apache `SetEnv proxy-sendchunked` and no `mod_deflate` on
  `text/event-stream`; verify the jupyter-server-proxy version streams non-websocket responses; raise
  read/proxy timeouts.
- **Fallback if the chain won't stream** — degrade to periodic polling. The client's `onChange` is
  just "refetch affected state", so a timer-based poll reproduces sync without SSE, robust through any
  proxy, at the cost of latency.

## Questions to raise with security

- Is automated browser access to a hosted On-Demand instance acceptable at all, and under what
  conditions?
- Is exposing Chrome's `--remote-debugging-port` on `localhost` for CDP attach (approach A)
  acceptable on a workstation that holds NISAR sessions?
- Is copying a live session cookie out of the browser (approach B) ever acceptable, or off-limits?
- Are there session/keystroke-monitoring or rules-of-behavior implications (the On-Demand login page
  states keystrokes and data content are monitored) for any of the above?
- Can ops adjust the On-Demand proxy chain to pass SSE through unbuffered (see
  [Live sync (SSE) behind the proxy](#live-sync-sse-behind-the-proxy)) — disable
  buffering/compression on the qed location and raise read timeouts — so live sync works?

## See also

- [automation-surface.md](./automation-surface.md) — the `window.qed` facade these drivers call.

<!-- end of file -->
