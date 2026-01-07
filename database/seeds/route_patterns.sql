INSERT INTO SSGG.route_patterns (`method`,path_pattern,name,description,is_active,created_at,updated_at,route_pattern_id) VALUES
	 ('GET','/users','search_users','Search and list users',1,NULL,NULL,1),
	 ('POST','/users','create_user','Create a new user',1,NULL,NULL,2),
	 ('GET','/users/{user_id}','get_user','Get specific user by ID',1,NULL,NULL,3),
	 ('PATCH','/users/{user_id}','update_user','Update user information',1,NULL,NULL,4),
	 ('DELETE','/users/{user_id}','delete_user','Delete a user',1,NULL,NULL,5),
	 ('POST','/users/{user_id}/reset-password','reset_user_password','Reset user password',1,NULL,NULL,6),
	 ('PATCH','/users/{user_id}/password','update_user_password','Update user password',1,NULL,NULL,7),
	 ('GET','/members','search_members','Search and list members',1,NULL,NULL,8),
	 ('POST','/members','create_member','Create a new member',1,NULL,NULL,9),
	 ('GET','/members/{member_id}','get_member','Get specific member by ID',1,NULL,NULL,10);
INSERT INTO SSGG.route_patterns (`method`,path_pattern,name,description,is_active,created_at,updated_at,route_pattern_id) VALUES
	 ('PUT','/members/{member_id}','update_member','Update member information',1,NULL,NULL,11),
	 ('DELETE','/members/{member_id}','delete_member','Delete a member',1,NULL,NULL,12),
	 ('GET','/members/{member_id}/attendance','get_member_attendance','Get member attendance records',1,NULL,NULL,13),
	 ('GET','/entities','search_entities','Search and list entities',1,NULL,NULL,14),
	 ('POST','/entities','create_entity','Create a new entity',1,NULL,NULL,15),
	 ('GET','/entities/{entity_id}','get_entity','Get specific entity by ID',1,NULL,NULL,16),
	 ('PUT','/entities/{entity_id}','update_entity','Update entity information',1,NULL,NULL,17),
	 ('DELETE','/entities/{entity_id}','delete_entity','Delete an entity',1,NULL,NULL,18),
	 ('POST','/entities/{entity_id}/members','assign_entity_members','Assign members to entity',1,NULL,NULL,19),
	 ('DELETE','/entities/{entity_id}/members/{member_id}','remove_entity_member','Remove member from entity',1,NULL,NULL,20);
INSERT INTO SSGG.route_patterns (`method`,path_pattern,name,description,is_active,created_at,updated_at,route_pattern_id) VALUES
	 ('POST','/entities/{entity_id}/members/roles','update_entity_member_roles','Update member roles in entity',1,NULL,NULL,21),
	 ('POST','/entities/transfer','transfer_members','Transfer members between entities',1,NULL,NULL,22),
	 ('GET','/events','search_events','Search and list events',1,NULL,NULL,23),
	 ('POST','/events','create_event','Create a new event',1,NULL,NULL,24),
	 ('GET','/events/{event_id}','get_event','Get specific event by ID',1,NULL,NULL,25),
	 ('PUT','/events/{event_id}','update_event','Update event information',1,NULL,NULL,26),
	 ('DELETE','/events/{event_id}','delete_event','Delete an event',1,NULL,NULL,27),
	 ('PUT','/events/{event_id}/attendance','update_event_attendance','Update event attendance',1,NULL,NULL,28),
	 ('GET','/events/{event_id}/attendance','get_event_attendance','Get event attendance records',1,NULL,NULL,29),
	 ('GET','/lookups','read_lookups','Read system lookup data',1,NULL,NULL,30);
INSERT INTO SSGG.route_patterns (`method`,path_pattern,name,description,is_active,created_at,updated_at,route_pattern_id) VALUES
	 ('GET','/health/report','read_health_report','Read detailed health report',1,NULL,NULL,31),
	 ('GET','/entities/{entity_id}/attendance','get_entity_attendance','Get aggregated entity attendance',1,NULL,NULL,32),
	 ('GET','/roles/{role_id}','get_role','Get role by ID',1,NULL,NULL,33),
	 ('GET','/roles','search_roles','Search and list roles',1,NULL,NULL,34),
	 ('POST','/roles','create_roles','Create roles',1,NULL,NULL,35),
	 ('PUT','/roles/{role_id}','update_role','Update role by ID',1,NULL,NULL,36),
	 ('DELETE','/roles/{role_id}','delete_role','Delete role by ID',1,NULL,NULL,37),
	 ('PUT','/roles/{role_id}/permissions','update_role_permissions','Update role permissions',1,NULL,NULL,38),
	 ('GET','/permissions','search_permissions','Search and list permissions',1,NULL,NULL,39),
	 ('POST','/permissions','create_permissions','Create permissions',1,NULL,NULL,40);
INSERT INTO SSGG.route_patterns (`method`,path_pattern,name,description,is_active,created_at,updated_at,route_pattern_id) VALUES
	 ('PUT','/permissions/{permission_id}','update_permission','Update permission by ID',1,NULL,NULL,41),
	 ('DELETE','/permissions/{permission_id}','delete_permission','Delete permission by ID',1,NULL,NULL,42),
	 ('GET','/permissions/{permission_id}','get_permission','Get permission by ID',1,NULL,NULL,43),
	 ('POST','/visualizer','execute_query','Execute Visualizer query',1,NULL,NULL,44),
	 ('GET','/visualizer/ddl','get_ddl','Get Database DDL',1,NULL,NULL,45);
