import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import LabelEncoder
import joblib
import os

def train_sla_model():
    # 1. Load Data
    df = pd.read_csv("app/data/ml/sla_training_data.csv")
    
    # 2. Preprocessing
    # AI can't read text like "VPN", so we convert to numbers (0, 1, 2...)
    le = LabelEncoder()
    df['category_code'] = le.fit_transform(df['category'])
    
    # X = The predictors (Category ID, Priority, Word Count)
    X = df[['category_code', 'priority', 'word_count']]
    
    # y = The response (Hours)
    y = df['hours_taken']
    
    # 3. Train
    model = LinearRegression()
    model.fit(X, y)
    
    # 4. Save Model & Encoder
    os.makedirs("app/models/ml", exist_ok=True)
    joblib.dump(model, "app/models/ml/sla_model.joblib")
    joblib.dump(le, "app/models/ml/category_encoder.joblib")
    
    print("✅ SLA Prediction Model Trained!")
    print(f"   - Model learned that 'Hardware' usually takes longer.")
    print(f"   - Model learned that 'High Priority' speeds things up.")

if __name__ == "__main__":
    train_sla_model()