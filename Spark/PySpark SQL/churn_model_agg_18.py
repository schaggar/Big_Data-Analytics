import sys
from pyspark.sql import SparkSession
import pyspark.sql.functions as f
from pyspark.sql.types import *
from pyspark.sql.types import DateType
from pyspark.sql.functions import *
from pyspark.sql.window import Window


if __name__ == "__main__":
    print("Churn Modelling")

# set the SparkSession
spark = SparkSession.builder.appName("Churn Modeling").master("local[3]").getOrCreate()

# read the datafile from the location
churn = spark.read.csv(r"D:\Code\DataSet\SparkDataSet\ChurnModeling.csv", inferSchema=True, header=True)
churn.show(5, truncate=False)

# select the required columns
churn = churn.selectExpr("CustomerId", "Balance", "Surname", "CreditScore", "Geography", "Gender", "Age", "Tenure") \
    .filter((churn.Geography.isin("France", "Spain")) & (churn.Gender.isin("Male","Female"))) \
    .filter((churn.Age >= 18) & (churn.HasCrCard != 1) & (churn.IsActiveMember != 0) & (churn.Tenure > 5)) \
    .filter((churn.Balance) != 0) \
    .sort("Age")

churn_extr = churn.select("CustomerId", "Balance", "CreditScore", "Geography", "Age",
                          rank().over(Window.partitionBy('Geography').orderBy(desc("Balance"))).alias("Rank"),
                          dense_rank().over(Window.partitionBy('Geography').orderBy(desc("Balance"))).alias("Dense_Rank"),
                          row_number().over(Window.partitionBy('Geography').orderBy(desc("Balance"))).alias("RNumber"))

churn_wfunc = churn_extr.createOrReplaceTempView("churn_extr_win_agg")

SQL_qry = spark.sql("""
                        select * from churn_extr_win_agg
                        where Rank between 1 and 10
                        order by Rank asc
                        """)
SQL_qry.show(SQL_qry.count(), truncate = False)

print(f'Records effected: {SQL_qry.count()}')
print(f"Number of Executor Partition: {SQL_qry.rdd.getNumPartitions()}")
