package BigData

import org.apache.spark.sql.SparkSession
import org.apache.spark.sql.types.{IntegerType, StructField, StructType}
import org.apache.spark.sql.{DataFrame, Row, SparkSession}
import org.apache.spark.sql.functions._
import org.apache.spark.SparkConf
import org.apache.spark.sql.types.StructType
import org.apache.spark.sql.types.StringType
import org.apache.spark.sql.types.IntegerType

object cars_schema_3 extends App {
  println("USA Cars Details using Seq & StructType")

  val spark = SparkSession.builder()
    .master("local[3]")
    .appName("USA Cars Details using StructType")
    .getOrCreate()

  // create the data
  val data = Seq(
    (100, "Monica", "London"),
    (110, "Kate", "Paris"),
    (120, "Norris", "" )
  )

  // define the DF
  val emp_df = spark.createDataFrame(data)

// implicit DF conversion
  import spark.implicits._
  val col_name = data.toDF("ID", "Name", "City")
  col_name.show()
}
