from unittest.mock import Mock, call, patch

from src.grout_deploy.region_metadata import GroutRegionMetadata


def mock_path_exists_impl(path=""):
    return path in ("testPath/d1", "testPath/d1/l1/art_d1_l1_file1.json")


def mock_get_region_metadata_level_details(dataset, level):
    return (
        "test_packit_server",
        f"{dataset} packet",
        f"art_{dataset}_{level}",
    )

def get_mock_cfg():
    mock_datasets_cfg = Mock()
    mock_datasets_cfg.get_dataset_names.return_value = ["d1", "d2"]
    mock_datasets_cfg.has_region_metadata.return_value = True
    mock_datasets_cfg.get_dataset_region_metadata_levels.return_value = ["l1", "l2"]
    mock_datasets_cfg.get_region_metadata_level_details.side_effect = (
        mock_get_region_metadata_level_details
    )
    return Mock(datasets=mock_datasets_cfg)

mock_packit_artefacts = {
    "art_d1_l1": ["level1/art_d1_l1_file1.json", "level1/art_d1_l1_file2.json"],
    "art_d1_l2": ["level2/art_d1_l2_file1.json"],
    "art_d2_l1": ["level1/art_d2_l1_file1.json", "level1/art_d2_l1_file2.json"],
    "art_d2_l2": ["level2/art_d2_l2_file1.json"]
}

@patch("os.path.exists")
@patch("os.makedirs")
@patch("os.remove")
@patch("src.grout_deploy.datasets.GroutPackit.download_file")
@patch("src.grout_deploy.datasets.GroutPackit.get_artefacts")
def test_download_no_refresh(
    mock_packit_get_artefacts, mock_packit_download, mock_remove, mock_makedirs, mock_path_exists
):
    mock_cfg = get_mock_cfg()
    path = "testPath"

    mock_packit_get_artefacts.return_value = mock_packit_artefacts
    mock_path_exists.side_effect = mock_path_exists_impl

    sut = GroutRegionMetadata(mock_cfg, path)
    sut.download(False)

    mock_makedirs.assert_has_calls(
        [
            call("testPath/d1/l2"),
            call("testPath/d2/l1"),
            call("testPath/d2/l2")
        ]
    )

    mock_remove.assert_not_called()
    mock_packit_download.assert_has_calls(
        [
            call(
                "test_packit_server",
                "d1 packet",
                "art_d1_l1_file2.json",
                "level1/art_d1_l1_file2.json",
                "testPath/d1/l1/art_d1_l1_file2.json",
            ),
            call(
                "test_packit_server",
                "d1 packet",
                "art_d1_l2_file1.json",
                "level2/art_d1_l2_file1.json",
                "testPath/d1/l2/art_d1_l2_file1.json",
            ),
            call(
                "test_packit_server",
                "d2 packet",
                "art_d2_l1_file1.json",
                "level1/art_d2_l1_file1.json",
                "testPath/d2/l1/art_d2_l1_file1.json",
            ),
            call(
                "test_packit_server",
                "d2 packet",
                "art_d2_l1_file2.json",
                "level1/art_d2_l1_file2.json",
                "testPath/d2/l1/art_d2_l1_file2.json",
            ),
            call(
                "test_packit_server",
                "d2 packet",
                "art_d2_l2_file1.json",
                "level2/art_d2_l2_file1.json",
                "testPath/d2/l2/art_d2_l2_file1.json",
            )
        ]
    )


@patch("os.path.exists")
@patch("os.makedirs")
@patch("os.remove")
@patch("src.grout_deploy.datasets.GroutPackit.download_file")
@patch("src.grout_deploy.datasets.GroutPackit.get_artefacts")
def test_download_refresh_all(
    mock_packit_get_artefacts, mock_packit_download, mock_remove, mock_makedirs, mock_path_exists
):
    mock_cfg = get_mock_cfg()
    path = "testPath"

    mock_packit_get_artefacts.return_value = mock_packit_artefacts
    mock_path_exists.side_effect = mock_path_exists_impl

    sut = GroutRegionMetadata(mock_cfg, path)
    sut.download(True)

    mock_makedirs.assert_has_calls(
        [
            call("testPath/d1/l2"),
            call("testPath/d2/l1"),
            call("testPath/d2/l2")
        ]
    )

    mock_remove.assert_called_once_with("testPath/d1/l1/art_d1_l1_file1.json")
    mock_packit_download.assert_has_calls(
        [
            call(
                "test_packit_server",
                "d1 packet",
                "art_d1_l1_file1.json",
                "level1/art_d1_l1_file1.json",
                "testPath/d1/l1/art_d1_l1_file1.json",
            ),
            call(
                "test_packit_server",
                "d1 packet",
                "art_d1_l1_file2.json",
                "level1/art_d1_l1_file2.json",
                "testPath/d1/l1/art_d1_l1_file2.json",
            ),
            call(
                "test_packit_server",
                "d1 packet",
                "art_d1_l2_file1.json",
                "level2/art_d1_l2_file1.json",
                "testPath/d1/l2/art_d1_l2_file1.json",
            ),
            call(
                "test_packit_server",
                "d2 packet",
                "art_d2_l1_file1.json",
                "level1/art_d2_l1_file1.json",
                "testPath/d2/l1/art_d2_l1_file1.json",
            ),
            call(
                "test_packit_server",
                "d2 packet",
                "art_d2_l1_file2.json",
                "level1/art_d2_l1_file2.json",
                "testPath/d2/l1/art_d2_l1_file2.json",
            ),
            call(
                "test_packit_server",
                "d2 packet",
                "art_d2_l2_file1.json",
                "level2/art_d2_l2_file1.json",
                "testPath/d2/l2/art_d2_l2_file1.json",
            )
        ]
    )


@patch("shutil.rmtree")
def test_delete_all(mock_rm_tree):
    mock_cfg = Mock()
    path = "testPath"
    sut = GroutRegionMetadata(mock_cfg, path)
    sut.delete_all()
    mock_rm_tree.assert_called_with(path)
