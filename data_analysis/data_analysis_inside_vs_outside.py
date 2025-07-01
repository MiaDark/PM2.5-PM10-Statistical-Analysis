import pandas as pd
import scipy.stats as stats
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import kstest
from matplotlib.font_manager import FontProperties

# Font settings
csfont = {"fontname": "Times New Roman"}
legend_font = FontProperties(family="Times New Roman")

# Load data
try:
    df = pd.read_csv(
        "resources/thingspeak_data_april_to_june_cleaned_outVSin.csv"
    )
except FileNotFoundError:
    print("Error: CSV file not found. Please check the file path.")
    exit()

# Check if required columns exist
required_columns = ["n1-pm10", "n1-pm25", "n2-pm10", "n2-pm25"]
if not all(col in df.columns for col in required_columns):
    missing_cols = [col for col in required_columns if col not in df.columns]
    print(
        f"Error: CSV must contain columns: {required_columns}. Missing: {missing_cols}"
    )
    exit()

# Check if DataFrame is empty
if df.empty:
    print("Error: CSV file is empty.")
    exit()

# Remove rows where any of n1-pm10, n1-pm25, n2-pm10, or n2-pm25 exceed 20 µg/m³
outlier_condition = (
    (df["n1-pm10"] > 20)
    | (df["n1-pm25"] > 20)
    | (df["n2-pm10"] > 20)
    | (df["n2-pm25"] > 20)
)
outlier_count = len(df[outlier_condition])
df = df[~outlier_condition]
print(
    f"Removed {outlier_count} row(s) where n1-pm10, n1-pm25, n2-pm10, or n2-pm25 > 20 µg/m³"
)

# Check if data remains after outlier removal
if df.empty:
    print("Error: No data remains after removing outliers.")
    exit()

# Rename columns
df = df.rename(
    columns={
        "n1-pm10": "Внатрешен сензор (PM10)",
        "n2-pm10": "Надворешен сензор (PM10)",
        "n1-pm25": "Внатрешен сензор (PM2.5)",
        "n2-pm25": "Надворешен сензор (PM2.5)",
    }
)

# Statistical comparisons
comparisons = [
    (
        df["Надворешен сензор (PM10)"].dropna(),
        df["Внатрешен сензор (PM10)"].dropna(),
        "Надворешен сензор (PM10)",
        "Внатрешен сензор (PM10)",
        "pm10: Outside vs Inside",
    ),
    (
        df["Надворешен сензор (PM2.5)"].dropna(),
        df["Внатрешен сензор (PM2.5)"].dropna(),
        "Надворешен сензор (PM2.5)",
        "Внатрешен сензор (PM2.5)",
        "pm25: Outside vs Inside",
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

# Visualization
plt.figure(figsize=(12, 6))
plt.subplot(2, 1, 1)
sns.boxplot(data=df[["Надворешен сензор (PM10)", "Внатрешен сензор (PM10)"]])
plt.title("Споредба на PM10 (Надвор / Внатре)", **csfont)
plt.ylabel("Концентрација (µg/m³)", **csfont)
plt.xlabel("Сензор", **csfont)

plt.subplot(2, 1, 2)
sns.boxplot(data=df[["Надворешен сензор (PM2.5)", "Внатрешен сензор (PM2.5)"]])
plt.title("Споредба на PM25 (Надвор / Внатре)", **csfont)
plt.ylabel("Концентрација (µg/m³)", **csfont)
plt.xlabel("Сензор", **csfont)

plt.tight_layout()
plt.savefig("inside_vs_outside_pm10_pm25.png")
plt.show()
