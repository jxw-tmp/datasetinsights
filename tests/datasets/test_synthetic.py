import os
import tempfile
from pathlib import Path

import pandas as pd

from datasetinsights.datasets.synthetic import (
    SynDetection2D,
    _get_split,
    read_bounding_box_2d,
)
from datasetinsights.datasets.unity_perception import Captures
from datasetinsights.io.bbox import BBox2D


def test_syn_detection_2d():
    parent_dir = Path(__file__).parent.parent.absolute()
    mock_data_dir = str(parent_dir / "mock_data" / "simrun")
    syn_det_2d = SynDetection2D(data_path=mock_data_dir)

    # From mock data, only one of the capture has 2D bounding box
    # annotations.
    assert len(syn_det_2d) == 1
    assert len(syn_det_2d[0]) == 2


def test_read_bounding_box_2d():
    annotation = pd.DataFrame(
        {
            f"{Captures.VALUES_COLUMN}.instance_id": ["...", "..."],
            f"{Captures.VALUES_COLUMN}.label_id": [27, 30],
            f"{Captures.VALUES_COLUMN}.label_name": ["car", "boy"],
            f"{Captures.VALUES_COLUMN}.x": [30, 40],
            f"{Captures.VALUES_COLUMN}.y": [50, 60],
            f"{Captures.VALUES_COLUMN}.width": [100, 50],
            f"{Captures.VALUES_COLUMN}.height": [80, 60],
        }
    )
    definition = {
        "id": 1243,
        "name": "...",
        "description": "...",
        "format": "JSON",
        "spec": [{"label_id": 27, "label_name": "car"}],
    }
    label_mappings = {
        m["label_id"]: m["label_name"] for m in definition["spec"]
    }

    assert read_bounding_box_2d(annotation, label_mappings) == [
        BBox2D(27, 30, 50, 100, 80)
    ]


def test_get_split():
    mock_captures = pd.DataFrame({"id": [i for i in range(10)]})
    actual_train = _get_split(
        split="train", captures=mock_captures, train_percentage=0.6
    )
    actual_val = _get_split(
        split="val", captures=mock_captures, train_percentage=0.6
    )
    expected_train = pd.DataFrame({"id": [3, 8, 0, 9, 6, 7]})
    expected_val = pd.DataFrame({"id": [2, 1, 4, 5]})
    pd.testing.assert_frame_equal(expected_train, actual_train)
    pd.testing.assert_frame_equal(expected_val, actual_val)


def test_is_dataset_files_present_returns_true():
    with tempfile.TemporaryDirectory() as tmp:
        temp_dir = os.path.join(tmp, "temp_name")
        os.mkdir(temp_dir)
        with open(os.path.join(temp_dir, "annotation.json"), "x"):
            assert SynDetection2D.is_dataset_files_present(tmp)


def test_is_dataset_files_present_returns_false():
    with tempfile.TemporaryDirectory() as tmp:
        temp_dir = os.path.join(tmp, "temp_name")
        os.mkdir(temp_dir)
        assert not SynDetection2D.is_dataset_files_present(tmp)
