import sys
from pyspark.sql import SparkSession
import pyspark.sql.functions as f
from pyspark.sql.types import *
from pyspark.sql.types import DateType
from pyspark.sql.functions import *
from pyspark.sql.window import Window
from pyspark.sql.functions import spark_partition_id

if __name__ == "__main__":
    print("Games Analysis")

# set the SparkSession
spark = SparkSession.builder.appName("Games Analysis").master("local[3]").getOrCreate()

# define schema for games df
games_schema = StructType(
                          [
                           StructField("game_id", IntegerType(), False),
                           StructField("season", IntegerType(), False),
                           StructField("type", StringType(), False),
                           StructField("date_time", StringType(), False),
                           StructField("date_time_GMT", TimestampType(), False),
                           StructField("away_team_id", StringType(), False),
                           StructField("home_team_id", IntegerType(), False),
                           StructField("away_goals", IntegerType(), False),
                           StructField("home_goals", IntegerType(), False),
                           StructField("outcome", StringType(), False),
                           StructField("home_rink_side_start", StringType(), False),
                           StructField("venue", StringType(), False),
                           StructField("venue_link", StringType(), False),
                           StructField("venue_time_zone_id", StringType(), False),
                           StructField("venue_time_zone_offset", IntegerType(), False),
                           StructField("venue_time_zone_tz", StringType(), False)
                           ]
                         )

# define schema for games df
games_shift_schema = StructType(
                          [
                           StructField("game_id", IntegerType(), False),
                           StructField("player_id", IntegerType(), False),
                           StructField("period", IntegerType(), False),
                           StructField("shift_start", IntegerType(), False),
                           StructField("shift_end", IntegerType(), False)
                           ]
                         )

# read the datafile from the location
games = (spark.read.option("header", "True")
         .option("schema", games_schema)
         .option("dateFormat", "dd-mm-yyyy")
         .option("timestampFormat", "dd-mm-yyyy hh24:mm:ss")
         .csv(r"D:\Code\DataSet\SparkDataSet\NHL\game.csv")
         .select("game_id", "season", "type", "date_time", "date_time_GMT", "away_team_id", "home_team_id", "away_goals",
                                  "home_goals", "outcome", "home_rink_side_start", "venue", "venue_link", "venue_time_zone_id", "venue_time_zone_offset",
                                  "venue_time_zone_tz")
         )
games = games.select("game_id", "season", "type", "date_time", "date_time_GMT", "away_team_id", "home_team_id", "away_goals",
                                  "home_goals", "outcome", "home_rink_side_start", "venue")
games.show(10, truncate=False)

# read the datafile from the location
game_shift = (spark.read.option("header", "True")
                       .option("schema", games_shift_schema)
                       .option("dateFormat", "dd-mm-yyyy")
                       .option("timestampFormat", "dd-mm-yyyy hh24:mm:ss")
                       .csv(r"D:\Code\DataSet\SparkDataSet\NHL\game_shifts_info.csv")
                       .select("game_id", "player_id", "period", "shift_start", "shift_end")
             )
game_shift.show(5, truncate=False)

# join 2 dataframes (games_cols, games_shift_cols)
join_df = games.join(game_shift, on="game_id", how='inner') \
                     .select("game_id", "player_id", "season", "type", "date_time", "date_time_GMT", "home_goals", "away_goals", "period",
                             "away_team_id", "home_team_id"
                             )

# # create a temp table
SQL_tab = join_df.createOrReplaceTempView("Player_Status")

# # query from temp table
SQL_qry = spark.sql("""select
                            game_id,
                            player_id,
                            period,
                            season,
                            date_format(date_time_GMT,'dd') as date,
                            date_format(date_time_GMT,'MM') as month,
                            date_format(date_time_GMT,'yyyy') as year,
                            type,
                            home_goals,
                            away_goals,
                            sum(home_goals) over (partition by season order by game_id asc ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) as sum_home_goals,
                            sum(away_goals) over (partition by season order by game_id asc ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) as sum_away_goals
                            from Player_Status
                            where type = 'P'
                            """)
SQL_qry.show(10, truncate=False)
print(f'Records returned: {SQL_qry.count()}')