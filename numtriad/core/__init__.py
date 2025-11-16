"""
NumTriad Core Module
====================

High-level integration of all NumTriad pillars.

Main exports:
  - NumTriadSystemV4: Unified facade for all 4 pillars
  - NumTriadSystemConfig: Configuration
  - DeepTriadTransformer: Sequence-level triad analysis
  - NumTriadRAGIndexV4: Triad-aware RAG index
"""

from .system_v4 import (
    NumTriadSystemV4,
    NumTriadSystemConfig,
    DeepTriadTransformer,
    DeepTriadTransformerConfig,
    NumTriadRAGIndexV4,
    IndexedDoc,
    TriadMode,
)

__all__ = [
    "NumTriadSystemV4",
    "NumTriadSystemConfig",
    "DeepTriadTransformer",
    "DeepTriadTransformerConfig",
    "NumTriadRAGIndexV4",
    "IndexedDoc",
    "TriadMode",
]

__version__ = "4.0.0"
