# coding=utf-8
"""
  Sample Data
"""
__author__ = 'rafi m feroze'


def get_base_nectar_project_data(user_id, contact_obj):
    """
        Nectar Project Data
    :param user_id:
    :param contact_obj:
    :return:
    """
    return {"title": "Creating allocation request testing1",
            "description": "Creating allocation request testing1",
            "project_question_responses": [
                {"question_response": "Tom, Jack",
                 "question": {
                     "key": "additionalresearchers"
                 }
                 },
                {
                    "question_response": "nectar supporting",
                    "question": {"key": "nectarvls"}
                },
                {
                    "question_response": "ncris supporting",
                    "question": {"key": "ncris"}
                }
            ],
            "institutions": [{"institution": "Monash"}],
            "publications": [{"reference": "pub1"}],
            "grants": [{"grant_type": {"id": 1},
                        "funding_body_and_scheme": "arc tests funding",
                        "grant_id": "arc-001",
                        "start_year": 2014,
                        "total_funding": 200}],
            "project_ids": [{"identifier": "allocation_request_testing1",
                             "system": {"id": 1,
                                        "system": "NeCTAR"},
                             "type": "R"}],
            "project_contacts": [{"contact": {"id": contact_obj.id,
                                              "email": contact_obj.email},
                                  "contact_role": {"id": 2}}],
            "domains": [{"percentage": 100,
                         "for_code": {"id": 1}}],
            "requests": [
                {
                    "compute_requests": [{
                        "instances": 21,
                        "approved_instances": 12,
                        "cores": 32,
                        "approved_cores": 22,
                        "core_hours": 744,
                        "approved_core_hours": 744,
                        "compute_product": {"id": 1},
                        "compute_question_responses": []
                    }],
                    "storage_requests": [
                        {"quota": 22,
                         "approved_quota": 12,
                         "storage_product": {"id": 3,
                                             "name": "Nectar Volume (Monash)"},

                         "storage_question_responses": []
                         }
                    ],
                    "request_question_responses": [
                        {"question_response": "1",
                         "question": {"key": "duration"}},
                        {"question_response": "False",
                         "question": {"key": "ptconversion"}},
                        {
                            "question_response": "Some Question Response",
                            "question": {"key": "researchcase"}},
                        {
                            "question_response": "Creating allocation request "
                                                 "testing1 patterns",
                            "question": {"key": "usagepattern"}},
                        {"question_response": "Monash",
                         "question": {"key": "homenode"}},
                        {"question_response": "Monash Node",
                         "question": {"key": "homerequirements"}},
                        {"question_response": 20000,
                         "question": {"key": "estimatedusers"}
                         }],
                    "request_status": {"id": 1},
                    "funding_scheme": {"id": 1},
                    "start_date": "2015-11-25",
                    "end_date": "2015-12-25",
                    "created_by": {"id": user_id},
                    "updated_by": {"id": user_id},
                    "approval_notes": ""
                }
            ]}


def get_project_only_no_request_data(user_id, contact_obj):
    """
        Project only data
    :param user_id:
    :param contact_obj:
    :return:
    """
    return {
        "title": "Creating project testing1",
        "description": "Creating project testing1",
        "project_question_responses": [
            {
                "question_response": "Tom, Jack",
                "question": {
                    "key": "additionalresearchers"
                }
            },
            {
                "question_response": "nectar supporting",
                "question": {
                    "key": "nectarvls"
                }
            },
            {
                "question_response": "ncris supporting",
                "question": {
                    "key": "ncris"
                }
            }
        ],
        "institutions": [
            {
                "institution": "Monash"
            }
        ],
        "publications": [
            {
                "reference": "pub1"
            }
        ],
        "grants": [
            {
                "grant_type": {
                    "id": 1
                },
                "funding_body_and_scheme": "arc tests funding",
                "grant_id": "arc-001",
                "start_year": 2014,
                "total_funding": 200
            }
        ],
        "project_ids": [
            {
                "identifier": "creating_project_testing1",
                "system": {
                    "id": 1,
                    "system": "NeCTAR"
                },
                "type": "R"
            }
        ],
        "project_contacts": [
            {
                "contact": {
                    "id": contact_obj.id,
                    "email": contact_obj.email
                },
                "contact_role": {
                    "id": 2
                }
            }
        ],
        "domains": [
            {
                "percentage": 100,
                "for_code": {
                    "id": 1
                }
            }
        ],
        "created_by": {
            "id": user_id
        },
        "updated_by": {
            "id": user_id
        }
    }


def get_vicnode_test_data(user_id, contact_obj):
    """
        Vicnode Test Data
    :param user_id:
    :param contact_obj:
    :return:
    """
    return {
        "title": "Test Collection",
        "description": "Test Collection Description",
        "project_question_responses": [

        ],
        "institutions": [

        ],
        "publications": [

        ],
        "grants": [

        ],
        "project_ids": [
            {
                "identifier": "Test Collection",
                "system": {
                    "id": 2
                }
            }
        ],
        "project_contacts": [
            {
                "contact": {
                    "id": contact_obj.id,
                    "email": contact_obj.email
                },
                "contact_role": {
                    "id": 2
                }
            }
        ],
        "domains": [
            {
                "percentage": 100,
                "for_code": {
                    "id": 186
                }
            }
        ],
        "requests": [
            {
                "compute_requests": [

                ],
                "storage_requests": [
                    {
                        "quota": 120,
                        "approved_quota": 120,
                        "storage_product": {
                            "id": 15,
                            "name": "VicNode Vault (Monash)"
                        },
                        "storage_question_responses": [
                            {
                                "question_response": 10,
                                "question": {
                                    "key": "vn_current_size"
                                }
                            }
                        ]
                    }
                ],
                "request_question_responses": [
                    {
                        "question_response": "Yes",
                        "question": {
                            "key": "vn_authorization"
                        }
                    },
                    {
                        "question_response": "On a PC",
                        "question": {
                            "key": "vn_data_migration_src"
                        }
                    },
                    {
                        "question_response": "Yes",
                        "question": {
                            "key": "vn_data_migration_assistance"
                        }
                    },
                    {
                        "question_response": "via a PC",
                        "question": {
                            "key": "vn_current_access_method"
                        }
                    },
                    {
                        "question_response": "Direct access via a PC",
                        "question": {
                            "key": "vn_preferred_access_method"
                        }
                    },
                    {
                        "question_response": ".txt",
                        "question": {
                            "key": "vn_data_format"
                        }
                    },
                    {
                        "question_response": "Yes",
                        "question": {
                            "key": "vn_only_copy"
                        }
                    },
                    {
                        "question_response": "Irreplaceable",
                        "question": {
                            "key": "vn_can_be_regenerated"
                        }
                    },
                    {
                        "question_response": "Lose job.",
                        "question": {
                            "key": "vn_loss_impact"
                        }
                    }
                ],
                "request_status": {
                    "id": 1
                },
                "funding_scheme": {
                    "id": 2
                },
                "start_date": "2016-01-01",
                "end_date": "2017-01-01",
                "created_by": {
                    "id": user_id
                },
                "updated_by": {
                    "id": user_id
                },
                "approval_notes":
                    "",

                "paent_request": None

            }
        ]
    }
