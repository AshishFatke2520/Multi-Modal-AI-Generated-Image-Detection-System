from google import genai
import logging
import json
import time
from typing import Optional, Dict, Any
from app.core.config import settings
from app.schemas.fusion import FusionResponse, ExplanationResponse

class ExplanationEngine:
    """
    Generates natural language explanations for detection results using Google Gemini.
    Strictly adheres to safety guidelines: no hallucination, no new facts, neutral tone.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.client_initialized = False
        self.client = None
        
        self.initialize_client()

    def initialize_client(self):
        if settings.GEMINI_API_KEY:
            try:
                # New SDK Client Initialization
                self.client = genai.Client(api_key=settings.GEMINI_API_KEY)
                self.client_initialized = True
                self.logger.info("Gemini client initialized successfully (google-genai SDK).")
            except Exception as e:
                self.logger.error(f"Failed to initialize Gemini: {e}")
                self.client_initialized = False
        else:
            self.logger.warning("No GEMINI_API_KEY found. Explanations will use rule-based fallback.")

    def _build_prompt(self, fusion_result: dict) -> str:
        """
        Constructs a prompt with strict instructions and data injection.
        """
        
        # Prepare data summary
        score = fusion_result['final_score']
        verdict = fusion_result['verdict']
        uncertainty = fusion_result['uncertainty']
        conflicts = fusion_result['conflicts']
        
        signals = fusion_result['normalized_scores']
        
        prompt = f"""
        You are an AI forensics assistant. Your task is to explain the results of an image analysis pipeline.
        
        DATA:
        - Overall Suspicion Score: {score:.1f}/100
        - Verdict: {verdict}
        - Uncertainty Level: {uncertainty:.2f} (0=Certain, 1=Unknown)
        - Detected Conflicts: {conflicts}
        
        SIGNAL BREAKDOWN (0.0 to 1.0, where 1.0 is highly suspicious):
        {json.dumps(signals, indent=2)}
        
        INSTRUCTIONS:
        1. Summarize the findings in 2-3 sentences. Use neutral, objective language.
        2. Specifically mention which signal contributed most to the score.
        3. If there are conflicts, explain that the evidence is inconsistent.
        4. If uncertainty is high (>0.5), advise caution.
        5. DO NOT invent facts. DO NOT say "I see an object/person". You cannot see the image.
        6. DO NOT use the word "proof". Use "indication" or "sign".
        7. Return ONLY a valid JSON object with the following fields: 
           - "text": (string) The explanation.
           - "confidence": (string) "High", "Medium", or "Low" based on uncertainty.
           - "factors": (list of strings) Key drivers.
           - "caveats": (string) Any limitations or conflict notes.

        JSON OUTPUT:
        """
        return prompt

    def generate_explanation(self, fusion_data: dict) -> ExplanationResponse:
        """
        Generates explanation. Uses fallback if API unavailable.
        """
        start_time = time.time()
        
        # 1. Check API availability
        if not self.client_initialized or not settings.ENABLE_LLM_EXPLANATIONS:
            return self.fallback_explanation(fusion_data, start_time)

        # 2. Call Gemini
        try:
            prompt = self._build_prompt(fusion_data)
            
            # New SDK Generation Call
            response = self.client.models.generate_content(
                model='gemini-1.5-flash',
                contents=prompt
            )
            
            # 3. Parse JSON
            # New SDK response object handling
            if response.text:
                raw_text = response.text.replace("```json", "").replace("```", "").strip()
                parsed = json.loads(raw_text)
                
                return ExplanationResponse(
                    explanation_text=parsed.get("text", "No explanation text provided."),
                    confidence_label=parsed.get("confidence", "Unknown"),
                    key_factors=parsed.get("factors", []),
                    uncertainty_notes=parsed.get("caveats", ""),
                    llm_model_version="gemini-1.5-flash",
                    generation_time_ms=(time.time()-start_time) * 1000
                )
            else:
                 raise ValueError("Empty response from model")
            
        except Exception as e:
            self.logger.error(f"Gemini generation failed: {e}")
            return self.fallback_explanation(fusion_data, start_time, error_msg=str(e))

    def fallback_explanation(self, fusion_data: dict, start_time: float, error_msg: str = None) -> ExplanationResponse:
        """
        Rule-based fallback when LLM is unavailable.
        """
        score = fusion_data['final_score']
        verdict = fusion_data['verdict']
        signals = fusion_data['normalized_scores']
        conflicts = fusion_data['conflicts']
        
        text = f"The analysis yielded a {verdict} suspicion score of {score:.1f}/100."
        
        # Find top driver
        if signals:
            top_signal = max(signals, key=signals.get)
            text += f" The primary indicator was {top_signal} analysis."
            
        if conflicts:
            text += " Note that conflicting evidence was detected between analysis modules."
            
        notes = "Generated via fallback logic."
        if error_msg:
             notes += f" (LLM Error: {error_msg})"
        elif not settings.ENABLE_LLM_EXPLANATIONS:
            notes += " (LLM Disabled)"
            
        return ExplanationResponse(
            explanation_text=text,
            confidence_label="N/A (Rule-based)",
            key_factors=[k for k, v in signals.items() if v > 0.5],
            uncertainty_notes=notes,
            llm_model_version="fallback-v1",
            generation_time_ms=(time.time() - start_time) * 1000
        )

explanation_engine = ExplanationEngine()

