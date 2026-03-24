📘 Module 1: Hadoop
📊 Hadoop Architecture
<p align="center"> <img src="https://upload.wikimedia.org/wikipedia/commons/3/38/Hadoop_Architecture.svg" width="600"/> </p>
1️⃣ What is Hadoop

Answer:
Hadoop is a distributed framework that provides both distributed storage and distributed processing mechanisms.

Uses HDFS (Hadoop Distributed File System) for storage
Uses MapReduce for processing
Highly durable and scalable


2️⃣ What are Hadoop Components

Answer:
Hadoop architecture consists of:

🟡 NameNode
🟡 Standby NameNode
🟡 DataNodes
🟡 JournalNodes
🟡 ZooKeeper


3️⃣ What is Block Size in Hadoop HDFS

Answer:

Hadoop Version	Block Size
Hadoop 1.0	64 MB
Hadoop 2.0+	128 MB (default)



4️⃣ What is Fault Tolerance in Hadoop

Answer:
Hadoop ensures fault tolerance using:

✅ Data Replication
✅ Task Resubmission
✅ High Availability


5️⃣ What is Split Brain Scenario in Hadoop

Answer:
Split-brain occurs when both Active and Standby NameNodes become active simultaneously due to network failure, leading to data inconsistency.

Prevention:

🔹 ZooKeeper
🔹 Fencing mechanisms



6️⃣ What is Speculative Execution in Hadoop

Answer:
Speculative execution is used to handle slow-running tasks (stragglers).

Hadoop runs a duplicate task on another node
The fastest result is accepted
The slower task is killed


7️⃣ What is High Availability and Federation in Hadoop
🔹 High Availability (HA)
Ensures cluster is always available
Uses Active + Standby NameNodes
Automatic failover
🔹 Federation
Multiple NameNodes in a cluster
Each manages a separate namespace
Improves scalability and performance
🚀 Quick Summary
Feature	Description
Storage	HDFS
Processing	MapReduce
Fault Tolerance	Replication + HA
Scalability	Horizontal
Performance	Parallel Processing
