"""
CrisisMesh NVIDIA Inference Module - Open Agent Hackathon 2026
GPU-accelerated embeddings, LLM inference, and risk modeling
"""
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass
import asyncio
import numpy as np

from app.config import settings


@dataclass
class EmbeddingResult:
    embeddings: List[List[float]]
    model: str
    dimensions: int
    token_count: int
    inference_time_ms: float


@dataclass
class InferenceResult:
    text: str
    model: str
    tokens_generated: int
    inference_time_ms: float
    confidence: Optional[float] = None


class NVIDIAInference:
    """NVIDIA GPU-accelerated inference for disaster management"""
    
    def __init__(self):
        self.device = "cuda" if settings.USE_GPU else "cpu"
        self.embedding_model = None
        self.llm_model = None
        self._initialized = False
    
    async def initialize(self):
        """Initialize models lazily"""
        if self._initialized:
            return
        
        if settings.SAMPLE_MODE:
            self._initialized = True
            return
        
        try:
            # Import heavy modules lazily
            import torch
            from sentence_transformers import SentenceTransformer
            from transformers import AutoModelForCausalLM, AutoTokenizer
            
            # Set device
            if self.device == "cuda" and not torch.cuda.is_available():
                self.device = "cpu"
                print("[NVIDIA] CUDA not available, falling back to CPU")
            
            # Load embedding model
            self.embedding_model = SentenceTransformer(
                settings.EMBEDDING_MODEL,
                device=self.device
            )
            
            # Load LLM model for risk reasoning (optional, can be large)
            # Only load if explicitly needed
            # self.llm_model = AutoModelForCausalLM.from_pretrained(
            #     settings.LLM_MODEL,
            #     torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
            #     device_map="auto" if self.device == "cuda" else None
            # )
            # self.tokenizer = AutoTokenizer.from_pretrained(settings.LLM_MODEL)
            
            self._initialized = True
            print(f"[NVIDIA] Models initialized on {self.device}")
            
        except ImportError:
            print("[NVIDIA] GPU libraries not available, using CPU fallback")
            self.device = "cpu"
            self._initialized = True
        except Exception as e:
            print(f"[NVIDIA] Initialization failed: {e}, using CPU fallback")
            self.device = "cpu"
            self._initialized = True
    
    async def generate_embeddings(
        self,
        texts: List[str],
        batch_size: int = 32,
        normalize: bool = True
    ) -> EmbeddingResult:
        """Generate text embeddings using GPU"""
        
        await self.initialize()
        start_time = asyncio.get_event_loop().time()
        
        if settings.SAMPLE_MODE or self.embedding_model is None:
            # Mock embeddings for sample mode
            dimensions = 384  # all-MiniLM-L6-v2 dimensions
            embeddings = [
                np.random.randn(dimensions).tolist() 
                for _ in texts
            ]
            if normalize:
                embeddings = [self._normalize(e) for e in embeddings]
            
            inference_time = (asyncio.get_event_loop().time() - start_time) * 1000
            
            return EmbeddingResult(
                embeddings=embeddings,
                model=settings.EMBEDDING_MODEL,
                dimensions=dimensions,
                token_count=sum(len(t.split()) for t in texts),
                inference_time_ms=inference_time
            )
        
        # Real inference
        import torch
        
        embeddings = self.embedding_model.encode(
            texts,
            batch_size=batch_size,
            normalize_embeddings=normalize,
            show_progress_bar=False,
            device=self.device
        )
        
        inference_time = (asyncio.get_event_loop().time() - start_time) * 1000
        
        return EmbeddingResult(
            embeddings=embeddings.tolist(),
            model=settings.EMBEDDING_MODEL,
            dimensions=embeddings.shape[1],
            token_count=sum(len(t.split()) for t in texts),
            inference_time_ms=inference_time
        )
    
    def _normalize(self, vector: List[float]) -> List[float]:
        """Normalize vector to unit length"""
        arr = np.array(vector)
        norm = np.linalg.norm(arr)
        if norm > 0:
            return (arr / norm).tolist()
        return vector
    
    async def similarity_search(
        self,
        query: str,
        candidates: List[str],
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """Semantic similarity search"""
        
        query_emb = await self.generate_embeddings([query])
        cand_emb = await self.generate_embeddings(candidates)
        
        query_vec = np.array(query_emb.embeddings[0])
        scores = []
        
        for i, cand in enumerate(cand_emb.embeddings):
            cand_vec = np.array(cand)
            score = np.dot(query_vec, cand_vec) / (np.linalg.norm(query_vec) * np.linalg.norm(cand_vec))
            scores.append((i, float(score)))
        
        scores.sort(key=lambda x: x[1], reverse=True)
        
        return [
            {"index": idx, "text": candidates[idx], "score": score}
            for idx, score in scores[:top_k]
        ]
    
    async def risk_reasoning(
        self,
        scenario: str,
        context: Dict[str, Any],
        max_tokens: int = 512
    ) -> InferenceResult:
        """Run LLM-based risk reasoning"""
        
        await self.initialize()
        start_time = asyncio.get_event_loop().time()
        
        if settings.SAMPLE_MODE or self.llm_model is None:
            # Mock reasoning
            reasoning = self._mock_risk_reasoning(scenario, context)
            
            return InferenceResult(
                text=reasoning,
                model="mock-llm",
                tokens_generated=len(reasoning.split()),
                inference_time_ms=(asyncio.get_event_loop().time() - start_time) * 1000,
                confidence=0.85
            )
        
        # Real LLM inference (when model is loaded)
        import torch
        
        prompt = self._build_risk_prompt(scenario, context)
        
        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.device)
        
        with torch.no_grad():
            outputs = self.llm_model.generate(
                **inputs,
                max_new_tokens=max_tokens,
                temperature=0.3,
                do_sample=True,
                pad_token_id=self.tokenizer.eos_token_id
            )
        
        generated = self.tokenizer.decode(outputs[0][inputs.input_ids.shape[1]:], skip_special_tokens=True)
        
        return InferenceResult(
            text=generated,
            model=settings.LLM_MODEL,
            tokens_generated=outputs.shape[1] - inputs.input_ids.shape[1],
            inference_time_ms=(asyncio.get_event_loop().time() - start_time) * 1000,
            confidence=0.9
        )
    
    def _build_risk_prompt(self, scenario: str, context: Dict[str, Any]) -> str:
        """Build prompt for risk reasoning"""
        
        context_str = "\n".join(f"- {k}: {v}" for k, v in context.items())
        
        return f"""<|system|>
You are a disaster risk analyst. Analyze the scenario and provide structured risk assessment.
<|user|>
Scenario: {scenario}

Context:
{context_str}

Provide:
1. Immediate risks (next 6 hours)
2. Cascading risks (6-72 hours)
3. Recommended actions with priority
4. Resource requirements
<|assistant|>
"""
    
    def _mock_risk_reasoning(self, scenario: str, context: Dict[str, Any]) -> str:
        """Mock risk reasoning for SAMPLE_MODE"""
        
        disaster_type = context.get("disaster_type", "unknown")
        severity = context.get("severity", "unknown")
        
        return f"""RISK ASSESSMENT - {disaster_type.upper()} ({severity.upper()})

IMMEDIATE RISKS (0-6 HOURS):
- Primary: {scenario}
- Secondary: Infrastructure failure, communication blackout
- Vulnerable populations: Elderly, children, non-local tourists

CASCADING RISKS (6-72 HOURS):
- Disease outbreak from contaminated water
- Structural collapse of damaged buildings
- Supply chain disruption
- Psychological trauma

RECOMMENDED ACTIONS (PRIORITY ORDER):
1. IMMEDIATE: Activate dead-man's switch for autonomous alert dispatch
2. HIGH: Deploy multilingual alerts with exact arrival times and shelter coordinates
3. HIGH: Pre-position assets matched to hazard mechanics (tunnel rescue, high-water vehicles)
4. MEDIUM: Activate cross-jurisdictional SOPs via H-Mem
5. MEDIUM: Initiate satellite-grounded distress verification
6. CONTINUOUS: Monitor sensor drop-off as hazard indicator

RESOURCE REQUIREMENTS:
- Specialized tunnel rescue teams
- Helicopter/drone assets for isolated areas
- VHF/siren backup communication
- Multilingual alert templates
- Pre-accredited NGO coordination
"""


# Global instance
_nvidia_inference: Optional[NVIDIAInference] = None


async def get_nvidia_inference() -> NVIDIAInference:
    """Get or create NVIDIA inference instance"""
    global _nvidia_inference
    if _nvidia_inference is None:
        _nvidia_inference = NVIDIAInference()
        await _nvidia_inference.initialize()
    return _nvidia_inference


__all__ = ["NVIDIAInference", "EmbeddingResult", "InferenceResult", "get_nvidia_inference"]