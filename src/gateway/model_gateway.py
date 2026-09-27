import os
from typing import Literal, Optional, Any, Type, TypeVar, Dict
from pydantic import BaseModel
from langchain_groq import ChatGroq
from dotenv import load_dotenv

load_dotenv()

T = TypeVar('T', bound=BaseModel)

class BudgetExceededException(Exception):
    pass

class ProviderUnavailableException(Exception):
    pass

class ModelGateway:
    """
    Unified abstraction layer for inference calls, handling mock mode,
    cost governance, and provider fallbacks.
    """
    def __init__(self, mode: Literal["LIVE", "MOCK", "FALLBACK"], cost_limit: float = 5.0):
        self.mode = mode
        self.cost_limit = cost_limit
        self.total_spent = 0.0
        
        self.llm = None
        if self.mode in ["LIVE", "FALLBACK"]:
            api_key = os.environ.get("Groq_API_Key") or os.environ.get("GROQ_API_KEY", "dummy_key")
            model_name = os.environ.get("model", "llama-3.1-70b-versatile")
            self.llm = ChatGroq(temperature=0, model_name=model_name, groq_api_key=api_key)

    def _estimate_cost(self, prompt: str) -> float:
        # Simplified token cost estimation for tracking budget limits
        return (len(prompt) / 4) * 0.0001

    def generate(self, prompt: str, schema: Type[T], mock_data: Optional[Dict[str, Any]] = None) -> T:
        """Generates a structured output constrained by the provided Pydantic schema."""
        if self.mode == "MOCK":
            if mock_data is None:
                raise ValueError("Mock data must be provided when running in MOCK mode.")
            return schema(**mock_data)
            
        estimated_cost = self._estimate_cost(prompt)
        if (self.total_spent + estimated_cost) > self.cost_limit:
            raise BudgetExceededException(f"Spending cap of ${self.cost_limit} reached.")
            
        try:
            # Enforce strict schema boundaries
            structured_llm = self.llm.with_structured_output(schema)
            
            # Force the model to use the tool instead of conversational fallback
            strict_prompt = prompt + "\n\n[SYSTEM]: You MUST use the provided tool/schema to output the structured report. Do NOT output conversational text. If you lack sufficient data, return an empty violation list instead of asking for more information."
            
            response = structured_llm.invoke(strict_prompt)
            self.total_spent += estimated_cost
            return response
        except Exception as e:
            if self.mode == "FALLBACK":
                raise ProviderUnavailableException(f"Provider failed: {e}")
            raise e
