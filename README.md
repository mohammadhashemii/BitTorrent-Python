# BitTorrent-Python
This is python implementation of the popular peer-to-peer protocol for file distribution. 
This project, was the course project of Computer Networks course at Shahid Beheshti University in Fall 2021.


## Introduction to BitTorrent

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

For deeper intuition to how BitTorrent works, please refer to [`docs/Computer_Networking_A_top_Down_Approach.pdf`](https://github.com/mohammadhashemii/BitTorrent-Python/Computer_Networking_A_top_Down_Approach.pdf).

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
  Firstly, the node *i* tells the tracker that it has this file on his system and want to be in a state of waiting other peers request for that specific file
  (More details are explained in the project report which is in [`docs/`](https://github.com/mohammadhashemii/BitTorrent-Python/docs)).
  A node can enter this mode by inputting like this:
  ```
  torrent -setMode send <filename>
  ```
  
- **download:** If node *i* wants to download a file, it must first informs the trackers that it needs this file.
Thus, the tracker search that file in the torrent and sort the neighbors which own this file based on their upload frequency
  list, the more a node uploads, the more chance it has for being selected. Then a fixed number of neighboring peers are selected 
  for node *i* for later to request that file from them. Next, node *i* request that file from those neighboring peers, and 
  conduct a UDP connection for getting a chunk of file from that peer. (More details are explained in the project report which is in [`docs/`](https://github.com/mohammadhashemii/BitTorrent-Python/docs))
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
## Configurations
All the parameters and configs which can be modified exist in `configs.py`. There is a JSON-like variable which is as follows:
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
The usages of these settings and configs are fully described in [`docs/`](https://github.com/mohammadhashemii/BitTorrent-Python/docs).