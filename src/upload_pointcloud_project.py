import globals as g
import supervisely as sly
from supervisely.io.json import load_json_file
from supervisely.api.module_api import ApiField
from supervisely.video_annotation.key_id_map import KeyIdMap

import init_ui_progress

def upload_sly_pcd(project_dir, workspace_id, project_name):
    project = g.api.project.create(workspace_id,
                                 project_name,
                                 type=sly.ProjectType.POINT_CLOUDS,
                                 change_name_if_conflict=True)

    project_fs = sly.PointcloudProject.read_single(project_dir)

    g.api.project.update_meta(project.id, project_fs.meta.to_json())
    sly.logger.info("Project {!r} [id={!r}] has been created".format(project.name, project.id))

    uploaded_objects = KeyIdMap()

    for dataset_fs in project_fs:
        dataset = g.api.dataset.create(project.id, dataset_fs.name, change_name_if_conflict=True)
        sly.logger.info("dataset {!r} [id={!r}] has been created".format(dataset.name, dataset.id))

        progress_items_cb = init_ui_progress.get_progress_cb(g.api, g.task_id, f'Uploading dataset: {dataset.name}', len(dataset_fs))
        for item_name in dataset_fs:
            item_path, related_images_dir, ann_path = dataset_fs.get_item_paths(item_name)

            item_meta = {}
            pointcloud = g.api.pointcloud.upload_path(dataset.id, item_name, item_path, item_meta)

            # validate_item_annotation
            ann_json = sly.io.json.load_json_file(ann_path)
            ann = sly.PointcloudAnnotation.from_json(ann_json, project_fs.meta)

            # ignore existing key_id_map because the new objects will be created
            g.api.pointcloud.annotation.append(pointcloud.id, ann, uploaded_objects)

            # upload related_images if exist
            related_items = dataset_fs.get_related_images(item_name)
            if len(related_items) != 0:
                rimg_infos = []
                for img_path, meta_json in related_items:
                    # img_name = sly.fs.get_file_name(img_path)
                    img = g.api.pointcloud.upload_related_image(img_path)[0]
                    rimg_infos.append({ApiField.ENTITY_ID: pointcloud.id,
                                       ApiField.NAME: meta_json[ApiField.NAME],
                                       ApiField.HASH: img,
                                       ApiField.META: meta_json[ApiField.META]})

                g.api.pointcloud.add_related_images(rimg_infos)
            progress_items_cb(1)

    fields = [
        {"field": "data.started", "payload": False},
        {"field": "data.finished", "payload": True},
        {"field": "data.resultProject", "payload": project.name},
        {"field": "data.resultProjectId", "payload": project.id},
        {"field": "data.resultProjectPreviewUrl", "payload": g.api.image.preview_url("https://i.imgur.com/qmuNM6J.png", 100, 100)}
    ]
    g.api.task.set_fields(g.task_id, fields)
    g.my_app.show_modal_window(f"'{project.name}' project has been successfully imported.")
    g.my_app.stop()
