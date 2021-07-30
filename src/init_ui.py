def init(data, state):
    data["started"] = False
    data["finished"] = False

    state["mode"] = "public"         # custom
    state["training"] = "train_100"  # train_0 train_100 train_200 train_300 train_400 train_500
    state["testing"] = "test_0"      # test_0 test_100 test_200 test_300 test_400 test_500
    state["customDataPath"] = ""

    state["resultingProjectName"] = "my_project"
    state["resultingTrainDatasetName"] = "training"
    state["resultingTestDatasetName"] = "testing"
