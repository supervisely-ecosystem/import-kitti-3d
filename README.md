<div align="center" markdown>
<img src="https://i.imgur.com/TzH2Bds.png"/>

# Import KITTI 3D

<p align="center">
  <a href="#Overview">Overview</a> •
  <a href="#Preparation">Preparation</a> •
  <a href="#How-To-Run">How To Run</a> •
  <a href="#How-To-Use">How To Use</a>
</p>
  
[![](https://img.shields.io/badge/supervisely-ecosystem-brightgreen)](https://ecosystem.supervise.ly/apps/supervisely-ecosystem/import-kitti-3d)
[![](https://img.shields.io/badge/slack-chat-green.svg?logo=slack)](https://supervise.ly/slack)
![GitHub release (latest SemVer)](https://img.shields.io/github/v/release/supervisely-ecosystem/import-kitti-3d)
[![views](https://app.supervise.ly/public/api/v3/ecosystem.counters?repo=supervisely-ecosystem/import-kitti-3d&counter=views&label=views)](https://supervise.ly)
[![used by teams](https://app.supervise.ly/public/api/v3/ecosystem.counters?repo=supervisely-ecosystem/import-kitti-3d&counter=downloads&label=used%20by%20teams)](https://supervise.ly)
[![runs](https://app.supervise.ly/public/api/v3/ecosystem.counters?repo=supervisely-ecosystem/import-kitti-3d&counter=runs&label=runs&123)](https://supervise.ly)

</div>

## Overview
Converts [KITTI 3D](http://www.cvlibs.net/datasets/kitti/) format to [Supervisely](https://docs.supervise.ly/data-organization/00_ann_format_navi) and creates a new project in selected `Team` -> `Workspace`. Backward compatible with [`Export to KITTI 3D`](https://github.com/supervisely-ecosystem/export-to-kitti-3d) app.

App can import sample data from original KITTI dataset with user selected amount of scenes for training and testing data: `100`, `200`, `300`, `400` or `500`. User also can import an archive with KITTI data from `Team Files`. If you want to import full KITTI dataset, you must download it manually from [KITTI website](http://www.cvlibs.net/datasets/kitti/eval_object.php?obj_benchmark=3d) and upload it to `Team Files`. **App supports only left color images**.

<img src="https://i.imgur.com/riv6fFJ.png">

KITTI object detection and orientation estimation benchmarks, consisting of 7481 training images and 7518 test images for each task, as well as the corresponding point clouds, comprising a total of 80.256 labeled objects, and 8 different labeled classes, only the classes `Car` and `Pedestrian` are evaluated in KITTI benchmark. `DontCare` labels denote regions in which objects have not been labeled, for example because they have been too far away from the laser scanner. You can use the `DontCare` labels in the training set to avoid that your object detector is harvesting hard negatives from those areas, in case you consider non-object regions from the training images as negative examples.

### Data Format Description

The data for training and testing can be found in the corresponding folders.
The sub-folders are structured as follows:

  - `image_02/` - contains the left color camera images (png)
  - `label_02/` - contains the left color camera label files (plain text files)
  - `calib/` - contains the calibration for all four cameras (plain text file)
  - `velodyne/` - contains KITTI LIDAR point cloud binary files

Sub-folder `label_02/` is not included in testing data because it don't have any labels. The label files contain the following information, which can be read and written using the matlab tools (readLabels.m, writeLabels.m) provided within this devkit. All values (numerical or strings) are separated via spaces, each row corresponds to one object.

**The 15 columns represent:**

<img src="https://i.imgur.com/JumBfcw.png" width=700>

###### [resource](https://github.com/bostondiditeam/kitti/blob/master/resources/devkit_object/readme.txt)

`archive tree structure here`

## How To Run 
**Step 1**: Add app to your team from [Ecosystem](https://ecosystem.supervise.ly/apps/import-kitti-3d) if it is not there.

**Step 2**: Run app from `Team` -> `Plugins & Apps` page. After running the app you will be redirected to the `Tasks` page.

<img src="https://i.imgur.com/HbDL4oQ.png"/>

**Step 3**: Waiting until the app is started.

Once app is started, new task will appear in `workspace tasks` (1). Wait for message `Application is started ...` and then press `Open` button (2).

<img src="https://i.imgur.com/4XGOoC4.png"/>

## How to use

**1. To import sample data from original KITTI 3D dataset** - select `Sample Data` in the gui and select a number of scenes to import. App will download and import KITTI data to a new project in selected `Team` -> `Workspace`.

1. Select `Sample Data`
2. Select a number of `training` data to import or select `None` if you don't need it.
3. Select a number of `testing` data to import or select `None` if you don't need it.
4. Select destination `Team`, `Workspace`, `Project name` and `Dataset` name (or names if you import both `training` and `testing` data)
5. Press `Run`

<img src="https://i.imgur.com/2qXcmeb.png" width=700/>

**2. To import your data in KITTI 3D format** - select `Custom Data`, upload archive with your dataset in KITTI format to `Team` -> `Files` and copy path to archive and paste it to the text input in the app gui.

1. Select `Custom Data`
2. Input path to your data from `Team` -> `Files`

<img src="https://i.imgur.com/olDBHFg.gif" width="700"/>

3. Select destination `Team`, `Workspace` and `Project name`
4. Press `Run`

<img src="https://i.imgur.com/plGTEH9.png"  width=700/>

You can access result project by clicking on it's name under the `Run` button. Resulting project will be saved to selected `Team` -> `Workspace`.

<img src="https://i.imgur.com/UhveUR6.png" width=700/>
