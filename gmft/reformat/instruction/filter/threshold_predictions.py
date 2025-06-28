from gmft.reformat.instruction import BaseInstruction


class PredictionThresholdInstruction(BaseInstruction):
    """
    Filter predictions based on a given threshold.
    """

    def __init__(self, threshold: float):
        """
        Initialize the filter instruction with a threshold.

        :param threshold: The threshold value for filtering predictions.
        """
        super().__init__()
        self.threshold = threshold
