select
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
    '%HR_TASK%',
    '%HR%CASE%',
    '%HR%TASK%'
  )
order by table_schema, table_name;
