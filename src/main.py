import os
import init_ui
import globals as g
import init_ui_progress
import supervisely_lib as sly

import kitti_downloader
import convert_kitti3d_to_sly
import upload_pointcloud_project



@g.my_app.callback("import_kitti")
@sly.timeit
def import_kitty(api: sly.Api, task_id, context, state, app_logger):
    kitti_downloader.start(state, app_logger)

    sly_project_name = state["resultingProjectName"]
    sly_ds_name = state["resultingDatasetName"]
    sly_proj_dir = os.path.join(g.sly_base_dir, sly_project_name)

    convert_kitti3d_to_sly.start(g.train_dir, sly_proj_dir, sly_ds_name)
    upload_pointcloud_project.upload_sly_pcd(sly_proj_dir, state["workspaceId"], sly_project_name)

    g.my_app.show_modal_window(f"'{state['resultingProjectName']}' project has been successfully imported.")
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
