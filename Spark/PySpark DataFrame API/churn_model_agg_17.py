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
churn_df = SparkSession.builder.appName("Churn Modeling").master("local[3]").getOrCreate()

# read the datafile from the location
churn = churn_df.read.csv(r"D:\Code\DataSet\SparkDataSet\ChurnModeling.csv", inferSchema=True, header=True)
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

churn_wfunc = churn_extr.selectExpr("CustomerId", "Balance", "CreditScore", "Geography", "Age", "Rank", "Dense_Rank", "RNumber") \
                        .filter(churn_extr.Rank == 1)

churn_wfunc.show(10, truncate=False)
print(f'Records effected: {churn_wfunc.count()}')
print(f"Number of Executor Partition: {churn_wfunc.rdd.getNumPartitions()}")
