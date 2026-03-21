
from pyspark.sql.functions import expr
data1 = [
    (1, "Henry"),
    (2, "Smith"),
    (3, "Hall")
]
columns1 = ["id", "name"]
rdd1 = sc.parallelize(data1,1)
df1 = rdd1.toDF(columns1)
df1.show()
data2 = [
    (1, 100),
    (2, 500),
    (4, 1000)
]
columns2 = ["id", "salary"]
rdd2 = sc.parallelize(data2,1)
df2 = rdd2.toDF(columns2)
df2.show()

joindf=df1.join(df2,on="id",how="left")
joindf.show()

semidf=joindf.withColumn("salary",expr(
    """
    case when salary is null then 0 else salary end
    """))
semidf.show()