# built-in libraries
from threading import Thread, Timer
from collections import defaultdict
import json
import datetime
import time
import warnings
warnings.filterwarnings("ignore")

# implemented classes
from utils import *
from messages.message import  Message
from messages.tracker2node import Tracker2Node
from segment import UDPSegment
from configs import CFG, Config
config = Config.from_json(CFG)

next_call = time.time()

class Tracker:
    def __init__(self):
        self.tracker_socket = set_socket(config.constants.TRACKER_ADDR[1])
        self.file_owners_list = defaultdict(list)
        self.send_freq_list = defaultdict(int)
        self.has_informed_tracker = defaultdict(bool)

    def send_segment(self, sock: socket.socket, data: bytes, addr: tuple,):
        ip, dest_port = addr
        segment = UDPSegment(src_port=sock.getsockname()[1],
                             dest_port=dest_port,
                             data=data)
        encrypted_data = segment.data
        sock.sendto(encrypted_data, addr)

    def add_file_owner(self, msg: dict, addr: tuple):
        entry = {
            'node_id': msg['node_id'],
            'addr': addr
        }
        log_content = f"Node {msg['node_id']} owns {msg['filename']} and is ready to send."
        log(node_id=0, content=log_content, is_tracker=True)

        self.file_owners_list[msg['filename']].append(json.dumps(entry))
        self.file_owners_list[msg['filename']] = list(set(self.file_owners_list[msg['filename']]))
        self.send_freq_list[msg['node_id']] += 1
        self.send_freq_list[msg['node_id']] -= 1

        self.save_db_as_json()

    def update_db(self, msg: dict):
        self.send_freq_list[msg["node_id"]] += 1
        self.save_db_as_json()

    def search_file(self, msg: dict, addr: tuple):
        log_content = f"Node{msg['node_id']} is searching for {msg['filename']}"
        log(node_id=0, content=log_content, is_tracker=True)

        matched_entries = []
        for json_entry in self.file_owners_list[msg['filename']]:
            entry = json.loads(json_entry)
            matched_entries.append((entry, self.send_freq_list[entry['node_id']]))

        tracker_response = Tracker2Node(dest_node_id=msg['node_id'],
                                        search_result=matched_entries,
                                        filename=msg['filename'])

        self.send_segment(sock=self.tracker_socket,
                          data=tracker_response.encode(),
                          addr=addr)

    def remove_node(self, node_id: int, addr: tuple):
        entry = {
            'node_id': node_id,
            'addr': addr
        }
        try:
            self.send_freq_list.pop(node_id)
        except KeyError:
            pass
        self.has_informed_tracker.pop((node_id, addr))
        node_files = self.file_owners_list.copy()
        for nf in node_files:
            if json.dumps(entry) in self.file_owners_list[nf]:
                self.file_owners_list[nf].remove(json.dumps(entry))
            if len(self.file_owners_list[nf]) == 0:
                self.file_owners_list.pop(nf)

        self.save_db_as_json()

    def check_nodes_periodically(self, interval: int):
        global next_call
        alive_nodes_ids = set()
        dead_nodes_ids = set()
        try:
            for node, has_informed in self.has_informed_tracker.items():
                node_id, node_addr = node[0], node[1]
                if has_informed: # it means the node has informed the tracker that is still in the torrent
                    self.has_informed_tracker[node] = False
                    alive_nodes_ids.add(node_id)
                else:
                    dead_nodes_ids.add(node_id)
                    self.remove_node(node_id=node_id, addr=node_addr)
        except RuntimeError: # the dictionary size maybe changed during iteration, so we check nodes in the next time step
            pass

        if not (len(alive_nodes_ids) == 0 and len(dead_nodes_ids) == 0):
            log_content = f"Node(s) {list(alive_nodes_ids)} is in the torrent and node(s){list(dead_nodes_ids)} have left."
            log(node_id=0, content=log_content, is_tracker=True)

        datetime.now()
        next_call = next_call + interval
        Timer(next_call - time.time(), self.check_nodes_periodically, args=(interval,)).start()

    def save_db_as_json(self):
        if not os.path.exists(config.directory.tracker_db_dir):
            os.makedirs(config.directory.tracker_db_dir)

        nodes_info_path = config.directory.tracker_db_dir + "nodes.json"
        files_info_path = config.directory.tracker_db_dir + "files.json"

        # saves nodes' information as a json file
        temp_dict = {}
        for key, value in self.send_freq_list.items():
            temp_dict['node'+str(key)] = value
        nodes_json = open(nodes_info_path, 'w')
        json.dump(temp_dict, nodes_json, indent=4, sort_keys=True)

        # saves files' information as a json file
        files_json = open(files_info_path, 'w')
        json.dump(self.file_owners_list, files_json, indent=4, sort_keys=True)

    def handle_node_request(self, data: bytes, addr: tuple):
        msg = Message.decode(data)
        mode = msg['mode']
        if mode == config.tracker_requests_mode.OWN:
            self.add_file_owner(msg=msg, addr=addr)
        elif mode == config.tracker_requests_mode.NEED:
            self.search_file(msg=msg, addr=addr)
        elif mode == config.tracker_requests_mode.UPDATE:
            self.update_db(msg=msg)
        elif mode == config.tracker_requests_mode.REGISTER:
            self.has_informed_tracker[(msg['node_id'], addr)] = True
        elif mode == config.tracker_requests_mode.EXIT:
            self.remove_node(node_id=msg['node_id'], addr=addr)
            log_content = f"Node {msg['node_id']} exited torrent intentionally."
            log(node_id=0, content=log_content, is_tracker=True)

    def listen(self):
        timer_thread = Thread(target=self.check_nodes_periodically, args=(config.constants.TRACKER_TIME_INTERVAL,))
        timer_thread.setDaemon(True)
        timer_thread.start()

        while True:
            data, addr = self.tracker_socket.recvfrom(config.constants.BUFFER_SIZE)
            t = Thread(target=self.handle_node_request, args=(data, addr))
            t.start()

    def run(self):
        log_content = f"***************** Tracker program started just right now! *****************"
        log(node_id=0, content=log_content, is_tracker=True)
        t = Thread(target=self.listen())
        t.daemon = True
        t.start()
        t.join()

if __name__ == '__main__':
    t = Tracker()
    t.run()