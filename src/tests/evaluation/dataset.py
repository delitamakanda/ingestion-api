import json

from pathlib import Path

from tests.evaluation.models import EvaluationCase


def load_dataset() -> list[EvaluationCase]:
    """
    Load the evaluation dataset from a JSON file.

    Returns:
        list[EvaluationCase]: A list of EvaluationCase objects loaded from the dataset.
    """
    dataset_path = Path(__file__).parent / "dataset.json"
    with open(dataset_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        return [EvaluationCase(**item) for item in data]