import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
import joblib
import os

def generate_and_train():
    print("🤖 Generating synthetic server data...")
    
    # 1. Generate Fake Data (1000 samples)
    # Logic: 1000 random servers with different stats
    n_samples = 1000
    cpu = np.random.uniform(10, 100, n_samples)  # CPU 10-100%
    ram = np.random.uniform(20, 100, n_samples)  # RAM 20-100%
    disk = np.random.uniform(30, 95, n_samples)  # Disk 30-95%
    temp = np.random.uniform(40, 90, n_samples)  # Temp 40-90C

    # 2. Define "Failure" Logic (Target Variable)
    # We teach the AI: "If CPU is high AND Temp is high, it crashes."
    status = []
    for i in range(n_samples):
        # Crash rule: CPU > 85% AND Temp > 80C
        if (cpu[i] > 85 and temp[i] > 80) or (ram[i] > 95):
            status.append(1) # 1 = Critical / Crash
        else:
            status.append(0) # 0 = Healthy

    df = pd.DataFrame({
        'cpu_usage': cpu,
        'ram_usage': ram,
        'disk_usage': disk,
        'temperature': temp,
        'status': status
    })

    # 3. Train the AI Model
    X = df[['cpu_usage', 'ram_usage', 'disk_usage', 'temperature']]
    y = df['status']
    
    # Use Random Forest (Great for classification)
    model = RandomForestClassifier(n_estimators=100)
    model.fit(X, y)
    
    # 4. Save the brain (.joblib file)
    output_dir = "app/models/ml"
    os.makedirs(output_dir, exist_ok=True)
    
    joblib.dump(model, f"{output_dir}/system_health_model.joblib")
    print(f"✅ Model trained and saved to {output_dir}/system_health_model.joblib")

if __name__ == "__main__":
    generate_and_train()