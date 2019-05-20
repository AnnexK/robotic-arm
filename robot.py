import pybullet as pb
import json
import os

class Robot:
    def __init__(self, filename):
        with open(filename, 'r') as fp:
            data = json.load(fp)
        path_list = filename.split(os.sep)[:-1:]
        urdf_filename = os.path.join(path_list, data['urdf_name'])
        self._id = pb.loadURDF(urdf_filename, flags=pb.URDF_USE_SELF_COLLISION)
        
    @property
    def id(self):
        return self._id
    
