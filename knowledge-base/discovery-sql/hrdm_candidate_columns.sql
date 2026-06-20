select
  table_schema,
  table_name,
  column_name,
  data_type,
  ordinal_position
from D_HRDATAMART.information_schema.columns
where table_schema in ('S_ANALYTICS', 'S_WORKDAY', 'S_CURATED', 'S_CURATED_SENSITIVE')
  and upper(column_name) like any (
    '%SITE%',
    '%LOCATION%',
    '%LOCATION_CODE%',
    '%FC%',
    '%REGION%',
    '%EMPLOYEE%',
    '%WORKER%',
    '%USER%',
    '%MANAGER%',
    '%BENEFICIARY%',
    '%BENEFIT%',
    '%EMERGENCY%',
    '%CONTACT%',
    '%DEPENDENT%',
    '%HIRE%',
    '%TENURE%',
    '%LOA%',
    '%LOAA%',
    '%CASE%',
    '%TASK%',
    '%SLA%',
    '%VOC%',
    '%CAT%',
    '%ECHO%',
    '%ROUND%',
    '%STAND%',
    '%FLO%',
    '%LEW%',
    '%QUALITY%',
    '%ONE%ON%ONE%'
  )
order by table_schema, table_name, ordinal_position
