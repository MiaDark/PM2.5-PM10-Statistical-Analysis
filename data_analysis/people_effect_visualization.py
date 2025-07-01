import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

csfont = {"fontname": "Times New Roman"}

# Load the dataset
df = pd.read_csv("resources/merged_sensor_data_labeled.csv")

# Set seaborn style for better aesthetics
sns.set(style="whitegrid")

# Create figure with two subplots (boxplots and violin plots)
plt.figure(figsize=(12, 8))
df["Occupied"] = df["Occupied"].replace({"Yes": "Да", "No": "Не"})


# Boxplot for n1-pm10
plt.subplot(2, 2, 1)
sns.boxplot(x="Occupied", y="n1-pm10", data=df)
plt.title("Податоци од сензорот при зафатена просторија", **csfont)
plt.ylabel("Концентрација на PM10 (µg/m³)", **csfont)
plt.xlabel("Зафатеност", **csfont)

# Boxplot for n1-pm25
plt.subplot(2, 2, 2)
sns.boxplot(x="Occupied", y="n1-pm25", data=df)
plt.title("Податоци од сензорот при зафатена просторија", **csfont)
plt.ylabel("PM25 Concentration (µg/m³)", **csfont)
plt.xlabel("Зафатеност", **csfont)

# Violin plot for n1-pm10
plt.subplot(2, 2, 3)
sns.violinplot(x="Occupied", y="n1-pm10", data=df)
plt.title("Податоци од сензорот при зафатена просторија", **csfont)
plt.ylabel("Концентрација на PM10 (µg/m³)", **csfont)
plt.xlabel("Зафатеност", **csfont)
# Violin plot for n1-pm25
plt.subplot(2, 2, 4)
sns.violinplot(x="Occupied", y="n1-pm25", data=df)
plt.title("Податоци од сензорот при зафатена просторија", **csfont)
plt.ylabel("PM25 Concentration (µg/m³)", **csfont)
plt.xlabel("Зафатеност", **csfont)


plt.tight_layout()
plt.savefig("resources/people_effect_pm.png")
plt.show()
