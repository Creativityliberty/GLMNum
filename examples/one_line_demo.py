#!/usr/bin/env python3
"""
Aura Model 1 - One Line Demo
============================
Demonstrates how to instantiate and use the Conscious GLM Kernel.
"""

import sys
import os
import logging

# Add parent dir to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.aura_system import AuraGLM

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    logger.info("🌀 Initializing Aura Model 1...")
    
    # 1. Instantiate the Conscious Kernel
    aura = AuraGLM()
    
    # 2. Process a complex query
    query = "Analyze the relationship between Quantum Mechanics and Consciousness."
    logger.info(f"🧠 Processing Query: '{query}'")
    
    result = aura.process_query(query, paradigm="analytical")
    
    # 3. Display Results
    print("\n" + "="*60)
    print("AURA RESPONSE (Conscious Output):")
    print("="*60)
    print(result["response"])
    
    print("\n" + "-"*60)
    print(f"Confidence: {result['quality_assessment']['quality_score']:.1%}")
    print(f"Paradigm: {result['self_awareness']['identity']}")
    print("-"*60)

if __name__ == "__main__":
    main()
