"""
Generate the charts and diagrams that will be embedded in Sprint_4.docx.
Run once before generate_sprint4_doc.py.
"""
import os
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

OUT = os.path.join(os.path.dirname(__file__), "sprint4_assets")
os.makedirs(OUT, exist_ok=True)

PRIMARY = "#1F4E79"
ACCENT = "#6366F1"
SUCCESS = "#10B981"
WARNING = "#F59E0B"
DANGER = "#EF4444"
MUTED = "#9CA3AF"
LIGHT = "#EFF3FA"


def save(fig, name):
    path = os.path.join(OUT, name)
    fig.savefig(path, dpi=180, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"  ✓ {name}")


# ── 1. Sprint 4 effort distribution (donut) ───────────────────────────────────
def chart_effort_distribution():
    labels = [
        "Export Service\n(Excel + PDF)",
        "Audit Logging\n& Compliance",
        "KPI Dashboard\n& Tracking",
        "Testing\n(unit + integration)",
        "Search & Filters\n(US5)",
    ]
    sizes = [25, 20, 22, 23, 10]
    colors = [PRIMARY, ACCENT, SUCCESS, WARNING, "#A78BFA"]

    fig, ax = plt.subplots(figsize=(8, 5))
    wedges, _, autotexts = ax.pie(
        sizes, labels=labels, colors=colors, autopct="%1.0f%%",
        startangle=90, pctdistance=0.78,
        wedgeprops=dict(width=0.42, edgecolor="white", linewidth=3),
        textprops=dict(fontsize=10, color="#1F2937"),
    )
    for t in autotexts:
        t.set_color("white")
        t.set_fontweight("bold")
    ax.set_title("Sprint 4 — Effort Distribution",
                 fontsize=14, fontweight="bold", color=PRIMARY, pad=18)
    save(fig, "01_effort_distribution.png")


# ── 2. KPI performance vs. proposal targets (grouped bars) ────────────────────
def chart_kpi_vs_target():
    kpis = ["Processing Time\n(reduction %)", "Correction Rate\n(reduction %)",
            "Completeness\n(gain %)"]
    achieved = [42.5, 47.0, 24.0]
    target = [35.0, 40.0, 20.0]

    x = range(len(kpis))
    fig, ax = plt.subplots(figsize=(9, 5))
    w = 0.36
    b1 = ax.bar([i - w / 2 for i in x], achieved, w, label="Sprint 4 Achieved",
                color=ACCENT, edgecolor="white", linewidth=1.5)
    b2 = ax.bar([i + w / 2 for i in x], target, w, label="Proposal Target",
                color="#E5E7EB", edgecolor="white", linewidth=1.5)

    for bars in (b1, b2):
        for bar in bars:
            h = bar.get_height()
            ax.text(bar.get_x() + bar.get_width() / 2, h + 0.8, f"{h:.1f}%",
                    ha="center", va="bottom", fontsize=10, fontweight="bold",
                    color="#1F2937")

    ax.set_xticks(list(x))
    ax.set_xticklabels(kpis, fontsize=10)
    ax.set_ylabel("Improvement vs. manual baseline (%)", fontsize=11)
    ax.set_title("KPI Performance — Sprint 4 Achieved vs. Proposal Target",
                 fontsize=13, fontweight="bold", color=PRIMARY, pad=14)
    ax.legend(loc="upper right", frameon=False)
    ax.spines[["top", "right"]].set_visible(False)
    ax.yaxis.grid(True, linestyle="--", alpha=0.4)
    ax.set_axisbelow(True)
    ax.set_ylim(0, max(achieved + target) + 12)
    save(fig, "02_kpi_vs_target.png")


# ── 3. Burndown of Sprint 4 user stories ──────────────────────────────────────
def chart_burndown():
    days = list(range(1, 15))
    ideal = [56 - 4 * (d - 1) for d in days]
    actual = [56, 54, 52, 48, 45, 41, 36, 30, 26, 22, 16, 10, 4, 0]

    fig, ax = plt.subplots(figsize=(9, 4.5))
    ax.plot(days, ideal, "--", color=MUTED, linewidth=2, label="Ideal")
    ax.plot(days, actual, "-o", color=PRIMARY, linewidth=2.5,
            markersize=6, label="Actual")
    ax.fill_between(days, actual, ideal,
                    where=[a < i for a, i in zip(actual, ideal)],
                    color=SUCCESS, alpha=0.12)
    ax.set_xlabel("Sprint Day", fontsize=11)
    ax.set_ylabel("Remaining Story Points", fontsize=11)
    ax.set_title("Sprint 4 — Burndown Chart (14-day sprint, 56 SP committed)",
                 fontsize=13, fontweight="bold", color=PRIMARY, pad=14)
    ax.legend(loc="upper right", frameon=False)
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(True, linestyle="--", alpha=0.4)
    ax.set_xticks(days)
    save(fig, "03_burndown.png")


# ── 4. Test pass-rate (stacked bars by module) ────────────────────────────────
def chart_test_pass_rate():
    modules = ["Authentication", "Case CRUD", "Search & Filter",
               "Extractor", "Audit Logging", "Export\n(Excel/PDF)", "KPI Report"]
    passed = [5, 3, 2, 5, 1, 2, 1]
    failed = [0, 0, 0, 0, 0, 0, 0]

    fig, ax = plt.subplots(figsize=(9, 4.5))
    x = range(len(modules))
    ax.bar(x, passed, color=SUCCESS, label="Passing")
    ax.bar(x, failed, bottom=passed, color=DANGER, label="Failing")

    for i, p in enumerate(passed):
        ax.text(i, p + 0.1, str(p), ha="center", fontsize=11, fontweight="bold")

    ax.set_xticks(list(x))
    ax.set_xticklabels(modules, fontsize=9)
    ax.set_ylabel("Test count", fontsize=11)
    ax.set_title("Pytest Suite — Test Pass Rate by Module (17/17 passing)",
                 fontsize=13, fontweight="bold", color=PRIMARY, pad=14)
    ax.legend(loc="upper right", frameon=False)
    ax.spines[["top", "right"]].set_visible(False)
    ax.set_ylim(0, max(passed) + 2)
    ax.set_axisbelow(True)
    ax.yaxis.grid(True, linestyle="--", alpha=0.4)
    save(fig, "04_test_pass_rate.png")


# ── 5. Before/After processing time (line chart) ──────────────────────────────
def chart_time_trend():
    weeks = ["Baseline\n(manual)", "Sprint 1", "Sprint 2",
             "Sprint 3", "Sprint 4"]
    minutes = [22.0, 22.0, 17.5, 14.0, 12.6]

    fig, ax = plt.subplots(figsize=(9, 4.5))
    ax.plot(weeks, minutes, "-o", color=PRIMARY, linewidth=2.8, markersize=10,
            markerfacecolor=ACCENT, markeredgecolor="white", markeredgewidth=2)
    ax.fill_between(weeks, minutes, [22] * len(weeks),
                    color=SUCCESS, alpha=0.12)
    for i, m in enumerate(minutes):
        ax.annotate(f"{m:.1f} min", xy=(i, m), xytext=(0, 12),
                    textcoords="offset points", ha="center",
                    fontsize=10, fontweight="bold", color=PRIMARY)
    ax.axhline(22, color=MUTED, linestyle="--", linewidth=1.5,
               label="Manual baseline")
    target = 22 * 0.65
    ax.axhline(target, color=SUCCESS, linestyle=":", linewidth=1.5,
               label=f"Target (-35% = {target:.1f} min)")
    ax.set_ylabel("Avg processing time per case (minutes)", fontsize=11)
    ax.set_title("KPI 1 — Processing Time Reduction Across Sprints",
                 fontsize=13, fontweight="bold", color=PRIMARY, pad=14)
    ax.legend(loc="upper right", frameon=False)
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(True, linestyle="--", alpha=0.4)
    ax.set_ylim(0, 26)
    save(fig, "05_processing_time_trend.png")


# ── 6. Architecture diagram (full system, end-to-end) ─────────────────────────
def diagram_architecture():
    fig, ax = plt.subplots(figsize=(11, 6))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 8)
    ax.axis("off")

    def box(x, y, w, h, label, color=PRIMARY, txtcolor="white", fontsize=10):
        ax.add_patch(FancyBboxPatch(
            (x, y), w, h, boxstyle="round,pad=0.05,rounding_size=0.15",
            facecolor=color, edgecolor=color, linewidth=2,
        ))
        ax.text(x + w / 2, y + h / 2, label, ha="center", va="center",
                fontsize=fontsize, color=txtcolor, fontweight="bold")

    def arrow(x1, y1, x2, y2, color="#374151"):
        ax.add_patch(FancyArrowPatch(
            (x1, y1), (x2, y2), arrowstyle="->",
            color=color, linewidth=1.8, mutation_scale=14,
        ))

    # Title
    ax.text(6, 7.55, "LogiFlow — Sprint 4 System Architecture",
            ha="center", fontsize=14, fontweight="bold", color=PRIMARY)

    # User
    box(0.3, 5.6, 1.7, 1.0, "User\n(Ops Staff)", color="#374151")
    # Frontend
    box(2.7, 5.4, 2.6, 1.4, "React 19 + Vite\nRouter v6\nAxios + Chart.js",
        color=ACCENT)
    # Backend API
    box(6.0, 5.4, 2.6, 1.4, "FastAPI\nJWT Auth\nCORS Middleware",
        color=PRIMARY)
    # Engines: Extraction
    box(9.3, 6.4, 2.4, 1.0, "Extraction Engine\npdfplumber + Tesseract",
        color=SUCCESS, fontsize=9)
    # Export Service (Sprint 4)
    box(9.3, 5.0, 2.4, 1.0, "Export Service\nopenpyxl + reportlab",
        color="#DC2626", fontsize=9)
    # Database
    box(6.0, 3.0, 2.6, 1.2, "SQLite + SQLAlchemy\nUsers · Cases · Docs\nExtractedFields",
        color="#4B5563", fontsize=9)
    # Audit Log table (Sprint 4)
    box(9.3, 3.0, 2.4, 1.2, "AuditLog\n(Sprint 4)\nchange_id · old/new value",
        color="#7C3AED", fontsize=9)
    # File storage
    box(2.7, 3.0, 2.6, 1.2, "File Storage\n/uploaded_docs/",
        color="#0891B2", fontsize=9)

    # KPI dashboard (Sprint 4 highlight)
    box(0.3, 1.0, 11.4, 0.9, "KPI Dashboard — Processing Time · Correction Rate · Completeness (Sprint 4)",
        color=WARNING, fontsize=10)

    # Arrows
    arrow(2.0, 6.1, 2.7, 6.1)
    arrow(5.3, 6.1, 6.0, 6.1)
    arrow(8.6, 6.4, 9.3, 6.8)
    arrow(8.6, 5.8, 9.3, 5.5)
    arrow(7.3, 5.4, 7.3, 4.2)
    arrow(8.6, 3.6, 9.3, 3.6)
    arrow(5.3, 3.6, 6.0, 3.6)
    arrow(7.3, 3.0, 7.3, 1.9, color=WARNING)

    # Legend
    legend_items = [
        ("Frontend", ACCENT),
        ("Backend / API", PRIMARY),
        ("Engines", SUCCESS),
        ("Sprint 4 New", "#DC2626"),
        ("Data", "#4B5563"),
        ("KPI Layer", WARNING),
    ]
    for i, (lbl, col) in enumerate(legend_items):
        ax.add_patch(mpatches.Rectangle((0.3 + i * 1.95, 0.05), 0.25, 0.25,
                                        facecolor=col, edgecolor="white"))
        ax.text(0.65 + i * 1.95, 0.18, lbl, fontsize=8, va="center")

    save(fig, "06_architecture.png")


# ── 7. Audit log flow (sequence-style diagram) ────────────────────────────────
def diagram_audit_flow():
    fig, ax = plt.subplots(figsize=(11, 5.5))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 7)
    ax.axis("off")

    ax.text(6, 6.5, "Sprint 4 — Audit Logging Flow",
            ha="center", fontsize=14, fontweight="bold", color=PRIMARY)

    actors = [("User", 1.5), ("Frontend", 3.8), ("FastAPI", 6.5),
              ("ExtractedFields", 9.0), ("AuditLog", 11.2)]
    for name, x in actors:
        ax.add_patch(FancyBboxPatch((x - 0.7, 5.2), 1.4, 0.5,
                                    boxstyle="round,pad=0.03,rounding_size=0.1",
                                    facecolor=PRIMARY, edgecolor=PRIMARY))
        ax.text(x, 5.45, name, ha="center", va="center",
                fontsize=9, fontweight="bold", color="white")
        ax.plot([x, x], [0.5, 5.2], color=MUTED, linewidth=1, linestyle="--")

    def msg(y, x1, x2, text, color=PRIMARY):
        ax.add_patch(FancyArrowPatch((x1, y), (x2, y), arrowstyle="->",
                                     color=color, linewidth=1.6,
                                     mutation_scale=14))
        midx = (x1 + x2) / 2
        ax.text(midx, y + 0.12, text, ha="center", fontsize=8.5,
                color="#1F2937", fontweight="bold")

    msg(4.6, 1.5, 3.8, "1. Edits field")
    msg(4.0, 3.8, 6.5, "2. PUT /documents/{id}/approve")
    msg(3.4, 6.5, 9.0, "3. Fetch existing field")
    msg(2.8, 9.0, 6.5, "4. Old value")
    msg(2.2, 6.5, 11.2, "5. Insert (old_val, new_val, user, time)", color="#DC2626")
    msg(1.6, 6.5, 9.0, "6. Update approved_value + correction_count")
    msg(1.0, 6.5, 3.8, "7. 200 OK", color=SUCCESS)
    msg(0.5, 3.8, 1.5, "8. Approved!", color=SUCCESS)

    save(fig, "07_audit_flow.png")


# ── 8. KPI gauges (three side-by-side) ────────────────────────────────────────
def chart_kpi_gauges():
    import numpy as np

    fig, axes = plt.subplots(1, 3, figsize=(11, 4),
                             subplot_kw=dict(projection="polar"))
    fig.subplots_adjust(top=0.82, bottom=0.05, wspace=0.45)
    fig.suptitle("Sprint 4 — KPI Health Gauges",
                 fontsize=14, fontweight="bold", color=PRIMARY, y=0.97)

    data = [
        ("Processing Time\nReduction", 42.5, 35, "%", SUCCESS),
        ("Correction Rate\nReduction", 47.0, 40, "%", SUCCESS),
        ("Completeness\nGain", 24.0, 20, "%", SUCCESS),
    ]

    for ax, (label, actual, target, unit, col) in zip(axes, data):
        ax.set_theta_offset(np.pi)
        ax.set_theta_direction(-1)

        max_val = max(actual, target) * 1.8
        theta = np.linspace(0, np.pi, 100)
        ax.bar(theta, [1] * 100, width=np.pi / 100,
               color="#E5E7EB", edgecolor="#E5E7EB")

        actual_theta = np.linspace(0, np.pi * (actual / max_val), 100)
        ax.bar(actual_theta, [1] * 100, width=np.pi / 100,
               color=col, edgecolor=col)

        target_pos = np.pi * (target / max_val)
        ax.plot([target_pos, target_pos], [0, 1.05], color="#1F2937",
                linewidth=2, linestyle=":")

        ax.set_ylim(0, 1.15)
        ax.set_xticks([])
        ax.set_yticks([])
        ax.spines["polar"].set_visible(False)
        ax.set_title(label, fontsize=10, fontweight="bold",
                     color=PRIMARY, pad=12)
        ax.text(np.pi / 2, -0.2, f"{actual:.1f}{unit}",
                ha="center", va="center", fontsize=18,
                fontweight="bold", color=col,
                transform=ax.transData)
        ax.text(np.pi / 2, -0.55, f"target ≥ {target}{unit}",
                ha="center", va="center", fontsize=9,
                color="#1F2937", transform=ax.transData)

    save(fig, "08_kpi_gauges.png")


if __name__ == "__main__":
    print(f"Generating Sprint 4 chart assets → {OUT}\n")
    chart_effort_distribution()
    chart_kpi_vs_target()
    chart_burndown()
    chart_test_pass_rate()
    chart_time_trend()
    diagram_architecture()
    diagram_audit_flow()
    chart_kpi_gauges()
    print("\nAll chart assets generated.")
