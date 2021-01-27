package BigData

import BigData.stock_price.{spark, stock_schema}
import org.apache.spark.sql.{DataFrame, Row, SaveMode, SparkSession}
import org.apache.spark.sql.types.{DateType, DoubleType, IntegerType, StringType, StructField, StructType}
import org.apache.spark.sql.functions._
import org.apache.spark.SparkConf
import org.apache.spark.sql.types.DoubleType
import org.apache.spark.sql.types.DateType
import org.apache.spark.sql.types.StringType

import java.util.Properties

object ipl extends App {
  println("Indian Premier League")

  //  define spark session
  val spark = SparkSession.builder()
    .master("local[3]")
    .appName("Indian Premier League")
    .getOrCreate()

//  define the schema for IPL DF

  val ipl_schema = StructType(List(
    StructField("id", IntegerType),
    StructField("city", StringType),
    StructField("schedule", DateType),
    StructField("player_of_match", StringType),
    StructField("venue", StringType),
    StructField("neutral_venue", StringType),
    StructField("team1", StringType),
    StructField("team2", StringType),
    StructField("toss_winner", StringType),
    StructField("toss_decision", StringType),
    StructField("winner", StringType),
    StructField("result", StringType),
    StructField("result_margin", StringType),
    StructField("eliminator", StringType),
    StructField("method", StringType),
    StructField("umpire1", StringType),
    StructField("umpire2", StringType),
  ))

//  read the IPL DF
  spark.conf.set("spark.sql.legacy.timeParserPolicy","LEGACY")
  val ipl_df = spark.read
    .format("csv")
    .option("header", "true")
    .schema(ipl_schema)
    .option("dateFormat", "yyyy-MM-dd")
    .option("mode", "failFast") // dropMalFormed, permissive
    .option("sep", ",")
    .option("nullValue", "")
    .option("compression", "snappy") // bzip2, gzip, lz4, deflate, uncompressed
    .option("path","D:/Code/DataSet/SparkDataSet/IndianPremierLeague.csv")
    .load()

//  ipl_df.printSchema()
//  ipl_df.show()

//  save IPL DF in tab separated format
  ipl_df.write
    .option("delimiter", "\t")
    .option("header", "true")
    .mode(SaveMode.Overwrite)
    .csv("H:/ScalaSparkOutput/IPL/")

  spark.stop()
}
