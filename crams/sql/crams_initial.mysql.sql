-- noinspection SqlDialectInspectionForFile
-- noinspection SqlNoDataSourceInspectionForFile
INSERT INTO crams_fundingbody (id, `name`, email) VALUES (1, 'NeCTAR', 'crams@rc.test.nectar.org.au');
INSERT INTO crams_fundingbody (id, `name`, email) VALUES (2, 'VicNode', 'crams@rc.test.nectar.org.au');
INSERT INTO crams_fundingbody (id, `name`, email) VALUES (3, 'Intersect', 'crams@rc.test.nectar.org.au');
INSERT INTO crams_fundingbody (id, `name`, email) VALUES (4, 'UoM', 'crams@rc.test.nectar.org.au');
INSERT INTO crams_fundingbody (id, `name`, email) VALUES (5, 'Monash', 'crams@rc.test.nectar.org.au');
INSERT INTO crams_fundingbody (id, `name`, email) VALUES (6, 'NCI', 'crams@rc.test.nectar.org.au');
INSERT INTO crams_fundingbody (id, `name`, email) VALUES (7, 'Pawsey', 'crams@rc.test.nectar.org.au');
INSERT INTO crams_fundingbody (id, `name`, email) VALUES (8, 'QCIF', 'crams@rc.test.nectar.org.au');
INSERT INTO crams_fundingbody (id, `name`, email) VALUES (9, 'eRSA', 'crams@rc.test.nectar.org.au');
INSERT INTO crams_fundingbody (id, `name`, email) VALUES (10, 'TPAC', 'crams@rc.test.nectar.org.au');

INSERT INTO crams_fundingscheme (id, funding_scheme, funding_body_id) VALUES (1, 'NeCTAR National Merit', 1);
INSERT INTO crams_fundingscheme (id, funding_scheme, funding_body_id) VALUES (2, 'NeCTAR Monash Priority Share', 5);
INSERT INTO crams_fundingscheme (id, funding_scheme, funding_body_id) VALUES (3, 'NeCTAR Instersect Priority Share', 3);
INSERT INTO crams_fundingscheme (id, funding_scheme, funding_body_id) VALUES (4, 'NeCTAR UoM Priority Share', 4);
INSERT INTO crams_fundingscheme (id, funding_scheme, funding_body_id) VALUES (5, 'NeCTAR TPAC Priority Share', 10);
INSERT INTO crams_fundingscheme (id, funding_scheme, funding_body_id) VALUES (6, 'NeCTAR NCI Priority Share', 6);
INSERT INTO crams_fundingscheme (id, funding_scheme, funding_body_id) VALUES (7, 'NeCTAR Pawsey Priority Share', 7);
INSERT INTO crams_fundingscheme (id, funding_scheme, funding_body_id) VALUES (8, 'NeCTAR QCIF Priority Share', 8);
INSERT INTO crams_fundingscheme (id, funding_scheme, funding_body_id) VALUES (9, 'NeCTAR eRSA Priority Share', 9);


INSERT INTO crams_granttype (id, description) VALUES (1, 'ARC');
INSERT INTO crams_granttype (id, description) VALUES (2, 'NHMRC');
INSERT INTO crams_granttype (id, description) VALUES (3, 'Australian Competitive Grant');
INSERT INTO crams_granttype (id, description) VALUES (4, 'Other Australian Government Grant');
INSERT INTO crams_granttype (id, description) VALUES (5, 'Other external funding');
INSERT INTO crams_granttype (id, description) VALUES (6, 'Institutional funding');
INSERT INTO crams_granttype (id, description) VALUES (7, 'Industry funding');

INSERT INTO crams_contactrole (id, `name`) VALUES (1, 'Applicant');
INSERT INTO crams_contactrole (id, `name`) VALUES (2, 'Chief Investigator');

INSERT INTO crams_projectidsystem (id, system) VALUES (1, 'NeCTAR');
INSERT INTO crams_projectidsystem (id, system) VALUES(2, 'NeCTAR_UUID');
INSERT INTO crams_projectidsystem (id, system) VALUES(3, 'NeCTAR_Created_By');
INSERT INTO crams_projectidsystem (id, system) VALUES(4, 'NeCTAR_DB_Id');

INSERT INTO crams_provider (id, `name`, active, crams_user_id, created_by_id, creation_ts, description, last_modified_ts, start_date, updated_by_id) VALUES (1, 'Intersect', true, NULL, NULL, '2016-02-01 09:42:48.669521', NULL, '2016-02-01 09:42:53.378836', '2016-02-01', NULL);
INSERT INTO crams_provider (id, `name`, active, crams_user_id, created_by_id, creation_ts, description, last_modified_ts, start_date, updated_by_id) VALUES (2, 'UoM', true, NULL, NULL, '2016-02-01 09:42:48.669521', NULL, '2016-02-01 09:42:53.378836', '2016-02-01', NULL);
INSERT INTO crams_provider (id, `name`, active, crams_user_id, created_by_id, creation_ts, description, last_modified_ts, start_date, updated_by_id) VALUES (3, 'Monash', true, NULL, NULL, '2016-02-01 09:42:48.669521', NULL, '2016-02-01 09:42:53.378836', '2016-02-01', NULL);
INSERT INTO crams_provider (id, `name`, active, crams_user_id, created_by_id, creation_ts, description, last_modified_ts, start_date, updated_by_id) VALUES (4, 'NCI', true, NULL, NULL, '2016-02-01 09:42:48.669521', NULL, '2016-02-01 09:42:53.378836', '2016-02-01', NULL);
INSERT INTO crams_provider (id, `name`, active, crams_user_id, created_by_id, creation_ts, description, last_modified_ts, start_date, updated_by_id) VALUES (5, 'Pawsey', true, NULL, NULL, '2016-02-01 09:42:48.669521', NULL, '2016-02-01 09:42:53.378836', '2016-02-01', NULL);
INSERT INTO crams_provider (id, `name`, active, crams_user_id, created_by_id, creation_ts, description, last_modified_ts, start_date, updated_by_id) VALUES (6, 'QCIF', true, NULL, NULL, '2016-02-01 09:42:48.669521', NULL, '2016-02-01 09:42:53.378836', '2016-02-01', NULL);
INSERT INTO crams_provider (id, `name`, active, crams_user_id, created_by_id, creation_ts, description, last_modified_ts, start_date, updated_by_id) VALUES (7, 'eRSA', true, NULL, NULL, '2016-02-01 09:42:48.669521', NULL, '2016-02-01 09:42:53.378836', '2016-02-01', NULL);
INSERT INTO crams_provider (id, `name`, active, crams_user_id, created_by_id, creation_ts, description, last_modified_ts, start_date, updated_by_id) VALUES (8, 'TPAC', true, NULL, NULL, '2016-02-01 09:42:48.669521', NULL, '2016-02-01 09:42:53.378836', '2016-02-01', NULL);
INSERT INTO crams_provider (id, `name`, active, crams_user_id, created_by_id, creation_ts, description, last_modified_ts, start_date, updated_by_id) VALUES (9, 'NeCTAR', true, NULL, NULL, '2016-02-01 09:42:48.669521', '', '2016-02-01 09:42:48.669521', '2016-02-01', NULL);

INSERT INTO crams_requeststatus (id, code, status) VALUES (1, 'N', 'New');
INSERT INTO crams_requeststatus (id, code, status) VALUES (2, 'E', 'Submitted');
INSERT INTO crams_requeststatus (id, code, status) VALUES (3, 'A', 'Approved');
INSERT INTO crams_requeststatus (id, code, status) VALUES (4, 'P', 'Provisioned');
INSERT INTO crams_requeststatus (id, code, status) VALUES (5, 'X', 'Update/Extension Requested');
INSERT INTO crams_requeststatus (id, code, status) VALUES (6, 'R', 'Declined');
INSERT INTO crams_requeststatus (id, code, status) VALUES (7, 'J', 'Update/Extension Declined');
INSERT INTO crams_requeststatus (id, code, status) VALUES (8, 'L', 'Legacy Submission');
INSERT INTO crams_requeststatus (id, code, status) VALUES (9, 'M', 'Legacy Approved');
INSERT INTO crams_requeststatus (id, code, status) VALUES (10, 'O', 'Legacy Rejected');

INSERT INTO crams_storagetype (id, storage_type) VALUES (1, 'Volume');
INSERT INTO crams_storagetype (id, storage_type) VALUES (2, 'Object');
INSERT INTO crams_storagetype (id, storage_type) VALUES (3, 'File System');

INSERT INTO crams_zone(id, `name`, description) VALUES (1, 'intersect', 'Intersect (NSW)');
INSERT INTO crams_zone(id, `name`, description) VALUES (2, 'melbourne', 'Melbourne');
INSERT INTO crams_zone(id, `name`, description) VALUES (3, 'monash', 'Monash (VIC)');
INSERT INTO crams_zone(id, `name`, description) VALUES (4, 'NCI', 'NCI (ACT)');
INSERT INTO crams_zone(id, `name`, description) VALUES (5, 'pawsey', 'Pawsey (WA)');
INSERT INTO crams_zone(id, `name`, description) VALUES (6, 'QRIScloud', 'Queensland');
INSERT INTO crams_zone(id, `name`, description) VALUES (7, 'sa', 'South Australia');
INSERT INTO crams_zone(id, `name`, description) VALUES (8, 'tasmania', 'Tasmania');
INSERT INTO crams_zone(id, `name`, description) VALUES (9, 'nectar', 'NeCTAR');

INSERT INTO crams_computeproduct(id, `name`, funding_body_id, provider_id) VALUES (1, 'NeCTAR Compute', 1, 9);

INSERT INTO crams_storageproduct (id, `name`, funding_body_id, provider_id, storage_type_id, zone_id) VALUES (1, 'Volume (Intersect)', 1, 9, 1, 1);
INSERT INTO crams_storageproduct (id, `name`, funding_body_id, provider_id, storage_type_id, zone_id) VALUES (2, 'Volume (UoM)', 1, 9, 1, 2);
INSERT INTO crams_storageproduct (id, `name`, funding_body_id, provider_id, storage_type_id, zone_id) VALUES (3, 'Volume (Monash)', 1, 9, 1, 3);
INSERT INTO crams_storageproduct (id, `name`, funding_body_id, provider_id, storage_type_id, zone_id) VALUES (4, 'Volume (NCI)', 1, 9, 1, 4);
INSERT INTO crams_storageproduct (id, `name`, funding_body_id, provider_id, storage_type_id, zone_id) VALUES (5, 'Volume (Pawsey)', 1, 9, 1, 5);
INSERT INTO crams_storageproduct (id, `name`, funding_body_id, provider_id, storage_type_id, zone_id) VALUES (6, 'Volume (QCIF)', 1, 9, 1, 6);
INSERT INTO crams_storageproduct (id, `name`, funding_body_id, provider_id, storage_type_id, zone_id) VALUES (7, 'Volume (eRSA)', 1, 9, 1, 7);
INSERT INTO crams_storageproduct (id, `name`, funding_body_id, provider_id, storage_type_id, zone_id) VALUES (8, 'Volume (TPAC)', 1, 9, 1, 8);
INSERT INTO crams_storageproduct (id, `name`, funding_body_id, provider_id, storage_type_id, zone_id) VALUES (9, 'Volume (NeCTAR)', 1, 9, 1, 9);
INSERT INTO crams_storageproduct (id, `name`, funding_body_id, provider_id, storage_type_id, zone_id) VALUES (10, 'Object (NeCTAR)', 1, 9, 2, 9);

INSERT INTO crams_duration (id, duration, duration_label) VALUES (1, 1, '1-month');
INSERT INTO crams_duration (id, duration, duration_label) VALUES (2, 3, '3-months');
INSERT INTO crams_duration (id, duration, duration_label) VALUES (3, 6, '6-months');
INSERT INTO crams_duration (id, duration, duration_label) VALUES (4, 12, '12-months');

INSERT INTO crams_allocationhome(id, code, description) VALUES (1, 'national', 'National/Unassigned');
INSERT INTO crams_allocationhome(id, code, description) VALUES (2, 'nci', 'Australian Capital Territory (NCI)');
INSERT INTO crams_allocationhome(id, code, description) VALUES (3, 'intersect', 'New South Wales (Intersect)');
INSERT INTO crams_allocationhome(id, code, description) VALUES (4, 'qcif', 'Queensland (QCIF)');
INSERT INTO crams_allocationhome(id, code, description) VALUES (5, 'ersa', 'South Australia (eRSA)');
INSERT INTO crams_allocationhome(id, code, description) VALUES (6, 'tpac', 'Tasmania (TPAC)');
INSERT INTO crams_allocationhome(id, code, description) VALUES (7, 'uom', 'Victoria (Melbourne)');
INSERT INTO crams_allocationhome(id, code, description) VALUES (8, 'monash', 'Victoria (Monash)');
INSERT INTO crams_allocationhome(id, code, description) VALUES (9, 'pawsey', 'Western Australia (Pawsey)');

INSERT INTO crams_question (id, `key`, question_type, question) VALUES (1, 'duration', 'nectar-general-request', 'Estimated duration');
INSERT INTO crams_question (id, `key`, question_type, question) VALUES (2, 'ptconversion', 'nectar-general-request', 'Convert project trial');
INSERT INTO crams_question (id, `key`, question_type, question) VALUES (3, 'researchcase', 'nectar-usage information-request', 'Research use case');
INSERT INTO crams_question (id, `key`, question_type, question) VALUES (4, 'usagepattern', 'nectar-usage information-request', 'Instance, object storage and volume storage usage patterns');
INSERT INTO crams_question (id, `key`, question_type, question) VALUES (5, 'homenode', 'nectar-usage information-request', 'Allocation home');
INSERT INTO crams_question (id, `key`, question_type, question) VALUES (6, 'homerequirements', 'nectar-usage information-request', 'Additional location requirements');
INSERT INTO crams_question (id, `key`, question_type, question) VALUES (7, 'estimatedusers', 'nectar-usage information-request', 'Estimated number of users');
INSERT INTO crams_question (id, `key`, question_type, question) VALUES (8, 'additionalresearchers', 'nectar-chief investigator-project', 'Additional Researchers');
INSERT INTO crams_question (id, `key`, question_type, question) VALUES (9, 'nectarvls', 'nectar-research grant information-project', 'List any NeCTAR virtual Laboratories supporting this request');
INSERT INTO crams_question (id, `key`, question_type, question) VALUES (10, 'ncris', 'nectar-research grant information-project', 'List NCRIS capabilities supporting this request');
INSERT INTO crams_question (id, `key`, question_type, question) VALUES (11, 'n_approver_email', 'nectar-general-request', 'Approver email');
INSERT INTO crams_question (id, `key`, question_type, question) VALUES (12, 'n_volume_storage_zone', 'nectar-storage-request', 'Volume Storage Zone');
INSERT INTO crams_question (id, `key`, question_type, question) VALUES (13, 'n_object_storage_zone', 'nectar-storage-request', 'Object Storage Zone');
INSERT INTO crams_question (id, `key`, question_type, question) VALUES (14, 'n_primary_instance_type', 'nectar-compute-request', 'Primary Instance Type');
