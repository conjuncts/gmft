from gmft.reformat.instruction import BaseInstruction


class FilterPredictionsInstruction(BaseInstruction):
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

    def execute(self, predictions):
        """
        Execute the filtering of predictions based on the threshold.

        :param predictions: List of predictions to filter.
        :return: Filtered list of predictions.
        """
        return [pred for pred in predictions if pred['score'] >= self.threshold]