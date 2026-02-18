-- dbt test: assert_gcs_downloaded
-- This test returns a row (and therefore fails) when the expected GCS object is missing
-- Usage: set `expected_gcs_object` as a dbt var and ensure `gcs_downloads` is a ref-able model/table

SELECT 1 AS missing
WHERE NOT EXISTS (
  SELECT 1 FROM {{ ref('gcs_downloads') }} WHERE gcs_object = '{{ var("expected_gcs_object") }}'
)
