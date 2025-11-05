"""
Performance Benchmarks for Batch vs Individual Classification

This test demonstrates the performance improvement of batch classification
over individual classification.

Run with: pytest tests/test_batch_performance.py -v -s
"""
import pytest
import time
from src.infrastructure.classifier import MLClassifier


# Sample transaction descriptions for testing
SAMPLE_TRANSACTIONS = [
    "COMPRA EXITO SUPERMERCADO",
    "RETIRO CAJERO BANCOLOMBIA",
    "PAGO NOMINA EMPRESA ABC",
    "UBER VIAJE CENTRO",
    "NETFLIX SUBSCRIPCION",
    "PAGO ENERGIA EPM",
    "RESTAURANTE FRISBY",
    "FARMACIA CRUZ VERDE",
    "PAGO ARRIENDO INMOBILIARIA",
    "CURSO ONLINE UDEMY"
] * 100  # 1000 transactions

SAMPLE_VALUES = [
    -85000.0, -200000.0, 3500000.0, -25000.0, -45000.0,
    -150000.0, -65000.0, -48000.0, -1200000.0, -89000.0
] * 100


@pytest.fixture
def classifier():
    """Fixture that provides an MLClassifier instance"""
    return MLClassifier()


@pytest.mark.asyncio
async def test_individual_classification_performance(classifier):
    """
    Test classification performance when classifying one-by-one (SLOW)

    This is the OLD method - kept for comparison only
    """
    print(f"\n{'='*70}")
    print("INDIVIDUAL CLASSIFICATION (One-by-one) - OLD METHOD")
    print(f"{'='*70}")

    start_time = time.time()

    predictions = []
    for desc, value in zip(SAMPLE_TRANSACTIONS, SAMPLE_VALUES):
        prediction = await classifier.classify(desc, transaction_value=value)
        predictions.append(prediction)

    end_time = time.time()
    elapsed_time = (end_time - start_time) * 1000  # Convert to ms

    print(f"\nTransactions processed: {len(SAMPLE_TRANSACTIONS)}")
    print(f"Total time: {elapsed_time:.2f}ms")
    print(f"Time per transaction: {elapsed_time/len(SAMPLE_TRANSACTIONS):.2f}ms")
    print(f"Throughput: {len(SAMPLE_TRANSACTIONS)/(elapsed_time/1000):.0f} tx/second")

    assert len(predictions) == len(SAMPLE_TRANSACTIONS)


@pytest.mark.asyncio
async def test_batch_classification_performance(classifier):
    """
    Test classification performance using batch prediction (FAST!)

    This is the NEW optimized method
    """
    print(f"\n{'='*70}")
    print("BATCH CLASSIFICATION - NEW OPTIMIZED METHOD")
    print(f"{'='*70}")

    start_time = time.time()

    predictions = await classifier.classify_batch(
        descriptions=SAMPLE_TRANSACTIONS,
        transaction_values=SAMPLE_VALUES
    )

    end_time = time.time()
    elapsed_time = (end_time - start_time) * 1000  # Convert to ms

    print(f"\nTransactions processed: {len(SAMPLE_TRANSACTIONS)}")
    print(f"Total time: {elapsed_time:.2f}ms")
    print(f"Time per transaction: {elapsed_time/len(SAMPLE_TRANSACTIONS):.2f}ms")
    print(f"Throughput: {len(SAMPLE_TRANSACTIONS)/(elapsed_time/1000):.0f} tx/second")

    assert len(predictions) == len(SAMPLE_TRANSACTIONS)


@pytest.mark.asyncio
async def test_performance_comparison(classifier):
    """
    Compare both methods and show the speedup factor

    This test shows the dramatic performance improvement
    """
    print(f"\n{'='*70}")
    print("PERFORMANCE COMPARISON")
    print(f"{'='*70}")

    # Warm up the model (load it once)
    await classifier.classify("TEST", transaction_value=-100.0)

    # Test individual classification
    start_individual = time.time()
    individual_predictions = []
    for desc, value in zip(SAMPLE_TRANSACTIONS[:100], SAMPLE_VALUES[:100]):
        prediction = await classifier.classify(desc, transaction_value=value)
        individual_predictions.append(prediction)
    time_individual = (time.time() - start_individual) * 1000

    # Test batch classification
    start_batch = time.time()
    batch_predictions = await classifier.classify_batch(
        descriptions=SAMPLE_TRANSACTIONS[:100],
        transaction_values=SAMPLE_VALUES[:100]
    )
    time_batch = (time.time() - start_batch) * 1000

    # Calculate speedup
    speedup = time_individual / time_batch if time_batch > 0 else 0

    print(f"\nTest size: 100 transactions")
    print(f"\nResults:")
    print(f"  Individual classification: {time_individual:.2f}ms")
    print(f"  Batch classification:      {time_batch:.2f}ms")
    print(f"\n  SPEEDUP: {speedup:.1f}x faster! 🚀")

    if speedup > 10:
        print(f"\n  ✅ Batch prediction is {speedup:.0f}x faster - EXCELLENT!")
    elif speedup > 5:
        print(f"\n  ✅ Batch prediction is {speedup:.0f}x faster - VERY GOOD!")
    else:
        print(f"\n  ⚠️  Speedup is only {speedup:.1f}x - expected >10x")

    print(f"\n  Estimated time for 10,000 transactions:")
    print(f"    Individual: {time_individual * 100:.0f}ms ({time_individual * 100/1000:.1f}s)")
    print(f"    Batch:      {time_batch * 100:.0f}ms ({time_batch * 100/1000:.1f}s)")

    assert len(individual_predictions) == len(batch_predictions)
    # Verify predictions are the same
    assert individual_predictions == batch_predictions


@pytest.mark.asyncio
async def test_large_batch_performance(classifier):
    """
    Test performance with a realistic large batch (5000 transactions)

    This simulates a real Excel file with thousands of transactions
    """
    print(f"\n{'='*70}")
    print("LARGE BATCH PERFORMANCE TEST (5000 transactions)")
    print(f"{'='*70}")

    # Create 5000 transactions
    large_batch = SAMPLE_TRANSACTIONS * 5  # 5000 transactions
    large_values = SAMPLE_VALUES * 5

    start_time = time.time()

    predictions = await classifier.classify_batch(
        descriptions=large_batch,
        transaction_values=large_values
    )

    end_time = time.time()
    elapsed_time = (end_time - start_time) * 1000

    print(f"\nTransactions processed: {len(large_batch)}")
    print(f"Total time: {elapsed_time:.2f}ms ({elapsed_time/1000:.2f}s)")
    print(f"Time per transaction: {elapsed_time/len(large_batch):.3f}ms")
    print(f"Throughput: {len(large_batch)/(elapsed_time/1000):.0f} tx/second")

    # Check category distribution
    from collections import Counter
    category_counts = Counter(predictions)

    print(f"\nCategory distribution:")
    for category, count in category_counts.most_common():
        pct = count / len(predictions) * 100
        print(f"  {category:<35} {count:>4} ({pct:>5.1f}%)")

    assert len(predictions) == len(large_batch)


# Run with: pytest tests/test_batch_performance.py -v -s
