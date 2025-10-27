from typing import List, Dict
from decimal import Decimal
from collections import defaultdict

from src.domain.entities import Transaction
from src.domain.llm_models import TransactionSummary


class TransactionAggregator:
    """Service to aggregate and summarize transactions for LLM analysis"""
    
    @staticmethod
    def aggregate_by_category(transactions: List[Transaction]) -> List[TransactionSummary]:
        """
        Groups transactions by category and creates summaries
        
        Args:
            transactions: List of user transactions
            
        Returns:
            List of transaction summaries grouped by category
        """
        if not transactions:
            return []
        
        # Group transactions by category and type
        grouped: Dict[tuple, dict] = defaultdict(lambda: {
            'total_amount': Decimal('0'),
            'count': 0,
            'category': '',
            'transaction_type': ''
        })
        
        for transaction in transactions:
            key = (
                str(transaction.id_category.value),
                transaction.transaction_type,
                transaction.category_description or 'Unknown'
            )
            
            grouped[key]['total_amount'] += transaction.value.amount
            grouped[key]['count'] += 1
            grouped[key]['category'] = transaction.category_description or 'Unknown'
            grouped[key]['transaction_type'] = transaction.transaction_type
        
        # Convert to TransactionSummary objects
        summaries = []
        for data in grouped.values():
            summary = TransactionSummary(
                category=data['category'],
                total_amount=data['total_amount'],
                transaction_count=data['count'],
                transaction_type=data['transaction_type']
            )
            summaries.append(summary)
        
        # Sort by amount descending (highest expenses first)
        summaries.sort(key=lambda x: x.total_amount, reverse=True)
        
        return summaries
