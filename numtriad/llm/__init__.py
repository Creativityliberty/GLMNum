# numtriad/llm/__init__.py
"""
LLM Integration Module - Gemini Triad-Aware Wrapper
====================================================

Orchestration layer combining:
- NumTriadEmbeddingV3 (advanced encoding)
- DeepTriadRAGIndex (triad-aware retrieval)
- Gemini 2.0 Flash (LLM generation)
- Triad-guided prompting

Author: GLM Research Team
Date: 2024-11-16
"""

from .gemini_triad_wrapper import (
    GeminiTriadWrapper,
    GeminiConfig,
    triad_to_style,
    format_triad,
)

__all__ = [
    "GeminiTriadWrapper",
    "GeminiConfig",
    "triad_to_style",
    "format_triad",
]
