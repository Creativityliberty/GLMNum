#!/usr/bin/env python3
import os
import sys
sys.path.insert(0, '/Volumes/Numtema/Ava agent/GLM/glm_prototype')

from dotenv import load_dotenv
load_dotenv('/Volumes/Numtema/Ava agent/GLM/glm_prototype/.env')

api_key = os.getenv("GEMINI_API_KEY")
model_name = os.getenv("LLM_MODEL", "gemini-2.0-flash")
print(f"✅ API Key loaded: {api_key[:20]}...")
print(f"✅ Model: {model_name}")

try:
    import google.generativeai as genai
    print("✅ google-generativeai imported")
    
    genai.configure(api_key=api_key)
    print("✅ Gemini configured")
    
    # Try the configured model
    print(f"\n🔄 Testing with {model_name}...")
    model = genai.GenerativeModel(model_name)
    response = model.generate_content("Say 'Hello from Gemini'")
    print(f"✅ Response: {response.text}")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
