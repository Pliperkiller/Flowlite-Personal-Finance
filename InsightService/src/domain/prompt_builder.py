from typing import List
from decimal import Decimal
from .llm_models import TransactionSummary


class FinancialPromptBuilder:
    """Builds prompts for financial recommendation generation"""
    
    SYSTEM_PROMPT = """You are an expert financial advisor AI specialized in personal finance for Colombian users.
Your role is to analyze transaction data and generate practical, actionable financial recommendations in Spanish.

Focus on:
- Identifying spending patterns and savings opportunities
- Suggesting budget optimizations
- Recommending better financial habits
- Providing context-aware advice based on the Colombian economy and currency (COP)

Be specific, actionable, and empathetic in your recommendations."""

    CATEGORY_TYPES = ['savings', 'spending', 'investment', 'debt', 'budget']
    
    @staticmethod
    def build_transaction_summary(transactions: List[TransactionSummary]) -> str:
        """Converts transaction data into a readable format for the LLM"""
        
        income_transactions = [t for t in transactions if t.transaction_type == 'income']
        expense_transactions = [t for t in transactions if t.transaction_type == 'expense']
        
        total_income = sum(t.total_amount for t in income_transactions)
        total_expenses = sum(t.total_amount for t in expense_transactions)
        net_balance = total_income - total_expenses
        
        summary = f"""Financial Summary:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Monthly Overview:
- Total Income: ${total_income:,.0f} COP
- Total Expenses: ${total_expenses:,.0f} COP
- Net Balance: ${net_balance:,.0f} COP
- Savings Rate: {(net_balance/total_income*100) if total_income > 0 else 0:.1f}%

"""
        
        if expense_transactions:
            # Sort by amount descending
            expense_transactions.sort(key=lambda x: x.total_amount, reverse=True)
            
            summary += "Expense Breakdown by Category:\n"
            summary += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            
            for idx, trans in enumerate(expense_transactions, 1):
                percentage = (trans.total_amount / total_expenses * 100) if total_expenses > 0 else 0
                avg_per_transaction = trans.total_amount / trans.transaction_count if trans.transaction_count > 0 else 0
                
                summary += f"""
{idx}. {trans.category}
   • Total: ${trans.total_amount:,.0f} COP ({percentage:.1f}% of expenses)
   • Transactions: {trans.transaction_count}
   • Average per transaction: ${avg_per_transaction:,.0f} COP
"""
        
        if income_transactions:
            summary += "\n\nIncome Sources:\n"
            summary += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            
            for trans in income_transactions:
                summary += f"• {trans.category}: ${trans.total_amount:,.0f} COP\n"
        
        return summary
    
    @staticmethod
    def build_task_instructions() -> str:
        """Builds the task instructions for the LLM"""
        return """
Task:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Based on the financial data above, generate 3-5 personalized financial recommendations in Spanish.

Requirements:
1. Focus on the categories with highest spending or greatest optimization potential
2. Be specific and actionable - users should know exactly what to do
3. Consider the Colombian economic context and local prices
4. Prioritize recommendations by potential financial impact
5. Be empathetic and encouraging in your tone

Output Format:
You MUST respond with ONLY a valid JSON array. No additional text, explanations, or markdown.

[
  {
    "category": "savings",
    "title": "Brief catchy title (max 60 characters)",
    "comment": "Detailed actionable advice in 2-4 sentences. Be specific about amounts and actions.",
    "relevance": 8
  }
]

Categories must be one of: savings, spending, investment, debt, budget

Relevance scale:
- 9-10: Critical financial impact (>20% potential savings/improvement)
- 7-8: High impact (10-20% potential savings/improvement)
- 5-6: Moderate impact (5-10% potential savings/improvement)
- 3-4: Low impact (<5% potential savings/improvement)
- 1-2: Informational only

CRITICAL: Return ONLY the JSON array. No markdown code blocks, no explanations, just the JSON.
"""
    
    @classmethod
    def build_complete_prompt(cls, transactions: List[TransactionSummary]) -> str:
        """Builds the complete prompt for the LLM"""
        
        if not transactions:
            raise ValueError("Cannot build prompt: no transactions provided")
        
        transaction_summary = cls.build_transaction_summary(transactions)
        task_instructions = cls.build_task_instructions()
        
        return f"""{cls.SYSTEM_PROMPT}

{transaction_summary}

{task_instructions}"""
