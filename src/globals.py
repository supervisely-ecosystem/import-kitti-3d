import os
import supervisely_lib as sly


my_app = sly.AppService()
api: sly.Api = my_app.public_api

task_id = my_app.task_id
team_id = int(os.environ['context.teamId'])
workspace_id = int(os.environ['context.workspaceId'])


storage_dir = os.path.join(my_app.data_dir, "kitty_importer")
sly.fs.mkdir(storage_dir, remove_content_if_exists=True)

kitty_small_dl_link = "https://drive.google.com/file/d/1Nm9elpMAQ6PJlueF9-vZdsS8-AS1I5Ep/view?usp=sharing"  # 20
kitty_med_dl_link = "https://drive.google.com/file/d/1QkS9V_YoCNC_O-wbn3OOSuPCQ1CYYP3X/view?usp=sharing"    # 800
kitty_big_dl_link = "https://drive.google.com/file/d/1LxHnk3PdSRxRkd2OjeUmP5d_S0xfEyBW/view?usp=sharing"    # 1600


path_to_kitty_ds = "/home/paul/Documents/Work/Applications/KITTY_data/unpacked"

train_dir = os.path.join(path_to_kitty_ds, "training")
test_dir = os.path.join(path_to_kitty_ds, "testing")

sm_kitty_path = "/home/paul/Documents/Work/Applications/SMALL_KITTY_data"
sm_train_dir = os.path.join(sm_kitty_path, "training")

med_kitty_path = "/home/paul/Documents/Work/Applications/MEDIUM_KITTY_data"
med_train_dir = os.path.join(med_kitty_path, "training")


sly_base_dir = "/home/paul/Documents/Work/Applications/SLY_data"
sly_project_name = "Kitty Project"
sly_proj_dir = os.path.join(sly_base_dir, sly_project_name)
