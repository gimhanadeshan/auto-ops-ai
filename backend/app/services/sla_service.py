import joblib
import os
import pandas as pd

class SLAService:
    def __init__(self):
        self.model_path = "app/models/ml/sla_model.joblib"
        self.encoder_path = "app/models/ml/category_encoder.joblib"
        self.model = None
        self.encoder = None
        self._load()

    def _load(self):
        if os.path.exists(self.model_path):
            self.model = joblib.load(self.model_path)
            self.encoder = joblib.load(self.encoder_path)

    def predict_resolution_time(self, category, priority_str, description):
        if not self.model: return 0
        
        # 1. Convert Inputs to Numbers
        # Priority Map
        p_map = {"low": 1, "medium": 2, "high": 3}
        priority_val = p_map.get(priority_str.lower(), 2)
        
        # Word Count
        word_count = len(description.split())
        
        # Category Code (Handle unknown categories safely)
        try:
            cat_code = self.encoder.transform([category])[0]
        except:
            cat_code = 0 # Default to 0 if unknown
            
        # 2. Predict
        features = pd.DataFrame([[cat_code, priority_val, word_count]], 
                              columns=['category_code', 'priority', 'word_count'])
        
        predicted_hours = self.model.predict(features)[0]
        return round(max(0.5, predicted_hours), 1)

sla_service = SLAService()