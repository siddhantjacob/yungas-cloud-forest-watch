import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import spearmanr

# 1. Load local CSV outputs
cloud_df = pd.read_csv("outputs/cloud_visibility_grid.csv")
loss_df = pd.read_csv("outputs/forest_loss_grid.csv")

# 2. Round coordinates and check for duplicates
cloud_df["lat_round"] = cloud_df["lat"].round(3)
cloud_df["lon_round"] = cloud_df["lon"].round(3)
loss_df["lat_round"] = loss_df["lat"].round(3)
loss_df["lon_round"] = loss_df["lon"].round(3)

print("Dupes in cloud_df:", cloud_df.duplicated(subset=["lat_round", "lon_round"]).sum())
print("Dupes in loss_df:", loss_df.duplicated(subset=["lat_round", "lon_round"]).sum())

# Merge grids
df = pd.merge(cloud_df, loss_df, on=["lat_round", "lon_round"], suffixes=("_cloud", "_loss"))
df = df.dropna(subset=["clear_fraction", "loss_fraction"])

print(f"Merged length: {len(df)} (cloud: {len(cloud_df)}, loss: {len(loss_df)})")

# 3. Descriptive Spearman correlation
rho, _ = spearmanr(df["clear_fraction"], df["loss_fraction"])
print(f"\nSpearman rho (clear_fraction vs loss_fraction): {rho:.3f}")

# 4. Corrected Quadrant Classification
# Visibility threshold: median clear fraction (~0.33)
# Forest loss threshold: > 0 (cells that actually experienced forest loss)
clear_median = df["clear_fraction"].median()

def classify(row):
    vis = "good_visibility" if row["clear_fraction"] >= clear_median else "poor_visibility"
    loss = "has_loss" if row["loss_fraction"] > 0 else "no_loss"
    return f"{vis}__{loss}"

df["quadrant"] = df.apply(classify, axis=1)
quadrant_counts = df["quadrant"].value_counts()
print("\nCells per quadrant:")
print(quadrant_counts)

# Quantify actual loss cells in poor visibility
total_loss_cells = (df["loss_fraction"] > 0).sum()
blind_spot_cells = quadrant_counts.get("poor_visibility__has_loss", 0)
blind_spot_pct = (blind_spot_cells / total_loss_cells) * 100 if total_loss_cells > 0 else 0

print(f"\nTotal 1km cells with forest loss (>0): {total_loss_cells} ({100 * total_loss_cells / len(df):.1f}% of belt)")
print(f"Forest loss cells in poor visibility (< {clear_median:.2f}): {blind_spot_cells} ({blind_spot_pct:.1f}% of loss cells)")

df.to_csv("outputs/combined_grid.csv", index=False)

# 5. Plot updated figure
colors = {
    "good_visibility__no_loss": "#4C9A2A",
    "good_visibility__has_loss": "#F2A93B",
    "poor_visibility__no_loss": "#9BB7D4",
    "poor_visibility__has_loss": "#D64545",  # monitoring blind spot
}

labels = {
    "good_visibility__no_loss": "Good visibility, no loss",
    "good_visibility__has_loss": "Good visibility, any detected loss",
    "poor_visibility__no_loss": "Poor visibility, no loss",
    "poor_visibility__has_loss": "POOR VISIBILITY, ANY DETECTED LOSS (34.9% of loss cells)",
}

fig, ax = plt.subplots(figsize=(8, 7))
for quad, color in colors.items():
    subset = df[df["quadrant"] == quad]
    ax.scatter(
        subset["clear_fraction"], subset["loss_fraction"],
        c=color, label=f"{labels[quad]} (n={len(subset)})",
        s=18, alpha=0.75, edgecolors="none",
    )

ax.axvline(clear_median, color="gray", linestyle="--", linewidth=1, label=f"Median Visibility ({clear_median:.2f})")
ax.axhline(0, color="gray", linestyle=":", linewidth=1)
ax.set_xlabel("Clear-observation fraction, 2021–2025 (Sentinel-2)")
ax.set_ylabel("Forest-loss fraction, 2021–2025 (Hansen GFC)")
ax.set_title(
    f"Yungas monitoring coverage vs. forest loss (n={len(df)} cells)\n"
    f"Spearman rho = {rho:.3f} (Visibility Median x Presence/Absence Split)"
)
ax.legend(loc="upper right", fontsize=8, framealpha=0.9)
plt.tight_layout()
plt.savefig("figures/figure3_monitoring_blindspot.png", dpi=300)