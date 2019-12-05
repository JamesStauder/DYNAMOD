#This code taken from stackoverflow at the following URL:
#https://stackoverflow.com/questions/26646362/numpy-array-is-not-json-serializable

import json
import numpy as np

class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return json.JSONEncoder.default(self, obj)