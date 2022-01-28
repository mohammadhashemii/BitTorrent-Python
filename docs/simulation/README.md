# A Sample Output

Here, we put some snapshots of how this project works and how peers and the tracker interact with each other. Each node can have some initial files in its project but it is not necessary. When nodes are created in run time, an empty directory will be inserted for it in `node_files/`. Assume we have these nodes files a the starting of the program:
```
.
├── ...
├── node_files              
│   ├── node1
│   │   ├── file_A.txt
│   │   ├── file_B.txt
│   │   ├── file_C.txt
│   │   ├── bittorrent.jpg
│   │
│   ├── node2
│   │   ├── file_A.txt
│   │   ├── file_B.txt
│   │   ├── file_C.txt
│   │
│   ├── node3  
│   │   ├── file_C.txt
│   │
└── ...
```

In this scenario, I set the `MAX_SPLITTNES_RATE = 3` which indicates number of neighboring peers which the node take chunks of a file in parallel. It can be modified in `configs.py`.

**Step 1:** Run the tracker, create three nodes with IDs 1, 2 and 3 respectively in terminal.

