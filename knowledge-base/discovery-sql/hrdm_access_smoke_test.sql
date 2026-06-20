select
  current_account() as active_account,
  current_role() as active_role,
  current_warehouse() as active_warehouse,
  current_database() as active_database,
  current_schema() as active_schema;
