📘 Module1 : Hadoop
1️⃣ What is Hadoop

Ans:
Hadoop a distributed framework which has distributged storage and distributed processing mechanism. It uses HDFS for distributed storage and MapReduce for distributed processing. Hadoop is highly durable and easily scalable.

2️⃣ What are Hadoop components

Ans:
Hadoop architecture consist of NameNode , Standby Name Node, Datanodes, Journal Nodes and Zookeeper.

3️⃣ What is Block size in Haodop HDFS

Ans:
128MB Default Block in Hadoop 2.0
64 MB in Hadoop 1.0

4️⃣ What is Fault Tolerance in Hadoop

Hadoop handles this through three primary mechanisms:

Data Replication
Task Resubmission
High Availability
5️⃣ What is split brain scenario in Hadoop

Ans:
Split-brain in Hadoop occurs when both Active and Standby NameNodes become active simultaneously due to network failure, leading to data inconsistency. It is prevented using ZooKeeper and fencing mechanisms

6️⃣ What is speculative execution in Hadoop

Ans:
Speculative execution is a latency optimization technique in Hadoop that handles the straggler problem. If a task is running slow, Hadoop launches the same task on another node. The result from the task that finishes first is accepted, and the other is killed

7️⃣ What is high Availability and federation in Hadoop

Ans:
In early Hadoop, the NameNode was a Single Point of Failure (SPOF). If it crashed, the whole cluster went down. the solution High Availability.

High Availability uses a backup NameNode for the same data to ensure no downtime, whereas Federation uses multiple NameNodes for different data to improve scalability.

8️⃣ What is Rack Awareness in Hadoop

Ans:
Rack awareness in Hadoop is the process of placing data across different racks while keeping it as close as possible to computation, to ensure fault tolerance and reduce network traffic.

9️⃣ What is Small file issues in Hadoop

Ans:
The small file problem in Hadoop happens when many files smaller than the block size increase metadata load on the NameNode. It can be solved by merging small files using Hadoop Archive (HAR) to improve performance.

🔟 Explain Hadoop Architecture

Ans:
Hadoop is Master-Slave framework designed for distributed storage and distributed processing. It is built on three core pillars: HDFS (Storage), YARN (Resource Management), and MapReduce (Processing).

1) HDFS (Hadoop Distributed File System) - The Storage Layer

HDFS follows a Master-Slave architecture to store massive datasets across common hardware

NameNode (Master): The "Brain" of the file system. It manages the Metadata (file names, permissions, and which DataNode holds which block). It does not store the actual data.
Secondary NameNode: (Crucial Point) It is not a backup for the NameNode. Its main job is to periodically merge the "Edit Logs" with the "FsImage" to keep the metadata lean and help the NameNode start up faster.
DataNode (Slave): The "Muscle." These nodes store the actual Data Blocks. They perform read/write requests and send "heartbeats" to the NameNode to prove they are still alive.
2) YARN (Yet Another Resource Negotiator) - The Operating System

Introduced in Hadoop 2.0, YARN manages the cluster's resources (CPU and RAM) and schedules jobs.

ResourceManager (Master): The ultimate authority. It knows how much RAM and CPU is available across the entire cluster and decides which jobs get those resources.
NodeManager (Slave): Runs on every DataNode. It monitors the local resource usage (containers) and reports back to the ResourceManager.
ApplicationMaster: A temporary "manager" created for each specific job. it negotiates resources from the ResourceManager and works with NodeManagers to execute tasks.
3) MapReduce - The Processing Layer
The Map Phase takes the data and breaks it down into key-value pairs (like counting words).
The Shuffle& Sort Phase organizes and moves that data across the network to the right 'buckets.'
The Reduce Phase takes those buckets and summarizes them into the final answer.
Reduce Phase
Aggregates results into final output
