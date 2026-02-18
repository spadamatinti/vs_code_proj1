-- dbt test: assert_s3_uploaded
-- This test returns a row (and therefore fails) when the expected S3 object is missing
-- Usage: set `expected_s3_key` as a dbt var and ensure `s3_uploads` is a ref-able model/table

SELECT 1 AS missing
WHERE NOT EXISTS (
  SELECT 1 FROM {{ ref('s3_uploads') }} WHERE s3_key = '{{ var("expected_s3_key") }}'
)
