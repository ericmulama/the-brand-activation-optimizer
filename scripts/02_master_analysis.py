import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import zipfile
import os

# Setup Paths
BASE_PATH = r"E:\GIS AND REMOTE SENSING\Activation_ROI_Optimizer"
ZIP_PATH = os.path.join(BASE_PATH, "data", "tza_admbnda_adm2_20181019.zip")
CSV_PATH = os.path.join(BASE_PATH, "data", "apex_horizon_marketing_data.csv")
OUT_DIR = os.path.join(BASE_PATH, "outputs")
os.makedirs(OUT_DIR, exist_ok=True)


def run_analysis():
    # 1. Load Spatial Data
    with zipfile.ZipFile(ZIP_PATH, "r") as z:
        z.extractall("temp_shp")
    shp_file = [f for f in os.listdir("temp_shp") if f.endswith(".shp")][0]
    gdf = gpd.read_file(os.path.join("temp_shp", shp_file), engine="pyogrio")

    # 2. Load & Process Business Data
    df = pd.read_csv(CSV_PATH)

    # --- PART A: FINANCIAL CONTROLLING LOGIC ---
    df["Variance_%"] = (
        (df["Actual_Spend_USD"] - df["Budget_USD"]) / df["Budget_USD"]
    ) * 100
    df["Audit_Status"] = df["Variance_%"].apply(
        lambda x: "Over Budget" if x > 10 else "Within Limits"
    )

    # --- PART B: MARKETING KPI LOGIC ---
    # Engagement Rate: How many people interacted vs how many saw it
    df["Engagement_Rate_%"] = (df["Total_Engagements"] / df["Total_Reach"]) * 100
    # ROI Score: Scaled metric for mapping
    df["ROI_Score"] = (df["Total_Engagements"] / df["Actual_Spend_USD"]) * 10
    # Cost Per Engagement (CPE)
    df["CPE_USD"] = df["Actual_Spend_USD"] / df["Total_Engagements"]

    # 3. Merge for Visualization
    merged = gdf.merge(df, on="ADM2_PCODE", how="left")

    # 4. Visualization
    fig, ax = plt.subplots(1, 1, figsize=(12, 10))
    gdf.plot(ax=ax, color="#f2f2f2", edgecolor="#adadad", linewidth=0.5)
    merged.dropna(subset=["ROI_Score"]).plot(
        column="ROI_Score",
        ax=ax,
        legend=True,
        cmap="YlGn",
        legend_kwds={"label": "District Performance ROI", "orientation": "horizontal"},
    )
    plt.title("Apex Horizon: Tanzania Regional Marketing Efficiency Audit", fontsize=15)
    ax.axis("off")
    plt.savefig(os.path.join(OUT_DIR, "Apex_Horizon_ROI_Map.png"), dpi=300)

    # 5. Export Reports (Separated for Stakeholders)

    # Report 01: For Finance & Controlling
    finance_cols = [
        "District",
        "Budget_USD",
        "Actual_Spend_USD",
        "Variance_%",
        "Audit_Status",
    ]
    df[finance_cols].to_csv(
        os.path.join(OUT_DIR, "Report_01_Financial_Audit.csv"), index=False
    )

    # Report 02: For Marketing Strategy & R&D
    marketing_cols = [
        "District",
        "Total_Reach",
        "Total_Engagements",
        "Engagement_Rate_%",
        "CPE_USD",
    ]
    df[marketing_cols].to_csv(
        os.path.join(OUT_DIR, "Report_02_Marketing_Funnel.csv"), index=False
    )

    print(f"✅ Analysis complete.")
    print(f"📊 Report 1 (Finance) and Report 2 (Marketing) saved in: {OUT_DIR}")


if __name__ == "__main__":
    run_analysis()
