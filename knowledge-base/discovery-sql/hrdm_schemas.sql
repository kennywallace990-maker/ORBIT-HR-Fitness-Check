select
  catalog_name,
  schema_name,
  schema_owner,
  created,
  last_altered
from D_HRDATAMART.information_schema.schemata
order by schema_name;
