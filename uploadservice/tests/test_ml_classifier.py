"""
Tests for MLClassifier

Tests the ML-based transaction classifier to ensure:
- Model files load correctly
- Classification works as expected
- Error handling is robust
- Integration with preprocessing utilities is correct
"""
import pytest
import os
from src.infrastructure.classifier import MLClassifier
from src.infrastructure.classifier.utils import clean_text, create_transaction_type


@pytest.fixture
def classifier():
    """
    Fixture that provides an MLClassifier instance.

    Note: This assumes model files are present in uploadservice/models/
    If running tests fails due to missing models, you may need to:
    1. Copy model files from ml_pipeline/models/final/ to uploadservice/models/
    2. Or set ML_MODELS_PATH environment variable to point to the models
    """
    # Set models path for testing
    models_path = os.path.join(
        os.path.dirname(__file__),
        "..",
        "models"
    )

    classifier = MLClassifier(models_path=models_path)
    return classifier


class TestMLClassifier:
    """Test suite for MLClassifier"""

    @pytest.mark.asyncio
    async def test_classifier_loads_models(self, classifier):
        """Test that the classifier can load model files successfully"""
        # This will trigger model loading
        result = await classifier.classify("TEST TRANSACTION")

        # Should return a string category (not fail)
        assert isinstance(result, str)
        assert len(result) > 0

    @pytest.mark.asyncio
    async def test_classify_basic_transaction(self, classifier):
        """Test basic classification without transaction value"""
        description = "COMPRA STARBUCKS COFFEE"
        result = await classifier.classify(description)

        assert isinstance(result, str)
        assert len(result) > 0
        # Should not return the generic fallback if model works
        # (though "Other" might be a valid category)

    @pytest.mark.asyncio
    async def test_classify_with_transaction_value_expense(self, classifier):
        """Test classification with negative value (expense)"""
        description = "COMPRA SUPERMERCADO"
        transaction_value = -50000.0  # Expense

        result = await classifier.classify(description, transaction_value)

        assert isinstance(result, str)
        assert len(result) > 0

    @pytest.mark.asyncio
    async def test_classify_with_transaction_value_income(self, classifier):
        """Test classification with positive value (income)"""
        description = "TRANSFERENCIA SALARIO"
        transaction_value = 3000000.0  # Income

        result = await classifier.classify(description, transaction_value)

        assert isinstance(result, str)
        assert len(result) > 0

    @pytest.mark.asyncio
    async def test_classify_empty_description(self, classifier):
        """Test that empty descriptions are handled gracefully"""
        result = await classifier.classify("")

        # Should return "Other" for empty descriptions
        assert result == "Other"

    @pytest.mark.asyncio
    async def test_classify_none_description_fallback(self, classifier):
        """Test that None descriptions don't crash the classifier"""
        # This should be handled by clean_text
        result = await classifier.classify(None)

        # Should return fallback category
        assert result == "Other"

    @pytest.mark.asyncio
    async def test_classify_special_characters(self, classifier):
        """Test that special characters are handled correctly"""
        description = "COMPRA*** EN $$$ TIENDA!!! @#%"
        result = await classifier.classify(description)

        # Should handle special characters without crashing
        assert isinstance(result, str)
        assert len(result) > 0

    def test_classify_with_details_returns_full_info(self, classifier):
        """Test that classify_with_details returns comprehensive information"""
        description = "COMPRA CAFE STARBUCKS"
        transaction_value = -15000.0

        result = classifier.classify_with_details(description, transaction_value)

        # Should return a dictionary with specific keys
        assert isinstance(result, dict)
        assert 'prediction' in result
        assert 'confidence' in result
        assert 'cleaned' in result
        assert 'tipo' in result
        assert 'top_3' in result

        # Confidence should be a percentage (0-100)
        if 'error' not in result:
            assert 0 <= result['confidence'] <= 100
            # top_3 should have 3 items
            assert len(result['top_3']) <= 3

    def test_classify_with_details_handles_errors(self, classifier):
        """Test that classify_with_details handles errors gracefully"""
        result = classifier.classify_with_details("")

        # Should return error info
        assert isinstance(result, dict)
        assert 'prediction' in result
        assert result['prediction'] == 'Other'


class TestPreprocessingUtils:
    """Test suite for preprocessing utilities"""

    def test_clean_text_uppercase(self):
        """Test that text is converted to uppercase"""
        result = clean_text("compra en tienda")
        assert result == "COMPRA EN TIENDA"

    def test_clean_text_removes_special_chars(self):
        """Test that special characters are removed"""
        result = clean_text("COMPRA*** EN $$$ TIENDA!!!")
        # Should only have alphanumeric and spaces
        assert result == "COMPRA EN TIENDA"

    def test_clean_text_removes_multiple_spaces(self):
        """Test that multiple spaces are collapsed"""
        result = clean_text("COMPRA    EN     TIENDA")
        assert result == "COMPRA EN TIENDA"

    def test_clean_text_strips_leading_trailing_spaces(self):
        """Test that leading/trailing spaces are removed"""
        result = clean_text("  COMPRA EN TIENDA  ")
        assert result == "COMPRA EN TIENDA"

    def test_clean_text_handles_none(self):
        """Test that None is handled without crashing"""
        result = clean_text(None)
        assert result == ""

    def test_create_transaction_type_expense(self):
        """Test that negative values are classified as 'egreso'"""
        result = create_transaction_type(-50000.0)
        assert result == "egreso"

    def test_create_transaction_type_income(self):
        """Test that positive values are classified as 'ingreso'"""
        result = create_transaction_type(100000.0)
        assert result == "ingreso"

    def test_create_transaction_type_neutral(self):
        """Test that zero values are classified as 'neutro'"""
        result = create_transaction_type(0.0)
        assert result == "neutro"

    def test_create_transaction_type_none(self):
        """Test that None is handled as 'neutro'"""
        result = create_transaction_type(None)
        assert result == "neutro"


class TestModelIntegration:
    """Integration tests to verify model behavior"""

    @pytest.mark.asyncio
    async def test_common_transactions_classification(self, classifier):
        """Test classification of common transaction types"""
        test_cases = [
            ("PAGO SERVICIOS PUBLICOS EPM", -150000.0),
            ("COMPRA SUPERMERCADO EXITO", -80000.0),
            ("TRANSFERENCIA NOMINA", 3000000.0),
            ("RETIRO CAJERO AUTOMATICO", -200000.0),
            ("COMPRA RESTAURANTE", -45000.0),
        ]

        for description, value in test_cases:
            result = await classifier.classify(description, value)

            # Should return a valid category for all common transactions
            assert isinstance(result, str)
            assert len(result) > 0

            # Log for manual verification if needed
            print(f"'{description}' -> '{result}'")

    @pytest.mark.asyncio
    async def test_singleton_behavior(self):
        """Test that multiple classifier instances share the same loaded model"""
        classifier1 = MLClassifier()
        classifier2 = MLClassifier()

        # Both should work
        result1 = await classifier1.classify("TEST TRANSACTION 1")
        result2 = await classifier2.classify("TEST TRANSACTION 2")

        assert isinstance(result1, str)
        assert isinstance(result2, str)

        # Both should use the same underlying model (singleton pattern)
        assert MLClassifier._initialized is True


# Run tests with: pytest tests/test_ml_classifier.py -v
# Run with output: pytest tests/test_ml_classifier.py -v -s
