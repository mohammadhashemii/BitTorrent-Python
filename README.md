# BitTorrent-Python
This is python implementation of the popular peer-to-peer protocol for file distribution. 
This project, was the course project of Computer Networks course at Shahid Beheshti University in Fall 2021.



Table of contents
==============

<!--ts-->
   * [Introduction to BitTorrent](#introduction)
   * [Installation](#installation)
   * [How to run](#how-to-run)
   * [Usage](#usage)
   * [Configurations](#configurations)
   * [Proposed Approach](#proposed-approach)
      * [Peers](#peers)
      * [Tracker](#tracker)
   * [Implementation Details](#implementation-details)
      * [`node.py`](#node.py)
      * [`tracker.py`](#tracker.py)
      * [`messages/`](#messages)
         * [`messages.py`](#message.py)
      * [`utils.py`](#utils.py)
   * [A Sample Output](#a-sample-output)
   * [Conclusion](#conclusion)

<!--te-->

## Introduction to BitTorrent

<p align="center">
  <img src="https://github.com/mohammadhashemii/BitTorrent-Python/blob/main/docs/bittorrent.jpg" height="400">	
</p>

Before you read this section, it must be noted that there is a complete and well-explained introduction to BitTorrent protocol
in the reference book [Computer Networking: A top-Down Approach](https://www.amazon.com/Computer-Networking-Top-Down-Approach-6th/dp/0132856204) which all intuition behind this source were inspired by materials in this book.
I also put the three pages of this book which is describing BitTorrent in [`docs/Computer_Networking_A_top_Down_Approach.pdf`](https://github.com/mohammadhashemii/BitTorrent-Python/Computer_Networking_A_top_Down_Approach.pdf).

Here there is a brief intro to BitTorrent:

BitTorrent is a popular P2P protocol for file distribution.
The collection of all peers participating in the distribution of a particular file is called a ***torrent***.
Peers in a torrent download equal-size chunks of the file from one another.
When a peer first joins a torrent, it has no chunks. Over time, it accumulates more and more chunks. 
While it downloads chunks it also uploads chunks to other peers.

Each torrent has an infrastructure node called a ***tracker***.
When a peer joins a torrent, it registers itself with the tracker and periodically informs the tracker that it is still in the torrent. 
In this manner, the tracker keeps track of the peers that are participating in the torrent.

## Installation
Clone the repository on your local system by running the commands below in terminal.
```
$ git clone https://github.com/mohammadhashemii/BitTorrent-Python
$ cd BitTorrent-Python
```
There is no third-party package to install. All the packages needed for this project are python built-in libraries.
But it is recommended to use Python version 3.6 or more.

## How to run
There are two main modules in BitTorrent, *(i)* node *a.k.a.* peer and *(ii)* tracker. So we must run each of these modules separately:

1. `tracker.py`:
```
$ python3 tracker.py
```
2. `node.py`: You can create peers as many as you want. An example of creating two nodes is as follows.
   (Note that each of them must be run in a separate window of your terminal if you are running this project in a single local computer)

```
$ python3 node.py -node_id 1
# in another tab of terminal
$ python3 node.py -node_id 2
```
As you can see, it takes an ID of the node you want to be created. For simplicity, we assume that nodes have unique IDs.

## Usage
Excellent! Now the peers are running in the torrent. But there are a lot to do. As it stated in the course project description,
each node can be in two modes. In other words, there are two functionalities for each node:
- **send (upload):** At any given time, a node *i* may want to upload a file in torrent for a neighboring peer.
  Firstly, the node *i* tells the tracker that it has this file on his system and want to be in a state of waiting other peers request for that specific file.
  A node can enter this mode by inputting like this:
  ```
  torrent -setMode send <filename>
  ```
  
- **download:** If node *i* wants to download a file, it must first informs the trackers that it needs this file.
Thus, the tracker search that file in the torrent and sort the neighbors which own this file based on their upload frequency
  list, the more a node uploads, the more chance it has for being selected. Then a fixed number of neighboring peers are selected 
  for node *i* for later to request that file from them. Next, node *i* request that file from those neighboring peers, and 
  conduct a UDP connection for getting a chunk of file from that peer.
  ```
  torrent -setMode download <filename>
  ```
- **exit - (Optional mode):**
An optional mode named **exit** has also implemented which is used for letting tracker know that a node has left the
torrent intentionally. But according to the reference book, tracker must automatically notices that a node has left.
This mechanism is described in the project report.
  ```
  torrent -setMode exit
  ```

  Each node and also the tracker has an individual log file in `logs/` directory which all the events in the torrent which is related to that node or the tracker will be written in.

  Also, you can add any files in each node local directory that be participated in the torrent. This can be found in `node_files/`.

## Configurations
All the parameters and configs which can be modified exist in `configs.py`. There is a JSON-like variable which is as follows. 

```json
{
    "directory": {
        "logs_dir": "logs/",
        "node_files_dir": "node_files/",
        "tracker_db_dir": "tracker_db/"
    },
    "constants": {
        "AVAILABLE_PORTS_RANGE": [1024, 65535], 
        "TRACKER_ADDR": ["localhost", 12345],
        "MAX_UDP_SEGMENT_DATA_SIZE": 65527,
        "BUFFER_SIZE": 9216,        
        "CHUNK_PIECES_SIZE": 7216, 
        "MAX_SPLITTNES_RATE": 3,    
        "NODE_TIME_INTERVAL": 20,        
        "TRACKER_TIME_INTERVAL": 22      
    },
    "tracker_requests_mode": {
        "REGISTER": 0,  
        "OWN": 1,       
        "NEED": 2,      
        "UPDATE": 3,    
        "EXIT": 4       
    }
}
```

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


<p align="center">
  <img src="https://github.com/mohammadhashemii/BitTorrent-Python/blob/main/docs/bittorrent_state_diagram.jpg">	
</p>


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

1. It first checks if the node has already owned this file. If yes, it returns.
2. If No, if calls `search_torrent()` to ask the tracker about the file owners.
3. After getting the result from the tracker, it calls `split_file_owners()` to split the file to equal-sized chunks.

```python  
def search_torrent(self, filename: str) -> dict
```

1. It sends a `Node2Tracker` message to the tracker with mode *NEED*. The tracker returns the *K* best peers information which this node can take file chunks of them. (*K* can be modified in the `configs.py`).
2. After receiving the result from the tracker, it returns the search result as python dictionary.

```python  
def split_file_owners(self, file_owners: list, filename: str): -> dict
```

This is the most important function of this class. Til now we have the owner of the file which we are going to download. We sort the owners based on their uploading frequency rate. There are 5 main steps we have to follow:
1. First we must ask the size of the desired file from one of the file owners. This is done by calling the `ask_file_size()`.
2. Now, we know the size, it's time to split it equally among peers to download chunks of it from them.
3. Now we iterate a thread for each neighbor peer to download a chunk from it. This done by iterating the threads and calling `receive_chunk()` for each individual one.
4. Now we have downloaded all the chunks of the file. It's time to sort them by calling `sort_downloaded_chunks()`. Because they may have received in-ordered.
5. Finally, we assemble the chunks to re-build the file and saving it in the node directory. This is done by calling `reassemble_file()`.

Now let's see how each of these five functions work:

```python  
def ask_file_size(self, filename: str, file_owner: tuple) -> int:
```

This function sends a `Node2Node` message to one of the neighboring peers for asking the file size.

```python  
def receive_chunk(self, filename: str, range: tuple, file_owner: tuple):
```

1. First we sends a `ChunkSharing` message to the neighboring peer to informs it that we want that chunk.
2. Then we wait for that chunk to be received.

```python  
def sort_downloaded_chunks(self, filename: str) -> list
```

All the downloaded chunks are stored in `self.downloaded_files`. But they are in-ordered and must be sorted. So we sort them based on theirs indices and return the result as a ordered list.

```python  
def reassemble_file(self, chunks: list, file_path: str):
   with open(file_path, "bw+") as f:
      for ch in chunks:
            f.write(ch)
      f.flush()
      f.close()
```

There are some more functions to be explained:

```python  
def inform_tracker_periodically(self, interval: int):
```

As mentioned earlier, this function is called periodically to inform the state of the node to the tracker by sending a `Node2Tracker` message.

```python  
def enter_torrent(self):
```
It sends a `Node2Tracker` message to the tracker to tells it that it enters the torrent.

```python  
def exit_torrent(self):
```
It sends a `Node2Tracker` message to the tracker to tells it that it left the torrent.

### `tracker.py`

There is a class named Tracker in `tracker.py` which has these fields:

| Field | Type | Description |
|--|--|--|
|`tracker_socket`|`socket.socket`|A socket for sending & receiving messages|
|`file_owners_list`|`defaultdict`|A python dictionary of the files with their owners in the torrent|
|`send_freq_list`|`defaultdict`|A python dictionary of the nodes with their upload frequency rate|
|`has_informed_tracker`|`defaultdict`|A python dictionary of the nodes with a boolean variable indicating their status in the torrent|

By running `tracker.py` a function named `run()` is called which performs the following steps:
1. It creates an instance of `Tracker`.
2. It creates a thread with a target of `listen()`

The implementation of `run()` is as follows:

```python  
def run(self):
   log_content = f"***************** Tracker program started just right now! *****************"
   log(node_id=0, content=log_content, is_tracker=True)
   t = Thread(target=self.listen())
   t.daemon = True
   t.start()
   t.join()
```

Now we describe the purpose of each function. We tried these explanations be brief but helpful.

```python  
def listen(self) -> None:
```

1. It first creates a thread to work as a timer, for checking the nodes status periodically by calling `check_nodes_periodically()`.
2. Then it enters an in-finit loop for listening to nodes requests. For handling the requests taken from the peers, it calls `handle_node_request()`.

```python  
def check_nodes_periodically(self, interval: int) -> None:
```

1. Every ***T*** seconds, this function is called and it is responsible to check if the nodes are still in the torrent.
2. It iterates the `self.has_informed_tracker` and if its value is true for a peer, it means the node has informed the tracker that is still in the torrent. In other hand, it it's value is False, it means that specific node has left the torrent and its database must be removed by calling `remove_node()`.

```python  
def remove_node(self, node_id: int, addr: tuple) -> None:
```

It removes all the information related to node with id of `node_id` and address of `addr` in the tracker database. 


```python  
def handle_node_request(self, data: bytes, addr: tuple):
```

This function is the heart of the `Tracker` class. Based on message modes comes from the nodes, it calls different functions:
1. Mode *OWN*: It calls `add_file_owner()`
2. Mode *NEED*: It calls `search_file()`
3. Mode *UPDATE*: It calls `update_db()`
4. Mode *REGISTER*: It updates the `self.has_informed_tracker` dictionary for a specific node.
5. Mode *EXIT*: It calls `remove_node()`

```python  
def add_file_owner(self, msg: dict, addr: tuple) -> None:
```

This function adds the node's file to the `self.file_owners_list`.

```python  
def search_file(self, msg: dict, addr: tuple) -> None:
```

1. It iterates the `self.file_owners_list` to find the owners of the file which is needed. Each owner will be appended to `matched_entries` list.
2. It sends a `Tracker2Node` message to the peer which has wanted from the tracker to search for the file owners.

```python  
def update_db(self, msg: dict):
```

It's simple. It increments the `self.send_freq_list` dictionary for a file.

There is also one other utility functions in `Tracker` class:

```python  
def save_db_as_json(self):
```

We save the database into two separate JSON files: *(i)* `nodes.json` which contains the information of nodes and theirs upload frequency rate, and *(ii)* `files.json` including the information of files and their owners. Whenever some changes occur in the database we call this function. These JSON files are in [tracker_DB/](https://github.com/mohammadhashemii/BitTorrent-Python/tree/main/tracker_DB) directory.

### `messages/`
There are multiple python files in the [`messages/`](https://github.com/mohammadhashemii/BitTorrent-Python/tree/main/messages) directory. `messages.py` has a class named `Message` which all the messages commuting among the nodes and the tracker are an instance of this class. In fact the other classes in other python files in directory are all **inheriting** from class `Message`. The implementation of `message.py` is as follows:

```python  
from __future__ import annotations
import pickle


class Message:
    def __init__(self):
        pass

    def encode(self) -> bytes:
        return pickle.dumps(self.__dict__)

    @staticmethod
    def decode(data: bytes) -> dict:
        return pickle.loads(data)

```
Other message class which are inheriting `Message` are as follows:

| Class | Description |
|--|--|
|`Node2Tracker`|Sending a message from node to the tracker|
|`Tracker2Node`|Sending a message from the tracker to a node|
|`Node2Node`|Sending a message from a node to another node|
|`ChunkSharing`|For file communication|

### `utils.py`
There are some helper functions in `utils.py`. All other python files have imported this script.

```python  
def set_socket(port: int) -> socket.socket:
```

This function takes a port number and creates a new UDP socket.

```python  
def free_socket(sock: socket.socket):
```

This function takes a socket and frees a socket to be able to be used by others.

```python  
def generate_random_port() -> int:
```

A function that generates a new(unused) random port number.

```python  
def parse_command(command: str):
```   

It parses the input command entered from the user.

```python  
def log(node_id: int, content: str, is_tracker=False) -> None:
``` 

It is called several times by nodes and the tracker to log the events occurred in the torrent. Each node has an individual log file in `logs/` directory.

## A Sample Output
For better intuition of how this project works and what kind of output we will get by running the codes, we put a sample output of the code. We created a torrent with 4 peers and a tracker. For some snapshots of the outputs go to [`docs/simulation/`](https://github.com/mohammadhashemii/BitTorrent-Python/tree/main/docs/simulation).

## Conclusion
Downloading movie, music perhaps game or very large size software is a pretty fun activity using BitTorrent communication protocol which helps in distributing large chunks of data over Internet. Fact is that one third of internet traffic contains BitTorrent data packets, which makes it one of most interesting and trending topics.

In this project we implemented a simple version of BitTorrent in Python language programming. Actually BitTorrent has evolved during the last decades and various version of it has been used. This implementation contains the main modules of every BitTorrent network which is useful for getting know how it works.

Of course, these codes has not tested in large scale cases due to the academical nature it has. We highly appreciate in case you give any kinds of feedback (*i.e.* creating issues, pull requests etc.) if you have found any problem or miss-understanding.
