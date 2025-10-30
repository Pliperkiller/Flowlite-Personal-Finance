from typing import Dict, Optional, Protocol
from uuid import UUID

from src.domain.value_objects import CategoryId


class CategoryRepository(Protocol):
    """Protocol for category repository"""
    def get_category_id_by_description(self, description: str) -> Optional[CategoryId]:
        """Get category ID by description"""
        ...


class CategoryMapper:
    """Maps LLM recommendation categories to database category IDs"""

    # Default mapping for insight categories (must match InsightCategory.description in DB)
    DEFAULT_CATEGORY_MAPPING: Dict[str, str] = {
        'savings': 'Ahorro',                    # ins-cat-001-ahorro
        'spending': 'Análisis de Gastos',       # ins-cat-003-gastos
        'investment': 'Tendencias',             # ins-cat-005-tendencias
        'debt': 'Alertas',                      # ins-cat-006-alertas
        'budget': 'Presupuesto',                # ins-cat-002-presupuesto
        'income': 'Análisis de Ingresos',       # ins-cat-004-ingresos
        'trends': 'Tendencias',                 # ins-cat-005-tendencias
        'alerts': 'Alertas',                    # ins-cat-006-alertas
        'general': 'Tendencias'                 # Fallback to Tendencias
    }

    def __init__(self, category_repository: Optional[CategoryRepository] = None):
        self._category_repository = category_repository
        self._category_cache: Dict[str, CategoryId] = {}

    def get_category_id(self, llm_category: str) -> CategoryId:
        """
        Maps an LLM category string to a CategoryId

        Args:
            llm_category: Category string from LLM (e.g., 'savings', 'spending')

        Returns:
            CategoryId for the mapped category
        """
        if llm_category in self._category_cache:
            return self._category_cache[llm_category]

        # Normalize category name
        normalized = llm_category.lower().strip()

        # Map to known category or use 'Tendencias' as fallback
        category_name = self.DEFAULT_CATEGORY_MAPPING.get(normalized, 'Tendencias')

        # Query database for the actual category ID
        if self._category_repository:
            category_id = self._category_repository.get_category_id_by_description(category_name)
            if category_id:
                self._category_cache[llm_category] = category_id
                return category_id
            else:
                # Category not found in database - this should not happen with correct mapping
                import logging
                logger = logging.getLogger(__name__)
                logger.error(
                    f"Category '{category_name}' not found in database for LLM category '{llm_category}'. "
                    f"This indicates a mapping error. Available categories should be: "
                    f"Ahorro, Presupuesto, Análisis de Gastos, Análisis de Ingresos, Tendencias, Alertas"
                )
                raise ValueError(
                    f"Category '{category_name}' not found in database. "
                    f"LLM returned category: '{llm_category}'"
                )

        # Fallback: Generate a deterministic UUID based on category name
        # This should not happen if category_repository is properly injected
        import hashlib
        import logging
        logger = logging.getLogger(__name__)
        logger.warning(
            f"No category repository available. Generating deterministic UUID for '{category_name}'. "
            f"This may cause foreign key constraint errors!"
        )

        category_hash = hashlib.md5(category_name.encode()).hexdigest()
        category_uuid = UUID(category_hash[:32])

        category_id = CategoryId(value=category_uuid)
        self._category_cache[llm_category] = category_id

        return category_id
