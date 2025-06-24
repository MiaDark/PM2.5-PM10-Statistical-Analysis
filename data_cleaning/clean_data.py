import pandas as pd

# Read the CSV file
df = pd.read_csv('../data_acquisition/thingspeak_data_april_to_june.csv')

# Drop rows with any missing values
df_cleaned = df.dropna()

# Save the cleaned data to a new CSV file
df_cleaned.to_csv('thingspeak_data_april_to_june_cleaned.csv', index=False)