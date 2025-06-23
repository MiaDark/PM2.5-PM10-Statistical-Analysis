import pandas as pd

# Read the sensor data file (cleaned file with no missing values)
sensor_df = pd.read_csv('../data_cleaning/thingspeak_data_april_to_june_cleaned.csv')

# Read the occupancy file
occupancy_df = pd.read_csv('occupancy_expanded.csv', sep=';')

# Parse the Date column in occupancy_df to extract day and month
occupancy_df['Date'] = pd.to_datetime(occupancy_df['Date'], format='%d.%m.%Y')
occupancy_df['day'] = occupancy_df['Date'].dt.day
occupancy_df['month'] = occupancy_df['Date'].dt.month

# Extract the starting hour from the Hour column (e.g., '00:00-01:00' -> 0)
occupancy_df['hour'] = occupancy_df['Hour'].str.split('-').str[0].str[:2].astype(int)

# Select relevant columns for merging
occupancy_df = occupancy_df[['day', 'month', 'hour', 'Occupied']]

# Merge the dataframes on day, month, and hour
# Use left join to keep all rows from sensor_df and add Occupied where available
merged_df = sensor_df.merge(occupancy_df, on=['day', 'month', 'hour'], how='left')

# Save the merged result to a new CSV file
merged_df.to_csv('merged_sensor_data_labeled.csv', index=False)