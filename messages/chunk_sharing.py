from messages.message import Message

class ChunkSharing(Message):
    def __init__(self, src_node_id: int, dest_node_id: int, filename: str,
                 range: tuple, idx: int =-1, chunk: bytes = None):

        super().__init__()
        self.src_node_id = src_node_id
        self.dest_node_id = dest_node_id
        self.filename = filename
        self.range = range
        self.idx = idx
        self.chunk = chunk
