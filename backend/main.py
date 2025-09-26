from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import pandas as pd
from .rule_based import apply_rules
from .optimization import optimize_trains
from .predictive import apply_predictive
from .whatif import what_if
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
import matplotlib
matplotlib.use("Agg")  # Non-GUI backend
import matplotlib.pyplot as plt
from pathlib import Path

# Create FastAPI app
app = FastAPI()

# Enable CORS for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Base directory for files (safe for Render)
BASE_DIR = Path(__file__).parent.resolve()

# -------------------------------
# Load dataset
# -------------------------------
def load_df():
    return pd.read_csv("kochimetro_25_trains.csv")

# -------------------------------
# APIs for ML Models
# -------------------------------
@app.get("/api/rules")
def rules():
    df = load_df()
    df[['status','alerts']] = df.apply(apply_rules, axis=1)
    return df.to_dict(orient='records')

@app.get("/api/optimization")
def optimization(k: int = 3):
    df = load_df()
    return optimize_trains(df, k)

@app.get("/api/predictive")
def predictive():
    df = load_df()
    return apply_predictive(df)

@app.post("/api/whatif")
def whatif(k: int = 3, branding_weight: float = 2000, stabling_weight: float = 5):
    df = load_df()
    return what_if(df, k, branding_weight, stabling_weight)

@app.get("/api/whatif/defaults")
def whatif_defaults():
    return {"k": 3, "branding_weight": 2000, "stabling_weight": 5}

# -------------------------------
# Helper function for PDFs
# -------------------------------
def save_pdf(filename: str, chart_path: str, title: str, text_lines: list):
    c = canvas.Canvas(BASE_DIR / filename, pagesize=letter)
    c.setFont("Helvetica-Bold", 16)
    c.drawString(100, 750, title)
    c.setFont("Helvetica", 12)
    y = 720
    for line in text_lines:
        c.drawString(100, y, line)
        y -= 20
    c.drawImage(ImageReader(BASE_DIR / chart_path), 100, y - 300, width=400, height=300)
    c.save()
    return BASE_DIR / filename

# -------------------------------
# Status Report PDF
# -------------------------------
@app.get("/api/report/status-pdf")
def generate_status_report():
    df = load_df()
    df[['status','alerts']] = df.apply(apply_rules, axis=1)

    eligible = (df["status"] == "Eligible").sum()
    blocked = (df["status"] != "Eligible").sum()

    # Pie chart
    plt.figure(figsize=(4,4))
    plt.pie([eligible, blocked], labels=["Eligible", "Blocked"], autopct='%1.1f%%', colors=["#4CAF50", "#F44336"])
    plt.title("Eligible vs Blocked Trains")
    chart_path = "status_chart.png"
    plt.savefig(BASE_DIR / chart_path)
    plt.close()

    filename = save_pdf("status_report.pdf", chart_path, "Eligible vs Blocked Trains Report",
                        [f"Eligible trains: {eligible}", f"Blocked trains: {blocked}"])
    return FileResponse(filename, media_type="application/pdf", filename=filename.name)

# -------------------------------
# What-If Report PDF
# -------------------------------
@app.get("/api/report/whatif-pdf")
def generate_whatif_report(k: int = 3, branding_weight: float = 2000, stabling_weight: float = 5):
    df = load_df()
    before_df = optimize_trains(df, k)
    after_df = what_if(df, k, branding_weight, stabling_weight)

    before_avg = sum(r["score"] for r in before_df) / len(before_df)
    after_avg = sum(r["score"] for r in after_df) / len(after_df)

    # Bar chart
    plt.figure(figsize=(4,4))
    plt.bar(["Before", "After"], [before_avg, after_avg], color=["#2196F3", "#FFC107"])
    plt.ylabel("Average Score")
    plt.title("What-If Analysis: Before vs After")
    chart_path = "whatif_chart.png"
    plt.savefig(BASE_DIR / chart_path)
    plt.close()

    filename = save_pdf("whatif_report.pdf", chart_path, "What-If Analysis Report",
                        [f"Before Avg Score: {before_avg:.2f}", f"After Avg Score: {after_avg:.2f}"])
    return FileResponse(filename, media_type="application/pdf", filename=filename.name)

# -------------------------------
# Alerts Report PDF
# -------------------------------
@app.get("/api/report/alerts-pdf")
def generate_alerts_report():
    df = load_df()
    df[['status','alerts']] = df.apply(apply_rules, axis=1)

    alert_counts = {}
    for row in df.itertuples():
        if row.alerts and row.alerts != "-":
            for alert in row.alerts.split(","):
                alert = alert.strip()
                alert_counts[alert] = alert_counts.get(alert, 0) + 1

    # Bar chart
    plt.figure(figsize=(6,4))
    plt.bar(alert_counts.keys(), alert_counts.values(), color="#ffc107")
    plt.ylabel("Number of Trains")
    plt.title("Alerts Distribution")
    plt.xticks(rotation=45, ha="right")
    chart_path = "alerts_chart.png"
    plt.tight_layout()
    plt.savefig(BASE_DIR / chart_path)
    plt.close()

    text_lines = [f"{alert}: {count}" for alert, count in alert_counts.items()]
    filename = save_pdf("alerts_report.pdf", chart_path, "Alerts Distribution Report", text_lines)
    return FileResponse(filename, media_type="application/pdf", filename=filename.name)
