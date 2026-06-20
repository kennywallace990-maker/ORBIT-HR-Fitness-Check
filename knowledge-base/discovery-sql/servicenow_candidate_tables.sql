select
  'D_HRDATAMART' as database_name,
  table_schema,
  table_name,
  table_type,
  created,
  last_altered
from D_HRDATAMART.information_schema.tables
where lower(table_name) in ('sn_hr_core_case', 'sn_hr_core_task')
   or upper(table_name) like any (
    '%SN_HR_CORE%',
    '%SERVICE%NOW%',
    '%SNOW%',
    '%HR_CASE%',
    '%HR_TASK%'
  )
union all
select
  'EDLDB' as database_name,
  table_schema,
  table_name,
  table_type,
  created,
  last_altered
from EDLDB.information_schema.tables
where lower(table_name) in ('sn_hr_core_case', 'sn_hr_core_task')
   or upper(table_name) like any (
    '%SN_HR_CORE%',
    '%SERVICE%NOW%',
    '%SNOW%',
    '%HR_CASE%',
    '%HR_TASK%'
  )
order by database_name, table_schema, table_name
