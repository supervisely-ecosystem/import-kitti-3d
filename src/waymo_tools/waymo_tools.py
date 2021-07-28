import numpy as np
import supervisely_lib as sly
import tensorflow as tf
import tqdm
from waymo_open_dataset import dataset_pb2 as open_dataset

from waymo_scene import WaymoScene
from kitty_scene import KittyScene
from scene.scene_to_sly_annotation import SlyAnnotation
from scene.upload_sly import UploadSly

import os
import glob

def read_waymo_tfrecord(pathname):
    """
    :param pathname: str path to *-segment-*.tfrecord
    :return: list of WaymoFrames
    """
    dataset = tf.data.TFRecordDataset(pathname, compression_type='')
    sequence = []

    for frame_idx, data in tqdm.tqdm(enumerate(dataset)):
        waymo_frame = open_dataset.Frame()
        waymo_frame.ParseFromString(bytearray(data.numpy()))
        fr = WaymoScene(waymo_frame)  # parse waymo frame as Scene class
        sequence.append(fr)
        if frame_idx > 10:
            break
    return sequence

def read_kitty_dataset(dataset_path):
    local_dataset_path = dataset_path
    assert os.path.isdir(local_dataset_path)
    bin_paths = glob.glob(local_dataset_path + "velodyne/*.bin")

    sequence = []
    for bin_path in tqdm.tqdm(bin_paths[0:10]):
        fr = KittyScene(bin_path)
        sequence.append(fr)
    return sequence


def collect_meta(sequence, geometry=sly.geometry.cuboid_3d.Cuboid3d):
    """
    :param labels: list of scenes [scene,scene,scene,scene]
    :return: sly.ProjectMeta
    """

    labels = sum([sc.labels for sc in sequence], [])  # sum(x, []) == np.flatten(x)
    unique_labels = np.unique(labels)
    obj_classes = [sly.ObjClass(k, geometry) for k in unique_labels]
    meta = sly.ProjectMeta(obj_classes=sly.ObjClassCollection(obj_classes))
    return meta


def main_waymo():
    global project_id, ds_name, readed_sequence
    project_id = 5351
    ds_name='waymo_cloud'

    # for 1 sequence Only (a lot of pointclouds in 1).
    readed_sequence = read_waymo_tfrecord(
        "/data/training_segment-10017090168044687777_6380_000_6400_000_with_camera_labels.tfrecord")


def main_kitty():
    global project_id, ds_name, readed_sequence
    project_id = 5359
    project_name = "Kitti_import"
    ds_name = 'Kitty_test_cloud'

    readed_sequence = read_kitty_dataset("/data/Kitti/training/")


if __name__ == "__main__":
    print("hello_world")
    #main_waymo()
    main_kitty()


    meta = collect_meta(readed_sequence)
    uploader = UploadSly(project_id=project_id, ds_name=ds_name)
    uploader.update_meta(meta)
    sa = SlyAnnotation(meta, tmp_dir='/data/', uploader=uploader)
    for scene in readed_sequence:
        sa.get_annotation(scene)
        sa.upload()




