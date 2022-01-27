# BitTorrent-Python: Report
This is the detailed description of the [BitTorrent-Python](https://github.com/mohammadhashemii/BitTorrent-Python) project. The authors of this project are:
- [Mohammad Hashemi](https://github.com/mohammadhashemii)
- [Koorosh Khavari](https://github.com/NukaColaQuantum666)


Table of contents
==============

<!--ts-->
   * [Proposed Approach](#proposed-approach)
      * [Peers](#peers)
      * [Tracker](#tracker)
   * [Implementation Details](#implementation-details)
      * [`node.py`](#node_py)
      * [`tracker.py`](#node_py)
      * [`messages/`](#messages)
         * [`messages/`](#messages)

<!--te-->

## Proposed Approach:
BitTorrent contains two main modules: *(i)* peers and *(ii)* tracker.
There are multiple nodes(peers), and a single tracker in this network.
We will explain each of these modules in details in the following sections.


### Peers

When a peer joins the torrent, it registers itself with the tracker and periodically informs the tracker that it is still in the torrent.
A peer functionality can be summarized in two functions:
#### 1. Send (Upload)
A peer can send a chunk of a file to a neighboring peer. In fact, before this happens,
it informs the torrent that it *OWN*s a specific file. Afterward, the trackers updates its database
and add this peer as the owner of that file. Then, the node is ready to send the file(actually a chunk of that)
to another peer which requested that file. Note that any given time, a peer can send different chunks of various files to
different neighboring peers (Thanks to the threads in programming languages, this is possible).
While the peer listening to requests, if a neighboring peers requests a file, it starts to send an specific chunk of that
file to it. The question is that how does it know to send an exact chunk of a file. We will answer this question later.

#### 2. Download
Downloading a file has two main steps. First step which is known as *search* step, we must inform the tracker that we *NEED*s
a specific file. The tracker after some processing (which is described in the next section), introduce some fixed-number of
peers which it can request that file from. Assume that we send downloading request to ***N*** peering nodes for getting a file with size of ***S***
Each peering node, sends ***S/N*** bytes of that file to the source peer in parallel.
After gathering all the chunks of the file, they must be re-assembled and be saved in the local directory of that node.

### Tracker
As we mentioned earlier, torrent has only a tracker. It manages the torrent and has general information of the peers.
This information contains:
1. Peers' files
2. The address (IP and port number) of each peer in torrent

Tracker database is updated periodically by peers. In fact each node, informs the torrent its state via a message periodically,
and the tracker updates its database in a pooling manner. If a peer does not informs the tracker for one cycle, it means
it has left the torrent and its information in the database must be deleted.
As we discussed, each peer may send different messages to the tracker. These messages can be categorized as follows:


| Mode | Description |
|--|--|
|*REGISTER*| Tells the tracker that it is in the torrent. |
|*OWN*| Tells the tracker that it is now in sending mode for a specific file. |
|*NEED*| Tells the torrent that it needs a file, so the file must be searched in the torrent. |
|*UPDATE*| Tells the tracker that it's upload frequency rate must be incremented. |
|*EXIT*| Tells the tracker that it left the torrent. |

We briefly explain what the tracker does when it receives these messages:

**1. REGISTER:**
The tracker receives this type of message in two conditions. First when a node enters the torrent. By this way, the node informs the tracker that it is in the torrent. Second, every ***T*** seconds a node informs the tracker that is still in the torrent.

**2. OWN:**
When a peer enters the SEND mode, it sends this message to the tracker. Then, the tracker updates its database of files in torrent.

**3. NEED:**
Obviously, when a peer needs a file, it informs the tracker that it needs file ***f***. The tracker searches the torrent and sort the owners of that file based on a clever trading algorithm. The basic idea is that the tracker gives priority to the peers that are currently supplying files **at the highest rate**. 

**4. UPDATE:**
When a file has been sent by a peer to some other node, its uploading frequency rate must be incremented. This is done by the tracker.

**5. EXIT:**
When a peer exits the torrent, all the information which is related to this peer must be deleted from the tracker database.


How these steps work and how they are implemented are explained in the following sections.

## Implementation Details:
Before you read this part, it must be noted that we tried to make the codes self-explainable by adding appropriate documentations and comments. But here we describe the general purpose of implementing functions in each file.

### `node.py`
There is a class named Node in `node.py` which has these fields:

| Field | Type | Description |
|--|--|--|
|`node_id`|`int`|A unique ID of the node|
|`rcv_socket`|`socket.socket`|A socket for receiving messages|
|`send_socket`|`socket.socket`|A socket for sending messages|
|`files`|`list`|A list of files which the node owns|
|`is_in_send_mode`|`bool`|a boolean variable which indicates that whether the node is in send mode|
|`downloaded_files`|`dict`|A dictionary with filename as keys and a list of file owners which the node takes the file from|

By running the `node.py`, the script calls `run()`. The following things are then performs:
1. Creating an instance of `Node` class as a new node.
2. Informing the tracker that it enters the torrent.
3. Creates a thread which works as a timer to sends a message to the tracker to inform its state to it.
4. Depending on what command the user inputs, it calls different functions which we will cover them now.

The implementation of `run()` is as follows:
```python
def run(args):
    node = Node(node_id=args.node_id,
                rcv_port=generate_random_port(),
                send_port=generate_random_port())
    log_content = f"***************** Node program started just right now! *****************"
    log(node_id=node.node_id, content=log_content)
    node.enter_torrent()

    # We create a thread to periodically informs the tracker to tell it is still in the torrent.
    timer_thread = Thread(target=node.inform_tracker_periodically, args=(config.constants.NODE_TIME_INTERVAL,))
    timer_thread.setDaemon(True)
    timer_thread.start()

    print("ENTER YOUR COMMAND!")
    while True:
        command = input()
        mode, filename = parse_command(command)

        #################### send mode ####################
        if mode == 'send':
            node.set_send_mode(filename=filename)
        #################### download mode ####################
        elif mode == 'download':
            t = Thread(target=node.set_download_mode, args=(filename,))
            t.setDaemon(True)
            t.start()
        #################### exit mode ####################
        elif mode == 'exit':
            node.exit_torrent()
            exit(0)
```

Now we describe the purpose of each function. We tried these explanations be brief but helpful.


#### **Send mode functions:**
```python  
def set_send_mode(self, filename: str) ->  None:
``` 

1. Send a message(`Node2Tracker` message) to the tacker to tells it that it has the file with name `filename` and is ready to listen to other peers requests.
2. Create a thread for listening to neighboring peers' requests. The thread calls `listen()` function.

```python  
def listen(self) ->  None:
``` 

1. It has a infinit loop for waiting for other peers' messages.
2. Just after it receives a message, it calls `handle_requests()`.

```python  
def handle_requests(self, msg: dict, addr: tuple) -> None:
```

1. The messages from peers can be categorized to groups. First the one which are asking for the size of a file. For this, we call `tell_file_size()` to calculate the size of the file.
2. In the second group, the nodes is asked for sending a chunk of a file. In this condition, it calls `send_chunk()`.

```python  
def tell_file_size(self, msg: dict, addr: tuple) -> None:
```

1. This function is simple. It calculates the file using `os.stat(file_path).stsize`.
2. Then we send the result by sending a message of type `None2Node`.

```python  
def send_chunk(self, filename: str, rng: tuple, dest_node_id: int, dest_port: int) -> None:
```

This is a quiet important function. As we said, file chunks must be sent piece by pieces(Due to the limited MTU of UDP protocol).
1. Thus the chunk is splitted to multiple pieces to be transfarabale by calling `split_file_to_chunks()`. It returns a list of pieces.
2. Now we iterate the pieces and send them to the neighboring peer withing a UDP segment. The piece is sent within a message of type `ChunkSharing`.

```python  
def split_file_to_chunks(self, file_path: str, rng: tuple) -> list:
```

1. This function takes the range of the file which has to be splitted to pieces of fixed-size (It this size can be modified in the `configs.py`). This is done by `mmap.mmap()` which is a python built-in function.
2. Then it returns the result as a list of chunk pieces.

```python  
def send_segment(self, sock: socket.socket, data: bytes, addr: tuple) -> None:
```

All the messages which are transferring among peers and tracker uses this function to be sent. It creates a `UDPSegment` instance and be sent with `socket.socket` functionalities.

#### **Download mode functions:**

```python  
def set_download_mode(self, filename: str) -> None:
```

1. It first check if the node has already owned this file or not. If yes, it returns.
2. If No, if calls `search_torrent()` to ask the tracker about the file owners.
3. After getting the result from the tracker, it calls `split_file_owners()` to split the file to equal-sized chunks.