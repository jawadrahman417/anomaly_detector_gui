import pandas as pd
import argparse
from sklearn.ensemble import IsolationForest
import sys
import os

# ===== Helper Functions =====

def time_of_day(hour):
    """Classify hour into time-of-day bucket."""
    if 5 <= hour < 12:
        return 'morning'
    elif 12 <= hour < 17:
        return 'afternoon'
    elif 17 <= hour < 21:
        return 'evening'
    else:
        return 'night'

def detect_anomalies(file_path, contamination):
    """Run Isolation Forest on login data CSV."""
    try:
        df = pd.read_csv(file_path)
    except Exception as e:
        print(f"❌ Error reading file: {e}")
        sys.exit(1)

    required_cols = {'username', 'login_time', 'location'}
    if not required_cols.issubset(df.columns):
        print(f"❌ CSV must contain columns: {', '.join(required_cols)}")
        sys.exit(1)

    if not pd.api.types.is_numeric_dtype(df['login_time']):
        print("❌ Column 'login_time' must be numeric (0–23 hours).")
        sys.exit(1)

    # Feature Engineering
    df['time_of_day'] = df['login_time'].apply(time_of_day)
    df_encoded = pd.get_dummies(df[['username', 'location', 'time_of_day']])
    df_encoded['login_time'] = df['login_time']

    # Model Training
    model = IsolationForest(contamination=contamination, random_state=42)
    model.fit(df_encoded)

    df['is_anomaly'] = model.predict(df_encoded)
    df['is_anomaly'] = df['is_anomaly'].apply(lambda x: 'Yes' if x == -1 else 'No')

    # Output files
    base_dir = os.path.dirname(file_path)
    analyzed_path = os.path.join(base_dir, "analyzed_logins.csv")
    anomalies_path = os.path.join(base_dir, "anomalies.csv")

    df.to_csv(analyzed_path, index=False)
    df[df['is_anomaly'] == 'Yes'].to_csv(anomalies_path, index=False)

    # Print summary
    total = len(df)
    anomalies = (df['is_anomaly'] == 'Yes').sum()
    print(f"\n✅ Detection complete!")
    print(f"📄 Total records: {total}")
    print(f"⚠️ Anomalies found: {anomalies}")
    print(f"📁 Saved analyzed data: {analyzed_path}")
    print(f"📁 Saved anomalies only: {anomalies_path}")

# ===== Main CLI =====

def main():
    parser = argparse.ArgumentParser(
        description="Login Anomaly Detector using Isolation Forest"
    )
    parser.add_argument(
        "-f", "--file",
        required=True,
        help="Path to input login CSV file"
    )
    parser.add_argument(
        "-c", "--contamination",
        type=float,
        default=0.2,
        help="Contamination rate (default: 0.2)"
    )

    args = parser.parse_args()

    detect_anomalies(args.file, args.contamination)

if __name__ == "__main__":
    main()
