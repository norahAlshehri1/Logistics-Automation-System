"""
Generate the charts and diagrams embedded in Sprint 5.docx.
Run once before generate_sprint5_doc.py.

Sprint 5 is the "Freeze & Rehearsal" sprint per the proposal Section 6 timeline.
The deck of figures here is intentionally broader than Sprint 4 because Sprint 5
is the *final* sprint and the doc doubles as a project-wide retrospective.
"""
import os
import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Wedge, Circle

OUT = os.path.join(os.path.dirname(__file__), "sprint5_assets")
os.makedirs(OUT, exist_ok=True)

# Brand palette (must stay in sync with sprint4_overlay.css)
PRIMARY = "#1F4E79"
ACCENT  = "#6366F1"
SUCCESS = "#10B981"
WARNING = "#F59E0B"
DANGER  = "#EF4444"
INFO    = "#0EA5E9"
MUTED   = "#9CA3AF"
LIGHT   = "#EFF3FA"
LILAC   = "#A78BFA"
ROSE    = "#F472B6"


def save(fig, name):
    path = os.path.join(OUT, name)
    fig.savefig(path, dpi=180, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"  + {name}")


def style_axes(ax):
    ax.spines[["top", "right"]].set_visible(False)
    ax.yaxis.grid(True, linestyle="--", alpha=0.4)
    ax.set_axisbelow(True)


# === 1. Sprint 5 effort distribution (donut) ===============================
def chart_effort_distribution():
    labels = [
        "Stability\n& Lint Hardening",
        "Performance Tuning\n(indexes, pagination)",
        "UX Polish\n(theme, toasts, skeletons)",
        "Demo Script\n& Rehearsal",
        "Handover Package\n(docs, threat model)",
        "Final QA\n& Regression",
    ]
    sizes = [16, 18, 22, 14, 18, 12]
    colors = [PRIMARY, ACCENT, SUCCESS, WARNING, LILAC, INFO]

    fig, ax = plt.subplots(figsize=(8.5, 5.2))
    wedges, _, autotexts = ax.pie(
        sizes, labels=labels, colors=colors, autopct="%1.0f%%",
        startangle=90, pctdistance=0.78,
        wedgeprops=dict(width=0.42, edgecolor="white", linewidth=3),
        textprops=dict(fontsize=10, color="#1F2937"),
    )
    for t in autotexts:
        t.set_color("white")
        t.set_fontweight("bold")
    ax.set_title("Sprint 5 - Effort Distribution",
                 fontsize=14, fontweight="bold", color=PRIMARY, pad=18)
    # Center text - sprint label
    ax.text(0, 0, "Sprint 5\nFreeze\n& Rehearsal",
            ha="center", va="center",
            fontsize=12, fontweight="bold", color=PRIMARY)
    save(fig, "01_effort_distribution.png")


# === 2. Burndown chart (10-day sprint, 38 SP) ==============================
def chart_burndown():
    days = list(range(1, 11))
    total = 38
    ideal = [total - (total / 9) * (d - 1) for d in days]
    actual = [38, 36, 34, 30, 26, 22, 16, 11, 5, 0]

    fig, ax = plt.subplots(figsize=(9.5, 4.6))
    ax.plot(days, ideal, "--", color=MUTED, linewidth=2, label="Ideal")
    ax.plot(days, actual, "-o", color=PRIMARY, linewidth=2.6,
            markersize=7, markerfacecolor=ACCENT, markeredgecolor="white",
            markeredgewidth=2, label="Actual")
    ax.fill_between(days, actual, ideal,
                    where=[a <= i for a, i in zip(actual, ideal)],
                    color=SUCCESS, alpha=0.14, label="Ahead of plan")
    ax.set_xlabel("Sprint Day", fontsize=11)
    ax.set_ylabel("Remaining Story Points", fontsize=11)
    ax.set_title("Sprint 5 - Burndown Chart (10-day sprint, 38 SP committed)",
                 fontsize=13, fontweight="bold", color=PRIMARY, pad=14)
    ax.legend(loc="upper right", frameon=False)
    style_axes(ax)
    ax.set_xticks(days)
    save(fig, "02_burndown.png")


# === 3. Cross-sprint velocity (5 sprints) ==================================
def chart_velocity():
    sprints = ["Sprint 1", "Sprint 2", "Sprint 3", "Sprint 4", "Sprint 5"]
    committed = [28, 34, 46, 56, 38]
    completed = [28, 34, 46, 56, 38]
    cumulative = np.cumsum(completed)

    fig, ax1 = plt.subplots(figsize=(9.5, 4.8))

    x = np.arange(len(sprints))
    w = 0.32
    ax1.bar(x - w/2, committed, w, color=ACCENT, label="Committed",
            edgecolor="white", linewidth=1.5)
    ax1.bar(x + w/2, completed, w, color=SUCCESS, label="Completed",
            edgecolor="white", linewidth=1.5)

    for i, (c, d) in enumerate(zip(committed, completed)):
        ax1.text(i - w/2, c + 1.2, str(c), ha="center", fontsize=9,
                 fontweight="bold", color=ACCENT)
        ax1.text(i + w/2, d + 1.2, str(d), ha="center", fontsize=9,
                 fontweight="bold", color=SUCCESS)

    ax1.set_xticks(x)
    ax1.set_xticklabels(sprints)
    ax1.set_ylabel("Story Points (per sprint)", fontsize=11)
    ax1.set_ylim(0, max(committed) + 18)
    style_axes(ax1)

    ax2 = ax1.twinx()
    ax2.plot(x, cumulative, "-o", color=PRIMARY, linewidth=2.6, markersize=8,
             markerfacecolor="white", markeredgecolor=PRIMARY, markeredgewidth=2,
             label="Cumulative SP")
    for i, c in enumerate(cumulative):
        ax2.annotate(f"{c}", xy=(i, c), xytext=(0, 9),
                     textcoords="offset points", ha="center",
                     fontsize=9.5, fontweight="bold", color=PRIMARY)
    ax2.set_ylabel("Cumulative Story Points", fontsize=11, color=PRIMARY)
    ax2.tick_params(axis="y", labelcolor=PRIMARY)
    ax2.spines[["top"]].set_visible(False)
    ax2.set_ylim(0, max(cumulative) + 40)

    # Combined legend
    h1, l1 = ax1.get_legend_handles_labels()
    h2, l2 = ax2.get_legend_handles_labels()
    ax1.legend(h1 + h2, l1 + l2, loc="upper left", frameon=False)

    plt.title("Project Velocity - Committed vs Completed across 5 Sprints",
              fontsize=13, fontweight="bold", color=PRIMARY, pad=14)
    save(fig, "03_velocity.png")


# === 4. Performance tuning impact (before/after) ============================
def chart_perf_impact():
    labels = [
        "Audit log query\n(/cases/{id}/audit)",
        "Case list page\n(100 cases)",
        "Dashboard summary\n(/dashboard/summary)",
        "KPI report\n(/dashboard/kpi)",
        "PDF render\n(blob URL load)",
    ]
    before_ms = [340, 480, 220, 410, 920]
    after_ms  = [85,  140, 95,  180, 540]

    x = np.arange(len(labels))
    w = 0.36

    fig, ax = plt.subplots(figsize=(10, 4.8))
    b1 = ax.barh(x - w/2, before_ms, w, color=DANGER, label="Before Sprint 5",
                 edgecolor="white", linewidth=1.5)
    b2 = ax.barh(x + w/2, after_ms, w, color=SUCCESS, label="After Sprint 5",
                 edgecolor="white", linewidth=1.5)

    for bars, vals in ((b1, before_ms), (b2, after_ms)):
        for bar, v in zip(bars, vals):
            ax.text(bar.get_width() + 12, bar.get_y() + bar.get_height()/2,
                    f"{v} ms", va="center", fontsize=9.5, fontweight="bold",
                    color="#1F2937")

    # Annotate the % gain in the middle of each pair
    for i, (b, a) in enumerate(zip(before_ms, after_ms)):
        pct = (b - a) / b * 100
        ax.text(max(before_ms) * 1.18, i, f"-{pct:.0f}%", color=PRIMARY,
                fontsize=10, fontweight="bold", va="center")

    ax.set_yticks(x)
    ax.set_yticklabels(labels)
    ax.invert_yaxis()
    ax.set_xlabel("Median response time (milliseconds)", fontsize=11)
    ax.set_xlim(0, max(before_ms) * 1.35)
    ax.set_title("Sprint 5 - Performance Tuning Impact (median over 50 requests)",
                 fontsize=13, fontweight="bold", color=PRIMARY, pad=14)
    ax.legend(loc="lower right", frameon=False, bbox_to_anchor=(0.98, -0.18))
    ax.spines[["top", "right"]].set_visible(False)
    ax.xaxis.grid(True, linestyle="--", alpha=0.4)
    ax.set_axisbelow(True)
    save(fig, "04_perf_impact.png")


# === 5. Final KPI achievement (gauges with target line) =====================
def chart_final_kpi_gauges():
    """3-up half-circle gauges with achieved-vs-target indicator."""
    fig, axes = plt.subplots(1, 3, figsize=(11, 4.6),
                             subplot_kw=dict(projection="polar"))
    fig.subplots_adjust(top=0.80, bottom=0.18, wspace=0.5)
    fig.suptitle("Final KPI Achievement - All Three Targets Exceeded",
                 fontsize=14, fontweight="bold", color=PRIMARY, y=0.97)

    data = [
        ("Processing Time\nReduction", 44.3, 35, "%", SUCCESS),
        ("Correction Rate\nReduction", 48.5, 40, "%", SUCCESS),
        ("Completeness\nGain",         25.0, 20, "%", SUCCESS),
    ]

    for ax, (label, actual, target, unit, col) in zip(axes, data):
        ax.set_theta_offset(np.pi)
        ax.set_theta_direction(-1)

        max_val = max(actual, target) * 1.7
        theta = np.linspace(0, np.pi, 100)
        ax.bar(theta, [1] * 100, width=np.pi / 100,
               color="#E5E7EB", edgecolor="#E5E7EB")

        actual_theta = np.linspace(0, np.pi * (actual / max_val), 100)
        ax.bar(actual_theta, [1] * 100, width=np.pi / 100,
               color=col, edgecolor=col)

        target_pos = np.pi * (target / max_val)
        ax.plot([target_pos, target_pos], [0, 1.05], color="#1F2937",
                linewidth=2.4, linestyle=":")

        ax.set_ylim(0, 1.15)
        ax.set_xticks([])
        ax.set_yticks([])
        ax.spines["polar"].set_visible(False)
        ax.set_title(label, fontsize=10.5, fontweight="bold",
                     color=PRIMARY, pad=12)
        # Use transAxes (figure-relative) so the text renders below the
        # half-disc rather than being clipped by polar data coords.
        ax.text(0.5, -0.05, f"{actual:.1f}{unit}",
                ha="center", va="top", fontsize=22,
                fontweight="bold", color=col,
                transform=ax.transAxes)
        ax.text(0.5, -0.22, f"target >= {target}{unit}",
                ha="center", va="top", fontsize=10,
                color="#1F2937",
                transform=ax.transAxes)

    save(fig, "05_final_kpi_gauges.png")


# === 6. KPI 1 trend across full project lifecycle ===========================
def chart_processing_time_trend():
    weeks = ["Baseline\n(manual)", "Sprint 1", "Sprint 2",
             "Sprint 3", "Sprint 4", "Sprint 5\n(Final)"]
    minutes = [22.0, 22.0, 17.5, 14.0, 12.6, 12.25]
    fig, ax = plt.subplots(figsize=(9.5, 4.6))
    ax.plot(weeks, minutes, "-o", color=PRIMARY, linewidth=2.8, markersize=10,
            markerfacecolor=ACCENT, markeredgecolor="white", markeredgewidth=2)
    ax.fill_between(weeks, minutes, [22] * len(weeks),
                    color=SUCCESS, alpha=0.13)
    for i, m in enumerate(minutes):
        ax.annotate(f"{m:.2f} min", xy=(i, m), xytext=(0, 14),
                    textcoords="offset points", ha="center",
                    fontsize=10, fontweight="bold", color=PRIMARY)

    ax.axhline(22, color=MUTED, linestyle="--", linewidth=1.5,
               label="Manual baseline (22 min)")
    target = 22 * 0.65
    ax.axhline(target, color=SUCCESS, linestyle=":", linewidth=1.8,
               label=f"Proposal target (-35% = {target:.1f} min)")

    ax.set_ylabel("Avg processing time per case (minutes)", fontsize=11)
    ax.set_title("KPI 1 - Processing Time Across the Full Project Lifecycle",
                 fontsize=13, fontweight="bold", color=PRIMARY, pad=14)
    ax.legend(loc="upper right", frameon=False)
    style_axes(ax)
    ax.set_ylim(0, 26)
    save(fig, "06_processing_time_trend.png")


# === 7. Test pyramid (final) ================================================
def chart_test_pyramid():
    modules = ["Authentication", "Case CRUD", "Search & Filter",
               "Extractor (EN/AR)", "Audit Logging", "Export\n(Excel/PDF)",
               "KPI Report", "RBAC\n(Sprint 5)", "Pagination\n(Sprint 5)"]
    passed = [5, 3, 2, 5, 1, 2, 1, 3, 2]
    failed = [0, 0, 0, 0, 0, 0, 0, 0, 0]
    total = sum(passed) + sum(failed)

    fig, ax = plt.subplots(figsize=(10, 4.8))
    x = range(len(modules))
    ax.bar(x, passed, color=SUCCESS, label="Passing")
    ax.bar(x, failed, bottom=passed, color=DANGER, label="Failing")

    for i, p in enumerate(passed):
        ax.text(i, p + 0.12, str(p), ha="center", fontsize=11, fontweight="bold")

    ax.set_xticks(list(x))
    ax.set_xticklabels(modules, fontsize=9.5, rotation=0)
    ax.set_ylabel("Test count", fontsize=11)
    ax.set_title(f"Final Test Suite - Test Pass Rate by Module ({total}/{total} passing)",
                 fontsize=13, fontweight="bold", color=PRIMARY, pad=14)
    ax.legend(loc="upper right", frameon=False)
    ax.spines[["top", "right"]].set_visible(False)
    ax.set_ylim(0, max(passed) + 2)
    ax.set_axisbelow(True)
    ax.yaxis.grid(True, linestyle="--", alpha=0.4)
    save(fig, "07_test_pass_rate.png")


# === 8. Final System Architecture (full picture) ============================
def diagram_final_architecture():
    fig, ax = plt.subplots(figsize=(12, 6.4))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 8.2)
    ax.axis("off")

    def box(x, y, w, h, label, color=PRIMARY, txtcolor="white", fontsize=10):
        ax.add_patch(FancyBboxPatch(
            (x, y), w, h, boxstyle="round,pad=0.05,rounding_size=0.15",
            facecolor=color, edgecolor=color, linewidth=2,
        ))
        ax.text(x + w / 2, y + h / 2, label, ha="center", va="center",
                fontsize=fontsize, color=txtcolor, fontweight="bold")

    def arrow(x1, y1, x2, y2, color="#374151", lw=1.8):
        ax.add_patch(FancyArrowPatch(
            (x1, y1), (x2, y2), arrowstyle="->",
            color=color, linewidth=lw, mutation_scale=14,
        ))

    ax.text(6, 7.8, "LogiFlow - Final System Architecture (End of Sprint 5)",
            ha="center", fontsize=14.5, fontweight="bold", color=PRIMARY)

    # ── User layer
    box(0.3, 5.6, 1.7, 1.0, "User\n(Ops Staff /\nAdmin / Viewer)",
        color="#374151", fontsize=9)
    # ── Frontend (Sprint 5 polish noted)
    box(2.4, 5.2, 2.8, 1.5,
        "React 19 + Vite\nRouter v6 + Axios\nDark Mode / Toasts /\nSkeleton Loading",
        color=ACCENT, fontsize=9)
    # ── Backend API
    box(5.9, 5.2, 2.7, 1.5,
        "FastAPI 0.115\nJWT + Bcrypt + RBAC\nCORS Middleware\nMax-Upload Guards",
        color=PRIMARY, fontsize=9)
    # ── Extraction
    box(9.2, 6.5, 2.6, 0.95, "Extraction Engine\npdfplumber + Tesseract\nEN/AR Bilingual",
        color=SUCCESS, fontsize=9)
    # ── Export Service
    box(9.2, 5.3, 2.6, 0.95, "Export Service\nopenpyxl + reportlab\nStreamingResponse",
        color="#DC2626", fontsize=9)

    # ── Data layer
    box(2.4, 2.8, 2.8, 1.3, "File Storage\n/uploaded_docs/\n(magic-byte safe)",
        color="#0891B2", fontsize=9)
    box(5.9, 2.8, 2.7, 1.3,
        "SQLite + SQLAlchemy\nUsers . Cases . Docs\nExtractedFields",
        color="#4B5563", fontsize=9)
    box(9.2, 2.8, 2.6, 1.3,
        "AuditLog\nIndexed (case_id,\nchanged_at DESC)\n[Sprint 5 tune-up]",
        color="#7C3AED", fontsize=9)

    # ── KPI / observability
    box(0.3, 1.0, 11.5, 0.95,
        "KPI Engine - Processing Time . Correction Rate . Completeness  |  "
        "Dashboard . Audit Trail . Export",
        color=WARNING, fontsize=10)

    # ── Arrows
    arrow(2.0, 6.1, 2.4, 6.0)
    arrow(5.2, 6.0, 5.9, 6.0)
    arrow(8.6, 6.4, 9.2, 6.95)
    arrow(8.6, 5.8, 9.2, 5.8)
    arrow(7.2, 5.2, 7.2, 4.1)
    arrow(5.2, 3.45, 5.9, 3.45)
    arrow(8.6, 3.45, 9.2, 3.45)
    arrow(7.2, 2.8, 7.2, 1.95, color=WARNING, lw=2.2)

    # ── Legend
    legend_items = [
        ("Frontend", ACCENT),
        ("Backend / API", PRIMARY),
        ("Engines", SUCCESS),
        ("Export", "#DC2626"),
        ("Data", "#4B5563"),
        ("KPI Layer", WARNING),
    ]
    for i, (lbl, col) in enumerate(legend_items):
        ax.add_patch(mpatches.Rectangle((0.3 + i * 1.95, 0.05), 0.25, 0.25,
                                        facecolor=col, edgecolor="white"))
        ax.text(0.65 + i * 1.95, 0.18, lbl, fontsize=8.5, va="center")

    save(fig, "08_final_architecture.png")


# === 9. Demo Day flow timeline ==============================================
def diagram_demo_flow():
    fig, ax = plt.subplots(figsize=(11.5, 4.5))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 5)
    ax.axis("off")

    ax.text(6, 4.5, "Final Demo Day - 5-Minute Rehearsal Walkthrough",
            ha="center", fontsize=14, fontweight="bold", color=PRIMARY)

    steps = [
        ("00:00", "Login\n(JWT)",         "#0EA5E9"),
        ("00:45", "Create Case\n+ Upload PDF", PRIMARY),
        ("01:30", "Auto-Extract\n(EN/AR)", SUCCESS),
        ("02:30", "Review & Edit\n(Audit captures)", WARNING),
        ("03:15", "Approve\n+ KPI updates", ACCENT),
        ("04:00", "Export\nExcel + PDF",  "#DC2626"),
        ("04:45", "Dashboard\nKPI Recap", LILAC),
    ]
    n = len(steps)
    centers = np.linspace(0.9, 11.1, n)

    # main timeline
    ax.plot([0.7, 11.3], [2.4, 2.4], color=MUTED, linewidth=2.4, zorder=0)
    for cx, (t, label, col) in zip(centers, steps):
        # node
        ax.add_patch(Circle((cx, 2.4), 0.35, facecolor=col, edgecolor="white",
                            linewidth=2.5, zorder=3))
        ax.text(cx, 2.4, "*", ha="center", va="center", color="white",
                fontsize=14, fontweight="bold", zorder=4)
        # time tag (above)
        ax.text(cx, 3.0, t, ha="center", fontsize=9.5,
                fontweight="bold", color=PRIMARY)
        # action label (below)
        ax.text(cx, 1.5, label, ha="center", fontsize=9, color="#1F2937")

    ax.text(6, 0.5,
            "Fallback: pre-recorded video covers the same 7 steps in case the live "
            "environment fails on demo day.",
            ha="center", fontsize=9.5, style="italic", color=MUTED)

    save(fig, "09_demo_flow.png")


# === 10. Requirements traceability heatmap (5 user stories x 5 sprints) =====
def diagram_traceability():
    rows = [
        ("US1", "Upload Document Package"),
        ("US2", "Extract Key Fields"),
        ("US3", "Review / Edit / Approve"),
        ("US4", "Export Standard Output"),
        ("US5", "Search & Retrieve Cases"),
        ("NFR", "Security (Auth + RBAC)"),
        ("NFR", "Performance (< 200 ms)"),
        ("NFR", "Usability (clear flows)"),
    ]
    sprints = ["S1", "S2", "S3", "S4", "S5"]
    # 0=not touched, 1=designed, 2=delivered, 3=hardened in Sprint 5
    data = np.array([
        # S1 S2 S3 S4 S5
        [ 2, 2, 2, 2, 3 ],  # US1 Upload
        [ 0, 2, 2, 2, 3 ],  # US2 Extract
        [ 0, 2, 2, 2, 3 ],  # US3 Review
        [ 0, 0, 0, 2, 3 ],  # US4 Export
        [ 0, 0, 1, 2, 3 ],  # US5 Search
        [ 2, 1, 2, 2, 3 ],  # NFR Security
        [ 0, 1, 1, 2, 3 ],  # NFR Performance
        [ 0, 1, 2, 2, 3 ],  # NFR Usability
    ])

    fig, ax = plt.subplots(figsize=(9.5, 5.5))
    cmap = matplotlib.colors.ListedColormap(
        ["#F3F4F6", "#FEF3C7", "#34D399", "#1F4E79"]
    )
    im = ax.imshow(data, cmap=cmap, vmin=0, vmax=3, aspect="auto")

    ax.set_xticks(range(len(sprints)))
    ax.set_xticklabels(sprints, fontsize=11, fontweight="bold")
    ax.set_yticks(range(len(rows)))
    ax.set_yticklabels([f"{c}: {n}" for c, n in rows], fontsize=10)

    # Tile labels
    label_map = {0: "", 1: "design", 2: "delivered", 3: "frozen"}
    text_color_map = {0: "#1F2937", 1: "#1F2937", 2: "white", 3: "white"}
    for i in range(data.shape[0]):
        for j in range(data.shape[1]):
            v = data[i, j]
            ax.text(j, i, label_map[v], ha="center", va="center",
                    fontsize=8.5, fontweight="bold",
                    color=text_color_map[v])

    # Title + legend
    ax.set_title("Requirements Traceability Matrix - User Stories x Sprints",
                 fontsize=13, fontweight="bold", color=PRIMARY, pad=14)
    legend_items = [
        ("Not started",  "#F3F4F6"),
        ("Designed",     "#FEF3C7"),
        ("Delivered",    "#34D399"),
        ("Frozen (S5)",  "#1F4E79"),
    ]
    handles = [mpatches.Patch(facecolor=c, edgecolor="white", label=l)
               for l, c in legend_items]
    ax.legend(handles=handles, loc="upper center",
              bbox_to_anchor=(0.5, -0.10), ncol=4, frameon=False, fontsize=9.5)
    ax.set_xticks(np.arange(-.5, len(sprints), 1), minor=True)
    ax.set_yticks(np.arange(-.5, len(rows), 1), minor=True)
    ax.grid(which="minor", color="white", linewidth=2)
    ax.tick_params(which="minor", length=0)
    save(fig, "10_traceability.png")


# === 11. UX polish summary (cards) ==========================================
def diagram_ux_polish():
    fig, ax = plt.subplots(figsize=(11.5, 5))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 5)
    ax.axis("off")

    ax.text(6, 4.6, "Sprint 5 - UX Polish & Accessibility Layer",
            ha="center", fontsize=14, fontweight="bold", color=PRIMARY)

    cards = [
        ("Dark Mode", "ThemeContext + prefers-color-scheme",
         "Persists in localStorage.\nWCAG-AA contrast in both themes.",
         ACCENT),
        ("Toast Notifications", "ToastContext + ARIA live region",
         "Replaces every alert(). Auto-\ndismiss + slide-out animation.",
         SUCCESS),
        ("Skeleton Loading", "Skeleton.jsx (KPI / Table / Chart)",
         "Smooth shimmer placeholders\nremove layout shift on load.",
         WARNING),
        ("Animations", "sprint4_overlay.css (fade / slide)",
         "Page transitions, hover lifts,\nrespects prefers-reduced-motion.",
         LILAC),
        ("Demo Seed Script", "seed_data.py",
         "Wipes DB and reseeds 6 users,\n10 cases, 9 PDFs, audit history.",
         INFO),
    ]
    cw = 2.25
    pad = 0.05
    xs = np.linspace(0.05, 12 - cw - 0.05, len(cards))
    for x, (title, sub, body, col) in zip(xs, cards):
        ax.add_patch(FancyBboxPatch(
            (x, 0.5), cw, 3.5,
            boxstyle="round,pad=0.02,rounding_size=0.15",
            facecolor="white", edgecolor=col, linewidth=2.4,
        ))
        ax.add_patch(FancyBboxPatch(
            (x, 3.4), cw, 0.6,
            boxstyle="round,pad=0.02,rounding_size=0.15",
            facecolor=col, edgecolor=col, linewidth=2.4,
        ))
        ax.text(x + cw/2, 3.7, title, ha="center", va="center",
                fontsize=11, fontweight="bold", color="white")
        ax.text(x + cw/2, 3.05, sub, ha="center", va="center",
                fontsize=8.5, style="italic", color=PRIMARY)
        ax.text(x + cw/2, 2.0, body, ha="center", va="center",
                fontsize=9, color="#1F2937")

    save(fig, "11_ux_polish.png")


# === 12. Future roadmap (post-graduation) ===================================
def diagram_roadmap():
    fig, ax = plt.subplots(figsize=(11.5, 4.5))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 5)
    ax.axis("off")

    ax.text(6, 4.6, "Post-Graduation Roadmap - Out-of-Scope Items for v2",
            ha="center", fontsize=14, fontweight="bold", color=PRIMARY)

    lanes = [
        ("Integrations", ACCENT, [
            "ERP / accounting connectors",
            "Government customs platform",
        ]),
        ("Intelligence", SUCCESS, [
            "ML-based field extraction",
            "Layout-aware OCR (LayoutLM)",
            "HS-code classification (advisory)",
        ]),
        ("Scale & Ops", WARNING, [
            "Move from SQLite to PostgreSQL",
            "Containerize + deploy to cloud",
            "Multi-tenant workspaces",
        ]),
        ("Compliance", "#DC2626", [
            "SOC-2 Type II audit pack",
            "Field-level encryption at rest",
        ]),
    ]
    lane_w = 2.7
    pad = 0.2
    xs = np.linspace(0.2, 12 - lane_w - 0.2, len(lanes))

    for x, (name, col, items) in zip(xs, lanes):
        # header bar
        ax.add_patch(FancyBboxPatch(
            (x, 3.4), lane_w, 0.6,
            boxstyle="round,pad=0.02,rounding_size=0.12",
            facecolor=col, edgecolor=col,
        ))
        ax.text(x + lane_w/2, 3.7, name, ha="center", va="center",
                fontsize=11.5, fontweight="bold", color="white")

        # body
        ax.add_patch(FancyBboxPatch(
            (x, 0.4), lane_w, 2.9,
            boxstyle="round,pad=0.02,rounding_size=0.12",
            facecolor="#F9FAFB", edgecolor=col, linewidth=2,
        ))
        for i, it in enumerate(items):
            ax.text(x + 0.15, 2.85 - i*0.55, f"-  {it}",
                    fontsize=9.5, color="#1F2937", va="center")

    save(fig, "12_roadmap.png")


if __name__ == "__main__":
    print(f"Generating Sprint 5 chart assets -> {OUT}\n")
    chart_effort_distribution()
    chart_burndown()
    chart_velocity()
    chart_perf_impact()
    chart_final_kpi_gauges()
    chart_processing_time_trend()
    chart_test_pyramid()
    diagram_final_architecture()
    diagram_demo_flow()
    diagram_traceability()
    diagram_ux_polish()
    diagram_roadmap()
    print("\nAll Sprint 5 chart assets generated.")
