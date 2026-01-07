INSERT INTO SSGG.permissions (permission_id,name,display_name,description,category,is_active,created_at,updated_at) VALUES
	 (37,'admin','admin','View admin','Views',1,'2025-12-17 19:55:30',NULL),
	 (1,'read_user','Read User','View user information and search users','User Management',1,'2025-10-06 19:08:22',NULL),
	 (2,'create_user','Create User','Create new user accounts','User Management',1,'2025-10-06 19:08:22',NULL),
	 (3,'update_user','Update User','Modify existing user information','User Management',1,'2025-10-06 19:08:22',NULL),
	 (4,'delete_user','Delete User','Remove user accounts from the system','User Management',1,'2025-10-06 19:08:22',NULL),
	 (5,'reset_password','Reset Password','Reset user passwords','User Management',1,'2025-10-06 19:08:22',NULL),
	 (6,'update_password','Update Password','Change user passwords','User Management',1,'2025-10-06 19:08:22',NULL),
	 (7,'read_member','Read Member','View member information and search members','Member Management',1,'2025-10-06 19:08:22',NULL),
	 (8,'create_member','Create Member','Add new members to the system','Member Management',1,'2025-10-06 19:08:22',NULL),
	 (9,'update_member','Update Member','Modify existing member information','Member Management',1,'2025-10-06 19:08:22',NULL);
INSERT INTO SSGG.permissions (permission_id,name,display_name,description,category,is_active,created_at,updated_at) VALUES
	 (10,'delete_member','Delete Member','Remove members from the system','Member Management',1,'2025-10-06 19:08:22',NULL),
	 (11,'read_member_attendance','Read Member Attendance','View member attendance records','Member Management',1,'2025-10-06 19:08:22',NULL),
	 (12,'read_entity','Read Entity','View entity information and search entities','Entity Management',1,'2025-10-06 19:08:22',NULL),
	 (13,'create_entity','Create Entity','Create new entities (groups, sections, etc.)','Entity Management',1,'2025-10-06 19:08:22',NULL),
	 (14,'update_entity','Update Entity','Modify existing entity information','Entity Management',1,'2025-10-06 19:08:22',NULL),
	 (15,'delete_entity','Delete Entity','Remove entities from the system','Entity Management',1,'2025-10-06 19:08:22',NULL),
	 (16,'assign_entity_members','Assign Entity Members','Add or remove members from entities','Entity Management',1,'2025-10-06 19:08:22',NULL),
	 (17,'update_entity_members_roles','Update Entity Member Roles','Change member roles within entities','Entity Management',1,'2025-10-06 19:08:22',NULL),
	 (18,'transfer_members','Transfer Members','Transfer members between entities','Entity Management',1,'2025-10-06 19:08:22',NULL),
	 (19,'read_event','Read Event','View event information and search events','Event Management',1,'2025-10-06 19:08:22',NULL);
INSERT INTO SSGG.permissions (permission_id,name,display_name,description,category,is_active,created_at,updated_at) VALUES
	 (20,'create_event','Create Event','Create new events and activities','Event Management',1,'2025-10-06 19:08:22',NULL),
	 (21,'update_event','Update Event','Modify existing event information','Event Management',1,'2025-10-06 19:08:22',NULL),
	 (22,'delete_event','Delete Event','Remove events from the system','Event Management',1,'2025-10-06 19:08:22',NULL),
	 (23,'update_event_attendance','Update Event Attendance','Modify event attendance records','Event Management',1,'2025-10-06 19:08:22',NULL),
	 (24,'read_event_attendance','Read Event Attendance','View event attendance records','Event Management',1,'2025-10-06 19:08:22',NULL),
	 (25,'read_lookups','Read Lookups','View system lookup data and configurations','System',1,'2025-10-06 19:08:22',NULL),
	 (26,'read_health_report','Read Full Health Report','View system health report','System',1,'2025-10-06 19:08:22',NULL),
	 (27,'read_entity_attendance','Read Entity Attendance','View aggregated entity attendance','Entity Management',1,'2025-10-06 19:08:22',NULL),
	 (28,'read_role','Read Role','View role','Role Management',1,'2025-10-06 19:08:22',NULL),
	 (29,'create_role','Create Role','Create role','Role Management',1,'2025-10-06 19:08:22',NULL);
INSERT INTO SSGG.permissions (permission_id,name,display_name,description,category,is_active,created_at,updated_at) VALUES
	 (30,'update_role','Update Role','Update role','Role Management',1,'2025-10-06 19:08:22',NULL),
	 (31,'delete_role','Delete Role','Delete role','Role Management',1,'2025-10-06 19:08:22',NULL),
	 (32,'update_role_permissions','Update Role Permissions','Update Role Permissions','Role Management',1,'2025-10-06 19:08:22',NULL),
	 (33,'read_permission','Read Permission','View Permission','Permission Management',1,'2025-10-06 19:08:22',NULL),
	 (34,'create_permission','Create Permission','Create Permission','Permission Management',1,'2025-10-06 19:08:22',NULL),
	 (35,'update_permission','Update Permission','Update Permission','Permission Management',1,'2025-10-06 19:08:22',NULL),
	 (36,'delete_permission','Delete Permission','Delete Permission','Permission Management',1,'2025-10-06 19:08:22',NULL),
	 (37,'execute_query','Execute Query','Execute Query','Visualizer',1,'2025-10-06 19:08:22',NULL),
	 (38,'read_ddl','Read DDL','Read DDL','Visualizer',1,'2025-10-06 19:08:22',NULL);
