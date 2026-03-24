📘 Module 1: Hadoop
1️⃣ What is Hadoop

Ans:
Hadoop is a distributed framework which has distributed storage and distributed processing mechanism.

It uses HDFS for distributed storage
It uses MapReduce for distributed processing
Hadoop is highly durable and easily scalable
2️⃣ What are Hadoop Components

Ans:
Hadoop architecture consists of:

NameNode
Standby NameNode
DataNodes
JournalNodes
ZooKeeper
3️⃣ What is Block Size in Hadoop HDFS

Ans:

Hadoop 2.0 → 128 MB (Default)
Hadoop 1.0 → 64 MB
4️⃣ What is Fault Tolerance in Hadoop

Ans:
Hadoop handles this through three primary mechanisms:

Data Replication
Task Resubmission
High Availability
5️⃣ What is Split Brain Scenario in Hadoop

Ans:
Split-brain in Hadoop occurs when both Active and Standby NameNodes become active simultaneously due to network failure, leading to data inconsistency.

Prevented using:
ZooKeeper
Fencing mechanisms
6️⃣ What is Speculative Execution in Hadoop

Ans:
Speculative execution is a latency optimization technique in Hadoop that handles the straggler problem.

If a task is running slow, Hadoop launches the same task on another node
The result from the task that finishes first is accepted
The other task is killed
7️⃣ What is High Availability and Federation in Hadoop

Ans:

In early Hadoop, the NameNode was a Single Point of Failure (SPOF). If it crashed, the whole cluster went down. The solution is High Availability.

High Availability:
Uses a backup NameNode for the same data
Ensures no downtime
Federation:
Uses multiple NameNodes for different data
Improves scalability
8️⃣ What is Rack Awareness in Hadoop

Ans:
Rack awareness in Hadoop is the process of placing data across different racks while keeping it as close as possible to computation.

Ensures fault tolerance
Reduces network traffic
9️⃣ What is Small File Issues in Hadoop

Ans:
The small file problem in Hadoop happens when many files smaller than the block size increase metadata load on the NameNode.

Solution:
Merge small files using Hadoop Archive (HAR)
Improves performance
🔟 Explain Hadoop Architecture

Ans:
Hadoop is a Master-Slave framework designed for distributed storage and distributed processing.

It is built on three core pillars:

HDFS (Storage)
YARN (Resource Management)
MapReduce (Processing)
1) HDFS (Hadoop Distributed File System) - Storage Layer

HDFS follows a Master-Slave architecture to store massive datasets.

NameNode (Master):
Brain of the system
Manages metadata (file names, permissions, block locations)
Does NOT store actual data
Secondary NameNode:
NOT a backup
Merges Edit Logs with FsImage
Helps faster startup
DataNode (Slave):
Stores actual data blocks
Handles read/write operations
Sends heartbeats to NameNode
2) YARN (Yet Another Resource Negotiator) - Resource Management

Introduced in Hadoop 2.0, YARN manages cluster resources.

ResourceManager (Master):
Manages cluster resources (CPU & RAM)
Allocates resources to jobs
NodeManager (Slave):
Runs on each DataNode
Monitors resource usage
ApplicationMaster:
Created per job
Negotiates resources and manages execution
3) MapReduce - Processing Layer

MapReduce is the programming model for parallel processing.

Map Phase
Breaks data into key-value pairs
Shuffle & Sort Phase
Organizes and distributes data
Reduce Phase
Aggregates results into final output
