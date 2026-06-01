Phase 1: Set Up Storage (S3 Buckets)We need to create the folders for our data lake and our orchestration code.Open the Amazon S3 Console.Click Create bucket. Name it exactly: ecommerce-analytics-data-lake.Inside this bucket, create four folders:raw-data/ (Where our incoming daily transactions sit)scripts/ (Where our PySpark code sits)processed-output/ (Where the final clean data will go)emr-logs/ (Where Spark execution errors/logs will save)Go back to the S3 home page, click Create bucket again. Name it exactly: mwaa-airflow-orchestrator-bucket.Inside this bucket, create one single folder:dags/ (Where our Airflow management script sits)Phase 2: Create local files and upload to S3File 1: The Raw DataCreate a file on your local computer named daily_transactions.csv and paste this mock transaction data inside:Code snippettransaction_id,user_id,product_category,amount,timestamp
TXN001,USR99,Electronics,1200.50,2026-05-30 14:22:11
TXN002,USR45,Apparel,45.00,2026-05-30 14:23:00
TXN003,USR99,Electronics,15.99,2026-05-30 14:25:12
📥 Action: Upload daily_transactions.csv to s3://ecommerce-analytics-data-lake/raw-data/.File 2: The PySpark ScriptCreate a file on your local computer named sales_transform.py and paste this Python code inside:Pythonfrom pyspark.sql import SparkSession
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
📥 Action: Upload sales_transform.py to s3://ecommerce-analytics-data-lake/scripts/.Phase 3: Create the EMR Security Role (IAM)Before we turn on EMR Serverless, we must build its security guard credentials so it can legally read/write to your S3 folders.Step 1: Create the Data Access PolicyOpen the AWS IAM Console.On the left menu, click Policies, then click Create policy.Click the JSON tab, delete whatever is there, and paste this block:JSON{
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
Click Next. Name this policy: EMRServerless-S3-Policy. Click Create policy.Step 2: Create the Role and Link the TrustOn the left IAM menu, click Roles, then click Create role.Select Custom trust policy as the type.Paste this configuration (this tells AWS that EMR Serverless is allowed to act as this role):JSON{
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
Click Next.In the permissions search box, find and check the box next to the policy you just created: EMRServerless-S3-Policy.Click Next. Name this role exactly: EMRServerlessExecutionRole.Click Create role.Copy the Role ARN string (e.g., arn:aws:iam::123456789012:role/EMRServerlessExecutionRole). You will need it for Airflow!Phase 4: Spin Up EMR ServerlessOpen the Amazon EMR Console and click EMR Serverless on the left menu.Click Create application.Name it: pyspark-processing-engine.Type: Choose Spark. Release: Choose stable emr-7.1.0.Application setup: Keep Use default settings turned on. This automatically keeps things lean and shuts down VMs when idling to save you money.Click Create Application.Once created, look at your dashboard and copy the Application ID string (e.g., 00f5abcdef123456).Phase 5: Provision Airflow (Amazon MWAA)Open the Amazon MWAA Console.Click Create environment. Name it production-orchestrator.Under DAG code location, click Browse S3 and pick: s3://mwaa-airflow-orchestrator-bucket/dags/.Under Networking, click Create new VPC (if you don't have private subnets ready).Under Execution role, select Create a new role.Click Create environment.⏳ Note: AWS takes 15-20 minutes to set up the Airflow servers. Wait until the status changes from "Creating" to "Available".Phase 6: Authorize Airflow to control EMRNow that MWAA has finished creating its automatic role, we must manually grant it permission to trigger EMR.Open the AWS IAM Console, click Roles.Search for the role that MWAA automatically generated (it will look like AmazonMWAA-production-orchestrator-...). Click it.Click Add permissions $\rightarrow$ Create inline policy.Choose the JSON tab and paste this specific block:JSON{
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
Name this policy: MWAA-Trigger-EMR-Policy and click Save.Phase 7: Write the Airflow DAG & Execute!Create a file on your local computer named ecommerce_orchestration_dag.py and paste this code inside. Make sure to change the placeholders at the top to match your real IDs:Pythonfrom datetime import datetime, timedelta
from airflow import DAG
from airflow.providers.amazon.aws.operators.emr import EmrServerlessStartJobOperator

# ==================== CONFIGURATION (REPLACE THESE) ====================
EMR_APP_ID = 'YOUR_EMR_APPLICATION_ID_FROM_PHASE_4' 
EMR_ROLE_ARN = 'YOUR_EMR_ROLE_ARN_FROM_PHASE_3'
S3_BUCKET = 'ecommerce-analytics-data-lake'
# =======================================================================

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
Upload this finished ecommerce_orchestration_dag.py to s3://mwaa-airflow-orchestrator-bucket/dags/.Go back to your Amazon MWAA Console, locate your environment, and click Open Airflow UI.On the Airflow dashboard, look for ecommerce_daily_transform_pipeline.Turn the toggle switch on the left from grey to Blue (Unpause), then click the Trigger (Play) button on the far right.Airflow will now run, command EMR Serverless to wake up compute resources, execute your Spark engine transformations, and output perfect analytical Parquet file tables right into s3://ecommerce-analytics-data-lake/processed-output/.
