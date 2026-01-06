# 🚀 Step-by-Step pSEO Implementation Plan

This guide outlines how to implement Programmatic SEO (pSEO) using your Gutenberg pattern **without breaking your current setup**.

**Core Concept:** We will continue to use the current "Directory Page" as the main hub, but we will *additionally* generate individual WordPress Posts for each event to capture long-tail search traffic.

---

## ✅ Phase 1: Preparation (Safe Mode)

**Goal:** Ensure the foundation is ready without touching any live code.

1.  **Preserve Current Setup:**
    *   Do NOT change your existing `/events` page.
    *   Do NOT deactivate the current plugin.
    *   The "Directory" will continue to work exactly as it does now.

2.  **WordPress Setup:**
    *   Go to your WordPress Admin.
    *   Create a new **Category** for posts called `Events` (Slug: `events-listing`).
    *   This keeps your programmatic posts separate from your regular blog posts.

---

## 🎨 Phase 2: Template Extraction

**Goal:** Get the raw code for your beautiful Gutenberg design.

1.  **Design Your Master Template:**
    *   In WordPress, go to **Posts → Add New**.
    *   Build the *perfect* event page using your blocks (Image, Title, Description, "Get Tickets" button).
    *   **Crucial:** Use dummy text for now (e.g., `{{EVENT_TITLE}}`, `{{EVENT_IMAGE}}`, `{{EVENT_DATE}}`).

2.  **Extract the Code:**
    *   Click the **three dots (⋮)** in the top-right corner of the editor.
    *   Select **Code editor** (or press `Ctrl+Shift+Alt+M`).
    *   **Copy everything.** It will look like HTML with comments (e.g., `<!-- wp:columns -->...`).
    *   Save this code in a text file on your desktop for Phase 3.

---

## ⚙️ Phase 3: Backend Integration

**Goal:** Teach the API to use your new template.

1.  **Create Template File:**
    *   We will create a new file `api/templates/wordpress_event.html` in your project.
    *   We will paste your Gutenberg code into this file.

2.  **Modify Python Logic:**
    *   I will modify `api/utils/wordpress.py`.
    *   Instead of using the hardcoded HTML (as it does now), it will read from `api/templates/wordpress_event.html`.
    *   It will replace the placeholders (`{{EVENT_TITLE}}`, etc.) with real data from the database.

---

## 🔄 Phase 4: Sync & Automation

**Goal:** Automatically create the posts.

1.  **Test with ONE Event:**
    *   We will create a test script `test_pseo_single.py`.
    *   It will pick *one* event and publish it to WordPress using the new template.
    *   You will verify it looks perfect in WordPress.

2.  **Bulk Sync Script:**
    *   We will create `sync_all_to_wordpress.py`.
    *   This script will:
        *   Loop through all "PUBLISHED" events.
        *   Check if they already exist in WordPress (to avoid duplicates).
        *   Create the post if it's missing.

---

## 🔗 Phase 5: The "Hybrid" Link (Final Polish)

**Goal:** Connect the Directory to the SEO Pages.

1.  **Update Plugin (Optional but Recommended):**
    *   Currently, your Directory "View Details" button goes to Ticketmaster/Eventbrite.
    *   **Change:** Update the plugin to link to your *new internal WordPress Post* instead.
    *   **Result:** User clicks "View Details" -> Goes to `your-site.com/event/awesome-concert` -> Then clicks "Buy Tickets" to go to Ticketmaster.
    *   **Benefit:** This keeps users on your site longer (Dwell Time) and signals to Google that your pages are valuable.

---

## 🛡️ Risk Assessment

| Action | Risk Level | Impact on Current Site |
| :--- | :--- | :--- |
| Creating `Events` Category | 🟢 None | Invisible to users until we publish. |
| Creating Template File | 🟢 None | Just a text file in the backend. |
| Publishing 1 Test Post | 🟢 None | Just one new post appears. |
| Bulk Syncing Events | 🟡 Low | You will have many new posts. If they look bad, we can bulk delete them in seconds. |
| Updating Plugin Links | 🟡 Low | Changes navigation flow. Reversible by reinstalling old plugin version. |

## 🚀 Ready to Start?

If you approve this plan, our **first step** is for you to:
1.  **Design that block** in WordPress.
2.  **Copy the code** from the Code Editor.
3.  **Paste it here** so I can set up the template file.
