import pandas as pd
import os

n_prime_df = pd.read_csv("n_prime.csv")
n1_df = pd.read_csv("n1.csv")
n2_df = pd.read_csv("n2.csv")
n3_df = pd.read_csv("n3.csv")

for df in [n_prime_df, n1_df, n2_df, n3_df]:
    df["UTC"] = pd.to_datetime(df["UTC"])


def assign_frequency_category(row):
    # Check if date is March 31st (holiday)
    if row["UTC"].date() == pd.to_datetime("2025-03-31").date():
        return "none"

    day_of_week = row["UTC"].dayofweek
    hour = row["UTC"].hour

    if day_of_week in [5, 6]:  # Weekend
        return "none"
    else:  # Weekday
        if 6 <= hour < 8:
            return "low"
        elif 8 <= hour < 19:
            return "high"
        else:
            return "none"


datasets = {"n'": n_prime_df, "n1": n1_df, "n2": n2_df, "n3": n3_df}

for sensor, df in datasets.items():
    df["frequency_category"] = df.apply(assign_frequency_category, axis=1)

    if sensor == "n3":
        df["windows_open"] = (
            (df["UTC"].dt.dayofweek < 5)
            & (df["UTC"].dt.hour >= 6)
            & (df["UTC"].dt.hour < 7)
        )

    print(f"\n{sensor} category counts:")
    print(df["frequency_category"].value_counts())

output_path = "data-sort/categories-by-frequency"
os.makedirs(output_path, exist_ok=True)
for sensor, df in datasets.items():
    df.to_csv(f"{output_path}/{sensor}_pm_data.csv", index=False)
    print(f"Saved updated {sensor} dataset with frequency_category column.")

print("\nn1 dataset sample with frequency_category:")
print(n1_df[["UTC", "pm25", "pm10", "frequency_category"]].head())

print("\nn3 dataset sample with frequency_category and windows_open:")
print(
    n3_df[["UTC", "pm25", "pm10", "frequency_category", "windows_open"]].head()
)
