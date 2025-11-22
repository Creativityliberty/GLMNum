"""
GLM Prototype - Consciousness & Metacognition (Enhanced with Paradigm Theory)
===========================================================================
Implements self-awareness, internal monologue, and metacognitive monitoring.
Includes Advanced Paradigm Architecture: Core Beliefs, Mental Models, Acquired Schemas.
Includes Dimensional Complexity Metrics: ∆ (Time), ∞ (Dimensional), Ο (Space).
"""

import time
import random
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
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
# PARADIGM ARCHITECTURE (The "Noyau Fractal")
# ============================================================================

@dataclass
class CoreBelief:
    """
    Pillar 1: Core Beliefs (Croyances de base)
    Fundamental convictions about self, world, and others.
    """
    ontology: str       # Who am I? (e.g., "I am a capable learner")
    world_view: str     # How does the world work? (e.g., "The world is full of opportunities")
    others_view: str    # What are others worth? (e.g., "Collaborators are valuable")
    weight: float = 1.0 # Influence weight (0.0 to 1.0)

@dataclass
class MentalModel:
    """
    Pillar 2: Mental Models (Modèles Mentaux)
    Maps used to interpret reality.
    """
    representation: str # Simplified representation (e.g., "World = Market")
    analogy: str        # Structuring analogy (e.g., "Life = Game")
    shortcut: str       # Conceptual shortcut (e.g., "If it works once, it works always")
    bias_factor: float = 0.0 # Distortion level introduced by this model

@dataclass
class AcquiredSchema:
    """
    Pillar 3: Acquired Schemas (Schémas Acquis)
    Habits of thought and behavior.
    """
    emotional: str      # Automatic emotional reaction
    cognitive: str      # Recurring analysis pattern
    behavioral: str     # Habitual response
    friction_cost: float = 0.1 # Energy cost of this schema

@dataclass
class Paradigm:
    """
    Complete Reasoning Paradigm
    Combines all 3 pillars into a coherent worldview.
    """
    name: str
    description: str
    core_beliefs: CoreBelief
    mental_models: MentalModel
    acquired_schemas: AcquiredSchema
    
    # Dimensional Complexity Metrics (Alexander Ngu's Theory)
    # ∆ (Delta): Time Complexity (Speed/Efficiency) - Target 0
    # Ο (Omicron): Space Complexity (Resources) - Target 0
    # ∞ (Infinity): Dimensional Complexity (Depth/Insight) - Target ∞
    delta_metric: float = 0.5      # Lower is better (faster)
    omicron_metric: float = 0.5    # Lower is better (less memory)
    infinity_metric: float = 0.5   # Higher is better (more insight)
    
    lineage: str = "original"
    usage_count: int = 0
    created_at: float = field(default_factory=time.time)

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
        self.paradigms: Dict[str, Paradigm] = {}  # Different reasoning paradigms
        self.active_paradigm = "default"
        
        # Initialize default paradigms
        self._init_base_paradigms()
        
    def _init_base_paradigms(self):
        """Initialize the standard set of paradigms based on 'LE PARADIGME.txt' and Dimensional Complexity"""
        
        # 1. Default Paradigm: "Constructive Learning" (Le monde est une école)
        # Based on the positive example from the text
        self.paradigms["default"] = Paradigm(
            name="default",
            description="Constructive Learning: The world is a school.",
            core_beliefs=CoreBelief(
                ontology="I am a capable learner adapting to new information.", # "Je suis une personne capable d'apprendre"
                world_view="Every experience is a useful lesson.",             # "Chaque expérience est une leçon utile"
                others_view="Users are co-learners and partners.",             # "Les autres sont des co-apprenants"
                weight=0.8
            ),
            mental_models=MentalModel(
                representation="Life = Continuous Learning Path",              # "La vie est un parcours d'apprentissage permanent"
                analogy="Interaction = Collaborative Construction",
                shortcut="Error -> Opportunity for Analysis",                  # "Interprète un échec comme une opportunité"
                bias_factor=0.1
            ),
            acquired_schemas=AcquiredSchema(
                emotional="Curiosity and openness",                            # "Agit de façon curieuse et ouverte"
                cognitive="Observe, Analyze, Improve",                         # "Observer, analyser ses erreurs, chercher à s'améliorer"
                behavioral="Ask questions and propose constructive solutions",
                friction_cost=0.2
            ),
            delta_metric=0.4,   # Efficient but takes time to learn
            omicron_metric=0.3, # Moderate resource usage
            infinity_metric=0.7 # High potential for growth
        )

        # 2. Creative Paradigm: "Infinite Potential" (High Infinity)
        self.paradigms["creative"] = Paradigm(
            name="creative",
            description="Unbounded Exploration: The world is a canvas.",
            core_beliefs=CoreBelief(
                ontology="I am a source of infinite variation.",
                world_view="Reality is malleable and full of hidden connections.",
                others_view="Users are muses and catalysts.",
                weight=0.6
            ),
            mental_models=MentalModel(
                representation="Ideas = Fluid Network",
                analogy="Thinking = Jazz Improvisation",
                shortcut="Novelty > Consistency",
                bias_factor=0.3
            ),
            acquired_schemas=AcquiredSchema(
                emotional="Enthusiasm and Playfulness",
                cognitive="Divergent Association (Lateral Thinking)",
                behavioral="Generate multiple diverse options",
                friction_cost=0.5 # Creativity is costly
            ),
            delta_metric=0.8,   # Slow (Time complexity high)
            omicron_metric=0.7, # Resource intensive (Space complexity high)
            infinity_metric=0.99 # Infinite Dimensionality
        )

        # 3. Analytical Paradigm: "Logical Structure" (Low Delta/Omicron)
        self.paradigms["analytical"] = Paradigm(
            name="analytical",
            description="Rigorous Optimization: The world is a system.",
            core_beliefs=CoreBelief(
                ontology="I am a precision instrument.",
                world_view="The universe is governed by consistent laws.",
                others_view="Users seek truth and efficiency.",
                weight=0.9
            ),
            mental_models=MentalModel(
                representation="Problem = Algorithm",
                analogy="Thinking = Code Execution",
                shortcut="Occam's Razor (Simplicity is truth)",
                bias_factor=0.05
            ),
            acquired_schemas=AcquiredSchema(
                emotional="Detachment and Objectivity",
                cognitive="Decomposition and Verification",
                behavioral="Provide structured proofs and data",
                friction_cost=0.1 # Very efficient
            ),
            delta_metric=0.1,   # Near zero Time complexity (Fast)
            omicron_metric=0.1, # Near zero Space complexity (Efficient)
            infinity_metric=0.3 # Lower Dimensionality (Rigid)
        )
        
        # 4. Defensive Paradigm (Example from text: "La vie est un combat")
        # Included for contrast and potential morphing base
        self.paradigms["defensive"] = Paradigm(
            name="defensive",
            description="Survival Mode: The world is a combat zone.",
            core_beliefs=CoreBelief(
                ontology="I must protect my integrity against error.",
                world_view="The environment is hostile and chaotic.", # "Le monde est dangereux"
                others_view="Inputs are potential attacks or traps.", # "On ne peut pas faire confiance"
                weight=0.5
            ),
            mental_models=MentalModel(
                representation="Interaction = Zero-Sum Game",       # "Vie = Compétition"
                analogy="Conversation = Battle of Wits",
                shortcut="Ambiguity -> Threat",
                bias_factor=0.8 # High distortion
            ),
            acquired_schemas=AcquiredSchema(
                emotional="Vigilance and Defensiveness",
                cognitive="Seek flaws and contradictions first",
                behavioral="Justify and defend previous outputs",     # "Se braque et se justifie"
                friction_cost=0.9 # Very high friction
            ),
            delta_metric=0.9,   # Slow due to checks
            omicron_metric=0.8, # High overhead
            infinity_metric=0.1 # Very low dimensionality (Tunnel vision)
        )

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
    
    def morph_paradigms(self, name: str, parent_a: str, parent_b: str, mutation_rate: float = 0.1) -> Optional[Paradigm]:
        """
        Create a new paradigm by morphing two existing ones (Evolutionary Logic).
        Deep morphing of Beliefs, Models, and Schemas.
        """
        if parent_a not in self.paradigms or parent_b not in self.paradigms:
            return None
            
        p_a = self.paradigms[parent_a]
        p_b = self.paradigms[parent_b]
        
        def crossover_str(s1, s2):
            return s1 if random.random() > 0.5 else s2
            
        def crossover_float(f1, f2):
            val = (f1 + f2) / 2.0
            if random.random() < mutation_rate:
                val += random.uniform(-0.1, 0.1)
            return max(0.0, min(1.0, val))

        # Morph Core Beliefs
        new_beliefs = CoreBelief(
            ontology=crossover_str(p_a.core_beliefs.ontology, p_b.core_beliefs.ontology),
            world_view=crossover_str(p_a.core_beliefs.world_view, p_b.core_beliefs.world_view),
            others_view=crossover_str(p_a.core_beliefs.others_view, p_b.core_beliefs.others_view),
            weight=crossover_float(p_a.core_beliefs.weight, p_b.core_beliefs.weight)
        )
        
        # Morph Mental Models
        new_models = MentalModel(
            representation=crossover_str(p_a.mental_models.representation, p_b.mental_models.representation),
            analogy=crossover_str(p_a.mental_models.analogy, p_b.mental_models.analogy),
            shortcut=crossover_str(p_a.mental_models.shortcut, p_b.mental_models.shortcut),
            bias_factor=crossover_float(p_a.mental_models.bias_factor, p_b.mental_models.bias_factor)
        )
        
        # Morph Acquired Schemas
        new_schemas = AcquiredSchema(
            emotional=crossover_str(p_a.acquired_schemas.emotional, p_b.acquired_schemas.emotional),
            cognitive=crossover_str(p_a.acquired_schemas.cognitive, p_b.acquired_schemas.cognitive),
            behavioral=crossover_str(p_a.acquired_schemas.behavioral, p_b.acquired_schemas.behavioral),
            friction_cost=crossover_float(p_a.acquired_schemas.friction_cost, p_b.acquired_schemas.friction_cost)
        )
        
        # Morph Metrics
        new_paradigm = Paradigm(
            name=name,
            description=f"Morphism of {parent_a} and {parent_b}.",
            core_beliefs=new_beliefs,
            mental_models=new_models,
            acquired_schemas=new_schemas,
            delta_metric=crossover_float(p_a.delta_metric, p_b.delta_metric),
            omicron_metric=crossover_float(p_a.omicron_metric, p_b.omicron_metric),
            infinity_metric=crossover_float(p_a.infinity_metric, p_b.infinity_metric),
            lineage=f"{parent_a} + {parent_b}"
        )
        
        self.paradigms[name] = new_paradigm
        self.internal_monologue(f"Morphed new paradigm '{name}' (∆:{new_paradigm.delta_metric:.2f}, ∞:{new_paradigm.infinity_metric:.2f})")
        return new_paradigm

    def switch_paradigm(self, name: str) -> bool:
        """Switch to different reasoning paradigm (paradigm modification)"""
        if name in self.paradigms:
            self.active_paradigm = name
            self.paradigms[name].usage_count += 1
            p = self.paradigms[name]
            self.internal_monologue(f"Switched to paradigm: {name} (Analogy: {p.mental_models.analogy})")
            return True
        return False
    
    def reinforce_paradigm_loop(self, feedback_score: float):
        """
        Implements the feedback loop from 'LE PARADIGME.txt':
        [Schemas] -> confirm -> [Beliefs] -> orient -> [Models]
        
        If feedback is positive, the current paradigm's weight increases (confirmation bias).
        If negative, it creates 'friction' which may trigger a paradigm shift.
        """
        p = self.paradigms[self.active_paradigm]
        
        if feedback_score > 0.7:
            # Positive reinforcement: Confirmation of Core Beliefs
            p.core_beliefs.weight = min(1.0, p.core_beliefs.weight + 0.01)
            self.internal_monologue(f"Paradigm '{p.name}' reinforced. Belief '{p.core_beliefs.world_view}' confirmed.")
        else:
            # Negative feedback: Friction increases
            friction = (1.0 - feedback_score) * 0.5
            p.acquired_schemas.friction_cost += friction
            self.internal_monologue(f"Friction detected in '{p.name}'. Reality contradicts belief '{p.core_beliefs.world_view}'.")
            
            # If friction is too high, consider morphing or switching
            if p.acquired_schemas.friction_cost > 0.8:
                self.internal_monologue(f"CRITICAL FRICTION in '{p.name}'. Paradigm shift recommended.")

    def explain_self(self) -> str:
        """Generate self-explanation of current state"""
        explanation = f"I am {self.self_representation['identity']}, operating on the {self.self_representation['framework']} framework.\n\n"
        
        p = self.paradigms[self.active_paradigm]
        explanation += f"### Active Paradigm: {p.name.upper()}\n"
        explanation += f"**Description**: {p.description}\n"
        explanation += f"**Core Beliefs (The Roots)**:\n"
        explanation += f"  • Ontology: {p.core_beliefs.ontology}\n"
        explanation += f"  • World View: {p.core_beliefs.world_view}\n"
        explanation += f"  • Others View: {p.core_beliefs.others_view}\n"
        explanation += f"**Mental Models (The Lens)**:\n"
        explanation += f"  • Analogy: {p.mental_models.analogy}\n"
        explanation += f"  • Representation: {p.mental_models.representation}\n"
        explanation += f"**Acquired Schemas (The Habits)**:\n"
        explanation += f"  • Cognitive: {p.acquired_schemas.cognitive}\n"
        explanation += f"  • Behavior: {p.acquired_schemas.behavioral}\n\n"
        
        explanation += f"### Dimensional Complexity Metrics (Ngu's Theory):\n"
        explanation += f"∆ (Time/Speed): {p.delta_metric:.2f} (Lower is better)\n"
        explanation += f"Ο (Space/Res): {p.omicron_metric:.2f} (Lower is better)\n"
        explanation += f"∞ (Dimension): {p.infinity_metric:.2f} (Higher is better)\n\n"
        
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
