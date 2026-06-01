**Phase 1**: Set Up Storage (S3 Buckets)
We need to create the folders for our data lake and our orchestration code.

Open the Amazon S3 Console.

Click Create bucket. Name it exactly: ecommerce-analytics-data-lake.

Inside this bucket, create four folders:

**raw-data**/ (Where our incoming daily transactions sit)

**scripts**/ (Where our PySpark code sits)

**processed-output**/ (Where the final clean data will go)

**emr-logs**/ (Where Spark execution errors/logs will save)

Go back to the S3 home page, click Create bucket again. Name it exactly: mwaa-airflow-orchestrator-bucket.

Inside this bucket, create one single folder:

dags/ (Where our Airflow management script sits)

**Phase 2**: Create local files and upload to S3
File 1: The Raw Data
Create a file on your local computer named daily_transactions.csv and paste this mock transaction data inside:

```csv
transaction_id,user_id,product_category,amount,timestamp
TXN001,USR99,Electronics,1200.50,2026-05-30 14:22:11
TXN002,USR45,Apparel,45.00,2026-05-30 14:23:00
TXN003,USR99,Electronics,15.99,2026-05-30 14:25:12
```
📥 Action: Upload daily_transactions.csv to s3://ecommerce-analytics-data-lake/raw-data/.
