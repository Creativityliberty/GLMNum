# numtriad/llm/gemini_triad_wrapper.py
"""
Gemini Triad-Aware Wrapper
==========================

Orchestrates:
1. NumTriadEmbeddingV3 for question encoding
2. DeepTriadRAGIndex for triad-aware retrieval
3. Gemini 2.0 Flash for generation
4. Triad-guided prompting

Author: GLM Research Team
Date: 2024-11-16
"""

from dataclasses import dataclass
from typing import List, Tuple, Optional, Any, Dict

from ..triad_types import Triad
from ..rag.deeptriad_rag import DeepTriadRAGIndex, DeepTriadDocument


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def triad_to_style(triad: Triad) -> str:
    """
    Maps a triad to a response style.
    
    Returns:
        "concrete" if Θ is dominant
        "abstract" if ∞ is dominant
        "structural" if Δ is dominant
    """
    d, inf, th = triad.delta, triad.infinity, triad.theta
    
    if th == max(d, inf, th):
        return "concrete"
    elif inf == max(d, inf, th):
        return "abstract"
    else:
        return "structural"


def format_triad(triad: Triad) -> str:
    """Formats a triad for display."""
    return f"Δ={triad.delta:.2f}, ∞={triad.infinity:.2f}, Θ={triad.theta:.2f}"


def style_to_description(style: str) -> str:
    """Returns a description of the style."""
    descriptions = {
        "concrete": "Practical, operational, with examples and steps",
        "abstract": "Theoretical, conceptual, linking to general principles",
        "structural": "Analytical, structured, breaking down into logical steps",
    }
    return descriptions.get(style, "Balanced approach")


# ============================================================================
# CONFIGURATION
# ============================================================================

@dataclass
class GeminiConfig:
    """Configuration for Gemini LLM"""
    model_name: str = "gemini-2.0-flash"
    max_output_tokens: int = 1024
    temperature: float = 0.3
    top_p: float = 0.95
    top_k: int = 40


# ============================================================================
# GEMINI WRAPPER
# ============================================================================

class GeminiTriadWrapper:
    """
    Orchestrator combining:
    - DeepTriadRAGIndex for context retrieval
    - Gemini Flash for generation
    - Triad-guided prompting
    
    Workflow:
    1. Encode question with NumTriadEmbeddingV3
    2. Retrieve documents with DeepTriadRAGIndex
    3. Build triad-aware prompts
    4. Call Gemini 2.0 Flash
    5. Return calibrated response
    """

    def __init__(
        self,
        rag_index: DeepTriadRAGIndex,
        gemini_client: Optional[Any] = None,
        gemini_cfg: Optional[GeminiConfig] = None,
    ):
        """
        Initialize the wrapper.
        
        Args:
            rag_index: DeepTriadRAGIndex instance
            gemini_client: Gemini API client (optional for now)
            gemini_cfg: GeminiConfig instance
        """
        self.rag_index = rag_index
        self.gemini = gemini_client
        self.cfg = gemini_cfg or GeminiConfig()

    # -----------------------
    # Prompt Building
    # -----------------------

    def _build_system_prompt(self) -> str:
        """
        Builds the system prompt for Gemini.
        Encodes the triad-aware reasoning rules.
        """
        return (
            "Tu es un assistant de raisonnement transformationnel basé sur ∆∞Θ.\n\n"
            "Tu reçois :\n"
            "- une question utilisateur\n"
            "- quelques documents de contexte\n"
            "- une triade (Δ, ∞, Θ) indiquant le niveau d'abstraction attendu.\n\n"
            "Règles de style :\n"
            "- Si Θ est dominant : sois concret, opérationnel, donne des exemples, des étapes, du code ou des cas d'usage.\n"
            "- Si ∞ est dominante : sois plutôt conceptuel, relie aux théories ou principes généraux.\n"
            "- Si Δ est dominante : structure la réponse en étapes logiques, algorithmiques ou méthodologiques.\n\n"
            "Directives :\n"
            "- Ne répète pas la triade, utilise-la pour calibrer ton ton, ta profondeur et tes exemples.\n"
            "- Appuie-toi sur les documents fournis, mais synthétise et reformule.\n"
            "- Sois concis mais complet.\n"
            "- Si les documents ne suffisent pas, dis-le clairement.\n"
        )

    def _build_user_prompt(
        self,
        query: str,
        triad_q: Triad,
        style: str,
        results: List[Tuple[DeepTriadDocument, float]],
    ) -> str:
        """
        Builds the user prompt with question, triad, and context.
        """
        lines = []
        
        # Question
        lines.append("### QUESTION")
        lines.append(query)
        lines.append("")
        
        # Triad
        lines.append("### TRIADE QUESTION")
        lines.append(format_triad(triad_q))
        lines.append(f"Style recommandé (interne): {style}")
        lines.append(f"Description: {style_to_description(style)}")
        lines.append("")
        
        # Context documents
        lines.append("### DOCUMENTS DE CONTEXTE")
        if not results:
            lines.append("[Aucun document trouvé]")
        else:
            for i, (doc, score) in enumerate(results, start=1):
                lines.append(f"[DOC {i}] score={score:.4f}, triade={format_triad(doc.triad)}")
                if doc.meta:
                    lines.append(f"  Meta: {doc.meta}")
                lines.append(f"  Texte: {doc.text[:500]}...")
                lines.append("")
        
        # Task
        lines.append("### TÂCHE")
        lines.append(
            "Réponds à la question en t'appuyant sur les documents ci-dessus, "
            "en respectant le niveau d'abstraction implicite de la triade. "
            "Sois clair, structuré et utile."
        )
        
        return "\n".join(lines)

    # -----------------------
    # Main Interface
    # -----------------------

    def answer(
        self,
        query: str,
        k: int = 5,
        triad_target_mode: str = "auto",
    ) -> Dict[str, Any]:
        """
        Generate a triad-aware answer to a question.
        
        Args:
            query: User question
            k: Number of documents to retrieve
            triad_target_mode: "auto", "abstract", "concrete", or "balanced"
        
        Returns:
            Dict with:
            - answer: Generated response text
            - triad_question: Question triad
            - style: Detected style
            - documents: Retrieved documents with scores
            - metadata: Additional metadata
        """
        # 1) RAG triad-aware retrieval
        results = self.rag_index.search(
            query=query,
            k=k,
            triad_target=triad_target_mode,
        )

        # 2) Get question triad via V3 encoder
        try:
            base, enriched, [triad_q] = self.rag_index.encoder.encode(
                [query],
                triad_mode=triad_target_mode,
                return_raw=True,
            )
        except Exception as e:
            print(f"⚠️ Error encoding question: {e}")
            triad_q = Triad.normalize([1/3, 1/3, 1/3])
        
        style = triad_to_style(triad_q)

        # 3) Build prompts
        system_prompt = self._build_system_prompt()
        user_prompt = self._build_user_prompt(query, triad_q, style, results)

        # 4) Call Gemini (if available)
        answer_text = None
        if self.gemini is not None:
            try:
                answer_text = self._call_gemini(system_prompt, user_prompt)
            except Exception as e:
                print(f"⚠️ Error calling Gemini: {e}")
                answer_text = None

        # 5) Fallback if Gemini not available
        if answer_text is None:
            answer_text = self._generate_fallback_answer(query, results, triad_q, style)

        # 6) Return structured result
        return {
            "answer": answer_text,
            "triad_question": {
                "delta": triad_q.delta,
                "infinity": triad_q.infinity,
                "theta": triad_q.theta,
            },
            "style": style,
            "documents": [
                {
                    "id": doc.doc_id,
                    "text": doc.text[:200],
                    "score": score,
                    "triad": {
                        "delta": doc.triad.delta,
                        "infinity": doc.triad.infinity,
                        "theta": doc.triad.theta,
                    },
                    "meta": doc.meta,
                }
                for doc, score in results
            ],
            "metadata": {
                "num_documents": len(results),
                "retrieval_mode": self.rag_index.retrieval_mode,
                "triad_target_mode": triad_target_mode,
            },
        }

    # -----------------------
    # Gemini Integration
    # -----------------------

    def _call_gemini(self, system_prompt: str, user_prompt: str) -> Optional[str]:
        """
        Calls Gemini 2.0 Flash.
        
        Requires: google-generative-ai library
        """
        if self.gemini is None:
            return None

        try:
            # Using google-generative-ai library
            response = self.gemini.generate_content(
                contents=[
                    {"role": "user", "parts": [{"text": f"{system_prompt}\n\n{user_prompt}"}]},
                ],
                generation_config={
                    "max_output_tokens": self.cfg.max_output_tokens,
                    "temperature": self.cfg.temperature,
                    "top_p": self.cfg.top_p,
                    "top_k": self.cfg.top_k,
                },
            )
            return response.text
        except Exception as e:
            print(f"❌ Gemini error: {e}")
            return None

    # -----------------------
    # Fallback Generation
    # -----------------------

    def _generate_fallback_answer(
        self,
        query: str,
        results: List[Tuple[DeepTriadDocument, float]],
        triad_q: Triad,
        style: str,
    ) -> str:
        """
        Generates a fallback answer when Gemini is not available.
        Simple synthesis of retrieved documents.
        """
        lines = []
        
        lines.append(f"## Réponse à: {query}\n")
        lines.append(f"**Style détecté**: {style} ({style_to_description(style)})\n")
        lines.append(f"**Triade question**: {format_triad(triad_q)}\n")
        
        if not results:
            lines.append("\n⚠️ Aucun document pertinent trouvé.\n")
        else:
            lines.append(f"\n### Synthèse des {len(results)} documents trouvés:\n")
            for i, (doc, score) in enumerate(results, start=1):
                lines.append(f"\n**Document {i}** (pertinence: {score:.2%})")
                lines.append(f"Triade: {format_triad(doc.triad)}")
                lines.append(f"\n{doc.text}\n")
        
        lines.append("\n---")
        lines.append("*Note: Réponse générée en mode fallback (sans Gemini)*")
        
        return "\n".join(lines)

    # -----------------------
    # Utilities
    # -----------------------

    def get_stats(self) -> Dict[str, Any]:
        """Returns statistics about the wrapper."""
        return {
            "rag_index_docs": len(self.rag_index.docs),
            "rag_retrieval_mode": self.rag_index.retrieval_mode,
            "rag_triad_weight": self.rag_index.triad_weight,
            "gemini_available": self.gemini is not None,
            "gemini_model": self.cfg.model_name,
            "gemini_temperature": self.cfg.temperature,
        }
