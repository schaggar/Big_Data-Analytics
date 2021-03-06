import sys
from pyspark.sql import *
import pyspark
from pyspark.sql import SparkSession
from pyspark.sql.types import *
from pyspark.sql.functions import *
import pyspark.sql.functions


if __name__ == "__main__":
    print("Churn Modelling")

# set the SparkSession
spark = SparkSession.builder.appName("Churn Modeling").master("local[3]").getOrCreate()

# read the datafile from the location
churn = spark.read.csv(r"D:\Code\DataSet\SparkDataSet\ChurnModeling.csv", inferSchema=True, header=True)
churn.show(5, truncate=False)

# select the required columns
churn_agg = churn.createOrReplaceTempView("Churn_Agg")

agg = spark.sql("""select * from
                    (select CustomerId,
                    Geography,
                    Gender
                    CreditScore,
                    sum(CreditScore) over (partition by Geography, Gender order by Age desc) as sum_credit_score,
                    rank(CreditScore) over (partition by Geography, Gender order by Age desc) as rank
                    from
                    Churn_Agg
                    where IsActiveMember = 1) temp
                    where rank = 1
                    """)
agg.show(agg.count(), truncate=False)
print(f"Records returned :{agg.count()}")
