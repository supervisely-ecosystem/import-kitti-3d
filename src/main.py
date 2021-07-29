import os
import globals as g
import supervisely_lib as sly

import convert_kitty3d_to_sly
import upload_pointcloud_project

import shutil
import requests
import init_ui
import init_ui_progress
from supervisely_lib.io.fs import download, file_exists


def kitty_downloader(link, save_path, file_name, app_logger):
    response = requests.head(link, allow_redirects=True)
    sizeb = int(response.headers.get('content-length', 0))
    progress_cb = init_ui_progress.get_progress_cb(g.api, g.task_id, f"Download {file_name}", sizeb, is_size=True)
    if not file_exists(save_path):
        download(link, save_path, cache=g.my_app.cache, progress=progress_cb)
        init_ui_progress.reset_progress(g.api, g.task_id)
        app_logger.info(f'{file_name} has been successfully downloaded')
    shutil.unpack_archive(save_path, g.storage_dir, format="tar")


@g.my_app.callback("import_kitty")
@sly.timeit
def import_kitty(api: sly.Api, task_id, context, state, app_logger):
    if state["mode"] == "public":
        if state["size"] == "small":
            trainval_archive = os.path.join(g.storage_dir, "Small_KITTY.zip")
            kitty_downloader(g.kitty_small_dl_link, trainval_archive, "Small_KITTY.zip", app_logger)
        elif state["size"] == "medium":
            test_archive = os.path.join(g.storage_dir, "Medium_KITTY.zip")
            kitty_downloader(g.kitty_med_dl_link, test_archive, "Medium_KITTY.zip", app_logger)
        elif state["size"] == "big":
            test_archive = os.path.join(g.storage_dir, "Big_KITTY.zip")
            kitty_downloader(g.kitty_big_dl_link, test_archive, "Big_KITTY.zip", app_logger)
        #if state["size"] == "full":
        #    test_archive = os.path.join(g.storage_dir, "Full_KITTY.zip"")
        #    kitty_downloader(g.pascal_test_dl_link, test_archive, "Full_KITTY.zip", app_logger)
    else:
        remote_dir = state["customDataPath"]
        local_archive = os.path.join(g.storage_dir, os.path.basename(os.path.normpath(remote_dir)))
        file_size = api.file.get_info_by_path(g.team_id, remote_dir).sizeb
        if not file_exists(os.path.join(g.storage_dir, os.path.basename(os.path.normpath(remote_dir)))):
            progress_upload_cb = init_ui_progress.get_progress_cb(g.api,
                                                                  task_id,
                                                                  f'Download "{os.path.basename(os.path.normpath(remote_dir))}"',
                                                                  total=file_size,
                                                                  is_size=True)
            api.file.download(g.team_id, remote_dir, local_archive, progress_cb=progress_upload_cb)
            app_logger.info(f'"{os.path.basename(os.path.normpath(remote_dir))}" has been successfully downloaded')
        shutil.unpack_archive(local_archive, g.storage_dir)


    convert_kitty3d_to_sly.start(g.sm_train_dir, g.sly_proj_dir, 'kitty_dataset')
    upload_pointcloud_project.upload_sly_pcd(g.sly_proj_dir, state["workspaceId"], g.sly_project_name)

    g.my_app.stop()


def main():
    sly.logger.info(
        "Script arguments",
        extra={
            "team_id": g.team_id,
            "workspace_id": g.workspace_id,
            "task_id": g.task_id
        }
    )

    data = {}
    state = {}

    init_ui.init(data, state)
    init_ui_progress.init_progress(data,state)
    g.my_app.run(data=data, state=state)


if __name__ == "__main__":
    sly.main_wrapper("main", main)
