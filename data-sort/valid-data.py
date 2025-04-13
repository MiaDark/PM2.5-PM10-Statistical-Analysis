import pandas as pd

# Load the datasets
n_prime_df = pd.read_csv("n_prime.csv")
n1_df = pd.read_csv("n1.csv")
n2_df = pd.read_csv("n2.csv")
n3_df = pd.read_csv("n3.csv")

# Ensure UTC is in datetime format
for df in [n_prime_df, n1_df, n2_df, n3_df]:
    df["UTC"] = pd.to_datetime(df["UTC"])


# Function to analyze time periods for a dataset
def check_time_periods(df, sensor_name):
    # Filter rows where both pm25 and pm10 are not null and sort
    valid_data = (
        df.dropna(subset=["pm25", "pm10"])
        .sort_values("UTC")
        .reset_index(drop=True)
    )

    if valid_data.empty:
        print(f"{sensor_name}: No valid PM2.5 and PM10 data.")
        return

    # Get the time range
    start_time = valid_data["UTC"].min()
    end_time = valid_data["UTC"].max()
    total_records = len(valid_data)

    # Check frequency of timestamps (assuming hourly data)
    time_diffs = valid_data["UTC"].diff().dropna()
    common_freq = time_diffs.mode().iloc[0] if not time_diffs.empty else "N/A"

    # Identify gaps (assuming hourly data, gaps > 1 hour)
    gaps = time_diffs[time_diffs > pd.Timedelta(hours=1)]
    gap_count = len(gaps)

    print(f"\n{sensor_name}:")
    print(f"Time period: {start_time} to {end_time}")
    print(f"Total valid records: {total_records}")
    print(f"Common timestamp frequency: {common_freq}")
    print(f"Number of gaps (>1 hour): {gap_count}")

    if gap_count > 0:
        # Find indices where gaps occur in time_diffs
        gap_indices = gaps.index
        # Get timestamps before gaps (gap_indices - 1 in valid_data)
        timestamps_before_gaps = valid_data.iloc[gap_indices - 1]["UTC"]
        print("Timestamps before gaps:")
        print(timestamps_before_gaps.to_string(index=False))


# Apply to each dataset
check_time_periods(n_prime_df, "n' sensor")
check_time_periods(n1_df, "n1 sensor")
check_time_periods(n2_df, "n2 sensor")
check_time_periods(n3_df, "n3 sensor")
