import os
import glob
import shutil
import numpy as np
import globals as g
import open3d as o3d
import init_ui_progress
import supervisely as sly
from supervisely.geometry.cuboid_3d import Cuboid3d, Vector3d
from supervisely.pointcloud_annotation.pointcloud_object_collection import PointcloudObjectCollection
from supervisely.project.pointcloud_project import OpenMode


def get_kitti_files_list(kitti_dataset_path):
    binfiles_glob = os.path.join(kitti_dataset_path, "velodyne/*.bin")
    bin_paths = sorted(glob.glob(binfiles_glob))
    if len(bin_paths) < 1:
        sly.logger.error(f"No pointclouds found! Check path: {binfiles_glob}")

    image_paths = [x.replace('velodyne', 'image_2').replace('.bin', '.png') for x in bin_paths]
    calib_paths = [x.replace('velodyne', 'calib').replace('.bin', '.txt') for x in bin_paths]

    if os.path.exists(os.path.join(kitti_dataset_path, "label_2")):
        label_paths = [x.replace('velodyne', 'label_2').replace('.bin', '.txt') for x in bin_paths]
    else:
        label_paths = []
        for x in bin_paths:
            label_paths.append(None)

    return bin_paths, label_paths, image_paths, calib_paths


def read_kitti_annotations(label_paths, calib_paths, ds_name):
    all_labels = []
    all_calib = []
    for label_file, calib_file in zip(label_paths, calib_paths):
        calib = o3d.ml.datasets.KITTI.read_calib(calib_file)
        if ds_name == "training":
            labels = o3d.ml.datasets.KITTI.read_label(label_file, calib)
            all_labels.append(labels)
        all_calib.append(calib)
        if ds_name == "testing":
            all_labels.append(None)
    return all_labels, all_calib


def convert_labels_to_meta(labels, geometry=Cuboid3d):
    labels = flatten(labels)
    unique_labels = np.unique([l.label_class for l in labels])
    obj_classes = [sly.ObjClass(k, geometry) for k in unique_labels]
    meta = sly.ProjectMeta(obj_classes=sly.ObjClassCollection(obj_classes))
    return meta


def convert_bin_to_pcd(bin_file, save_filepath):
    bin = np.fromfile(bin_file, dtype=np.float32).reshape(-1, 4)
    points = bin[:, 0:3]
    intensity = bin[:, -1]
    intensity_fake_rgb = np.zeros((intensity.shape[0], 3))
    intensity_fake_rgb[:,0] = intensity
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


def convert_label_to_annotation(label, meta):
    geometries = _convert_label_to_geometry(label)
    figures = []
    objs = []
    for l, geometry in zip(label, geometries):  # by object in point cloud
        pcobj = sly.PointcloudObject(meta.get_obj_class(l.label_class))
        figures.append(sly.PointcloudFigure(pcobj, geometry))
        objs.append(pcobj)

    annotation = sly.PointcloudAnnotation(PointcloudObjectCollection(objs), figures)
    return annotation


def convert_calib_to_image_meta(image_name, calib_path, camera_num=2):
    with open(calib_path, 'r') as f:
        lines = f.readlines()

    assert 0 < camera_num < 4
    intrinsic_matrix = lines[camera_num].strip().split(' ')[1:]
    intrinsic_matrix = np.array(intrinsic_matrix, dtype=np.float32).reshape(3, 4)[:3, :3]

    obj = lines[4].strip().split(' ')[1:]
    rect_4x4 = np.eye(4, dtype=np.float32)
    rect_4x4[:3, :3] = np.array(obj, dtype=np.float32).reshape(3, 3)

    obj = lines[5].strip().split(' ')[1:]
    Tr_velo_to_cam = np.eye(4, dtype=np.float32)
    Tr_velo_to_cam[:3] = np.array(obj, dtype=np.float32).reshape(3, 4)
    world_cam = np.transpose(rect_4x4 @ Tr_velo_to_cam)
    extrinsic_matrix = world_cam[:4,:3].T

    data = {
        "name": image_name,
        "meta": {
            "sensorsData": {
                "extrinsicMatrix": list(extrinsic_matrix.flatten().astype(float)),
                "intrinsicMatrix": list(intrinsic_matrix.flatten().astype(float))
            }
        }
    }
    return data


def start(kitti_base_dir, sly_project_path, train_ds_name, test_ds_name):
    shutil.rmtree(sly_project_path, ignore_errors=True)  # WARN!
    project_fs = sly.PointcloudProject(sly_project_path, OpenMode.CREATE)

    for kitti_dataset_path in os.listdir(kitti_base_dir):
        kitti_dataset_name = kitti_dataset_path
        kitti_dataset_path = os.path.join(kitti_base_dir, kitti_dataset_path)

        bin_paths, label_paths, image_paths, calib_paths = get_kitti_files_list(kitti_dataset_path)
        kitti_labels, kitti_calibs = read_kitti_annotations(label_paths, calib_paths, kitti_dataset_name)

        sly.logger.info(f"Loading KITTI dataset with {len(bin_paths)} pointclouds")
        if kitti_dataset_name == "training":
            dataset_fs = project_fs.create_dataset(train_ds_name)
        elif kitti_dataset_name == "testing":
            dataset_fs = project_fs.create_dataset(test_ds_name)
        else:
            raise Exception(f"Expecting: 'training' or 'testing' dataset name, instead of '{kitti_dataset_name}'")

        sly.logger.info(f"Created Supervisely dataset with {dataset_fs.name} at {dataset_fs.directory}")
        if kitti_dataset_name == "training":
            meta = convert_labels_to_meta(kitti_labels)
            project_fs.set_meta(meta)

        progress_items_cb = init_ui_progress.get_progress_cb(g.api,
                                                             g.task_id,
                                                             f'Converting dataset: {kitti_dataset_name}',
                                                             len(bin_paths))

        for bin_path, kitti_label, image_path, calib_path in zip(bin_paths, kitti_labels, image_paths, calib_paths):
            item_name = sly.fs.get_file_name(bin_path) + ".pcd"
            item_path = dataset_fs.generate_item_path(item_name)

            convert_bin_to_pcd(bin_path, item_path)  # automatically save pointcloud to itempath

            if kitti_dataset_name == "training":
                ann = convert_label_to_annotation(kitti_label, meta)
                dataset_fs.add_item_file(item_name, item_path, ann)
            else:
                dataset_fs.add_item_file(item_name, item_path)

            related_images_path = dataset_fs.get_related_images_path(item_name)
            os.makedirs(related_images_path, exist_ok=True)
            image_name = sly.fs.get_file_name_with_ext(image_path)
            sly_path_img = os.path.join(related_images_path, image_name)
            shutil.copy(src=image_path, dst=sly_path_img)

            img_info = convert_calib_to_image_meta(image_name, calib_path)
            sly.json.dump_json_file(img_info, sly_path_img + '.json')
            #sly.logger.info(f".bin -> {item_name}")
            progress_items_cb(1)

        sly.logger.info(f"Job done, dataset converted. Project_path: {sly_project_path}")
