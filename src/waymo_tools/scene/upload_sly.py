import supervisely_lib as sly
import logging

import os
logger = logging.getLogger()


class UploadSly:
    def __init__(self, project_id=None, project_name='KITTI_import', ds_name='pointcloud'):

        self.api = sly.Api.from_env()
        if project_id:
            self.project = self.api.project.get_info_by_id(project_id)
        else:
            self.project = self.api.project.create(os.environ["context.workspaceId"],
                                                   project_name,
                                                   type=sly.ProjectType.POINT_CLOUDS,
                                                   change_name_if_conflict=True)
        self.dataset = self.api.dataset.create(self.project.id, f'{ds_name}', change_name_if_conflict=True)
        logger.info(f"Api create new dataset: {self.dataset.name}")

    def update_meta(self, meta):
        self.api.project.update_meta(self.project.id, meta.to_json())
        logger.info(f'Meta udpdated')

    def upload(self, pointcloud_filepaths, annotation, name):
        upload_info = self.api.pointcloud.upload_path(self.dataset.id, name=name, path=pointcloud_filepaths)
        self.api.pointcloud.annotation.append(upload_info.id, annotation)  # annotation upload
        logger.info(f'{name} uploaded')

