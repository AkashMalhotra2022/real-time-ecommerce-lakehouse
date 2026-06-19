output "s3_bucket"       { value = aws_s3_bucket.streaming.bucket }
output "kinesis_stream"  { value = aws_kinesis_stream.events.name }
output "firehose_stream" { value = aws_kinesis_firehose_delivery_stream.to_s3.name }