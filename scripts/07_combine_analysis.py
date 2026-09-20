import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import spearmanr

# 1. Load local CSV outputs saved in Step 5 and Step 6
cloud_df = pd.read_csv("outputs/cloud_visibility_grid.csv")
loss_df = pd.read_csv("outputs/forest_loss_grid.csv")

# 2. Round coordinates to align the 1km grid cells
cloud_df["lat_round"] = cloud_df["lat"].round(3)
cloud_df["lon_round"] = cloud_df["lon"].round(3)
loss_df["lat_round"] = loss_df["lat"].round(3)
loss_df["lon_round"] = loss_df["lon"].round(3)

# 3. Merge grids locally on rounded coordinates
df = pd.merge(cloud_df, loss_df, on=["lat_round", "lon_round"], suffixes=("_cloud", "_loss"))
df = df.dropna(subset=["clear_fraction", "loss_fraction"])

# Clean up column names
df["lat"] = df["lat_cloud"]
df["lon"] = df["lon_cloud"]
df = df.drop(columns=["lat_cloud", "lon_cloud", "lat_loss", "lon_loss", "lat_round", "lon_round"])

df.to_csv("outputs/combined_grid.csv", index=False)
print(f"Successfully merged {len(df)} grid cells locally.")

# 4. Descriptive Spearman correlation
rho, _ = spearmanr(df["clear_fraction"], df["loss_fraction"])
print(f"\nSpearman rho (clear_fraction vs loss_fraction): {rho:.3f}")
print("Reported as a descriptive association only -- grid cells are spatially")
print("correlated with their neighbours, so no p-value is quoted here.")

# 5. Median-split quadrant classification
clear_median = df["clear_fraction"].median()
loss_median = df["loss_fraction"].median()

def classify(row):
    vis = "good_visibility" if row["clear_fraction"] >= clear_median else "poor_visibility"
    dist = "high_loss" if row["loss_fraction"] >= loss_median else "low_loss"
    return f"{vis}__{dist}"

df["quadrant"] = df.apply(classify, axis=1)
quadrant_counts = df["quadrant"].value_counts()
print("\nCells per quadrant:")
print(quadrant_counts)

blind_spot_n = quadrant_counts.get("poor_visibility__high_loss", 0)
print(f"\nMonitoring blind spot (poor visibility + high loss): {blind_spot_n} cells "
      f"({100 * blind_spot_n / len(df):.1f}% of the belt's 1km grid)")

# 6. Generate Figure 3
colors = {
    "good_visibility__low_loss": "#4C9A2A",
    "good_visibility__high_loss": "#F2A93B",
    "poor_visibility__low_loss": "#9BB7D4",
    "poor_visibility__high_loss": "#D64545",  # monitoring blind spot
}
labels = {
    "good_visibility__low_loss": "Good visibility, low loss",
    "good_visibility__high_loss": "Good visibility, high loss",
    "poor_visibility__low_loss": "Poor visibility, low loss",
    "poor_visibility__high_loss": "MONITORING BLIND SPOT (poor visibility, high loss)",
}

fig, ax = plt.subplots(figsize=(8, 7))
for quad, color in colors.items():
    subset = df[df["quadrant"] == quad]
    ax.scatter(
        subset["clear_fraction"], subset["loss_fraction"],
        c=color, label=f"{labels[quad]} (n={len(subset)})",
        s=18, alpha=0.75, edgecolors="none",
    )

ax.axvline(clear_median, color="gray", linestyle="--", linewidth=1)
ax.axhline(loss_median, color="gray", linestyle="--", linewidth=1)
ax.set_xlabel("Clear-observation fraction, 2021–2025 (Sentinel-2)")
ax.set_ylabel("Forest-loss fraction, 2021–2025 (Hansen GFC)")
ax.set_title(
    f"Yungas monitoring coverage vs. forest loss (n={len(df)} cells)\n"
    f"Spearman rho = {rho:.3f} (descriptive, spatially correlated data)"
)
ax.legend(loc="upper right", fontsize=8, framealpha=0.9)
plt.tight_layout()
plt.savefig("figures/figure3_monitoring_blindspot.png", dpi=300)
print("\nSaved figures/figure3_monitoring_blindspot.png")