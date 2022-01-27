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
peers which it can request that file from. Assume that we send downloading request to *N* peering nodes for getting a file with size of *S*
Each peering node, sends $\frac{S}{N}$ bytes of that file to the source peer in parallel.
After gathering all the chunks of the file, they must be re-assembled and be saved in the local directory of that node.

### Tracker
How these steps work and how they are implemented are explained in the following sections.