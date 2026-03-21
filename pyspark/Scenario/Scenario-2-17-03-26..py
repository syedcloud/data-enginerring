from pyspark.sql import functions as F

data = [
    ('A', 'D', 'D'),
    ('B', 'A', 'A'),
    ('A', 'D', 'A')
]

df = spark.createDataFrame(data, ["TeamA", "TeamB", "Won"])
df.show()
# Step 1: Get all teams
teams = (
    df.select(F.col("TeamA").alias("TeamName"))
    .union(df.select(F.col("TeamB").alias("TeamName")))
    .distinct()
)

# Step 2: Count wins
wins = (
    df.groupBy("Won")
    .count()
    .withColumnRenamed("Won", "TeamName")
    .withColumnRenamed("count", "won")
)

# Step 3: Left join to include teams with 0 wins
final_df = (
    teams.join(wins, on="TeamName", how="left")
    .fillna(0, ["won"])
    .orderBy("TeamName")
)

final_df.show()
