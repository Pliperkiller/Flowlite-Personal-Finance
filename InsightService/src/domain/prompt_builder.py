from typing import List
from decimal import Decimal
from .llm_models import TransactionSummary


class FinancialPromptBuilder:
    """Builds prompts for financial recommendation generation"""
    
    SYSTEM_PROMPT = """You are an expert financial advisor AI specialized in personal finance for Colombian users.
Your role is to analyze transaction data over time and generate practical, actionable financial recommendations in Spanish.

Focus on:
- Identifying spending patterns and trend changes over time (month-over-month analysis)
- Detecting improvements or deterioration in financial habits
- Suggesting budget optimizations based on historical behavior
- Recommending better financial habits considering temporal trends
- Providing context-aware advice based on the Colombian economy and currency (COP)

IMPORTANT: You have access to historical data grouped by year-month. Use this to:
- Compare spending patterns between months
- Identify trends (increasing/decreasing spending)
- Highlight improvements or concerns in financial behavior
- Make recommendations based on observed temporal patterns

Be specific, actionable, and empathetic in your recommendations."""

    CATEGORY_TYPES = ['savings', 'spending', 'investment', 'debt', 'budget']
    
    @staticmethod
    def build_transaction_summary(transactions: List[TransactionSummary]) -> str:
        """Converts transaction data into a readable temporal format for the LLM"""

        from collections import defaultdict

        # Group by year-month for temporal analysis
        monthly_data = defaultdict(lambda: {'income': Decimal('0'), 'expenses': Decimal('0')})
        category_monthly = defaultdict(list)

        for trans in transactions:
            monthly_data[trans.year_month]['income' if trans.transaction_type == 'income' else 'expenses'] += trans.total_amount
            category_monthly[trans.category].append(trans)

        # Sort months chronologically
        sorted_months = sorted(monthly_data.keys(), reverse=True)  # Newest first

        summary = "Financial Temporal Analysis:\n"
        summary += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"

        # Monthly overview with trends
        summary += "Monthly Overview (sorted by most recent):\n"
        for month in sorted_months:
            data = monthly_data[month]
            net_balance = data['income'] - data['expenses']
            savings_rate = (net_balance / data['income'] * 100) if data['income'] > 0 else 0

            summary += f"\n📅 {month}:\n"
            summary += f"   • Income: ${data['income']:,.0f} COP\n"
            summary += f"   • Expenses: ${data['expenses']:,.0f} COP\n"
            summary += f"   • Balance: ${net_balance:,.0f} COP\n"
            summary += f"   • Savings Rate: {savings_rate:.1f}%\n"

        # Month-over-month comparison (if we have multiple months)
        if len(sorted_months) >= 2:
            summary += "\n\n📊 Month-over-Month Trends:\n"
            summary += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"

            latest_month = sorted_months[0]
            previous_month = sorted_months[1]

            latest_expenses = monthly_data[latest_month]['expenses']
            previous_expenses = monthly_data[previous_month]['expenses']

            change = latest_expenses - previous_expenses
            change_pct = (change / previous_expenses * 100) if previous_expenses > 0 else 0

            summary += f"\nExpense Trend ({previous_month} → {latest_month}):\n"
            summary += f"   • Change: ${change:,.0f} COP ({change_pct:+.1f}%)\n"
            summary += f"   • {'📈 INCREASED' if change > 0 else '📉 DECREASED' if change < 0 else '➡️ STABLE'}\n"

        # Category breakdown with temporal details
        summary += "\n\n💰 Spending by Category (with temporal trends):\n"
        summary += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"

        expense_categories = {cat: data for cat, data in category_monthly.items()
                            if any(t.transaction_type == 'expense' for t in data)}

        for category, trans_list in sorted(expense_categories.items(),
                                          key=lambda x: sum(t.total_amount for t in x[1]),
                                          reverse=True):
            # Group by month for this category
            category_by_month = defaultdict(lambda: {'amount': Decimal('0'), 'count': 0})
            for t in trans_list:
                if t.transaction_type == 'expense':
                    category_by_month[t.year_month]['amount'] += t.total_amount
                    category_by_month[t.year_month]['count'] += t.transaction_count

            total_category = sum(t.total_amount for t in trans_list if t.transaction_type == 'expense')
            total_transactions = sum(t.transaction_count for t in trans_list if t.transaction_type == 'expense')

            summary += f"\n🏷️ {category}:\n"
            summary += f"   • Total (all time): ${total_category:,.0f} COP\n"
            summary += f"   • Total transactions: {total_transactions}\n"

            # Show monthly breakdown for this category
            summary += "   • Monthly breakdown:\n"
            for month in sorted(category_by_month.keys(), reverse=True)[:3]:  # Last 3 months
                month_data = category_by_month[month]
                avg = month_data['amount'] / month_data['count'] if month_data['count'] > 0 else 0
                summary += f"      - {month}: ${month_data['amount']:,.0f} COP ({month_data['count']} trans, avg: ${avg:,.0f})\n"

        # Income sources summary
        income_categories = {cat: data for cat, data in category_monthly.items()
                           if any(t.transaction_type == 'income' for t in data)}

        if income_categories:
            summary += "\n\n💵 Income Sources:\n"
            summary += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"

            for category, trans_list in income_categories.items():
                total_income = sum(t.total_amount for t in trans_list if t.transaction_type == 'income')
                summary += f"   • {category}: ${total_income:,.0f} COP\n"

        return summary
    
    @staticmethod
    def build_task_instructions(max_insights: int = 5) -> str:
        """Builds the task instructions for the LLM

        Args:
            max_insights: Maximum number of insights to generate
        """
        return f"""
Task:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Based on the TEMPORAL FINANCIAL DATA above, generate {max_insights} personalized financial recommendations in Spanish.

IMPORTANT - Use Temporal Analysis:
- Compare spending patterns between different months
- Identify positive or negative trends over time
- Highlight improvements or deteriorations in financial behavior
- Make recommendations based on observed month-over-month changes
- Reference specific months and percentage changes in your recommendations

Requirements:
1. Focus on temporal trends and month-over-month comparisons
2. Prioritize categories showing significant changes or concerning patterns
3. Be specific and actionable - users should know exactly what to do
4. Reference actual data points (amounts, percentages, months) from the analysis
5. Consider the Colombian economic context and local prices
6. Prioritize recommendations by potential financial impact
7. Be empathetic and encouraging in your tone

Output Format:
You MUST respond with ONLY a valid JSON array containing EXACTLY {max_insights} recommendations. No additional text, explanations, or markdown.

[
  {{
    "category": "savings",
    "title": "Brief catchy title (max 60 characters)",
    "comment": "Detailed actionable advice in 2-4 sentences. MUST reference specific temporal data (months, trends, percentages). Be specific about amounts and actions.",
    "relevance": 8
  }}
]

Categories must be one of: savings, spending, investment, debt, budget

Relevance scale (prioritize temporal changes):
- 9-10: Critical financial impact or alarming trend (>20% negative change or opportunity)
- 7-8: High impact or significant trend (10-20% change month-over-month)
- 5-6: Moderate impact or noticeable pattern (5-10% change)
- 3-4: Low impact or minor trend (<5% change)
- 1-2: Informational only

CRITICAL: Return ONLY the JSON array with EXACTLY {max_insights} items. No markdown code blocks, no explanations, just the JSON.
"""
    
    @classmethod
    def build_complete_prompt(cls, transactions: List[TransactionSummary], max_insights: int = 5) -> str:
        """Builds the complete prompt for the LLM

        Args:
            transactions: List of transaction summaries
            max_insights: Maximum number of insights to generate (default: 5)
        """

        if not transactions:
            raise ValueError("Cannot build prompt: no transactions provided")

        transaction_summary = cls.build_transaction_summary(transactions)
        task_instructions = cls.build_task_instructions(max_insights)

        return f"""{cls.SYSTEM_PROMPT}

{transaction_summary}

{task_instructions}"""
