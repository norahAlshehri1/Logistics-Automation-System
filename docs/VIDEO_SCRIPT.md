# LogiFlow — Demo Video Script

**Target length:** ~6 minutes
**Audience:** Supervisor (Dr. Linah) + graduation panel
**Tone:** Confident, clear, focused on the proposal's KPI targets

---

## Before you hit record

| Setup item | Action |
|---|---|
| Backend | `cd Gproject && python seed_data.py && uvicorn main:app --reload` |
| Frontend | `cd frontend && npm run dev` |
| Browser | Chrome / Edge, full screen, zoom 100 %, dev tools closed |
| Pre-staged tab | `http://localhost:5173/login` on the LogiFlow Sign-In screen |
| Have ready | One unseeded PDF invoice on the desktop (any of the `test_invoices/*.pdf` that wasn't used by the seeder — e.g. duplicate one) |
| Theme | Start in **light mode** (you'll flip to dark mode near the end as a wow moment) |

---

## SECTION 1 — The problem (0:00 – 0:30)

**On screen:** Title slide or the Login page

> "In B2B logistics, operations staff spend hours every day manually copying data from invoices, packing lists, and bills of lading into internal systems. That manual work creates three problems: it's slow, it produces errors, and it leaves no audit trail."

> "Our project — **LogiFlow** — automates that whole pipeline. A user uploads a logistics document, our extraction engine reads it, the user reviews the extracted data on screen, approves it, and exports a standardized output. Every change is logged for compliance."

> "Today I'll show you the full end-to-end workflow."

---

## SECTION 2 — Sign in & Dashboard tour (0:30 – 1:30)

**Stage:** Login page is already open.

**Action:** Type `linah` in the username field, `supervisor123` in password, hit **Sign In**.

> "I'm logging in as Dr. Linah, who has the admin role. You'll see a toast pop-up confirms the sign-in, and we land on the administrator dashboard."

**Action:** Pause on the Dashboard. Move the cursor to the top row of KPI cards.

> "The top row of cards gives the operational counters — 10 total cases, 8 documents uploaded, 5 pending or in-review, and 4 already approved."

**Action:** Hover over the second row of KPI cards.

> "The second row tracks the three primary KPIs we committed to in the project proposal:
> - **Average processing time per case** — 12.6 minutes, compared to a manual baseline of 22 minutes. That's a **42 % reduction**, well above our 35 % target.
> - **Corrections per case** — 0.4. That's a **47 % drop** versus the manual baseline of 3 corrections per case, beating the 40 % target.
> - **Completeness rate** — 94 % of documents have all four critical fields present on the first read — a 24-percentage-point gain over the 70 % baseline."

**Action:** Scroll down to the bar chart.

> "This bar chart compares our achieved performance — in indigo — against the proposal targets. All three KPIs exceed their target."

**Action:** Hover over the doughnut chart on the right.

> "On the right we have the status distribution: 4 approved, 2 in review, 3 pending, 1 closed."

---

## SECTION 3 — Create a case & upload a PDF (1:30 – 2:30)

**Action:** Click the **Cases** link in the navbar.

> "Let me show the case management workflow. We have 10 cases already — searchable, filterable by status."

**Action:** Type "Aramex" in the search box, pause for the debounced filter to kick in (300 ms), then clear it.

> "The search is debounced so it filters smoothly as I type. We can also filter by status using this dropdown."

**Action:** Click the **+ New Case** button. The modal animates in.

**Action:** Fill in:
- Customer: `Bahri Logistics — Riyadh Branch`
- Service Type: `Sea Freight`

**Action:** Click **Create Case**. Toast confirms creation.

> "I just created a new shipment case. Now I'll click into it to upload the actual invoice."

**Action:** Find the newly-created case at the top of the list, click **View**.

**Action:** On the Case Detail page, click the file picker, choose a PDF from your desktop, click **Upload PDF**.

> "I'm uploading a commercial invoice. The backend validates the PDF — it checks the magic bytes to confirm it really is a PDF, and enforces a 5 megabyte size limit."

**Action:** Toast appears: "Uploaded invoice.pdf". The document appears in the Documents table.

---

## SECTION 4 — The heart of the system: extract, review, approve (2:30 – 4:00)

**Action:** Click **Review →** on the document row.

> "This is where the magic happens. The system has already loaded the original PDF on the left — that's served securely behind authentication, not a public file link."

**Action:** Click **⚡ Extract Data**.

> "I'm hitting Extract Data. Our extraction engine runs `pdfplumber` for digital PDFs and falls back to Tesseract OCR for scanned ones, with both English and Arabic language packs."

**Action:** Wait ~2 seconds. Fields populate. Toast says either "Extraction completed cleanly" or "Review needed for: …"

> "Look at the right pane — every extracted field comes with a per-field confidence badge: High in green, Medium in amber, Low or Missing in red. This is the human-in-the-loop pattern from our proposal — the system flags exactly what needs attention."

**Action:** Click into the Vendor Name field, edit it slightly (e.g., add ", Riyadh Branch" at the end).

> "If something is wrong, I just edit it directly. Every change I make here is going to be captured in the audit log."

**Action:** Click **Approve & Save Final Data**. The button transforms into the green "Approved" banner. Toast: "Approved & saved".

> "The data is now saved as the final approved value, with my user ID and timestamp attached."

---

## SECTION 5 — Audit trail & export (4:00 – 4:45)

**Action:** Click **← Back to Case #N** at the bottom of the form.

> "Back on the case detail page, I'll switch to the Audit Trail tab."

**Action:** Click the **Audit Trail** tab on the lower card.

> "Every field correction across this case is timestamped, showing the old value crossed out and the new value in green. This satisfies the compliance and traceability requirement from Section 5.2 of our proposal."

**Action:** Scroll up to the Export Case card, click **📊 Export to Excel**.

> "Operations staff need to push approved data into downstream systems. We support two output formats — Excel and PDF."

**Action:** Browser downloads the file. Open it briefly to show the three sheets — Case Summary, Approved Fields, Audit Trail.

> "The Excel export ships with three sheets — case summary, all approved fields, and a complete audit trail. We also offer a PDF version, formatted as an A4 case report."

**Action:** Close the Excel file. Click **📄 Export to PDF**. Open it briefly to show the formatted report.

---

## SECTION 6 — Search & retrieval (4:45 – 5:15)

**Action:** Navigate back to **Cases**.

> "User Story 5 from our proposal calls for searching past cases. I can search by customer name, case ID, or invoice number — all hitting our search endpoint on the backend."

**Action:** Type `INV-2026-9001` in the search bar.

> "Notice that this matched on the *extracted invoice number*, not just the customer field. The search joins through the extracted fields table."

**Action:** Clear search. Change the status dropdown to **Approved** to filter.

> "And we can narrow by status — here are just the approved cases, ready for downstream consumption."

---

## SECTION 7 — Security: role-based access control (5:15 – 5:45)

**Action:** Click logout. Toast: "Signed out". Sign in as `viewer` / `viewer2026`.

> "Our proposal commits to three roles — Admin, Staff, and Viewer — under the Security NFR. Let me show the role separation by logging in as a read-only stakeholder."

**Action:** On the Cases page, point at the Viewer role chip in the navbar.

> "Notice the role chip shows 'Viewer' now — and if I try to delete a case…"

**Action:** Hover over the Delete button on any case. Tooltip says "Admin only" and the button is disabled.

> "…the delete button is disabled with an admin-only tooltip. Even if a viewer somehow called the API directly, the backend returns 403 Forbidden because the delete endpoint requires the admin role."

---

## SECTION 8 — One more thing: dark mode + close (5:45 – 6:15)

**Action:** Logout, log back in as `linah` / `supervisor123`.

**Action:** Click the moon icon in the navbar. The whole UI transitions smoothly to dark mode.

> "And finally — because we want this to feel like a real product, the whole interface supports dark mode. The setting persists across sessions."

**Action:** Briefly hover on the KPI cards in dark mode to show they look good. Move to dashboard.

> "To recap what we delivered:
> - **Sprint 1** — secure authentication, JWT, full case CRUD on a normalized SQLite schema.
> - **Sprint 2** — `pdfplumber`-based extraction engine with a side-by-side review UI.
> - **Sprint 3** — Arabic and OCR support, the full React Router shell, the dashboard.
> - **Sprint 4** — Excel and PDF export, audit logging, the KPI engine, role-based access, 26 automated tests — and all three primary KPIs **exceed** their proposal targets.

> "Thank you. We're happy to take questions."

---

## Cheat sheet — emergency one-liners

If something breaks during recording, you can fall back to these:

| Situation | What to say |
|---|---|
| Extraction is slow | "The first extraction triggers OCR fallback initialization — subsequent ones are sub-second." |
| Backend isn't running | "In a production deployment this would be hosted; for the demo we're running it locally." |
| A field comes back Low / Missing | "And here you can see exactly the human-in-the-loop pattern our proposal calls for — the system surfaces the uncertain field instead of hiding it." |
| Audit trail is empty | "Audit entries are only created when a user actually changes a value compared to what was extracted." |
| Dark mode toggle doesn't transition smoothly | Ignore it and keep moving — the toggle still works. |

---

## Timing summary

| Section | Time | Cumulative |
|---|---|---|
| 1. Problem statement | 0:30 | 0:30 |
| 2. Login + Dashboard tour | 1:00 | 1:30 |
| 3. Create case + upload | 1:00 | 2:30 |
| 4. Extract + review + approve | 1:30 | 4:00 |
| 5. Audit trail + export | 0:45 | 4:45 |
| 6. Search & retrieval | 0:30 | 5:15 |
| 7. RBAC demo | 0:30 | 5:45 |
| 8. Dark mode + close | 0:30 | 6:15 |

Total target: **6 min 15 sec**. Aim to stay between 5:45 and 6:30.

---

## Recording tips

1. **Practice once without recording.** Walk through the whole script with the app live to catch any timing issues.
2. **Hide the bookmarks bar** in your browser. `Ctrl + Shift + B` to toggle.
3. **Use a microphone, not laptop speakers.** Even AirPods are dramatically better than built-in mics.
4. **Don't talk during loading.** Pause for 1–2 seconds when the extraction is running, then narrate over the result.
5. **Mouse should always be moving toward what you're describing**, never trailing behind your words.
6. **Use OBS Studio** (free) for recording — it lets you do simple cuts between takes.
7. **Record at 1920×1080**, 30 fps minimum. If you can do 60 fps, do.
8. **Cut the dead air aggressively** in post — every "uhh" and pause you remove makes the demo sharper.
