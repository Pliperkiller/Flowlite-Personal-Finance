from ...domain.ports import ClassifierPort


class SimpleClassifier(ClassifierPort):
    """
    Simple classifier that always returns 'Other'
    In the future, this will be replaced by an ML model
    """

    async def classify(self, description: str) -> str:
        """
        Classify a transaction based on its description

        Args:
            description: The transaction description

        Returns:
            The category name (currently always 'Other')
        """
        # TODO: Integrate ML model here
        return "Other"
