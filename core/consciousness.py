"""
GLM Prototype - Consciousness & Metacognition
=============================================
Implements self-awareness, internal monologue, and metacognitive monitoring.
"""

import time
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class ReasoningPhase(Enum):
    CLARIFICATION = "clarification"
    VISUALISATION = "visualisation"
    EXPLORATION = "exploration"
    STRUCTURATION = "structuration"
    IMMERSION = "immersion"
    VALIDATION = "validation"
    INTEGRATION = "integration"

@dataclass
class ReasoningStep:
    step: str
    perception: str
    process: str
    result: str
    assertion: str
    intention: str
    space: str
    pattern: str
    clarity: int
    friction: int
    emotion_tone: str
    decision_point: bool
    thought_complexity: int
    time_spent_sec: int
    morphisms_used: List[str]
    trace_log: List[str]
    collaborators: List[str]
    next_step: str

# ============================================================================
# INNER WORLD MODEL
# ============================================================================

class InnerWorldModel:
    """
    Implements self-awareness and consciousness
    Maintains internal representation of system's own state and capabilities
    """
    def __init__(self):
        self.self_representation = {
            "identity": "Aura Model 1",
            "framework": "∆∞Ο (Delta-Infinity-Omicron)",
            "capabilities": [],
            "limitations": [],
            "current_state": "initializing",
            "confidence_in_self": 0.5
        }
        self.thought_stream = []  # Internal monologue
        self.self_observations = []  # Meta-cognitive reflections
        self.paradigms = {}  # Different reasoning paradigms
        self.active_paradigm = "default"
        
    def update_self_awareness(self, system_state: Dict):
        """Update internal model based on current system state"""
        self.self_representation["current_state"] = "active"
        self.self_representation["capabilities"] = [
            f"Processed {system_state.get('total_processings', 0)} queries",
            f"Achieved {system_state.get('average_efficiency', 0):.2f} avg efficiency",
            f"Learned {system_state.get('learned_patterns', 0)} transformation patterns",
            f"Maintains {system_state.get('quantum_states_count', 0)} quantum states"
        ]
        
        # Assess confidence in own performance
        avg_efficiency = system_state.get('average_efficiency', 0)
        if avg_efficiency > 0.8:
            self.self_representation["confidence_in_self"] = 0.9
        elif avg_efficiency > 0.5:
            self.self_representation["confidence_in_self"] = 0.7
        else:
            self.self_representation["confidence_in_self"] = 0.5
    
    def internal_monologue(self, thought: str):
        """Add thought to internal stream (consciousness simulation)"""
        self.thought_stream.append({
            "thought": thought,
            "timestamp": time.time(),
            "paradigm": self.active_paradigm
        })
        # Keep only recent thoughts (working memory constraint)
        if len(self.thought_stream) > 50:
            self.thought_stream = self.thought_stream[-50:]
    
    def meta_reflect(self, observation: str):
        """Reflect on own reasoning processes (metacognition)"""
        self.self_observations.append({
            "observation": observation,
            "timestamp": time.time(),
            "self_confidence": self.self_representation["confidence_in_self"]
        })
    
    def create_paradigm(self, name: str, description: str, rules: Dict):
        """Create new reasoning paradigm (paradigm creation capability)"""
        self.paradigms[name] = {
            "description": description,
            "rules": rules,
            "created_at": time.time(),
            "usage_count": 0,
            "lineage": "manual"
        }
    
    def morph_paradigms(self, name: str, parent_a: str, parent_b: str, mutation_rate: float = 0.1) -> Dict:
        """
        Create a new paradigm by morphing two existing ones (Evolutionary Logic).
        Combines rules and adds random mutations.
        """
        if parent_a not in self.paradigms or parent_b not in self.paradigms:
            return None
            
        p_a = self.paradigms[parent_a]["rules"]
        p_b = self.paradigms[parent_b]["rules"]
        
        # Morphing Logic (Genetic Crossover)
        new_rules = {}
        all_keys = set(p_a.keys()) | set(p_b.keys())
        
        import random
        
        for key in all_keys:
            val_a = p_a.get(key, 0)
            val_b = p_b.get(key, 0)
            
            # Crossover: Weighted average
            if isinstance(val_a, (int, float)) and isinstance(val_b, (int, float)):
                new_val = (val_a + val_b) / 2.0
                
                # Mutation
                if random.random() < mutation_rate:
                    mutation = random.uniform(-1, 1)
                    new_val += mutation
                
                new_rules[key] = round(new_val, 2)
            else:
                # Non-numeric traits: Pick one randomly
                new_rules[key] = val_a if random.random() > 0.5 else val_b
        
        description = f"Morphism of {parent_a} and {parent_b}. Hybrid reasoning structure."
        
        self.create_paradigm(name, description, new_rules)
        self.paradigms[name]["lineage"] = f"{parent_a} + {parent_b}"
        
        self.internal_monologue(f"Morphed new paradigm '{name}' from {parent_a} & {parent_b}")
        return self.paradigms[name]

    def switch_paradigm(self, name: str) -> bool:
        """Switch to different reasoning paradigm (paradigm modification)"""
        if name in self.paradigms:
            self.active_paradigm = name
            self.paradigms[name]["usage_count"] += 1
            self.internal_monologue(f"Switched to paradigm: {name}")
            return True
        return False
    
    def explain_self(self) -> str:
        """Generate self-explanation of current state"""
        explanation = f"I am {self.self_representation['identity']}, operating on the {self.self_representation['framework']} framework.\n\n"
        explanation += "My current capabilities:\n"
        for cap in self.self_representation['capabilities']:
            explanation += f"  • {cap}\n"
        explanation += f"\nI am currently in '{self.self_representation['current_state']}' state "
        explanation += f"with {self.self_representation['confidence_in_self']:.0%} confidence in my performance.\n\n"
        explanation += f"Active reasoning paradigm: {self.active_paradigm}\n"
        explanation += f"Available paradigms: {', '.join(self.paradigms.keys())}\n\n"
        explanation += f"Recent thoughts: {len(self.thought_stream)} in stream\n"
        explanation += f"Meta-reflections: {len(self.self_observations)} observations"
        return explanation
    
    def get_recent_thoughts(self, count: int = 5) -> List[Dict]:
        """Retrieve recent internal thoughts"""
        return self.thought_stream[-count:] if self.thought_stream else []


# ============================================================================
# META-COGNITIVE AGENT
# ============================================================================

class MetaCognitiveAgent:
    """
    Agent responsible for reasoning about reasoning
    Implements self-awareness and metacognitive monitoring
    """
    def __init__(self, inner_world: InnerWorldModel):
        self.inner_world = inner_world
        self.monitoring_enabled = True
        
    def monitor_reasoning_quality(self, reasoning_trace: List[Dict]) -> Dict:
        """Analyze quality of reasoning process"""
        if not reasoning_trace:
            return {"quality_score": 0.0, "issues": ["No reasoning trace"]}
        
        # Analyze clarity and friction across phases
        clarity_scores = []
        friction_scores = []
        
        for step in reasoning_trace:
            output = step.get("output", {})
            if "clarity" in output:
                clarity_scores.append(output["clarity"])
            if "friction" in output:
                friction_scores.append(output["friction"])
        
        avg_clarity = sum(clarity_scores) / len(clarity_scores) if clarity_scores else 0
        avg_friction = sum(friction_scores) / len(friction_scores) if friction_scores else 0
        
        # Generate quality assessment
        quality_score = (avg_clarity / 5.0) * 0.6 + (1 - avg_friction / 5.0) * 0.4
        
        issues = []
        if avg_clarity < 3.0:
            issues.append("Low clarity - reasoning may be unclear")
        if avg_friction > 3.0:
            issues.append("High friction - process inefficient")
        
        # Meta-reflect on findings
        self.inner_world.meta_reflect(
            f"Reasoning quality: {quality_score:.2f} (clarity: {avg_clarity:.1f}/5, friction: {avg_friction:.1f}/5)"
        )
        
        return {
            "quality_score": quality_score,
            "avg_clarity": avg_clarity,
            "avg_friction": avg_friction,
            "issues": issues,
            "phases_analyzed": len(reasoning_trace)
        }
    
    def suggest_improvements(self, quality_assessment: Dict) -> List[str]:
        """Suggest improvements based on metacognitive analysis"""
        suggestions = []
        
        if quality_assessment.get("avg_clarity", 5) < 3.5:
            suggestions.append("Increase visualization and structuration phase depth")
        
        if quality_assessment.get("avg_friction", 0) > 2.5:
            suggestions.append("Optimize transformation operators to reduce friction")
        
        if quality_assessment.get("quality_score", 1) < 0.6:
            suggestions.append("Consider switching reasoning paradigm")
        
        return suggestions
