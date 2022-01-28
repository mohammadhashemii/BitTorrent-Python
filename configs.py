"""configs in json format"""
import json

CFG = {
    "directory": {
        "logs_dir": "logs/",
        "node_files_dir": "node_files/",
        "tracker_db_dir": "tracker_db/"
    },
    "constants": {
        "AVAILABLE_PORTS_RANGE": (1024, 65535), # range of available ports on the local computer
        "TRACKER_ADDR": ('localhost', 12345),
        "MAX_UDP_SEGMENT_DATA_SIZE": 65527,
        "BUFFER_SIZE": 9216,        # MACOSX UDP MTU is 9216
        "CHUNK_PIECES_SIZE": 9216 - 2000, # Each chunk pieces(segments of UDP) must be lower than UDP buffer size
        "MAX_SPLITTNES_RATE": 3,    # number of neighboring peers which the node take chunks of a file in parallel
        "NODE_TIME_INTERVAL": 20,        # the interval time that each node periodically informs the tracker (in seconds)
        "TRACKER_TIME_INTERVAL": 22      #the interval time that the tracker periodically checks which nodes are in the torrent (in seconds)
    },
    "tracker_requests_mode": {
        "REGISTER": 0,  # tells the tracker that it is in the torrent
        "OWN": 1,       # tells the tracker that it is now in sending mode for a specific file
        "NEED": 2,      # tells the torrent that it needs a file, so the file must be searched in torrent
        "UPDATE": 3,    # tells tracker that it's upload freq rate must be incremented)
        "EXIT": 4       # tells the tracker that it left the torrent
    }
}


class Config:
    """Config class which contains directories, constants, etc."""

    def __init__(self, directory, constants, tracker_requests_mode):
        self.directory = directory
        self.constants = constants
        self.tracker_requests_mode = tracker_requests_mode

    @classmethod
    def from_json(cls, cfg):
        """Creates config from json"""
        params = json.loads(json.dumps(cfg), object_hook=HelperObject)
        return cls(params.directory, params.constants, params.tracker_requests_mode)


class HelperObject(object):
    """Helper class to convert json into Python object"""
    def __init__(self, dict_):
        self.__dict__.update(dict_)