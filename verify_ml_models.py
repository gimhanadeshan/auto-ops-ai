#!/usr/bin/env python3
"""
Verification script to check if ML models are accessible.
Run this inside the Docker container or locally to debug model loading issues.
"""
import sys
from pathlib import Path

def verify_ml_models():
    """Check if ML models exist and can be loaded"""
    print("=" * 60)
    print("ML Models Verification Script")
    print("=" * 60)
    
    # Get the script directory
    script_dir = Path(__file__).resolve().parent
    print(f"\n📂 Script directory: {script_dir}")
    
    # Check for backend/app structure
    backend_app_dir = script_dir / "backend" / "app"
    if backend_app_dir.exists():
        print(f"✅ backend/app directory exists: {backend_app_dir}")
    else:
        print(f"❌ backend/app directory NOT found: {backend_app_dir}")
        return False
    
    # Check for ML models directory
    models_dir = backend_app_dir / "models" / "ml"
    if models_dir.exists():
        print(f"✅ ML models directory exists: {models_dir}")
    else:
        print(f"❌ ML models directory NOT found: {models_dir}")
        return False
    
    # List contents of models directory
    print(f"\n📋 Contents of {models_dir}:")
    for item in models_dir.iterdir():
        size_kb = item.stat().st_size / 1024
        print(f"   - {item.name} ({size_kb:.2f} KB)")
    
    # Check specific model files
    required_models = ["sla_model.joblib", "category_encoder.joblib"]
    all_found = True
    print("\n🔍 Checking required models:")
    for model_name in required_models:
        model_path = models_dir / model_name
        if model_path.exists():
            size_kb = model_path.stat().st_size / 1024
            print(f"   ✅ {model_name} ({size_kb:.2f} KB)")
        else:
            print(f"   ❌ {model_name} NOT FOUND")
            all_found = False
    
    # Try to load the models
    print("\n🔬 Attempting to load models...")
    try:
        import joblib
        
        sla_model_path = models_dir / "sla_model.joblib"
        encoder_path = models_dir / "category_encoder.joblib"
        
        if sla_model_path.exists():
            model = joblib.load(str(sla_model_path))
            print(f"   ✅ Successfully loaded SLA model: {type(model).__name__}")
        
        if encoder_path.exists():
            encoder = joblib.load(str(encoder_path))
            print(f"   ✅ Successfully loaded encoder: {type(encoder).__name__}")
        
        print("\n✅ All models loaded successfully!")
        return True
        
    except Exception as e:
        print(f"\n❌ Error loading models: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return all_found

if __name__ == "__main__":
    success = verify_ml_models()
    print("\n" + "=" * 60)
    if success:
        print("✅ VERIFICATION PASSED - All ML models are accessible")
        sys.exit(0)
    else:
        print("❌ VERIFICATION FAILED - ML models are missing or inaccessible")
        sys.exit(1)
