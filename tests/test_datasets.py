from unittest.mock import Mock, call, patch

from src.grout_deploy.datasets import GroutDatasets


def mock_path_exists_impl(path=""):
    return path in ("testPath/d1", "testPath/d1/l1.mbtiles")


def mock_get_tile_level_details(dataset, level):
    return (
        "test_packit_server",
        f"{dataset} packet",
        f"{level}.download.mbtiles",
    )


def get_mock_cfg():
    mock_datasets_cfg = Mock()
    mock_datasets_cfg.get_dataset_names.return_value = ["d1", "d2"]
    mock_datasets_cfg.get_dataset_tile_levels.return_value = ["l1", "l2"]
    mock_datasets_cfg.get_tile_level_details.side_effect = (
        mock_get_tile_level_details
    )
    return Mock(datasets=mock_datasets_cfg)


@patch("os.path.exists")
@patch("os.makedirs")
@patch("os.remove")
@patch("src.grout_deploy.datasets.GroutPackit.download_file")
def test_download_no_refresh(
    mock_packit_download, mock_remove, mock_makedirs, mock_path_exists
):
    mock_cfg = get_mock_cfg()
    path = "testPath"

    mock_path_exists.side_effect = mock_path_exists_impl

    sut = GroutDatasets(mock_cfg, path)
    sut.download(False)

    mock_makedirs.assert_called_once_with("testPath/d2")
    mock_remove.assert_not_called()
    mock_packit_download.assert_has_calls(
        [
            call(
                "test_packit_server",
                "d1 packet",
                "l2.download.mbtiles",
                "testPath/d1/l2.mbtiles",
            ),
            call(
                "test_packit_server",
                "d2 packet",
                "l1.download.mbtiles",
                "testPath/d2/l1.mbtiles",
            ),
            call(
                "test_packit_server",
                "d2 packet",
                "l2.download.mbtiles",
                "testPath/d2/l2.mbtiles",
            ),
        ]
    )


@patch("os.path.exists")
@patch("os.makedirs")
@patch("os.remove")
@patch("src.grout_deploy.datasets.GroutPackit.download_file")
def test_download_refresh_all(
    mock_packit_download, mock_remove, mock_makedirs, mock_path_exists
):
    mock_cfg = get_mock_cfg()
    path = "testPath"

    mock_path_exists.side_effect = mock_path_exists_impl

    sut = GroutDatasets(mock_cfg, path)
    sut.download(True)

    mock_makedirs.assert_called_once_with("testPath/d2")
    mock_remove.assert_called_once_with("testPath/d1/l1.mbtiles")
    mock_packit_download.assert_has_calls(
        [
            call(
                "test_packit_server",
                "d1 packet",
                "l1.download.mbtiles",
                "testPath/d1/l1.mbtiles",
            ),
            call(
                "test_packit_server",
                "d1 packet",
                "l2.download.mbtiles",
                "testPath/d1/l2.mbtiles",
            ),
            call(
                "test_packit_server",
                "d2 packet",
                "l1.download.mbtiles",
                "testPath/d2/l1.mbtiles",
            ),
            call(
                "test_packit_server",
                "d2 packet",
                "l2.download.mbtiles",
                "testPath/d2/l2.mbtiles",
            ),
        ]
    )


@patch("shutil.rmtree")
def test_delete_all(mock_rm_tree):
    mock_cfg = Mock()
    path = "testPath"
    sut = GroutDatasets(mock_cfg, path)
    sut.delete_all()
    mock_rm_tree.assert_called_with(path)
