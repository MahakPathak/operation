from fastapi import FastAPI, Request, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.templating import Jinja2Templates
import os
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import ImageReader

# Import your modules
from .rule_based import apply_rules
from .optimization import optimize_trains
from .predictive import apply_predictive
from .whatif import what_if

# -------------------------------
# FastAPI app
# -------------------------------
app = FastAPI()

# -------------------------------
# Enable CORS
# -------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static files (CSS/JS)
app.mount("/static", StaticFiles(directory="../frontend/static"), name="static")

# Serve index.html
@app.get("/", include_in_schema=False)
def serve_index():
    index_path = os.path.join("../frontend/templates", "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"error": "index.html not found"}
    return templates.TemplateResponse("index.html", {"request": request})

# -------------------------------
# Helper to load dataset
# -------------------------------
def load_df():
    return pd.read_csv("kochimetro_25_trains.csv")

# -------------------------------
# RULES API
# -------------------------------
@app.get("/api/rules")
def rules():
    df = load_df()
    df[['status','alerts']] = df.apply(apply_rules, axis=1)
    return df.to_dict(orient='records')

# -------------------------------
# OPTIMIZATION API
# -------------------------------
@app.get("/api/optimization")
def optimization(k: int = 3):
    df = load_df()
    return optimize_trains(df, k)

# -------------------------------
# PREDICTIVE API
# -------------------------------
@app.get("/api/predictive")
def predictive():
    df = load_df()
    return apply_predictive(df)

# -------------------------------
# WHAT-IF API
# -------------------------------
@app.post("/api/whatif")
def whatif(
    k: int = 3,
    branding_weight: float = 2000,
    stabling_weight: float = 5
):
    df = load_df()
    return what_if(df, k, branding_weight, stabling_weight)

@app.get("/api/whatif/defaults")
def whatif_defaults():
    return {"k": 3, "branding_weight": 2000, "stabling_weight": 5}

# -------------------------------
# PDF REPORTS
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
    chart_path = "status_chart.png"
    plt.savefig(chart_path)
    plt.close()

    # PDF
    filename = "status_report.pdf"
    c = canvas.Canvas(filename, pagesize=letter)
    c.setFont("Helvetica-Bold", 16)
    c.drawString(100, 750, "Eligible vs Blocked Trains Report")
    c.setFont("Helvetica", 12)
    c.drawString(100, 720, f"Eligible trains: {eligible}")
    c.drawString(100, 700, f"Blocked trains: {blocked}")
    c.drawImage(ImageReader(chart_path), 100, 400, width=300, height=300)
    c.save()

    return FileResponse(filename, media_type="application/pdf", filename=filename)

@app.get("/api/report/whatif-pdf")
def generate_whatif_report(
    k: int = 3,
    branding_weight: float = 2000,
    stabling_weight: float = 5
):
    df = load_df()
    before_df = optimize_trains(df, k)
    after_df = what_if(df, k, branding_weight, stabling_weight)

    before_avg = sum(r["score"] for r in before_df) / len(before_df)
    after_avg = sum(r["score"] for r in after_df) / len(after_df)

    plt.figure(figsize=(4,4))
    plt.bar(["Before","After"], [before_avg, after_avg], color=["#2196F3","#FFC107"])
    chart_path = "whatif_chart.png"
    plt.savefig(chart_path)
    plt.close()

    filename = "whatif_report.pdf"
    c = canvas.Canvas(filename, pagesize=letter)
    c.setFont("Helvetica-Bold", 16)
    c.drawString(100, 750, "What-If Analysis Report")
    c.setFont("Helvetica", 12)
    c.drawString(100, 720, f"Before Avg Score: {before_avg:.2f}")
    c.drawString(100, 700, f"After Avg Score: {after_avg:.2f}")
    c.drawImage(ImageReader(chart_path), 100, 400, width=300, height=300)
    c.save()

    return FileResponse(filename, media_type="application/pdf", filename=filename)

@app.get("/api/report/alerts-pdf")
def generate_alerts_report():
    df = load_df()
    df[['status','alerts']] = df.apply(apply_rules, axis=1)

    alert_counts = {}
    for row in df.itertuples():
        if row.alerts and row.alerts != "-":
            for alert in row.alerts.split(";"):
                alert_counts[alert.strip()] = alert_counts.get(alert.strip(), 0) + 1

    plt.figure(figsize=(6,4))
    plt.bar(alert_counts.keys(), alert_counts.values(), color="#ffc107")
    plt.ylabel("Number of Trains")
    plt.title("Alerts Distribution")
    plt.xticks(rotation=45, ha="right")
    chart_path = "alerts_chart.png"
    plt.tight_layout()
    plt.savefig(chart_path)
    plt.close()

    filename = "alerts_report.pdf"
    c = canvas.Canvas(filename, pagesize=letter)
    c.setFont("Helvetica-Bold", 16)
    c.drawString(100, 750, "Alerts Distribution Report")
    c.setFont("Helvetica", 12)
    y = 720
    for alert, count in alert_counts.items():
        c.drawString(100, y, f"{alert}: {count}")
        y -= 20
    c.drawImage(ImageReader(chart_path), 100, y - 300, width=400, height=300)
    c.save()

    return FileResponse(filename, media_type="application/pdf", filename=filename)
