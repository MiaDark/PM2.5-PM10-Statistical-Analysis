import pandas as pd

data = pd.read_csv("pm-dataset.csv")

data["UTC"] = pd.to_datetime(data["UTC"])

common_cols = [
    "UTC",
    "day",
    "month",
    "hour",
    "maxtempC",
    "mintempC",
    "DewPointC",
    "WindGustKmph",
    "cloudcover",
    "humidity",
    "pressure",
    "tempC",
    "precipMM",
    "winddirDegree",
    "windspeedKmph",
]

# Separate dataset for each sensor
n_prime_df = data[common_cols + ["n'-2.5", "n'-10"]].copy()
n1_df = data[common_cols + ["n1-pm25", "n1-pm10"]].copy()
n2_df = data[common_cols + ["n2-pm25", "n2-pm10"]].copy()
n3_df = data[common_cols + ["n3-pm25", "n3-pm10"]].copy()


n_prime_df.rename(columns={"n'-2.5": "pm25", "n'-10": "pm10"}, inplace=True)
n1_df.rename(columns={"n1-pm25": "pm25", "n1-pm10": "pm10"}, inplace=True)
n2_df.rename(columns={"n2-pm25": "pm25", "n2-pm10": "pm10"}, inplace=True)
n3_df.rename(columns={"n3-pm25": "pm25", "n3-pm10": "pm10"}, inplace=True)

n_prime_df.to_csv("n_prime.csv")
n1_df.to_csv("n1.csv")
n2_df.to_csv("n2.csv")
n3_df.to_csv("n3.csv")
