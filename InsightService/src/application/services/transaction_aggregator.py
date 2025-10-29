from typing import List, Dict
from decimal import Decimal
from collections import defaultdict

from src.domain.entities import Transaction
from src.domain.llm_models import TransactionSummary


class TransactionAggregator:
    """Service to aggregate and summarize transactions for LLM temporal analysis"""

    @staticmethod
    def aggregate_by_category(transactions: List[Transaction]) -> List[TransactionSummary]:
        """
        Groups transactions by category, year-month, and type for temporal analysis

        This allows the LLM to detect trends like:
        - "Your spending on restaurants increased 30% from Jan to Feb"
        - "Your savings rate improved from 10% to 15% over the last 3 months"

        Args:
            transactions: List of user transactions

        Returns:
            List of transaction summaries grouped by category and year-month
        """
        if not transactions:
            return []

        # Group transactions by category, year-month, and type
        grouped: Dict[tuple, dict] = defaultdict(lambda: {
            'total_amount': Decimal('0'),
            'count': 0,
            'category': '',
            'year_month': '',
            'transaction_type': ''
        })

        for transaction in transactions:
            # Extract year-month from transaction date
            year_month = transaction.transaction_date.strftime('%Y-%m')

            key = (
                str(transaction.id_category.value),
                year_month,
                transaction.transaction_type,
                transaction.category_description or 'Unknown'
            )

            grouped[key]['total_amount'] += transaction.value.amount
            grouped[key]['count'] += 1
            grouped[key]['category'] = transaction.category_description or 'Unknown'
            grouped[key]['year_month'] = year_month
            grouped[key]['transaction_type'] = transaction.transaction_type

        # Convert to TransactionSummary objects
        summaries = []
        for data in grouped.values():
            average_amount = data['total_amount'] / data['count'] if data['count'] > 0 else Decimal('0')

            summary = TransactionSummary(
                category=data['category'],
                year_month=data['year_month'],
                total_amount=data['total_amount'],
                transaction_count=data['count'],
                transaction_type=data['transaction_type'],
                average_amount=average_amount
            )
            summaries.append(summary)

        # Sort by year-month (newest first), then by amount
        summaries.sort(key=lambda x: (x.year_month, x.total_amount), reverse=True)

        return summaries
