# fid-main Events Data Contract

**Audience:** the events-scraper repo (Railway backend)  
**Purpose:** documents exactly how fid-main *reads* events — the contract the scraper must satisfy  
**fid-main only reads; the scraper owns all writes**

---

## 1. Event Data Source

### API client

`lib/events/client.ts` — all event fetching goes through this module.

**Base URL env var:** `NEXT_PUBLIC_EVENTS_API_URL`  
Example value: `https://wonderful-vibrancy-production.up.railway.app`  
**Auth:** none — all endpoints are public (no Authorization header sent).

### Endpoints consumed

| Endpoint | Called by | Purpose |
|---|---|---|
| `GET /api/events/?{params}` | `listEvents()` | Paginated event list with filters |
| `GET /api/events/{id}` | `getEventById()` | Single event by numeric ID |
| `GET /api/events/cities/list` | `listCities()` | Array of city strings for filter UI |
| `GET /api/events/categories/list` | `listCategories()` | Array of category strings for filter UI and static params |
| `GET /api/featured/active` | `listFeaturedEvents()` | Featured event slots (event detail page only) |

Query params accepted by `GET /api/events/`:

| Param | Type | Default | Notes |
|---|---|---|---|
| `include_past` | `boolean` | `false` | fid-main always passes explicitly |
| `limit` | `number` | `50` | |
| `offset` | `number` | `0` | |
| `city` | `string` | — | Filter by city |
| `category` | `string` | — | Filter by category name (not slug) |
| `price_tier` | `string` | — | Filter by price tier |

fid-main calls `listEvents()` with a client-side published filter on top:

```typescript
const events = await apiFetch<ApiEvent[]>(`/api/events/?${search}`)
return events.filter(e => e.status === 'PUBLISHED').map(toEvent)
```

The scraper should pre-filter to PUBLISHED at the API level; fid-main filters again as a safety net.

### Build-time vs runtime fetching

| Page | Strategy | Prerendered at build | Revalidation |
|---|---|---|---|
| `/events/[slug]/` | ISR | Top 50 upcoming events (`generateStaticParams`) | 600 s |
| `/events/category/[category]/` | ISR | All categories from `/api/events/categories/list` | 600 s |
| `/events/` | SSR/ISR | Nothing prerendered (filter-dependent) | 600 s |
| Homepage sidebar | SSR | Nothing | 600 s |
| Blog post sidebar | ISR per post | At post build time | 3600 s |

`generateStaticParams` in `/events/[slug]/page.tsx` calls `listEvents({ include_past: false, limit: 50, offset: 0 })` at build time. New events beyond the top 50 are served on-demand (ISR) on first request.

---

## 2. The Event Record — Full Field Contract

### TypeScript types

```typescript
// lib/events/types.ts

export type EventStatus = 'PUBLISHED' | 'DRAFT' | 'PENDING' | 'REJECTED';
export type PriceTier   = 'free' | 'paid' | string;

export interface ApiEvent {
  id:           number;
  title:        string;
  description:  string;
  start_at:     string;          // ISO 8601 UTC — see §3
  end_at:       string;          // ISO 8601 UTC — see §3
  venue:        string;
  address:      string;
  city:         string;
  price_tier:   PriceTier;
  price_amount: number | null;
  image_url:    string;
  source_url:   string;
  source_type:  string;
  category:     string;
  fid_hash:     string;
  status:       EventStatus;
  wp_post_id:   number | null;
  created_at:   string;
  updated_at:   string;
}

// Internal to fid-main — ApiEvent + generated slug (never stored in API):
export interface Event extends ApiEvent {
  slug: string;
}
```

> **Note on nullability:** The TypeScript types above declare most string fields as non-nullable, but the Railway API may return `null` for some. fid-main defensively guards the most critical ones (see below). The scraper should treat all non-`| null` fields as MUST provide non-null.

### Field-by-field contract

| Field | Required? | What fid-main does with it |
|---|---|---|
| `id` | **REQUIRED** | Slug generation (`-{id}` suffix); `getEventById(id)`; React `key`. **Breaking if missing or non-integer.** |
| `title` | **REQUIRED** | Displayed as `<h1>` / `<h3>`; slug prefix; schema `name`; fallback description; meta title. **Breaking if missing.** |
| `status` | **REQUIRED** | Filtered: only `'PUBLISHED'` events render. `'DRAFT'` / `'PENDING'` / `'REJECTED'` → 404. |
| `start_at` | **REQUIRED** | Date grouping; time display; `isEventPast()`; schema `startDate`; sidebar badge. Must be valid ISO 8601 UTC. **Breaking if missing or unparseable.** |
| `price_tier` | **REQUIRED in logic** | `'free'` triggers Free badge, "More Info" CTA, offers.price = 0 in schema. Any other value = paid. Never null-checked — send `'free'` or `'paid'`. |
| `end_at` | Optional | Time range display; schema `endDate`. **Graceful fallback: start_at + 2 hours** (see §3). Preferred: always provide correct UTC end time. |
| `venue` | Optional | Displayed in meta row; schema `location.name` (null-guarded — omitted if falsy). Fallback description uses it. Send `""` rather than `null` when unknown. |
| `address` | Optional | Displayed in Maps link; schema `location.address`. `filter(Boolean)` handles empty. |
| `city` | Optional | Displayed on cards/sidebar; schema `location.address.addressLocality`; filter param. `filter(Boolean)` handles empty. |
| `price_amount` | Optional (`number \| null`) | `formatEventPrice`: displayed as `$${amount}` if `> 0`. Schema `offers.price`. Safe to be `null`. |
| `image_url` | Optional | Displayed in `<EventImage>` / `<Image>`; schema `image`. All consumers guard truthiness — fallback to title initial or no image. |
| `source_url` | Optional | CTA button href ("Get Tickets" / "More Info"). Schema `offers.url`. If null: no ticket button; offers may omit url. |
| `description` | Optional | Displayed if `hasMeaningfulDescription()`: length ≥ 15, not a placeholder (`'tbd'`, `'tba'`, `'n/a'`, `'description'`, `'month year'`). HTML is stripped in schema. Falls back to title/venue/city composite. |
| `category` | Optional | Category chip on detail page; related-events fetch; category page routing. Pass-through string — no fixed enum, but see §5 for known values. |
| `source_type` | Optional | Not displayed or used in fid-main. Metadata only. |
| `fid_hash` | Optional | Not used in fid-main. |
| `wp_post_id` | Optional | Not used in fid-main. |
| `created_at` | Optional | Not used in fid-main. |
| `updated_at` | Optional | Not used in fid-main. |

### Slug derivation

```typescript
// lib/events/slug.ts

function slugifyTitle(title: string): string {
  return title
    .toLowerCase()
    .normalize('NFKD')
    .replace(/[̀-ͯ]/g, '')   // strip diacritics
    .replace(/[^a-z0-9\s-]/g, '')      // keep alphanumeric, spaces, hyphens only
    .trim()
    .replace(/\s+/g, '-')              // spaces → hyphens
    .replace(/-+/g, '-')               // collapse consecutive hyphens
    .replace(/^-|-$/g, '')             // strip leading/trailing hyphens
    .slice(0, 80)                      // max 80-char prefix
}

export function buildEventSlug(event: { id: number; title: string }): string {
  return `${slugifyTitle(event.title)}-${event.id}`
}
```

**URL format:** `/events/{slugified-title}-{id}/`  
**Example:** title `"Oktoberfest at Fair Park"`, id `1234` → `/events/oktoberfest-at-fair-park-1234/`

**Parse logic:** `parseEventSlug` splits on the **last** `-` and reads the trailing integer as the ID. The prefix is SEO-only. The scraper just needs `id` (positive integer) and `title` (any non-empty string) — slug generation is handled entirely by fid-main.

**Implication:** if two events have the same title and different IDs they will not conflict. If an event's title changes in the scraper, fid-main will 301-redirect old slugs to the new slug on next fetch (detail page has a redirect guard).

---

## 3. Timezone Contract

This is the section most critical to fix in the scraper.

### What fid-main expects

> **Contract:** `start_at` and `end_at` MUST be true UTC expressed as ISO 8601 with an explicit `Z` suffix.  
> fid-main renders UTC → `America/Chicago` and will faithfully display whatever is stored.  
> **There is no timezone correction in fid-main.** Wrong stored UTC = wrong display.

### Display code (fid-main side — do not change)

```typescript
// app/events/[slug]/page.tsx and app/events/page.tsx
const TZ = 'America/Chicago'

function formatTimeRange(startIso: string, endIso: string): string {
  const opts: Intl.DateTimeFormatOptions = {
    timeZone: TZ,
    hour: 'numeric',
    minute: '2-digit',
    hour12: true,
  }
  const start = new Date(startIso).toLocaleTimeString('en-US', opts)
  const end   = new Date(endIso).toLocaleTimeString('en-US', opts)
  return `${start} – ${end}`
}

// lib/events/format.ts (sidebar + category page)
export function formatEventDateBadge(isoString: string): { day: string; date: string } {
  const d = new Date(isoString)
  const day  = d.toLocaleDateString('en-US', { weekday: 'short', timeZone: TZ }).toUpperCase()
  const date = d.toLocaleDateString('en-US', { day: 'numeric',   timeZone: TZ })
  return { day, date }
}
```

All conversion is `new Date(isoString)` → `Intl.DateTimeFormat` with `timeZone: 'America/Chicago'`. No manual offset arithmetic. No secondary conversion.

### Worked example — the current bug (event 4434)

| Step | Value |
|---|---|
| Correct event time | 10:00 AM CDT (Klyde Warren source page) |
| Correct UTC to store | **15:00Z** (`2026-05-27T15:00:00Z`) |
| Actual stored value | `2026-05-27T10:00:00Z` |
| fid-main renders 10:00Z in America/Chicago | **5:00 AM CT** ← wrong |
| fid-main would render 15:00Z in America/Chicago | **10:00 AM CT** ← correct |

**Root cause (scraper):** the scraper read "10:00 AM" from the Klyde Warren source page as a zone-naive string and constructed the datetime as:

```python
# Python equivalent (dateutil)
date_parser.parse("Wednesday, May 27, 2026 10:00 AM")
# → datetime(2026, 5, 27, 10, 0, 0)  — no tzinfo
# stored as-is → 2026-05-27T10:00:00Z (naive treated as UTC)
```

The CDT offset was never applied — 10:00 AM Dallas time was stored as 10:00 AM UTC.

**Correct scraper pattern (Python):**

```python
# ✅ Parse source time as America/Chicago, convert to UTC
from dateutil import tz as dateutil_tz, parser as date_parser

_DALLAS_TZ = dateutil_tz.gettz('America/Chicago')

def ensure_utc(dt):
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=_DALLAS_TZ)
    return dt.astimezone(dateutil_tz.UTC)

stored = ensure_utc(date_parser.parse("Wednesday, May 27, 2026 10:00 AM"))
# → 2026-05-27T15:00:00+00:00  ✓  (10 AM CDT = 15:00 UTC)
```

Never do: `new Date("2026-05-27T14:00:00").toISOString()` — this treats the time as UTC.

### CST vs CDT offset

| Period | Offset | Notes |
|---|---|---|
| CDT (summer) | UTC−5 | Second Sunday March → first Sunday November |
| CST (winter) | UTC−6 | First Sunday November → second Sunday March |

Use the IANA timezone identifier `'America/Chicago'` (not a fixed offset) so DST is handled automatically.

### `end_at` fallback (fid-main behavior)

```typescript
// lib/events/date.ts
export function getEventEndDate(event: { start_at: string; end_at?: string | null }): Date {
  if (event.end_at) {
    const end = new Date(event.end_at)
    if (!isNaN(end.getTime()) && end.getTime() > 0) return end
  }
  // Fallback: start + 2 hours
  const start = new Date(event.start_at)
  return new Date(start.getTime() + 2 * 60 * 60 * 1000)
}
```

fid-main uses `getEventEndDate` for schema `endDate` and the past-event check. If `end_at` is absent, empty, or not a valid date, fid-main assumes a 2-hour duration. **The scraper should always provide a real UTC end time.** The fallback exists as a safety net, not an intended usage.

---

## 4. Every Place Events Are Rendered

### 4a. Homepage sidebar

**File:** `app/(marketing)/page.tsx` → `EventsSidebar` component  
**Fetch:** `getUpcomingEvents(5)` → `listEvents({ include_past: false, limit: 5, offset: 0 })`  
**Fields consumed:** `id`, `title`, `start_at`, `image_url`, `city`, `price_tier`, `price_amount`, `slug`  
**JSON-LD:** none (homepage emits WebSite + Organization from layout; no event schema)

### 4b. Blog post sidebar

**File:** `app/(marketing)/[slug]/page.tsx` → `EventsSidebar compact`  
**Fetch:** `getUpcomingEvents(4)`  
**Fields consumed:** same as homepage sidebar  
**JSON-LD:** none

### 4c. Events index — `/events/`

**File:** `app/events/page.tsx`  
**Fetch:** `listEvents({ city, category, price_tier, include_past: false, limit: 25, offset })`  
**Fields consumed:** all display fields + `slug` for links

**JSON-LD emitted — `ItemList` wrapping `Event` objects:**

```json
{
  "@context": "https://schema.org",
  "@type": "ItemList",
  "name": "Events in Dallas",
  "url": "https://firstindallas.com/events/",
  "numberOfItems": 24,
  "itemListElement": [
    {
      "@type": "ListItem",
      "position": 1,
      "item": {
        "@type": "Event",
        "name": "← title",
        "startDate": "← start_at (raw string)",
        "endDate": "← getEventEndDate(e).toISOString()",
        "location": {
          "@type": "Place",
          "name": "← venue",
          "address": { "@type": "PostalAddress", "addressLocality": "← city" }
        },
        "url": "https://firstindallas.com/events/{slug}/",
        "image": "← image_url (omitted if falsy)",
        "eventAttendanceMode": "https://schema.org/OfflineEventAttendanceMode",
        "eventStatus": "https://schema.org/EventScheduled"
      }
    }
  ]
}
```

**Schema fields ← event fields:** `name ← title`, `startDate ← start_at`, `endDate ← getEventEndDate`, `location.name ← venue`, `location.address.addressLocality ← city`, `image ← image_url`

### 4d. Event detail — `/events/[slug]/`

**File:** `app/events/[slug]/page.tsx` + `components/events/EventJsonLd.tsx`  
**Fetch:** `getEventById(id)` (id parsed from slug suffix)  
**Fields consumed:** all

**JSON-LD block 1 — `Event` (EventJsonLd component):**

```json
{
  "@context": "https://schema.org",
  "@type": "Event",
  "name": "← title",
  "startDate": "← start_at",
  "endDate": "← getEventEndDate(event).toISOString()",
  "eventStatus": "https://schema.org/EventScheduled",
  "eventAttendanceMode": "https://schema.org/OfflineEventAttendanceMode",
  "location": {
    "@type": "Place",
    "name": "← venue  (omitted if null/empty)",
    "address": "← [address, city].filter(Boolean).join(', ')"
  },
  "description": "← description stripped of HTML, capped 500 chars (fallback: title+venue+city)",
  "url": "https://firstindallas.com/events/{slug}/",
  "organizer": { "@type": "Organization", "name": "First in Dallas", "url": "https://firstindallas.com" },
  "image": ["← image_url"],
  "offers": {
    "@type": "Offer",
    "price": "0 (if free) | price_amount as string (if paid+source_url+price_amount)",
    "priceCurrency": "USD",
    "url": "← source_url (if present)",
    "availability": "https://schema.org/InStock"
  }
}
```

`offers` is only emitted when: `price_tier === 'free'` OR (`source_url` is truthy AND `price_amount != null`).

**JSON-LD block 2 — `BreadcrumbList`:**

```json
{
  "@context": "https://schema.org",
  "@type": "BreadcrumbList",
  "itemListElement": [
    { "@type": "ListItem", "position": 1, "name": "Events", "item": "https://firstindallas.com/events/" },
    { "@type": "ListItem", "position": 2, "name": "← title", "item": "https://firstindallas.com/events/{slug}/" }
  ]
}
```

### 4e. Event category page — `/events/category/[category]/`

**File:** `app/events/category/[category]/page.tsx`  
**Fetch:** `listEvents({ category: categoryName, ... })`  
**Route generation:** `listCategories()` → `slugifyCategory(name)` for static params  
**Fields consumed:** `id`, `title`, `start_at`, `end_at`, `venue`, `city`, `price_tier`, `price_amount`, `image_url`, `slug`

**JSON-LD block 1 — `ItemList` (stub format, capped at 20):**

```json
{
  "@context": "https://schema.org",
  "@type": "ItemList",
  "name": "{categoryName} Events in Dallas",
  "url": "https://firstindallas.com/events/category/{slug}/",
  "numberOfItems": 20,
  "itemListElement": [
    { "@type": "ListItem", "position": 1, "url": "← event URL", "name": "← title" }
  ]
}
```

**JSON-LD block 2 — `BreadcrumbList`:**

```json
{
  "@context": "https://schema.org",
  "@type": "BreadcrumbList",
  "itemListElement": [
    { "@type": "ListItem", "position": 1, "name": "Events", "item": "https://firstindallas.com/events/" },
    { "@type": "ListItem", "position": 2, "name": "← categoryName", "item": "https://firstindallas.com/events/category/{slug}/" }
  ]
}
```

---

## 5. Fields fid-main Needs That the Scraper May Not Provide

### venue — null/empty risk

TypeScript types it as `string` (non-null), but the scraper may omit it for online or location-TBD events.

**fid-main behavior:** venue is null-guarded in EventJsonLd (`...(event.venue ? { name: event.venue } : {})`). The display meta row also guards it. **Send `""` (empty string) rather than `null` when venue is unknown** — avoids a TypeScript mismatch and is handled gracefully.

A null venue means:
- No `location.name` in schema (valid — Google accepts Place without name)
- No venue shown in the detail page meta row
- Fallback description omits the venue clause

### image_url — null/empty

All consumers check truthiness. Safe to send `null` or `""`. Sidebar falls back to a coloured box with the event's first letter.

### description — placeholder risk

`hasMeaningfulDescription()` rejects: `null`, length < 15, or strings matching `'tbd'`, `'tba'`, `'n/a'`, `'description'`, `'month year'`. Scraper should send the real description or omit it entirely (send `""`) — never one of the placeholder strings, as they'll pass the null check but fail the content gate and cause confusing UI.

`description` may be raw HTML — fid-main handles this correctly (strips tags for schema, renders HTML in the article body).

### end_at — missing or zone-naive

If absent or invalid, fid-main falls back to `start_at + 2h`. This is acceptable for short events but wrong for multi-hour events. **Always provide correct UTC end time.**

### price_tier — unknown values

fid-main only treats `'free'` specially. Any other string (including `'paid'`, `'donation'`, `'rsvp-required'`) is displayed via `formatEventPrice` as a capitalized string or price. Safe to pass through — nothing breaks. But schema `offers` will not emit for a paid event unless `source_url` and `price_amount` are also present.

### price_amount — for paid events

If `price_tier !== 'free'` and the scraper knows the ticket price, set `price_amount` as a number. If unknown, send `null`. With `null`, fid-main shows the capitalized `price_tier` string and does not emit schema `offers`.

### category — expected values

fid-main's category handling is **fully dynamic** — it fetches available categories from `/api/events/categories/list` and builds routes from whatever that returns. There is no hardcoded enum in the routing code.

However, `lib/events/category.ts` contains SEO descriptions for these known values. Events with categories outside this list get a generic description. The scraper should normalize to these slugs where the category matches:

| Normalized slug | Meaning |
|---|---|
| `music` | Concerts, performances, festivals |
| `food` | Food/drink events, tastings |
| `sports` | Games, tournaments, fitness events |
| `arts` | Galleries, theater, cultural |
| `comedy` | Stand-up, improv |
| `family` | Kid-friendly, community |
| `nightlife` | Bars, clubs, after-dark |
| `fitness` | Classes, runs, wellness |
| `education` | Workshops, seminars |
| `community` | Neighborhood, volunteer |
| `film` | Screenings, cinema |
| `tech` | Meetups, hackathons, conferences |

Category values are matched case-sensitively in `listEvents({ category: categoryName })` — the display name from the API (e.g. `"Family & Kids"`) must round-trip through `slugifyCategory()` and `unslugifyCategory()`. If the category page route fails to resolve, the page 404s. Consistency between `/api/events/categories/list` and the `category` field on individual events is critical.

### status — visibility gate

Only `'PUBLISHED'` events appear in fid-main. The scraper controls all visibility:
- `'DRAFT'` → not listed, detail page 404s
- `'PENDING'` → same
- `'REJECTED'` → same
- `'PUBLISHED'` → fully visible

---

## Contract Checklist

Use this list to audit the scraper against fid-main's requirements:

**Timestamps**
- [ ] `start_at` is true UTC expressed as ISO 8601 with explicit `Z` suffix (e.g. `"2026-05-27T19:00:00Z"`)
- [ ] `end_at` is true UTC with `Z` suffix, or absent/empty when unknown
- [ ] Source wall-clock times are converted via `America/Chicago` IANA identifier (not a fixed offset)
- [ ] DST transitions handled correctly: CDT (UTC−5) March–November, CST (UTC−6) November–March
- [ ] No zone-naive `new Date("...T10:00:00").toISOString()` calls — always attach offset before calling `.toISOString()`

**Required fields (scraper must always provide non-null)**
- [ ] `id` is a positive integer, unique, stable across updates
- [ ] `title` is a non-empty string
- [ ] `status` is one of `'PUBLISHED'` | `'DRAFT'` | `'PENDING'` | `'REJECTED'`
- [ ] `start_at` is a valid ISO 8601 UTC datetime string

**Optional fields (scraper should provide where known)**
- [ ] `end_at` provided for all events with a known end time
- [ ] `venue` is `""` (not `null`) when the venue is unknown
- [ ] `description` is the real event description — not `"TBD"`, `"N/A"`, or other placeholders
- [ ] `description` ≥ 15 characters if meaningful content exists
- [ ] `image_url` is a direct image URL (not a page URL), or `""` when no image
- [ ] `source_url` is the ticket/RSVP/info URL, or `""` when none
- [ ] `price_tier` is `'free'` for free events; `'paid'` or descriptive string for paid
- [ ] `price_amount` is a positive number when the ticket price is known

**Category**
- [ ] `category` values are consistent between `/api/events/categories/list` and individual event records
- [ ] Category slugs normalize to one of the 12 known values where applicable (`music`, `food`, `sports`, `arts`, `comedy`, `family`, `nightlife`, `fitness`, `education`, `community`, `film`, `tech`)
- [ ] No category string contains characters that would produce an empty slug after `slugifyCategory()`

**Visibility**
- [ ] Only events ready to be shown publicly have `status: 'PUBLISHED'`
- [ ] Past events that should be de-indexed have `status` set to `'DRAFT'` or left as `'PUBLISHED'` (fid-main sets `robots: noindex` on past event detail pages automatically via `isEventPast()`)

**Slug compatibility**
- [ ] `id` is a positive integer (the trailing `-{id}` in the URL slug must parse as `parseInt(id, 10) > 0`)
- [ ] `id` is stable — changing an event's ID breaks existing URLs and cached static pages
- [ ] `title` changes are safe (fid-main 301-redirects old slug → new slug on next ISR)
