import sys
from pyspark.sql import SparkSession
import pyspark.sql.functions as f
from pyspark.sql.types import *
from pyspark.sql.types import DateType
from pyspark.sql.functions import *
from pyspark.sql.window import Window
# from pyspark.sql.functions import spark_partition_id

if __name__ == "__main__":
    print("Games Analysis")

# set the SparkSession
spark = SparkSession.builder.appName("Games Analysis").master("local[3]").getOrCreate()

games = spark.read.csv(r"D:\Code\DataSet\SparkDataSet\NHL\game.csv", inferSchema=True, header=True)
games.show(5, truncate=False)

# drop unwanted columns from the DF
games = games.drop("date_time_GMT", "away_team_id", "home_team_id", "venue_link", "venue_time_zone_id", "venue_time_zone_offset", "venue_time_zone_tz")

# select the required columns
games_sel = games.selectExpr("game_id", "season", "type", "away_goals", "home_goals",
                         "venue", "outcome", "home_rink_side_start") \
                 .filter((games.type != "P") & (games.home_rink_side_start == "right")) \
                 .where("home_rink_side_start in ('right', 'left')") \
                 .where("away_goals >= 6 and away_goals > home_goals")

games_agg = games_sel.select("game_id", "season", "type", "away_goals", "home_goals", "venue", "outcome", "home_rink_side_start",
                     sum("away_goals").over(Window.partitionBy('season').orderBy(asc("game_id"))).alias("sum_away_goals"),
                     sum("home_goals").over(Window.partitionBy('season').orderBy(asc("game_id"))).alias("sum_home_goals")
                             )
games_lim = games_agg.select("game_id", "season", "type", "away_goals", "home_goals", "venue",
                             "outcome", "home_rink_side_start","sum_away_goals", "sum_home_goals") \
                    .where("sum_away_goals > sum_home_goals") \
                    .where("venue like '%Arena'")

# create temp table
SQL_tab = games_lim.createOrReplaceTempView("games")

# query from temp table
SQL_qry = spark.sql("""select game_id, season, type, away_goals,
                              home_goals, venue, outcome,
                              home_rink_side_start, sum_away_goals, sum_away_goals
                              from games order by 1""")
# get count of each partition
df_with_id = games_lim.withColumn("partitionId", spark_partition_id())
SQL_part_ID = df_with_id.createOrReplaceTempView("partition_dtls")

part_cal = spark.sql("""select partitionId, count(1) as num_records
                               from partition_dtls
                               group by partitionId
                               order by num_records asc
                               """)

SQL_qry.show(10, truncate = False)
print(f"Records Effected: {SQL_qry.count()}")
print(f"Number of partition: {SQL_qry.rdd.getNumPartitions()}")

print('-------------------------------------------------------------------------------------------------------------------------------------------')

part_cal.show(10, truncate = False)
print(f"Records Effected: {part_cal.count()}")
print(f"Number of records in each partition: {part_cal.rdd.getNumPartitions()}")