import pandas as pd
import scipy.stats as stats
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import kstest

plt.rcParams["font.family"] = "Times New Roman"

# Load data
try:
    df = pd.read_csv("resources/merged_sensor_data_labeled.csv")
except FileNotFoundError:
    print("Error: CSV file not found. Please check the file path.")
    exit()

required_columns = [
    "hour",
    "Occupied",
    "n1-pm10",
    "n1-pm25",
    "n2-pm10",
    "n2-pm25",
    "day",
    "month",
]
if not all(col in df.columns for col in required_columns):
    missing_cols = [col for col in required_columns if col not in df.columns]
    print(
        f"Error: CSV must contain columns: {required_columns}. Missing: {missing_cols}"
    )
    exit()

if df.empty:
    print("Error: CSV file is empty.")
    exit()


if df["day"].isnull().all() or df["month"].isnull().all():
    print("Warning: 'day' or 'month' column contains only null values.")
    df["day"] = df["day"].fillna("Unknown")
    df["month"] = df["month"].fillna("Unknown")
else:
    df["day"] = df["day"].astype(str)
    df["month"] = df["month"].astype(str)

# Remove specific outliers (day 7, month 4, hours 13, 14, or 15)
outlier_condition = (
    (df["day"] == "7")
    & (df["month"] == "4")
    & ((df["hour"] == 13) | (df["hour"] == 14) | (df["hour"] == 15))
)
outlier_count = len(df[outlier_condition])
df = df[~outlier_condition]
print(
    f"Removed {outlier_count} row(s) with day=7, month=4, hours=13, 14, or 15"
)

if df.empty:
    print("Error: No data remains after removing the specified outliers.")
    exit()

# Replace 'Yes'/'No' with 'Да'/'Не'
df["Occupied"] = df["Occupied"].replace({"Yes": "Да", "No": "Не"})

# Define comparisons for statistical tests
comparisons = [
    (
        df[df["Occupied"] == "Да"]["n1-pm10"].dropna(),
        df[df["Occupied"] == "Да"]["n2-pm10"].dropna(),
        "n1-pm10 (Зафатено=Да)",
        "n2-pm10 (Зафатено=Да)",
        "n1-pm10 наспроти n2-pm10 (Зафатено=Да)",
    ),
    (
        df[df["Occupied"] == "Да"]["n1-pm25"].dropna(),
        df[df["Occupied"] == "Да"]["n2-pm25"].dropna(),
        "n1-pm25 (Зафатено=Да)",
        "n2-pm25 (Зафатено=Да)",
        "n1-pm25 наспроти n2-pm25 (Зафатено=Да)",
    ),
    (
        df[df["Occupied"] == "Не"]["n1-pm10"].dropna(),
        df[df["Occupied"] == "Да"]["n1-pm10"].dropna(),
        "n1-pm10 (Зафатено=Не)",
        "n1-pm10 (Зафатено=Да)",
        "n1-pm10: Зафатено=Не наспроти Зафатено=Да",
    ),
    (
        df[df["Occupied"] == "Не"]["n1-pm25"].dropna(),
        df[df["Occupied"] == "Да"]["n1-pm25"].dropna(),
        "n1-pm25 (Зафатено=Не)",
        "n1-pm25 (Зафатено=Да)",
        "n1-pm25: Зафатено=Не наспроти Зафатено=Да",
    ),
]

# Perform statistical tests
print("Проверка на нормалност и варијанса, резултати од статистички тестови:\n")
for data1, data2, label1, label2, description in comparisons:
    print(f"--- {description} ---")
    stat1, p1 = kstest(data1, "norm", args=(data1.mean(), data1.std()))
    stat2, p2 = kstest(data2, "norm", args=(data2.mean(), data2.std()))
    normal1 = p1 >= 0.05
    normal2 = p2 >= 0.05
    print(
        f"  {label1}: K-S p-вредност={p1:.4f} {'(Нормално)' if normal1 else '(Ненормално)'}"
    )
    print(
        f"  {label2}: K-S p-вредност={p2:.4f} {'(Нормално)' if normal2 else '(Ненормално)'}"
    )
    stat_var, p_var = stats.levene(data1, data2)
    equal_var = p_var >= 0.05
    print(
        f"  Levene p-вредност={p_var:.4f} {'(Еднакви варијанси)' if equal_var else '(Нееднакви варијанси)'}"
    )
    if normal1 and normal2 and equal_var:
        t_stat, p_val = stats.ttest_ind(data1, data2, equal_var=True)
        test_name = "Студентов t-тест"
    elif not (normal1 and normal2):
        t_stat, p_val = stats.mannwhitneyu(
            data1, data2, alternative="two-sided"
        )
        test_name = "Ман-Витни U тест"
    else:
        t_stat, p_val = stats.ttest_ind(data1, data2, equal_var=False)
        test_name = "Велчов t-тест"
    print(
        f"  {test_name}: Статистика={t_stat:.2f}, p-вредност={p_val:.4f} {'(Значајно)' if p_val < 0.05 else '(Незначајно)'}"
    )
    print(
        f"    {label1}: Средина={data1.mean():.2f}, Стд={data1.std():.2f}, N={len(data1)}"
    )
    print(
        f"    {label2}: Средина={data2.mean():.2f}, Стд={data2.std():.2f}, N={len(data2)}\n"
    )

# Visualization: Sensor comparisons when Occupied=Да
plt.figure(figsize=(12, 6))
plt.subplot(2, 1, 1)
sns.boxplot(data=df[df["Occupied"] == "Да"][["n1-pm10", "n2-pm10"]])
plt.title("n1-pm10 наспроти n2-pm10 (Зафатено=Да)")
plt.ylabel("Концентрација (µg/m³)")
plt.xlabel("Сензор")

plt.subplot(2, 1, 2)
sns.boxplot(data=df[df["Occupied"] == "Да"][["n1-pm25", "n2-pm25"]])
plt.title("n1-pm25 наспроти n2-pm25 (Зафатено=Да)")
plt.ylabel("Концентрација (µg/m³)")
plt.xlabel("Сензор")

plt.tight_layout()
plt.savefig("visuelizations/same_room_two_sensors.jpg")
plt.show()

# Visualization: PM concentrations by occupancy
plt.figure(figsize=(12, 6))
plt.subplot(2, 1, 1)
sns.boxplot(x="Occupied", y="n1-pm10", data=df)
plt.title("Концентрација на PM10 според зафатеност")
plt.ylabel("Концентрација (µg/m³)")
plt.xlabel("Зафатеност")

plt.subplot(2, 1, 2)
sns.boxplot(x="Occupied", y="n1-pm25", data=df)
plt.title("Концентрација на PM25 според зафатеност")
plt.ylabel("Концентрација (µg/m³)")
plt.xlabel("Зафатеност")

plt.tight_layout()
plt.savefig("visuelizations/occupied_non-occupied_01_07_removed_outliers.jpg")
plt.show()
