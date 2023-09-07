import os
import shutil
import requests
import globals as g
import init_ui_progress
from supervisely.io.fs import download, file_exists, silent_remove, unpack_archive


def download_kitty(link, save_path, file_name, app_logger):
    response = requests.head(link, allow_redirects=True)
    sizeb = int(response.headers.get("content-length", 0))
    progress_cb = init_ui_progress.get_progress_cb(
        g.api, g.task_id, f"Download {file_name}", sizeb, is_size=True
    )
    if not file_exists(save_path):
        download(link, save_path, cache=g.my_app.cache, progress=progress_cb)
        init_ui_progress.reset_progress(g.api, g.task_id)
        app_logger.info(f"{file_name} has been successfully downloaded")
    unpack_archive(save_path, g.kitti_base_dir, remove_junk=True)
    # shutil.unpack_archive(save_path, g.kitti_base_dir, format="zip")
    silent_remove(save_path)


def start(state, app_logger):
    if state["mode"] == "public":
        if state["training"] == "train_0":
            pass
        if state["training"] == "train_100":
            trainval_archive = os.path.join(g.storage_dir, "100_KITTY_TRAIN.zip")
            download_kitty(
                g.train_100, trainval_archive, "100_KITTY_TRAIN.zip", app_logger
            )
        if state["training"] == "train_200":
            test_archive = os.path.join(g.storage_dir, "200_KITTY_TRAIN.zip")
            download_kitty(g.train_200, test_archive, "200_KITTY_TRAIN.zip", app_logger)
        if state["training"] == "train_300":
            test_archive = os.path.join(g.storage_dir, "300_KITTY_TRAIN.zip")
            download_kitty(g.train_300, test_archive, "300_KITTY_TRAIN.zip", app_logger)
        if state["training"] == "train_400":
            test_archive = os.path.join(g.storage_dir, "400_KITTY_TRAIN.zip")
            download_kitty(g.train_400, test_archive, "400_KITTY_TRAIN.zip", app_logger)
        if state["training"] == "train_500":
            test_archive = os.path.join(g.storage_dir, "500_KITTY_TRAIN.zip")
            download_kitty(g.train_500, test_archive, "500_KITTY_TRAIN.zip", app_logger)
        if state["testing"] == "test_0":
            pass
        if state["testing"] == "test_100":
            test_archive = os.path.join(g.storage_dir, "100_KITTY_TEST.zip")
            download_kitty(g.test_100, test_archive, "100_KITTY_TEST.zip", app_logger)
        if state["testing"] == "test_200":
            test_archive = os.path.join(g.storage_dir, "200_KITTY_TEST.zip")
            download_kitty(g.test_200, test_archive, "200_KITTY_TEST.zip", app_logger)
        if state["testing"] == "test_300":
            test_archive = os.path.join(g.storage_dir, "300_KITTY_TEST.zip")
            download_kitty(g.test_300, test_archive, "300_KITTY_TEST.zip", app_logger)
        if state["testing"] == "test_400":
            test_archive = os.path.join(g.storage_dir, "400_KITTY_TEST.zip")
            download_kitty(g.test_400, test_archive, "400_KITTY_TEST.zip", app_logger)
        if state["testing"] == "test_500":
            test_archive = os.path.join(g.storage_dir, "500_KITTY_TEST.zip")
            download_kitty(g.test_500, test_archive, "500_KITTY_TEST.zip", app_logger)
    else:
        remote_dir = state["customDataPath"]
        local_archive = os.path.join(
            g.kitti_base_dir, os.path.basename(os.path.normpath(remote_dir))
        )
        try:
            file_size = g.api.file.get_info_by_path(g.team_id, remote_dir).sizeb
        except AttributeError:
            raise Exception(
                f"File with path {remote_dir} wasn't found in TeamFiles of given Team ID {g.team_id}. "
                "Please check that the path is correct and the file exists."
            )
        if not file_exists(
            os.path.join(
                g.kitti_base_dir, os.path.basename(os.path.normpath(remote_dir))
            )
        ):
            progress_upload_cb = init_ui_progress.get_progress_cb(
                g.api,
                g.task_id,
                f'Download "{os.path.basename(os.path.normpath(remote_dir))}"',
                total=file_size,
                is_size=True,
            )
            g.api.file.download(
                g.team_id, remote_dir, local_archive, progress_cb=progress_upload_cb
            )
            app_logger.info(
                f'"{os.path.basename(os.path.normpath(remote_dir))}" has been successfully downloaded'
            )
        shutil.unpack_archive(local_archive, g.kitti_base_dir)
        silent_remove(local_archive)
