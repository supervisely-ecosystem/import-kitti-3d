def init(data, state):
    data["started"] = False
    data["finished"] = False

    state["mode"] = "public"
    state["samplePercent"] = 10
    state["size"] = "train_100"  # train_100 train_200 train_300 train_400 train_500 test_100 etc
    state["customDataPath"] = None

    state["resultingProjectName"] = "My KITTI Project"  # "KITTI Project"
    state["resultingDatasetName"] = "My KITTI Dataset"  # "KITTI Dataset"
