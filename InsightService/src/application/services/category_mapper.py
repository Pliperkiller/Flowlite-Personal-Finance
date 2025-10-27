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

    # Default mapping for insight categories
    DEFAULT_CATEGORY_MAPPING: Dict[str, str] = {
        'savings': 'Ahorro',
        'spending': 'Gastos',
        'investment': 'Inversión',
        'debt': 'Deuda',
        'budget': 'Presupuesto',
        'general': 'General'
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

        # Map to known category or use 'general' as fallback
        category_name = self.DEFAULT_CATEGORY_MAPPING.get(normalized, 'General')

        # Query database for the actual category ID
        if self._category_repository:
            category_id = self._category_repository.get_category_id_by_description(category_name)
            if category_id:
                self._category_cache[llm_category] = category_id
                return category_id

        # Fallback: Generate a deterministic UUID based on category name
        # This should not happen if category_repository is properly injected
        import hashlib
        category_hash = hashlib.md5(category_name.encode()).hexdigest()
        category_uuid = UUID(category_hash[:32])

        category_id = CategoryId(value=category_uuid)
        self._category_cache[llm_category] = category_id

        return category_id
