from typing import List
import logging

from src.domain.entities import Insight
from src.domain.value_objects import UserId, BatchId
from src.domain.repositories import (
    TransactionRepository, 
    InsightRepository, 
    BatchRepository
)
from src.application.interfaces.llm_service import LLMService
from src.application.services.transaction_aggregator import TransactionAggregator
from src.application.services.category_mapper import CategoryMapper
from src.application.dtos import GenerateInsightsResponse, InsightDTO
from src.application.exceptions import (
    TransactionNotFoundError,
    BatchNotFoundError,
    BatchNotProcessedError,
    InsightGenerationError
)


logger = logging.getLogger(__name__)


class GenerateInsightsUseCase:
    """
    Use case for generating financial insights based on user's complete transaction history

    Flow:
    1. Validate that batch exists and is processed (trigger validation)
    2. Retrieve ALL user transactions (complete history)
    3. Aggregate transactions by category
    4. Generate recommendations using LLM (analyzing trends and patterns)
    5. Map recommendations to Insight entities
    6. Persist insights to database
    """
    
    def __init__(
        self,
        transaction_repository: TransactionRepository,
        insight_repository: InsightRepository,
        batch_repository: BatchRepository,
        llm_service: LLMService,
        transaction_aggregator: TransactionAggregator,
        category_mapper: CategoryMapper,
        max_insights: int = 5
    ):
        self._transaction_repo = transaction_repository
        self._insight_repo = insight_repository
        self._batch_repo = batch_repository
        self._llm_service = llm_service
        self._aggregator = transaction_aggregator
        self._category_mapper = category_mapper
        self._max_insights = max_insights
    
    def execute(self, user_id: UserId, batch_id: BatchId) -> GenerateInsightsResponse:
        """
        Executes the insight generation process based on user's complete transaction history

        This use case analyzes ALL transactions of the user (not just the current batch)
        to generate insights based on historical patterns, trends, and financial behavior
        over time. This allows for recommendations like:
        - "Your spending on restaurants has increased 30% compared to last month"
        - "You've improved your savings rate from 10% to 15%"
        - "Your entertainment expenses show a concerning upward trend"

        Args:
            user_id: ID of the user to analyze
            batch_id: ID of the processed batch (used only for trigger validation)

        Returns:
            Response containing generated insights based on complete history

        Raises:
            BatchNotFoundError: If batch doesn't exist
            BatchNotProcessedError: If batch is not in 'completed' status
            TransactionNotFoundError: If no transactions found for user
            InsightGenerationError: If insight generation fails
        """
        logger.info(f"Starting insight generation for user={user_id}, triggered by batch={batch_id}")

        # Step 1: Validate batch (confirms the trigger is valid)
        self._validate_batch(batch_id)
        logger.info(f"Batch {batch_id} validated - proceeding with full user analysis")

        # Step 2: Retrieve ALL user transactions (complete history for trend analysis)
        transactions = self._transaction_repo.find_by_user(user_id)

        if not transactions:
            logger.warning(f"No transactions found for user={user_id}")
            raise TransactionNotFoundError(
                f"No transactions found for user {user_id}"
            )

        logger.info(f"Retrieved {len(transactions)} historical transactions for analysis")
        
        # Step 3: Aggregate transactions
        transaction_summaries = self._aggregator.aggregate_by_category(transactions)
        logger.info(f"Aggregated into {len(transaction_summaries)} categories")
        
        # Step 4: Generate recommendations with LLM
        try:
            llm_recommendations = self._llm_service.generate_recommendations(
                transaction_summaries,
                max_insights=self._max_insights
            )
            logger.info(f"LLM generated {len(llm_recommendations)} recommendations (max={self._max_insights})")
        except Exception as e:
            logger.error(f"LLM service error: {str(e)}")
            raise InsightGenerationError(f"Failed to generate recommendations: {str(e)}")
        
        # Step 5: Map to domain entities
        insights = self._map_to_insights(user_id, llm_recommendations)
        
        # Step 6: Persist insights
        try:
            saved_insights = self._insight_repo.save_batch(insights)
            logger.info(f"Successfully saved {len(saved_insights)} insights")
        except Exception as e:
            logger.error(f"Failed to save insights: {str(e)}")
            raise InsightGenerationError(f"Failed to save insights: {str(e)}")
        
        # Step 7: Build response
        return GenerateInsightsResponse(
            user_id=user_id.value,
            batch_id=batch_id.value,
            insights_generated=len(saved_insights),
            insights=[InsightDTO.from_entity(insight) for insight in saved_insights]
        )
    
    def _validate_batch(self, batch_id: BatchId) -> None:
        """Validates that batch exists and is processed"""
        batch = self._batch_repo.find_by_id(batch_id)
        
        if not batch:
            raise BatchNotFoundError(f"Batch {batch_id} not found")
        
        if not batch.is_processed():
            raise BatchNotProcessedError(
                f"Batch {batch_id} has status '{batch.process_status}', expected 'completed'"
            )
    
    def _map_to_insights(self, user_id: UserId, llm_recommendations) -> List[Insight]:
        """Maps LLM recommendations to Insight entities"""
        insights = []
        
        for recommendation in llm_recommendations:
            category_id = self._category_mapper.get_category_id(recommendation.category)
            
            insight = Insight.create(
                id_user=user_id,
                id_category=category_id,
                title=recommendation.title,
                text=recommendation.comment,
                relevance=recommendation.relevance
            )
            insights.append(insight)
        
        return insights

