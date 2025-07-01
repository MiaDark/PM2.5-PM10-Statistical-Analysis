import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.font_manager import FontProperties

csfont = {"fontname": "Times New Roman"}
legend_font = FontProperties(family="Times New Roman")

try:
    df = pd.read_csv("resources/merged_sensor_data_labeled.csv")
except FileNotFoundError:
    print("Error: CSV file not found. Please check the file path.")
    exit()

required_columns = ["hour", "Occupied", "n1-pm10", "n1-pm25", "day", "month"]
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

df["Occupied"] = df["Occupied"].replace({"Yes": "Да", "No": "Не"})

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
    print("Error: No data remains after removing the specified outlier.")
    exit()

grouped = (
    df.groupby(["hour", "Occupied"])[["n1-pm10", "n1-pm25"]]
    .mean()
    .reset_index()
)

if grouped.empty:
    print("Error: Grouped data is empty. Check 'hour' and 'Occupied' columns.")
    exit()

sns.set_theme(style="whitegrid")

plt.figure(figsize=(14, 6))

# Plot for n1-pm10
plt.subplot(1, 2, 1)
sns.lineplot(data=grouped, x="hour", y="n1-pm10", hue="Occupied", marker="o")
plt.title("Средна вредност на PM10 по час и зафатеност", **csfont)
plt.ylabel("Средна вредност на PM10 (µg/m³)", **csfont)
plt.xlabel("Час", **csfont)
plt.legend(
    title="Зафатеност", prop=legend_font, title_fontproperties=legend_font
)

# Plot for n1-pm25
plt.subplot(1, 2, 2)
sns.lineplot(data=grouped, x="hour", y="n1-pm25", hue="Occupied", marker="o")
plt.title("Средна вредност на PM25 по час и зафатеност", **csfont)
plt.ylabel("Средна вредност на PM25 (µg/m³)", **csfont)
plt.xlabel("Час", **csfont)
plt.legend(
    title="Зафатеност", prop=legend_font, title_fontproperties=legend_font
)

plt.tight_layout()
plt.savefig("visuelizations/people_effect_temporal_interaction.png")
plt.show()

# Print mean concentrations by hour and occupancy
print("Mean PM Concentrations by Hour and Occupancy:\n")
for hour in sorted(grouped["hour"].unique()):
    print(f"Hour {hour}:")
    for occ in ["Не", "Да"]:
        subset = grouped[
            (grouped["hour"] == hour) & (grouped["Occupied"] == occ)
        ]
        if not subset.empty:
            print(f"  Occupied={occ}:")
            print(f"    n1-pm10: {subset['n1-pm10'].values[0]:.2f} µg/m³")
            print(f"    n1-pm25: {subset['n1-pm25'].values[0]:.2f} µg/m³")
        else:
            print(f"  Occupied={occ}: No data")
    print()
