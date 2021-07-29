def init(data, state):
    data["started"] = False
    data["finished"] = False

    state["mode"] = "public"
    state["samplePercent"] = 10
    state["size"] = "medium"
    state["customDataPath"] = None

    state["resultingProjectName"] = "KITTI Project"
