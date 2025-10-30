from dataclasses import dataclass
from typing import List
from decimal import Decimal


@dataclass
class TransactionSummary:
    """Transaction summary to send to LLM with temporal information"""
    category: str
    year_month: str  # Format: "YYYY-MM" for temporal analysis
    total_amount: Decimal
    transaction_count: int
    transaction_type: str  # income - expense
    average_amount: Decimal  # Average transaction amount


@dataclass
class RecommendationRequest:
    """Request to generate recommendations"""
    user_transactions: List[TransactionSummary]
    user_id: str
    batch_id: str


@dataclass
class LLMRecommendation:
    """LLM response with a recommendation"""
    category: str
    title: str
    comment: str
    relevance: int
    
    def __post_init__(self):
        if not 1 <= self.relevance <= 10:
            raise ValueError("Relevance must be between 1 and 10")
