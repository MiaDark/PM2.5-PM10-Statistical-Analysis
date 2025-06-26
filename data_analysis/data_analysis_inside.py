import pandas as pd
import scipy.stats as stats
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import kstest, norm

# Load the dataset
df = pd.read_csv("../data_labeling/merged_sensor_data_labeled.csv")

# Define the four comparisons
comparisons = [
    # (data1, data2, label1, label2, description)
    (
        df[df["Occupied"] == "Yes"]["n1-pm10"].dropna(),
        df[df["Occupied"] == "Yes"]["n2-pm10"].dropna(),
        "n1-pm10 (Occupied=Yes)",
        "n2-pm10 (Occupied=Yes)",
        "n1-pm10 vs n2-pm10 when Occupied=Yes",
    ),
    (
        df[df["Occupied"] == "Yes"]["n1-pm25"].dropna(),
        df[df["Occupied"] == "Yes"]["n2-pm25"].dropna(),
        "n1-pm25 (Occupied=Yes)",
        "n2-pm25 (Occupied=Yes)",
        "n1-pm25 vs n2-pm25 when Occupied=Yes",
    ),
    (
        df[df["Occupied"] == "No"]["n1-pm10"].dropna(),
        df[df["Occupied"] == "Yes"]["n1-pm10"].dropna(),
        "n1-pm10 (Occupied=No)",
        "n1-pm10 (Occupied=Yes)",
        "n1-pm10: Occupied=No vs Occupied=Yes",
    ),
    (
        df[df["Occupied"] == "No"]["n1-pm25"].dropna(),
        df[df["Occupied"] == "Yes"]["n1-pm25"].dropna(),
        "n1-pm25 (Occupied=No)",
        "n1-pm25 (Occupied=Yes)",
        "n1-pm25: Occupied=No vs Occupied=Yes",
    ),
]

print("Normality and Variance Checks, Statistical Test Results:\n")

for data1, data2, label1, label2, description in comparisons:
    print(f"--- {description} ---")

    # Normality checks
    stat1, p1 = kstest(data1, "norm", args=(data1.mean(), data1.std()))
    stat2, p2 = kstest(data2, "norm", args=(data2.mean(), data2.std()))
    normal1 = p1 >= 0.05
    normal2 = p2 >= 0.05
    print(
        f"  {label1}: K-S p-value={p1:.4f} {'(Normal)' if normal1 else '(Non-normal)'}"
    )
    print(
        f"  {label2}: K-S p-value={p2:.4f} {'(Normal)' if normal2 else '(Non-normal)'}"
    )

    # Variance check
    stat_var, p_var = stats.levene(data1, data2)
    equal_var = p_var >= 0.05
    print(
        f"  Levene's p-value={p_var:.4f} {'(Equal variances)' if equal_var else '(Unequal variances)'}"
    )

    # Select and perform appropriate test
    if normal1 and normal2 and equal_var:
        t_stat, p_val = stats.ttest_ind(data1, data2, equal_var=True)
        test_name = "Student's t-test"
    elif not (normal1 and normal2):
        t_stat, p_val = stats.mannwhitneyu(
            data1, data2, alternative="two-sided"
        )
        test_name = "Mann-Whitney U test"
    else:
        t_stat, p_val = stats.ttest_ind(data1, data2, equal_var=False)
        test_name = "Welch's t-test"

    print(
        f"  {test_name}: Statistic={t_stat:.2f}, p-value={p_val:.4f} {'(Significant)' if p_val < 0.05 else '(Not significant)'}"
    )
    print(
        f"    {label1}: Mean={data1.mean():.2f}, Std={data1.std():.2f}, N={len(data1)}"
    )
    print(
        f"    {label2}: Mean={data2.mean():.2f}, Std={data2.std():.2f}, N={len(data2)}\n"
    )

# Optional: Visualization (customize as needed)
plt.figure(figsize=(12, 6))
plt.subplot(2, 2, 1)
sns.boxplot(data=df[df["Occupied"] == "Yes"][["n1-pm10", "n2-pm10"]])
plt.title("n1-pm10 vs n2-pm10 (Occupied=Yes)")

plt.subplot(2, 2, 2)
sns.boxplot(data=df[df["Occupied"] == "Yes"][["n1-pm25", "n2-pm25"]])
plt.title("n1-pm25 vs n2-pm25 (Occupied=Yes)")

plt.subplot(2, 2, 3)
sns.boxplot(x="Occupied", y="n1-pm10", data=df)
plt.title("n1-pm10 by Occupancy")

plt.subplot(2, 2, 4)
sns.boxplot(x="Occupied", y="n1-pm25", data=df)
plt.title("n1-pm25 by Occupancy")

plt.tight_layout()
plt.show()
