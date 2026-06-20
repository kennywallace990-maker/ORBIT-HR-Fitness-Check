select
  table_schema,
  table_name,
  table_type,
  created,
  last_altered
from EDLDB.information_schema.tables
where table_schema = 'UKG'
   or upper(table_name) like any (
    '%UKG%',
    '%TIMECARD%',
    '%SCHEDULE%',
    '%ACCRUAL%',
    '%ATTENDANCE%',
    '%ROSTER%',
    '%TIME_ENTRY%',
    '%PUNCH%',
    '%MEAL%',
    '%LUNCH%',
    '%VTO%',
    '%VET%'
  )
order by table_schema, table_name
