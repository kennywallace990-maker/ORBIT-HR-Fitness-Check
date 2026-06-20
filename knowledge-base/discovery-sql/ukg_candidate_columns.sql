select
  table_schema,
  table_name,
  column_name,
  data_type,
  ordinal_position
from EDLDB.information_schema.columns
where table_schema = 'UKG'
  and upper(column_name) like any (
    '%SITE%',
    '%LOCATION%',
    '%LOCATION_CODE%',
    '%FC%',
    '%REGION%',
    '%EMPLOYEE%',
    '%WORKER%',
    '%USER%',
    '%SCHEDULE%',
    '%SCHEDULE_GROUP%',
    '%MISSING%',
    '%PUNCH%',
    '%MEAL%',
    '%LUNCH%',
    '%PAYCODE%',
    '%HOURS%',
    '%TIME%',
    '%SHIFT%',
    '%ACCRUAL%',
    '%VTO%',
    '%VET%',
    '%MET%'
  )
order by table_schema, table_name, ordinal_position
