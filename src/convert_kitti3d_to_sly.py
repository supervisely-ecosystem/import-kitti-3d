import glob
import os
import shutil
from collections import defaultdict

import numpy as np
import open3d as o3d
import supervisely as sly
from supervisely.geometry.cuboid_3d import Cuboid3d, Vector3d
from supervisely.geometry.pointcloud import Pointcloud
from supervisely.io.fs import file_exists
from supervisely.pointcloud_annotation.pointcloud_object_collection import (
    PointcloudObjectCollection,
)
from supervisely.project.pointcloud_project import OpenMode

import globals as g
import init_ui_progress

cls_map_inv = defaultdict(str)

def get_kitti_files_list(kitti_dataset_path):
    binfiles_glob = os.path.join(kitti_dataset_path, "velodyne/*.bin")
    bin_paths = sorted(glob.glob(binfiles_glob))
    if len(bin_paths) < 1:
        raise Exception(f"Failed to find any pointclouds in the directory: {kitti_dataset_path}")

    filtered_bin_paths = []
    image_paths, missing_image_paths = [], []
    calib_paths, missing_calib_paths = [], []
    bbox_label_paths = []
    points_label_paths = []
    for bin_path in bin_paths:
        image_path = bin_path.replace("velodyne", "image_2").replace(".bin", ".png")
        calib_path = bin_path.replace("velodyne", "calib").replace(".bin", ".txt")
        if file_exists(image_path) and file_exists(calib_path):
            filtered_bin_paths.append(bin_path)
            image_paths.append(image_path)
            calib_paths.append(calib_path)

            bbox_label_path = bin_path.replace("velodyne", "label_2").replace(".bin", ".txt")
            label_dir = os.path.dirname(bbox_label_path)
            if not os.path.exists(label_dir):
                bbox_label_path = None
            elif not os.path.exists(bbox_label_path):
                bbox_label_path = None
            bbox_label_paths.append(bbox_label_path)

            points_label_path = bbox_label_path.replace(".txt", ".label")
            if not os.path.exists(points_label_path):
                points_label_path = None
            points_label_paths.append(points_label_path)

        else:
            sly.logger.warn(f"Skipping pointcloud: {sly.fs.get_file_name_with_ext(bin_path)}.")

            if not file_exists(image_path):
                missing_image_paths.append(image_path)

            if not file_exists(calib_path):
                missing_calib_paths.append(calib_path)

    if len(missing_image_paths) > 0 or len(missing_calib_paths) > 0:
        image_names = [sly.fs.get_file_name_with_ext(x) for x in missing_image_paths]
        calib_names = [sly.fs.get_file_name_with_ext(x) for x in missing_calib_paths]
        err_msg = (
            "Some files are missing:\n"
            f"  - {len(missing_image_paths)} photo context - {image_names},\n"
            f"  - {len(missing_calib_paths)} calibration files - {calib_names}"
        )
        sly.logger.warn(err_msg)

    return filtered_bin_paths, bbox_label_paths, image_paths, calib_paths, points_label_paths


def read_kitti_annotations(bbox_label_paths, calib_paths, ds_name, points_label_paths):
    bbox_labels = []
    all_calib = []
    points_labels = []
    for bbox, calib_file, pcd_label in zip(bbox_label_paths, calib_paths, points_label_paths):
        calib = o3d.ml.datasets.KITTI.read_calib(calib_file)
        if ds_name == "training":
            if bbox is None:
                raise Exception(
                    f"One of the pointclouds in the training dataset does not have a corresponding label file"
                )
            labels = o3d.ml.datasets.KITTI.read_label(bbox, calib)
            bbox_labels.append(labels)
            if pcd_label is not None:
                labels = np.fromfile(pcd_label, dtype=np.uint32)
                points_labels.append(labels)
            else:
                points_labels.append(None)
        all_calib.append(calib)
        if ds_name == "testing":
            bbox_labels.append(None)
            points_labels.append(None)
    return bbox_labels, all_calib, points_labels


def convert_labels_to_meta(labels, points_labels):
    labels = flatten(labels)
    unique_labels = np.unique([l.label_class for l in labels])
    obj_classes = [sly.ObjClass(k, Cuboid3d) for k in unique_labels]
    meta = sly.ProjectMeta(obj_classes=sly.ObjClassCollection(obj_classes))

    global cls_map_inv
    for lbl in points_labels:
        if lbl is not None:
            sem_label = np.array([l & 0xFFFF for l in lbl], dtype=np.uint16).astype(np.uint8)

            unique_labels = np.unique(sem_label)
            for p in unique_labels:
                if p == 0:
                    continue
                cls_map_inv[p] = f"Object_{len(cls_map_inv)}"

    obj_classes = [sly.ObjClass(k, Pointcloud) for k in cls_map_inv.values()]
    meta = meta.add_obj_classes(obj_classes)

    return meta


def convert_bin_to_pcd(bin_file, save_filepath):
    try:
        bin = np.fromfile(bin_file, dtype=np.float32).reshape(-1, 4)
    except ValueError as e:
        raise Exception(
            f"Incorrect data in the KITTI 3D pointcloud file: {bin_file}. "
            f"There was an error while trying to reshape the data into a 4-column matrix: {e}. "
            "Please ensure that the binary file contains a multiple of 4 elements to be "
            "successfully reshaped into a (N, 4) array.\n"
        )
    points = bin[:, 0:3]
    intensity = bin[:, -1]
    intensity_fake_rgb = np.zeros((intensity.shape[0], 3))
    intensity_fake_rgb[:, 0] = intensity
    pc = o3d.geometry.PointCloud(o3d.utility.Vector3dVector(points))
    pc.colors = o3d.utility.Vector3dVector(intensity_fake_rgb)
    o3d.io.write_point_cloud(save_filepath, pc)


def flatten(list_2d):
    return sum(list_2d, [])


def _convert_label_to_geometry(label):
    geometries = []
    for l in label:
        bbox = l.to_xyzwhlr()
        dim = bbox[[3, 5, 4]]
        pos = bbox[:3] + [0, 0, dim[1] / 2]
        yaw = bbox[-1]
        position = Vector3d(float(pos[0]), float(pos[1]), float(pos[2]))
        rotation = Vector3d(0, 0, float(-yaw))

        dimension = Vector3d(float(dim[0]), float(dim[2]), float(dim[1]))
        geometry = Cuboid3d(position, rotation, dimension)
        geometries.append(geometry)
    return geometries


def convert_bbox_label_to_annotation(label, meta):
    geometries = _convert_label_to_geometry(label)
    figures = []
    objs = []
    for l, geometry in zip(label, geometries):  # by object in point cloud
        pcobj = sly.PointcloudObject(meta.get_obj_class(l.label_class))
        figures.append(sly.PointcloudFigure(pcobj, geometry))
        objs.append(pcobj)

    return objs, figures


def convert_points_label_to_annotation(label, meta):
    sem_label = np.array([l & 0xFFFF for l in label], dtype=np.uint16).astype(np.uint8)
    inst_label = np.array([l >> 16 for l in label], dtype=np.uint16).astype(np.uint8)

    figures = []
    objs = []
    unique_figures = np.unique(inst_label)
    for i in unique_figures:
        if i == 0:
            continue
        curr_inst = np.where(inst_label == i)[0]
        segm_cls_id = sem_label[curr_inst[0]]
        cls_name = cls_map_inv.get(segm_cls_id)
        pcobj = sly.PointcloudObject(meta.get_obj_class(cls_name))
        figures.append(sly.PointcloudFigure(pcobj, Pointcloud(curr_inst.tolist())))
        objs.append(pcobj)

    return objs, figures


def convert_calib_to_image_meta(image_name, calib_path, camera_num=2):
    with open(calib_path, "r") as f:
        lines = f.readlines()

    assert 0 < camera_num < 4
    intrinsic_matrix = lines[camera_num].strip().split(" ")[1:]
    intrinsic_matrix = np.array(intrinsic_matrix, dtype=np.float32).reshape(3, 4)[:3, :3]

    obj = lines[4].strip().split(" ")[1:]
    rect_4x4 = np.eye(4, dtype=np.float32)
    rect_4x4[:3, :3] = np.array(obj, dtype=np.float32).reshape(3, 3)

    obj = lines[5].strip().split(" ")[1:]
    Tr_velo_to_cam = np.eye(4, dtype=np.float32)
    Tr_velo_to_cam[:3] = np.array(obj, dtype=np.float32).reshape(3, 4)
    world_cam = np.transpose(rect_4x4 @ Tr_velo_to_cam)
    extrinsic_matrix = world_cam[:4, :3].T

    data = {
        "name": image_name,
        "meta": {
            "deviceId": "CAM_LEFT",
            "sensorsData": {
                "extrinsicMatrix": list(extrinsic_matrix.flatten().astype(float)),
                "intrinsicMatrix": list(intrinsic_matrix.flatten().astype(float)),
            },
        },
    }
    return data


def start(kitti_base_dir, sly_project_path, train_ds_name, test_ds_name):
    shutil.rmtree(sly_project_path, ignore_errors=True)  # WARN!
    project_fs = sly.PointcloudProject(sly_project_path, OpenMode.CREATE)

    sly.fs.remove_junk_from_dir(kitti_base_dir)
    sly.logger.debug(f"Removed junk files from {kitti_base_dir}...")

    def _check_function(path):
        if not os.path.isdir(path):
            return False
        if len(os.listdir(path)) == 0:
            return False
        if all([x in ["training", "testing"] for x in os.listdir(path)]):
            return True
        return False

    base_dir = [x for x in sly.fs.dirs_filter(kitti_base_dir, _check_function)]

    if len(base_dir) == 0:
        raise Exception(f"KITTI 3D datasets not found in the dataset {kitti_base_dir}")
    kitti_base_dir = base_dir[0]
    for kitti_dataset_name in os.listdir(kitti_base_dir):
        kitti_dataset_path = os.path.join(kitti_base_dir, kitti_dataset_name)

        bin_paths, bbox_label_paths, image_paths, calib_paths, points_label_paths = (
            get_kitti_files_list(kitti_dataset_path)
        )
        if len(bin_paths) == 0:
            sly.logger.warn(
                f"Skipping KITTI dataset: {kitti_dataset_name}. Not found correct data."
            )
            continue
        kitti_labels, _, points_labels = read_kitti_annotations(
            bbox_label_paths, calib_paths, kitti_dataset_name, points_label_paths
        )

        sly.logger.info(f"Loading KITTI dataset with {len(bin_paths)} pointclouds")
        if kitti_dataset_name == "training":
            dataset_fs = project_fs.create_dataset(train_ds_name)
        elif kitti_dataset_name == "testing":
            dataset_fs = project_fs.create_dataset(test_ds_name)
        else:
            raise Exception(
                f"Expecting: 'training' or 'testing' dataset name, instead of '{kitti_dataset_name}'"
            )

        sly.logger.info(
            f"Created Supervisely dataset with {dataset_fs.name} at {dataset_fs.directory}"
        )
        if kitti_dataset_name == "training":
            meta = convert_labels_to_meta(kitti_labels, points_labels)
            project_fs.set_meta(meta)

        progress_items_cb = init_ui_progress.get_progress_cb(
            g.api,
            g.task_id,
            f"Converting dataset: {kitti_dataset_name}",
            len(bin_paths),
        )

        for bin_path, kitti_label, image_path, calib_path, points_label in zip(
            bin_paths, kitti_labels, image_paths, calib_paths, points_labels
        ):
            item_name = sly.fs.get_file_name(bin_path) + ".pcd"
            item_path = dataset_fs.generate_item_path(item_name)

            convert_bin_to_pcd(bin_path, item_path)  # automatically save pointcloud to itempath

            if kitti_dataset_name == "training":
                objs, figures = convert_bbox_label_to_annotation(kitti_label, meta)
                if points_label is not None:
                    extra_objs, extra_figures = convert_points_label_to_annotation(
                        points_label, meta
                    )
                    objs.extend(extra_objs)
                    figures.extend(extra_figures)
                ann = sly.PointcloudAnnotation(PointcloudObjectCollection(objs), figures)
                dataset_fs.add_item_file(item_name, item_path, ann)
            else:
                dataset_fs.add_item_file(item_name, item_path)

            related_images_path = dataset_fs.get_related_images_path(item_name)
            os.makedirs(related_images_path, exist_ok=True)
            image_name = sly.fs.get_file_name_with_ext(image_path)
            sly_path_img = os.path.join(related_images_path, image_name)
            shutil.copy(src=image_path, dst=sly_path_img)

            img_info = convert_calib_to_image_meta(image_name, calib_path)
            sly.json.dump_json_file(img_info, sly_path_img + ".json")
            # sly.logger.info(f".bin -> {item_name}")
            progress_items_cb(1)

        sly.logger.info(f"Job done, dataset converted. Project_path: {sly_project_path}")
