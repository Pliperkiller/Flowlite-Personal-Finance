"""
Utility Functions for Transaction Classification

Common functions used for text processing and transaction type detection.
These functions must match exactly the preprocessing used during model training.
"""

import pandas as pd
import re


def clean_text(text):
    """
    Clean and normalize transaction description text

    This function applies the same preprocessing steps used during model training.
    Any changes here must be synchronized with the training pipeline.

    Args:
        text (str): Raw transaction description

    Returns:
        str: Cleaned and normalized text
    """
    if pd.isna(text):
        return ""

    # Convert to uppercase
    text = str(text).upper()

    # Remove special characters, keep only alphanumeric and spaces
    text = re.sub(r'[^A-Z0-9\s]', ' ', text)

    # Replace multiple spaces with single space
    text = re.sub(r'\s+', ' ', text)

    # Strip leading/trailing spaces
    text = text.strip()

    return text


def create_transaction_type(value):
    """
    Create transaction type based on value sign

    Args:
        value (float): Transaction value

    Returns:
        str: 'ingreso', 'egreso', or 'neutro'
    """
    if pd.isna(value):
        return 'neutro'

    if value > 0:
        return 'ingreso'
    elif value < 0:
        return 'egreso'
    else:
        return 'neutro'
