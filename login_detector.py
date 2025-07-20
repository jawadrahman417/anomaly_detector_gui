import pandas as pd
from sklearn.ensemble import IsolationForest
import matplotlib.pyplot as plt
import seaborn as sns

# Sample login data
data = {
    'username': ['ali', 'ali', 'ahmed', 'ali', 'ahmed', 'hassan', 'ali', 'unknown'],
    'login_time': [9, 9, 10, 9, 10, 8, 9, 3],
    'location': ['Lahore', 'Lahore', 'Karachi', 'Lahore', 'Karachi', 'Islamabad', 'Lahore', 'Unknown']
}

df = pd.DataFrame(data)

# Time of day function
def time_of_day(hour):
    if 5 <= hour < 12:
        return 'morning'
    elif 12 <= hour < 17:
        return 'afternoon'
    elif 17 <= hour < 21:
        return 'evening'
    else:
        return 'night'

df['time_of_day'] = df['login_time'].apply(time_of_day)

# Encode for model
df_encoded = pd.get_dummies(df[['username', 'location', 'time_of_day']])
df_encoded['login_time'] = df['login_time']

# Isolation Forest
model = IsolationForest(contamination=0.2, random_state=42)
model.fit(df_encoded)
df['is_anomaly'] = model.predict(df_encoded)
df['is_anomaly'] = df['is_anomaly'].apply(lambda x: 'Yes' if x == -1 else 'No')

# Visualization starts here

# Count of anomalies by username
plt.figure(figsize=(8,4))
sns.countplot(data=df, x='username', hue='is_anomaly')
plt.title('Anomalies by Username')
plt.show()

# Count of anomalies by time_of_day
plt.figure(figsize=(8,4))
order = ['morning', 'afternoon', 'evening', 'night']
sns.countplot(data=df, x='time_of_day', hue='is_anomaly', order=order)

plt.title('Anomalies by Time of Day')
plt.show()

# Count of anomalies by location
plt.figure(figsize=(8,4))
sns.countplot(data=df, x='location', hue='is_anomaly')
plt.title('Anomalies by Location')
plt.xticks(rotation=45)
plt.show()
