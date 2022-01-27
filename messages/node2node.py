from messages.message import Message

class Node2Node(Message):
    def __init__(self, src_node_id: int, dest_node_id: int, filename: str, size: int = -1):

        super().__init__()
        self.src_node_id = src_node_id
        self.dest_node_id = dest_node_id
        self.filename = filename
        self.size = size    # size = -1 means a node is asking for size
