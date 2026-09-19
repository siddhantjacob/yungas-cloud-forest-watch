import pandas as pd
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA

df = pd.read_csv("outputs/pca_env.csv")
variables = ["elevation", "temp_c", "precip_mm"]

# PCA needs variables on the same scale, or the one with the biggest raw
# numbers (precip_mm, in the hundreds-to-thousands) will dominate for no
# real reason -- StandardScaler rescales each variable to mean 0, std 1
X = StandardScaler().fit_transform(df[variables])

pca = PCA(n_components=2)
coords = pca.fit_transform(X)
df["PC1"] = coords[:, 0]
df["PC2"] = coords[:, 1]

variance_explained = pca.explained_variance_ratio_
print(f"PC1 explains {variance_explained[0]*100:.1f}% of variation")
print(f"PC2 explains {variance_explained[1]*100:.1f}% of variation")
# If these two numbers add up to well under 70%, the 2D plot is hiding a lot
# of real structure -- worth saying so honestly in the README rather than
# ignoring it.

fig, ax = plt.subplots(figsize=(8, 6))
for group, color in [("background", "#7fb3d5"), ("occurrence", "#e67e22")]:
    subset = df[df["group"] == group]
    ax.scatter(subset["PC1"], subset["PC2"], label=f"{group} (n={len(subset)})",
               alpha=0.5, s=20, color=color)
ax.set_xlabel(f"PC1 ({variance_explained[0]*100:.0f}% of variation)")
ax.set_ylabel(f"PC2 ({variance_explained[1]*100:.0f}% of variation)")
ax.set_title("Environmental space: historical tiger-cat records vs.\nBolivian Yungas landscape background")
ax.legend()
fig.tight_layout()
fig.savefig("figures/figure1_pca.png", dpi=300)
print("Saved figures/figure1_pca.png")

df.to_csv("outputs/pca_results.csv", index=False)