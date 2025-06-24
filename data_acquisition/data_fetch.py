import pandas as pd
import requests
from datetime import datetime, timedelta
import time
import concurrent.futures
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# [Your existing imports and setup code remain unchanged]
# Set date range
end_date = datetime(2025, 6, 1)
start_date = datetime(2025, 4, 1)

# ThingSpeak channels
channels = [
    {"id": "481426", "api_key": "04BRBQC8TINJHYQI", "metrics": ["pm25", "pm10", "CO", "NO2"]},
    {"id": "481429", "api_key": "P9BGUFJI73H1CFRX", "metrics": ["pm25", "pm10"]}
]

# Field mapping
field_mapping = {"field1": "pm25", "field2": "pm10", "field3": "CO", "field4": "NO2"}

# Function to fetch data for a channel (with retry logic)
def fetch_channel_data(channel_id, api_key, start_str, end_str, channel_name):
    # Set up session with retry strategy
    session = requests.Session()
    retries = Retry(total=3, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504])
    session.mount('https://', HTTPAdapter(max_retries=retries))
    
    url = f"https://api.thingspeak.com/channels/{channel_id}/feeds.json?api_key={api_key}&start={start_str}&end={end_str}&timescale=60"
    try:
        response = session.get(url, timeout=30)
        if response.status_code == 200:
            data = response.json()
            if 'feeds' in data and data['feeds']:
                df = pd.DataFrame(data['feeds'])
                df['channel'] = channel_name
                df['timestamp'] = pd.to_datetime(df['created_at']).dt.tz_localize(None)
                for field, metric in field_mapping.items():
                    if field in df.columns:
                        df[metric] = pd.to_numeric(df[field], errors='coerce')
                return df[['timestamp', 'channel'] + [m for m in field_mapping.values() if m in df.columns]]
            print(f"No data for {channel_name} in this period")
            return pd.DataFrame()
        print(f"Error {response.status_code} for {channel_name}")
        return pd.DataFrame()
    except Exception as e:
        print(f"Exception for {channel_name}: {str(e)}")
        return pd.DataFrame()
    finally:
        session.close()

# [Your existing hourly template code remains unchanged]
# Create hourly template
all_hours = pd.date_range(start=start_date, end=end_date, freq='H')
template_df = pd.DataFrame({
    'timestamp': all_hours,
    'day': all_hours.day,
    'month': all_hours.month,
    'hour': all_hours.hour
})

# Process data in chunks
chunk_size = timedelta(days=3)
current_start = start_date
all_data = []

# Modified channel iteration with parallel fetching
while current_start < end_date:
    current_end = min(current_start + chunk_size, end_date)
    start_str = current_start.strftime("%Y-%m-%d%%20%H:%M:%S")
    end_str = current_end.strftime("%Y-%m-%d%%20%H:%M:%S")
    
    print(f"Processing {current_start} to {current_end}")
    
    # Fetch data for all channels concurrently
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        # Map fetch_channel_data to each channel
        future_to_channel = {
            executor.submit(
                fetch_channel_data,
                channel['id'],
                channel['api_key'],
                start_str,
                end_str,
                f"n{i+1}"
            ): f"n{i+1}" for i, channel in enumerate(channels)
        }
        
        # Collect results as they complete
        for future in concurrent.futures.as_completed(future_to_channel):
            channel_name = future_to_channel[future]
            try:
                df = future.result()
                if not df.empty:
                    all_data.append(df)
                # Respect ThingSpeak rate limits (e.g., 15-second delay between batches)
                time.sleep(0.5)  # Small delay per channel to avoid overwhelming API
            except Exception as e:
                print(f"Error processing {channel_name}: {str(e)}")
    
    current_start = current_end

# [Your existing combine and process data code remains unchanged]
if all_data:
    combined_df = pd.concat(all_data, ignore_index=True)
    
    # Round timestamps to nearest hour
    combined_df['hour_timestamp'] = combined_df['timestamp'].dt.round('H')
    
    # Pivot data for each channel and metric
    result_df = template_df.copy()
    for i, channel in enumerate(channels):
        channel_name = f"n{i+1}"
        channel_data = combined_df[combined_df['channel'] == channel_name]
        
        for metric in channel['metrics']:
            metric_data = channel_data.groupby(channel_data['hour_timestamp'])[metric].mean().reset_index()
            metric_data.columns = ['timestamp', f"{channel_name}-{metric}"]
            result_df = pd.merge(result_df, metric_data, on='timestamp', how='left')

    # Format output
    result_df['UTC'] = result_df.apply(
        lambda row: f"{int(row['month'])}/{int(row['day'])}/{end_date.year} {int(row['hour'])}:00:00",
        axis=1
    )
    result_df['ID'] = range(len(result_df))
    
    # Reorder columns
    id_cols = ['ID', 'UTC', 'day', 'month', 'hour']
    data_cols = sorted([col for col in result_df.columns if col not in id_cols + ['timestamp']])
    result_df = result_df[id_cols + data_cols]
    
    # Format numbers
    for col in data_cols:
        result_df[col] = pd.to_numeric(result_df[col], errors='coerce').round(3)
        result_df[col] = result_df[col].apply(lambda x: int(x) if pd.notnull(x) and x == int(x) else x)
    
    # Save to Excel
    result_df.to_csv("thingspeak_data_april_to_june.csv", index=False)
    print(f"Processed {len(result_df)} hourly records")
else:
    print("No data retrieved")