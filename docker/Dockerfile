# cuda:11.1-cudnn8-runtime-ubuntu20.04 + py3.8 + opencv + other bacis CV packages
# learn more here: https://github.com/supervisely/supervisely/blob/master/base_images/py/Dockerfile
FROM supervisely/base-py-sdk:6.1.104

RUN apt-get update
RUN pip install supervisely==6.1.104
RUN python -m pip install open3d==0.13.0
RUN pip install scikit-image==0.18.3
