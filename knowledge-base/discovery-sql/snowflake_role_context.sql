select
  current_role() as active_role,
  current_secondary_roles() as active_secondary_roles,
  current_database() as active_database,
  current_schema() as active_schema
