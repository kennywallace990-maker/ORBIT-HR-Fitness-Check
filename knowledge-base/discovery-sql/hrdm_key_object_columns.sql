select
  table_schema,
  table_name,
  column_name,
  data_type,
  ordinal_position
from D_HRDATAMART.information_schema.columns
where (table_schema = 'S_ANALYTICS' and table_name in (
    'ROSTER_DAY_END',
    'ROSTER_WEEK_END',
    'ROSTER_PERIOD_END',
    'WORKDAY_TRENDED_MANAGER_HIERARCHY',
    'BRASS_TACKS_TABLEAU_WD_PROD'
  ))
  or (table_schema = 'S_WORKDAY' and table_name in (
    'WD_DATAMARTFEED',
    'WD_DATAMARTFEED_TRENDED',
    'WORKDAY_TRENDED',
    'V_WORKDAY_TRENDED',
    'WD_LOCATION',
    'WD_SECURITY',
    'WD_FWA'
  ))
  or (table_schema = 'S_CURATED' and table_name in (
    'CURRENT_EMPLOYEES',
    'TERMINATED_EMPLOYEES',
    'EMPLOYEE_JOB_HISTORY',
    'ROSTER_WEEK_END',
    'ROSTER_PERIOD_END'
  ))
order by table_schema, table_name, ordinal_position;
