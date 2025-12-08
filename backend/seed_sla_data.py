import random
import pandas as pd
from datetime import datetime, timedelta
import joblib
import os

# 1. Define Complexity (The "Rules" we want the AI to learn)
# Format: Category: (Min Hours, Max Hours)
CATEGORY_RULES = {
    "Password Reset": (0.5, 2),   # Fast
    "VPN Connection": (1, 4),     # Medium
    "Software Crash": (2, 8),     # Medium-Slow
    "Printer Issue": (1, 5),      # Medium
    "Hardware Failure": (24, 72)  # Very Slow
}

def generate_sla_data():
    print("⏳ Generating historical resolution times...")
    
    data = []
    
    # Generate 500 fake completed tickets
    for _ in range(500):
        category = random.choice(list(CATEGORY_RULES.keys()))
        min_h, max_h = CATEGORY_RULES[category]
        
        # Predictor 1: Category Complexity (We map text to a number later)
        
        # Predictor 2: Priority (1=Low, 2=Med, 3=High)
        priority = random.choice([1, 2, 3])
        
        # Predictor 3: Description Length (Word count)
        words = random.randint(5, 100)
        
        # GENERATE THE RESPONSE VARIABLE (Actual Hours taken)
        # Base time based on category
        actual_hours = random.uniform(min_h, max_h)
        
        # Logic: High priority tickets get solved FASTER (usually)
        if priority == 3: actual_hours *= 0.7 
        
        # Logic: Long descriptions often mean complex/confusing issues -> SLOWER
        if words > 50: actual_hours *= 1.2
        
        data.append({
            "category": category,
            "priority": priority,
            "word_count": words,
            "hours_taken": round(actual_hours, 1)  # <--- Target Variable (y)
        })

    df = pd.DataFrame(data)
    
    # Save for training
    os.makedirs("app/data/ml", exist_ok=True)
    df.to_csv("app/data/ml/sla_training_data.csv", index=False)
    print("✅ SLA Training Data Created!")

if __name__ == "__main__":
    generate_sla_data()