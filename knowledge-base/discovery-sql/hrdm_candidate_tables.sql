select
  table_schema,
  table_name,
  table_type,
  created,
  last_altered
from D_HRDATAMART.information_schema.tables
where table_schema in ('S_ANALYTICS', 'S_WORKDAY', 'S_CURATED', 'S_CURATED_SENSITIVE')
   or upper(table_name) like any (
    '%ROSTER%',
    '%WORKDAY%',
    '%SNOW%',
    '%SERVICE%NOW%',
    '%SN_HR_CORE%',
    '%ECHO%',
    '%CAT%',
    '%VOC%',
    '%STAND%',
    '%ROUND%',
    '%SURVEY%',
    '%BENEFICIARY%',
    '%EMERGENCY%',
    '%LOA%',
    '%LOAA%',
    '%FLO%',
    '%TALENT%',
    '%ONE%ON%ONE%',
    '%LEW%',
    '%QUALITY%'
  )
order by table_schema, table_name
