import os
import shutil
import requests
import globals as g
import init_ui_progress
from supervisely_lib.io.fs import download, file_exists


def download_kitty(link, save_path, file_name, app_logger):
    response = requests.head(link, allow_redirects=True)
    sizeb = int(response.headers.get('content-length', 0))
    progress_cb = init_ui_progress.get_progress_cb(g.api, g.task_id, f"Download {file_name}", sizeb, is_size=True)
    if not file_exists(save_path):
        download(link, save_path, cache=g.my_app.cache, progress=progress_cb)
        init_ui_progress.reset_progress(g.api, g.task_id)
        app_logger.info(f'{file_name} has been successfully downloaded')
    shutil.unpack_archive(save_path, g.storage_dir, format="zip")


def start(state, app_logger):
    if state["mode"] == "public":
        if state["size"] == "train_100":
            trainval_archive = os.path.join(g.storage_dir, "100_KITTY_TRAIN.zip")
            download_kitty(g.train_100, trainval_archive, "100_KITTY_TRAIN.zip", app_logger)
        elif state["size"] == "train_200":
            test_archive = os.path.join(g.storage_dir, "200_KITTY_TRAIN.zip")
            download_kitty(g.train_200, test_archive, "200_KITTY_TRAIN.zip", app_logger)
        elif state["size"] == "train_300":
            test_archive = os.path.join(g.storage_dir, "300_KITTY_TRAIN.zip")
            download_kitty(g.train_300, test_archive, "300_KITTY_TRAIN.zip", app_logger)
        elif state["size"] == "train_400":
            test_archive = os.path.join(g.storage_dir, "400_KITTY_TRAIN.zip")
            download_kitty(g.train_400, test_archive, "400_KITTY_TRAIN.zip", app_logger)
        elif state["size"] == "train_500":
            test_archive = os.path.join(g.storage_dir, "500_KITTY_TRAIN.zip")
            download_kitty(g.train_500, test_archive, "500_KITTY_TRAIN.zip", app_logger)
        elif state["size"] == "test_100":
            test_archive = os.path.join(g.storage_dir, "100_KITTY_TEST.zip")
            download_kitty(g.test_100, test_archive, "100_KITTY_TEST.zip", app_logger)
        elif state["size"] == "test_200":
            test_archive = os.path.join(g.storage_dir, "200_KITTY_TEST.zip")
            download_kitty(g.test_200, test_archive, "200_KITTY_TEST.zip", app_logger)
        elif state["size"] == "test_300":
            test_archive = os.path.join(g.storage_dir, "300_KITTY_TEST.zip")
            download_kitty(g.test_300, test_archive, "300_KITTY_TEST.zip", app_logger)
        elif state["size"] == "test_400":
            test_archive = os.path.join(g.storage_dir, "400_KITTY_TEST.zip")
            download_kitty(g.test_400, test_archive, "400_KITTY_TEST.zip", app_logger)
        elif state["size"] == "test_500":
            test_archive = os.path.join(g.storage_dir, "500_KITTY_TEST.zip")
            download_kitty(g.test_500, test_archive, "500_KITTY_TEST.zip", app_logger)
    else:
        remote_dir = state["customDataPath"]
        local_archive = os.path.join(g.storage_dir, os.path.basename(os.path.normpath(remote_dir)))
        file_size = g.api.file.get_info_by_path(g.team_id, remote_dir).sizeb
        if not file_exists(os.path.join(g.storage_dir, os.path.basename(os.path.normpath(remote_dir)))):
            progress_upload_cb = init_ui_progress.get_progress_cb(g.api,
                                                                  g.task_id,
                                                                  f'Download "{os.path.basename(os.path.normpath(remote_dir))}"',
                                                                  total=file_size,
                                                                  is_size=True)
            g.api.file.download(g.team_id, remote_dir, local_archive, progress_cb=progress_upload_cb)
            app_logger.info(f'"{os.path.basename(os.path.normpath(remote_dir))}" has been successfully downloaded')
        shutil.unpack_archive(local_archive, g.storage_dir)
