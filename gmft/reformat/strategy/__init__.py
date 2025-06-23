class StrategySettings:
    """
    A class to hold settings for a specific reformatting strategy.

    Strategies include as_is, lta (large table assumption), hybrid
    """

    _smallest_supported_text_height: float = 0.1
    """The smallest supported text height. Text smaller than this height will be ignored. 
    Helps prevent very small text from creating huge arrays under large table assumption."""