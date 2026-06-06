***Phase 1***: Storage Infrastructure Creation (S3)

We need to isolate our raw data and analytics storage from the Python control files running our pipeline.

1. Open the Amazon S3 Console.

2. Click Create bucket. Name it exactly: ecommerce-analytics-data-lake-4-6-26. Leave all default settings and click Create bucket.

3. Click into your newly created bucket and use the Create folder button to create these four folders:

      o  raw-data/
      
      o  scripts/
      
      o  processed-output/
      
      o  emr-logs/

4. Go back to the main S3 page, click Create bucket again, and provision your orchestration bucket: mwaa-airflow-orchestrator-bucket.

5. Click into it and create a single folder named: dags/.

***Phase 2***: Create Scripts & Upload Source Data

1. ***The Source Dataset*** (daily_transactions.csv)
On your computer, open a text editor (like Notepad or TextEdit), paste this text inside, and save it as daily_transactions.csv:

```
transaction_id,user_id,product_category,amount,timestamp
TXN001,USR99,Electronics,1200.50,2026-05-30 14:22:11
TXN002,USR45,Apparel,45.00,2026-05-30 14:23:00
TXN003,USR99,Electronics,15.99,2026-05-30 14:25:12
```

o Upload: Go to your S3 bucket $\rightarrow$ ecommerce-analytics-data-lake-4-6-26 $\rightarrow$ raw-data/ and upload this file.

2. The ***Big Data Processing Script*** (sales_transform.py)

Create another file on your computer named sales_transform.py and paste this PySpark script inside:
```
from pyspark.sql import SparkSession
from pyspark.sql.functions import current_date, sum as _sum

def main():
    # Initialize the Distributed Spark Context
    spark = SparkSession.builder.appName("Ecommerce-Daily-Aggregation").getOrCreate()
    
    input_uri = "s3://ecommerce-analytics-data-lake-4-6-26/raw-data/daily_transactions.csv"
    output_uri = "s3://ecommerce-analytics-data-lake-4-6-26/processed-output/"

    # Ingest CSV and drop rows missing financial data
    df = spark.read.csv(input_uri, header=True, inferSchema=True)
    cleaned_df = df.dropna(subset=["transaction_id", "amount"])
    
    # Calculate revenue summaries
    aggregated_df = cleaned_df.groupBy("product_category").agg(
        _sum("amount").alias("total_revenue")
    ).withColumn("processing_date", current_date())

    # Write results back to S3 as compressed analytical Parquet data
    aggregated_df.write.mode("overwrite").parquet(output_uri)
    spark.stop()

if __name__ == "__main__":
    main()
```

o Upload: Go to your S3 bucket $\rightarrow$ ecommerce-analytics-data-lake-4-6-26 $\rightarrow$ scripts/ and upload this file.

***Phase 3***: Configure EMR Serverless Execution Role
The EMR engine requires explicit security permissions to read your script and write out the processed analytical Parquet files.

1. Open the AWS IAM Console. On the left panel, click Roles, then click Create role.
2. Select Custom trust policy and paste this block to allow EMR Serverless to assume this identity:
```
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "emr-serverless.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
```
3. Click Next. On the permissions window, click Create policy (opens a new tab).
4. Click the JSON button, wipe out the default text, and paste this bucket authorization layout:
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
                "arn:aws:s3:::ecommerce-analytics-data-lake-4-6-26",
                "arn:aws:s3:::ecommerce-analytics-data-lake-4-6-26/*"
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
5. Click Next, name it EMRServerless-S3-Policy, and click Create policy.
6. Switch back to your original Role Creation browser tab. Refresh the policy list, search for EMRServerless-S3-Policy, and check the box next to it.
7. Click Next. Name the role EMRServerlessExecutionRole and click Create role.
8. Copy the Role ARN string (e.g., arn:aws:iam::123456789012:role/EMRServerlessExecutionRole). You will need it for Airflow!

***Phase 4***: Spin Up EMR Serverless Application Engine
1. Open the Amazon EMR Console and navigate to EMR Serverless on the left menu.
2. Click Create application.
3. Configure these parameters:

o Name: pyspark-processing-engine
o Type: SPARK
o Release version: emr-7.1.0

4. Leave everything else as default and click Create application.
5. Once created, copy the alphanumeric Application ID string from the dashboard (e.g., 00g66u087egrdn09). You will need it for Airflow!

***Phase 5***: Provision Amazon MWAA (Airflow Orchestrator)
1. Open the Amazon MWAA Console (Managed Workflows for Apache Airflow).
2. Click Create environment. Name it production-orchestrator.
3. Under DAG code location, click Browse S3, select your bucket mwaa-airflow-orchestrator-bucket, and choose the dags/ folder.
4. Scroll down to Networking. Under VPC, click Create a new VPC. (AWS will automatically build a secure network environment with subnets and NAT Gateways).
5. Under Permissions, ensure Create a new role is selected.
6. Click Create environment. (Grab a coffee—AWS will take about 20 minutes to securely stand up your environment).

***Phase 6***: Authorize Airflow to Control EMR
To allow Airflow to manage your processing engine, we must attach a custom policy to the security role that MWAA generated.
1. Once the MWAA environment turns green and reads Available, click on its name to view details.
2. Under Permissions settings, click the link next to Execution role. This opens that unique role directly in the IAM console.
3. Under the Permissions tab of that role, click Add permissions $\rightarrow$ Create inline policy.
4. Select the JSON input box and overwrite everything with this management layout:
```
{
	"Version": "2012-10-17",
	"Statement": [
		{
			"Sid": "EMRServerlessOrchestration",
			"Effect": "Allow",
			"Action": [
				"emr-serverless:GetApplication",
				"emr-serverless:StartApplication",
				"emr-serverless:StartJobRun",
				"emr-serverless:GetJobRun",
				"emr-serverless:CancelJobRun"
			],
			"Resource": "*"
		},
		{
			"Sid": "AllowPassRoleToEMRTemporary",
			"Effect": "Allow",
			"Action": [
				"iam:PassRole"
			],
			"Resource": "*"
		}
	]
}
```
5. Click Next, name the policy MWAA-Trigger-EMR-Policy, and click Create policy.

***Phase 7***: Deploy & Run the Airflow DAG File
Create a file on your computer named ecommerce_orchestration_dag.py and paste this orchestration framework inside. Ensure the EMR_APP_ID matches your code from Phase 4 step 5 and EMR_ROLE_ARN mathces your code from phase 3 step 8
```
from datetime import datetime, timedelta
from airflow import DAG
from airflow.providers.amazon.aws.operators.emr import EmrServerlessStartJobOperator

# ==================== PIPELINE CONFIGURATION ====================
EMR_APP_ID = 'YOUR_EMR_APPLICATION_ID_FROM_PHASE_4'  # Update this with your actual ID from Phase 4 setp 5
EMR_ROLE_ARN = 'YOUR_EMR_ROLE_ARN_FROM_PHASE_3'  #update this with your actual ROLe ARN from PHase 3 step 8
S3_BUCKET = 'ecommerce-analytics-data-lake-4-6-26'
# ================================================================

default_args = {
    'owner': 'analytics',
    'start_date': datetime(2026, 1, 1),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    dag_id='ecommerce_daily_transform_pipeline',
    default_args=default_args,
    schedule='@daily',
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

2. Upload: Go to your S3 bucket $\rightarrow$ mwaa-airflow-orchestrator-bucket $\rightarrow$ dags/ and upload this file.
3. Open your Amazon MWAA Dashboard, click the Open Airflow UI link.
4. Locate ecommerce_daily_transform_pipeline, click the toggle on the left to Unpause, and click the Trigger (Play button) on the far right to run it.

Phase 8: Output Verification via AWS CloudShell

 Now that your manually constructed architecture has successfully run through Airflow, let's execute your requested confirmation checkpoint using the terminal.

 1. Open AWS CloudShell by clicking the terminal console logo [>_] in the very top right browser header navigation bar.
 2. Copy and paste this exact command block into the terminal window and hit Enter:
```
# 1. Install localized Parquet engines into the CloudShell sandbox environment
pip3 install pandas pyarrow --quiet

# 2. Grab your newly calculated dataset files down from your S3 target data lake folder
aws s3 cp s3://ecommerce-analytics-data-lake-4-6-26/processed-output/ . --recursive --exclude "*" --include "*.parquet"

# 3. Read the output structures to ensure formatting and math validations match
python3 -c "
import pandas as pd
import glob
parquet_files = glob.glob('*.parquet')
if parquet_files:
    df = pd.read_parquet(parquet_files[0])
    print('\n=== PIPELINE OUTPUT VERIFICATION ===')
    print(df.to_string(index=False))
else:
    print('No parquet files found!')
"
```

***Expected Output Terminal Screen:***
Your terminal should cleanly display your analytics results:
```
=== PIPELINE OUTPUT VERIFICATION ===
product_category  total_revenue  processing_date
     Electronics        1216.49       2026-06-05
         Apparel          45.00       2026-06-05

```



   
