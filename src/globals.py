import os

import supervisely as sly
from dotenv import load_dotenv
from supervisely.app.v1.app_service import AppService

if sly.is_development():
    load_dotenv("local.env")
    load_dotenv(os.path.expanduser("~/supervisely.env"))


my_app = AppService(ignore_task_id=True)
api = my_app.public_api

task_id = my_app.task_id
team_id = sly.env.team_id()
workspace_id = sly.env.workspace_id()


storage_dir = os.path.join(my_app.data_dir, "kitti_importer")
kitti_base_dir = os.path.join(storage_dir, "kitti_base_dir")
train_dir = os.path.join(kitti_base_dir, "training")
test_dir = os.path.join(kitti_base_dir, "testing")

sly.fs.mkdir(storage_dir, remove_content_if_exists=True)
sly.fs.mkdir(kitti_base_dir, remove_content_if_exists=True)


sly_base_dir = os.path.join(storage_dir, "supervisely")
sly.fs.mkdir(sly_base_dir, remove_content_if_exists=True)

### LINKS
train_100 = "https://github.com/supervisely-ecosystem/import-kitti-3d-sample-files/releases/download/v0.0.3/100_training.zip"
test_100 = "https://github.com/supervisely-ecosystem/import-kitti-3d-sample-files/releases/download/v0.0.3/100_testing.zip"

train_200 = "https://github.com/supervisely-ecosystem/import-kitti-3d-sample-files/releases/download/v0.0.3/200_training.zip"
test_200 = "https://github.com/supervisely-ecosystem/import-kitti-3d-sample-files/releases/download/v0.0.3/200_testing.zip"

train_300 = "https://github.com/supervisely-ecosystem/import-kitti-3d-sample-files/releases/download/v0.0.3/300_training.zip"
test_300 = "https://github.com/supervisely-ecosystem/import-kitti-3d-sample-files/releases/download/v0.0.3/300_testing.zip"

train_400 = "https://github.com/supervisely-ecosystem/import-kitti-3d-sample-files/releases/download/v0.0.3/400_training.zip"
test_400 = "https://github.com/supervisely-ecosystem/import-kitti-3d-sample-files/releases/download/v0.0.3/400_testing.zip"

train_500 = "https://github.com/supervisely-ecosystem/import-kitti-3d-sample-files/releases/download/v0.0.3/500_training.zip"
test_500 = "https://github.com/supervisely-ecosystem/import-kitti-3d-sample-files/releases/download/v0.0.3/500_testing.zip"
