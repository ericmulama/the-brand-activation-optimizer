import pandas as pd
import numpy as np
import os
import geopandas as gpd
import zipfile

# Configuration
PATH = r"E:\GIS AND REMOTE SENSING\Activation_ROI_Optimizer"
ZIP_PATH = os.path.join(PATH, "data", "tza_admbnda_adm2_20181019.zip")
os.makedirs(os.path.join(PATH, "data"), exist_ok=True)


def generate_nationwide_data():
    # 1. Extract the zip to get the full list of districts
    with zipfile.ZipFile(ZIP_PATH, "r") as z:
        z.extractall("temp_list")

    shp_file = [f for f in os.listdir("temp_list") if f.endswith(".shp")][0]
    # We use pyogrio here too for consistency
    gdf = gpd.read_file(os.path.join("temp_list", shp_file), engine="pyogrio")

    # 2. Extract all unique District PCodes and Names from your shapefile
    all_districts = gdf[["ADM2_PCODE", "ADM2_EN"]].copy()

    # 3. Generate random marketing data for EVERY district
    np.random.seed(42)
    data = []

    for _, row in all_districts.iterrows():
        # Logic: Make some districts "Major Hubs" with bigger budgets
        is_hub = any(
            city in row["ADM2_EN"]
            for city in ["Ilala", "Kinondoni", "Arusha", "Mwanza", "Dodoma"]
        )
        multiplier = 5 if is_hub else 1

        budget = np.random.randint(2000, 8000) * multiplier
        actual = budget * np.random.uniform(0.8, 1.3)
        reach = int(actual * np.random.uniform(20, 60))
        engagements = int(reach * np.random.uniform(0.03, 0.12))

        data.append(
            {
                "ADM2_PCODE": row["ADM2_PCODE"],
                "District": row["ADM2_EN"],
                "Budget_USD": budget,
                "Actual_Spend_USD": round(actual, 2),
                "Total_Reach": reach,
                "Total_Engagements": engagements,
            }
        )

    # 4. Save the full nationwide dataset
    df = pd.DataFrame(data)
    df.to_csv(
        os.path.join(PATH, "data", "apex_horizon_marketing_data.csv"), index=False
    )
    print(f"✅ Nationwide data generated! {len(df)} districts included in the CSV.")


if __name__ == "__main__":
    generate_nationwide_data()
