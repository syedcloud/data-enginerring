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

File 2: The PySpark Script
Create a file on your local computer named sales_transform.py and paste this Python code inside:

```
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, current_date, sum as _sum

def main():
    # Start distributed Spark cluster session
    spark = SparkSession.builder.appName("Ecommerce-Daily-Aggregation").getOrCreate()
    
    input_uri = "s3://ecommerce-analytics-data-lake/raw-data/daily_transactions.csv"
    output_uri = "s3://ecommerce-analytics-data-lake/processed-output/"

    # Read, clean data, and perform a aggregation calculation
    df = spark.read.csv(input_uri, header=True, inferSchema=True)
    cleaned_df = df.dropna(subset=["transaction_id", "amount"])
    
    aggregated_df = cleaned_df.groupBy("product_category").agg(
        _sum("amount").alias("total_revenue")
    ).withColumn("processing_date", current_date())

    # Write output back to S3 as compressed Parquet files
    aggregated_df.write.mode("overwrite").parquet(output_uri)
    spark.stop()

if __name__ == "__main__":
    main()
```

**Phase 3**: Create the EMR Security Role (IAM)
Before we turn on EMR Serverless, we must build its security guard credentials so it can legally read/write to your S3 folders.

Step 1: Create the Data Access Policy

1 : Open the AWS IAM Console.

2 : On the left menu, click Policies, then click Create policy.

3 : Click the JSON tab, delete whatever is there, and paste this block:

```
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "S3Access",
            "Effect": "Allow",
            "Action": [
                "s3:GetObject",
                "s3:PutObject",
                "s3:DeleteObject",
                "s3:ListBucket"
            ],
            "Resource": [
                "arn:aws:s3:::ecommerce-analytics-data-lake",
                "arn:aws:s3:::ecommerce-analytics-data-lake/*"
            ]
        },
        {
            "Sid": "GlueAccess",
            "Effect": "Allow",
            "Action": [
                "glue:GetDatabase",
                "glue:GetDataTables",
                "glue:CreateTable",
                "glue:GetTable"
            ],
            "Resource": "*"
        }
    ]
}
```
4 : Click Next. Name this policy: EMRServerless-S3-Policy. Click Create policy.
5 : In the permissions search box, find and check the box next to the policy you just created: EMRServerless-S3-Policy.

6 :  Click Next. Name this role exactly: EMRServerlessExecutionRole.

7 : Click Create role.

8 : Copy the Role ARN string (e.g., arn:aws:iam::123456789012:role/EMRServerlessExecutionRole). You will need it for Airflow!

**Phase 4**: Configure Airflow (Amazon MWAA)
Next, we establish your master orchestration environment.

1 : Open the Amazon MWAA console.

2 : Click Create environment. Name it production-orchestrator.

3 : Under Airflow version, choose the latest version available.

4 : Under DAG code location, select Browse S3 and click on your dedicated folder: s3://mwaa-airflow-orchestrator-bucket/dags/.

5 : Under Networking, click Create new VPC if you don't have an existing private subnet cluster setup. MWAA requires secure private routing paths.

6 : Under Execution role, select Create a new role. AWS will auto-generate an IAM framework role for you. Click Create environment.

⚠️ Note: MWAA environments take roughly 15 to 25 minutes to fully provision their backend systems. Don't worry if it stays in a "Creating" state for a while.

**Phase 5**: Link Permissions (IAM)For Airflow to control EMR Serverless, we need to explicitly connect them.

1 : Open the AWS IAM Console and find the execution role created by MWAA in the previous step (e.g., AmazonMWAA-production-orchestrator-...).

2 : Click Add permissions $\rightarrow$ Create inline policy.

3 : Select the JSON tab and paste this permission chunk to allow Airflow to run EMR serverless jobs:

```
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "emr-serverless:StartJobRun",
                "emr-serverless:GetJobRun"
            ],
            "Resource": "*"
        }
    ]
}
```
4 : Save it as MWAA-to-EMRServerless-Policy. Make sure your EMR engine execution role has reading and writing permission access to your ecommerce-analytics-data-lake bucket as well

**Phase 6**: Upload the DAG & Trigger
1 : Create a local file named ecommerce_orchestration_dag.py and replace the configuration placeholders at the top with your real AWS strings:

```
from datetime import datetime, timedelta
from airflow import DAG
from airflow.providers.amazon.aws.operators.emr import EmrServerlessStartJobOperator

# PASTE YOUR SYSTEM IDs HERE
EMR_APP_ID = '00f5abcdef123456' 
EMR_ROLE_ARN = 'arn:aws:iam::123456789012:role/YourEMRExecutionRole'
S3_BUCKET = 'ecommerce-analytics-data-lake'

default_args = {
    'owner': 'analytics',
    'start_date': datetime(2026, 1, 1),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    dag_id='ecommerce_daily_transform_pipeline',
    default_args=default_args,
    schedule_interval='@daily',
    catchup=False
) as dag:

    execute_pyspark_transform = EmrServerlessStartJobOperator(
        task_id='execute_pyspark_transform',
        application_id=EMR_APP_ID,
        execution_role_arn=EMR_ROLE_ARN,
        job_driver={
            'sparkSubmit': {
                'entryPoint': f's3://{S3_BUCKET}/scripts/sales_transform.py',
                'sparkSubmitParameters': '--conf spark.executor.cores=2 --conf spark.executor.memory=4g'
            }
        },
        configuration_overrides={
            'monitoringConfiguration': {
                's3MonitoringConfiguration': {
                    'logUri': f's3://{S3_BUCKET}/emr-logs/'
                }
            }
        }
    )
```

2 : Upload this file into your orchestration bucket: s3://mwaa-airflow-orchestrator-bucket/dags/.

3 : Open your Amazon MWAA Console, select your environment, and click the link labeled Airflow UI.

4 : Inside the Airflow dashboard, find ecommerce_daily_transform_pipeline. Flip the left toggle to On, and click the Trigger (Play) button on the right to manually initiate execution.

 Your workflow will execute immediately, request nodes from EMR, process the data, output optimized Parquet aggregates to your S3 folder, and tear down seamlessly.

 Here is exactly how to create it and ensure your data lake is securely accessible:

Step 1: Create the Permission Policy (S3 Access)
Open the AWS IAM Console (console.aws.amazon.com/iam).

On the left navigation pane, click Policies, then click Create policy.

Select the JSON tab, delete everything inside, and paste this configuration:


```
```
