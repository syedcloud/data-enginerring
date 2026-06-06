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
