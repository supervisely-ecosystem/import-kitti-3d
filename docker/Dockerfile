# cuda:11.1-cudnn8-runtime-ubuntu20.04 + py3.8 + opencv + other bacis CV packages
# learn more here: https://github.com/supervisely/supervisely/blob/master/base_images/py/Dockerfile
FROM supervisely/base-py:6.1.6

RUN apt-get update
RUN pip install scikit-image
RUN python -m pip install open3d==0.13.0
