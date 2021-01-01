import sys
from pyspark.sql import SparkSession
import pyspark.sql.functions as f
from pyspark.sql.types import *
from pyspark.sql.window import Window
from pyspark.sql.types import DateType
from pyspark.sql.functions import *


if __name__ == "__main__":
    print("Churn Modelling")

# set the SparkSession
churn_df = SparkSession.builder.appName("Churn Modeling").master("local[3]").getOrCreate()

# read the datafile from the location
churn = churn_df.read.csv(r"D:\Code\DataSet\SparkDataSet\ChurnModeling.csv", inferSchema=True, header=True)
churn.show(5, truncate=False)
, 
# select the required columns
churn = churn.selectExpr("CustomerId", "Surname", "CreditScore", "Geography", "Gender", "Age", "Tenure") \
    .filter((churn.Geography.isin("France", "Spain")) & (churn.Gender == "Male")) \
    .filter((churn.Age >= 18) & (churn.HasCrCard == 1) & (churn.IsActiveMember == 0)) \
    .groupBy("Geography", "Gender") \
    .agg(avg("Age").alias("Avg_Age")) \
    .orderBy(asc("Avg_Age"))

    # .where(churn.Age >= 18) \
#     .where(churn.IsActiveMember == 0) \

churn.show(15)
print(f'Records effected: {churn.count()}')
