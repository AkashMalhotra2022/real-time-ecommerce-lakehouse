data "aws_caller_identity" "current" {}

# Warehouse: S3 bucket for raw streaming data.
# force_destroy lets `terraform destroy` delete it even with files inside.
resource "aws_s3_bucket" "streaming" {
  bucket        = "${var.project}-streaming-${data.aws_caller_identity.current.account_id}"
  force_destroy = true
}

# Conveyor belt: Kinesis stream (1 shard is plenty for our volume).
resource "aws_kinesis_stream" "events" {
  name             = "${var.project}-events"
  shard_count      = 1
  retention_period = 24
  stream_mode_details {
    stream_mode = "PROVISIONED"
  }
}

# Badge: an IAM role Firehose can wear, allowing it to read Kinesis and write S3.
resource "aws_iam_role" "firehose" {
  name = "${var.project}-firehose-role"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect    = "Allow"
      Principal = { Service = "firehose.amazonaws.com" }
      Action    = "sts:AssumeRole"
    }]
  })
}

resource "aws_iam_role_policy" "firehose" {
  name = "${var.project}-firehose-policy"
  role = aws_iam_role.firehose.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect   = "Allow"
        Action   = ["s3:AbortMultipartUpload", "s3:GetBucketLocation", "s3:GetObject",
                    "s3:ListBucket", "s3:ListBucketMultipartUploads", "s3:PutObject"]
        Resource = [aws_s3_bucket.streaming.arn, "${aws_s3_bucket.streaming.arn}/*"]
      },
      {
        Effect   = "Allow"
        Action   = ["kinesis:DescribeStream", "kinesis:GetShardIterator",
                    "kinesis:GetRecords", "kinesis:ListShards"]
        Resource = aws_kinesis_stream.events.arn
      },
      {
        Effect   = "Allow"
        Action   = ["logs:CreateLogGroup", "logs:CreateLogStream", "logs:PutLogEvents"]
        Resource = "*"
      }
    ]
  })
}

# Truck: Firehose reads the Kinesis belt and drops batched files into S3,
# organized into year/month/day/hour folders.
resource "aws_kinesis_firehose_delivery_stream" "to_s3" {
  name        = "${var.project}-to-s3"
  destination = "extended_s3"

  kinesis_source_configuration {
    kinesis_stream_arn = aws_kinesis_stream.events.arn
    role_arn           = aws_iam_role.firehose.arn
  }

  extended_s3_configuration {
    role_arn            = aws_iam_role.firehose.arn
    bucket_arn          = aws_s3_bucket.streaming.arn
    prefix              = "raw/streaming/year=!{timestamp:yyyy}/month=!{timestamp:MM}/day=!{timestamp:dd}/hour=!{timestamp:HH}/"
    error_output_prefix = "raw/streaming_errors/!{firehose:error-output-type}/"
    buffering_size      = 5
    buffering_interval  = 60
    compression_format  = "UNCOMPRESSED"
  }
}