-- noinspection SqlDialectInspectionForFile
-- noinspection SqlNoDataSourceInspectionForFile

-- Update NeCTAR notification templates
-- Status - New
insert into crams_notificationtemplate(template_file_path, funding_body_id, request_status_id) values('notification/nectar/submit.html',1,1);
-- Status - Submitted
insert into crams_notificationtemplate(template_file_path, funding_body_id, request_status_id) values('notification/nectar/submit.html',1,2);
-- Status - Approved
insert into crams_notificationtemplate(template_file_path, funding_body_id, request_status_id) values('notification/nectar/approve.html',1,3);
-- Status - Provisioned
insert into crams_notificationtemplate(template_file_path, funding_body_id, request_status_id) values('notification/nectar/provision.html',1,4);
-- Status - Update/Extension Requested
insert into crams_notificationtemplate(template_file_path, funding_body_id, request_status_id) values('notification/nectar/submit.html',1,5);
-- Status - Declined
insert into crams_notificationtemplate(template_file_path, funding_body_id, request_status_id) values('notification/nectar/reject.html',1,6);
-- Status - Update/Extension Declined
insert into crams_notificationtemplate(template_file_path, funding_body_id, request_status_id) values('notification/nectar/reject.html',1,7);
-- Status - Legacy Submission
-- insert into crams_notificationtemplate(template_file_path, funding_body_id, request_status_id) values('notification/nectar/submit.html',1,8);
-- Status - Legacy Approved
-- insert into crams_notificationtemplate(template_file_path, funding_body_id, request_status_id) values('notification/nectar/submit.html',1,9);
-- Status - Legacy Rejected
-- insert into crams_notificationtemplate(template_file_path, funding_body_id, request_status_id) values('notification/nectar/submit.html',1,10);
select * from crams_notificationtemplate;
