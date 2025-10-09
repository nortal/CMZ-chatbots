"""
Float validation utilities to handle precision issues with temperature and other decimal values.
"""

def round_to_precision(value: float, precision: float) -> float:
    """
    Round a value to the nearest multiple of precision.

    Examples:
        round_to_precision(0.7, 0.1) -> 0.7
        round_to_precision(0.75, 0.1) -> 0.8
        round_to_precision(0.74, 0.1) -> 0.7
    """
    if precision == 0:
        return value
    return round(value / precision) * precision


def validate_temperature(value: float) -> float:
    """
    Validate and normalize temperature value.

    Temperature must be between 0.0 and 2.0 in increments of 0.1.
    Due to floating-point precision, we round to nearest 0.1.
    """
    # Round to 1 decimal place
    normalized = round(value, 1)

    # Ensure within bounds
    if normalized < 0.0:
        normalized = 0.0
    elif normalized > 2.0:
        normalized = 2.0

    return normalized


def validate_top_p(value: float) -> float:
    """
    Validate and normalize top_p value.

    top_p must be between 0.0 and 1.0 in increments of 0.01.
    Due to floating-point precision, we round to nearest 0.01.
    """
    # Round to 2 decimal places
    normalized = round(value, 2)

    # Ensure within bounds
    if normalized < 0.0:
        normalized = 0.0
    elif normalized > 1.0:
        normalized = 1.0

    return normalized


def normalize_animal_config(config: dict) -> dict:
    """
    Normalize all float values in animal config to avoid validation errors.
    """
    if 'temperature' in config:
        config['temperature'] = validate_temperature(config['temperature'])

    if 'topP' in config:
        config['topP'] = validate_top_p(config['topP'])

    return config
