from messages.message import Message

class Tracker2Node(Message):
    def __init__(self, dest_node_id: int, search_result: list, filename: str):

        super().__init__()
        self.dest_node_id = dest_node_id
        self.search_result = search_result
        self.filename = filename
