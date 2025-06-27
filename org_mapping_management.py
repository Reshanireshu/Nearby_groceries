from flask_restful import Resource, reqparse
from flask import request
from sqlalchemy import and_, select, func, or_, Integer, cast, update, DateTime, literal
from sqlalchemy import Table, MetaData, and_, select, func, or_, text, not_
from flask_restful import Resource
from db import db, Base
from common_helper.common_helper import CommonHelper
from helper.org_process_mapping_helper import OrgProcessMappingHelper
from constants.request_parser import keys_to_remove_org_proc_mapping
from helper.org_hierarchy_mapping_helper import OrgHierarchyMappingHelper
from datetime import date, datetime
from fuzzywuzzy import fuzz
import re
from collections import defaultdict
import pandas as pd
from schemas.org_history_schema import OrgHistorySchema
from authentication import (
    user_or_admin_authentication_required,
    get_user_from_token,
)


class OrganizationMappingManagement(Resource):

    def __init__(self):
        super().__init__()
        self.common_helper = CommonHelper()
        self.org_process_mapping_helper = OrgProcessMappingHelper()
        self.org_mapping_helper = OrgHierarchyMappingHelper()

    @user_or_admin_authentication_required
    def get(self):
        try:
            # Query for distinct record IDs from Org Hierarchy Mapping
            distinct_mapping_id = (
                self.org_process_mapping_helper._get_distinct_mapping_ids(
                    request.args.get("source_system_cd"),
                    request.args.get("process_area"),
                )
            )
            merged_records = []

            org_process_area_records = (
                self.org_process_mapping_helper._get_org_process_area_records(
                    distinct_mapping_id["mapping_id"]
                )
            )

            for each_process_area_record in org_process_area_records:

                org_record = self.org_process_mapping_helper._get_org_record(
                    each_process_area_record["org_id"]
                )
                if org_record:
                    merged_records.append(
                        self.org_process_mapping_helper._merge_records(
                            org_record, each_process_area_record
                        )
                    )
                # else:
                #     merged_records.append(
                #         self.org_process_mapping_helper._merge_records(
                #             empty_org_record, each_process_area_record
                #         )
                #     )
            if not len(merged_records):
                return {
                    "message": "The provided process area doesn't have any mapping combination."
                }, 404
            deduplicated_records = (
                self.common_helper.remove_unnecessary_keys_in_list_of_dict(
                    merged_records, keys_to_remove_org_proc_mapping
                )
            )

            return (
                self.org_process_mapping_helper.replace_org_name_by_org_id(
                    deduplicated_records
                ),
                200,
            )

        except Exception as e:
            return {
                "message": "Something went wrong",
                "data": None,
                "error": str(e),
            }, 500


class MappingComboManagement(Resource):

    def __init__(self):
        super().__init__()
        self.common_helper = CommonHelper()
        self.org_process_mapping_helper = OrgProcessMappingHelper()

    @user_or_admin_authentication_required
    def get(self):
        try:
            # Retrieve query parameters for process area and source system code
            process_area = request.args.get("process_area")
            source_system_cd = request.args.get("source_system_cd")

            # Query for distinct record IDs from Org Hierarchy Mapping with both parameters
            distinct_mapping_id = (
                self.org_process_mapping_helper._get_mapping_field_combo(
                    process_area, source_system_cd
                )
            )
            if not distinct_mapping_id:
                return {
                    "message": "The provided process area and source system code don't have any mapping combination."
                }, 404
            else:
                return distinct_mapping_id, 200
        except Exception as e:
            return {
                "message": "Something went wrong",
                "data": None,
                "error": str(e),
            }, 500


class OrgHierarchyAPI(Resource):

    def __init__(self):
        # Initialize the table reference in the constructor
        self.org_hierarchy = Base.metadata.tables["db_nxtgen.Org_Hierarchy"]
        self.org_hier_mapping_table = Base.metadata.tables["db_nxtgen.Org_Hier_Mapping"]
        self.kpi_input = Base.metadata.tables["db_nxtgen.Kpi_Input"]
        self.org_process_mapping_helper = OrgProcessMappingHelper()
        self.org_hier_mapping_helper = OrgHierarchyMappingHelper()

    @user_or_admin_authentication_required
    def get(self):
        """
        GET API for listing organization hierarchy.
        :param: org_id (optional filter)
        :param: level1 (optional filter)
        :param: status (optional filter)
        :return: list of hierarchy data
        """
        try:
            sub_base_query = (
                db.session.query(
                    self.org_hierarchy,
                    func.row_number()
                    .over(
                        partition_by=self.org_hierarchy.c.org_id,
                        order_by=self.org_hierarchy.c.record_id.desc(),
                    )
                    .label("row_number"),
                )
                .filter(
                    and_(
                        or_(
                            self.org_hierarchy.c.rec_end_date.is_(None),
                            self.org_hierarchy.c.rec_end_date
                            == "9999-01-01 00:00:00.000",
                        ),
                        self.org_hierarchy.c.is_deleted == 0,
                    )
                )
                .filter(
                    or_(
                        self.org_hierarchy.c.is_leaf_node == True,
                        self.org_hierarchy.c.is_leaf_node.is_(None),
                    )
                )
                .subquery()
            )

            bquery = (
                db.session.query(sub_base_query)
                .filter(
                    sub_base_query.c.hier_type
                    == request.args.get("hier_type", "Standard")
                )
                .filter(
                    or_(
                        and_(
                            sub_base_query.c.row_number == 1,
                            cast(sub_base_query.c.record_cut_over_date, DateTime)
                            > func.current_date(),
                        ),
                        sub_base_query.c.record_cut_over_date.is_(None),
                    )
                )
                .order_by(sub_base_query.c.org_level.asc())
            )
            (
                construct_org_name_and_org_id,
                construct_org_name_and_parent_pending_status,
            ) = self.org_process_mapping_helper.construct_org_name_and_org_id()

            # Fetch the organization hierarchy data
            org_hierarchy_data = bquery.all()
            if not org_hierarchy_data:
                return {"message": "Organization Hierarchy Not Found"}, 404

            # Initialize response list
            response = []
            # Map org_id to org_name for lookup
            org_id_to_name = {}

            # Process each record in the query result
            for record in org_hierarchy_data:
                # List of levels to check
                levels = [
                    record.level1,
                    record.level2,
                    record.level3,
                    record.level4,
                    record.level5,
                    record.level6,
                    record.level7,
                ]

                # Check if any level has 'Pending' as its value in the dictionary
                # is_parentpending = any(
                #     construct_org_name_and_parent_pending_status.get(level) == True
                #     for level in levels
                # )
                is_parentpending = (record.is_parent_pending,)
                created_date = (record.created_date,)
                updated_date = record.updated_date

                # Calculate approval status
                approval_status = self.org_hier_mapping_helper.calculate_status(
                    record.approval_1_status, record.approval_2_status
                )

                # Add the org_id and org_name to the lookup mapping
                org_id_to_name[record.org_id] = record.org_name

                # Create a dictionary for the current record
                org_hierarchy_table_data = {
                    "org_id": record.org_id,
                    "record_id": record.record_id,
                    "org_name": record.org_name,
                    "hier_type": record.hier_type,
                    "org_level": record.org_level,
                    "level1": record.level1 or "",
                    "level1_org_id": (
                        construct_org_name_and_org_id.get(record.level1, None)
                        if record.level1
                        else None
                    ),
                    "level2": record.level2 or "",
                    "level2_org_id": (
                        construct_org_name_and_org_id.get(record.level2, None)
                        if record.level2
                        else None
                    ),
                    "level3": record.level3 or "",
                    "level3_org_id": (
                        construct_org_name_and_org_id.get(record.level3, None)
                        if record.level3
                        else None
                    ),
                    "level4": record.level4 or "",
                    "level4_org_id": (
                        construct_org_name_and_org_id.get(record.level4, None)
                        if record.level4
                        else None
                    ),
                    "level5": record.level5 or "",
                    "level5_org_id": (
                        construct_org_name_and_org_id.get(record.level5, None)
                        if record.level5
                        else None
                    ),
                    "level6": record.level6 or "",
                    "level6_org_id": (
                        construct_org_name_and_org_id.get(record.level6, None)
                        if record.level6
                        else None
                    ),
                    "level7": record.level7 or "",
                    "level7_org_id": (
                        construct_org_name_and_org_id.get(record.level7, None)
                        if record.level7
                        else None
                    ),
                    "is_deleted": record.is_deleted,
                    "h_id": record.h_id,
                    "status": approval_status,
                    "is_parentpending": is_parentpending,
                    "created_date": (
                        record.created_date.isoformat()
                        if record.created_date.isoformat()
                        else None
                    ),
                    "updated_date": (
                        None
                        if record.updated_date is None
                        else record.updated_date.isoformat()
                    ),
                }

                # Append the processed data to the response list
                response.append(org_hierarchy_table_data)
            # return response
            return (
                self.org_process_mapping_helper.construct_hier_org_records(response),
                200,
            )

        except Exception as e:
            return {
                "message": "Something went wrong",
                "data": None,
                "error": str(e),
            }, 500


class OrgHierarchyDeactivation(Resource):

    def __init__(self):
        # Initialize the table reference in the constructor
        self.org_hierarchy = Base.metadata.tables["db_nxtgen.Org_Hierarchy"]
        self.org_hier_mapping_table = Base.metadata.tables["db_nxtgen.Org_Hier_Mapping"]
        self.kpi_input = Base.metadata.tables["db_nxtgen.Kpi_Input"]
        self.org_process_mapping_helper = OrgProcessMappingHelper()
        self.org_hier_mapping_helper = OrgHierarchyMappingHelper()

    @user_or_admin_authentication_required
    def post(self):
        """Handles organization deactivation requests."""
        try:
            deactivation_record = request.get_json()
            if deactivation_record["action"] == "deactivate":
                return self.org_hier_mapping_helper.handle_deactivate_mapping(
                    deactivation_record
                )

        except Exception as e:
            # Rollback the transaction in case of any errors
            db.session.rollback()
            return {"message": "An error occurred", "error": str(e)}, 500
        



class MappingDeactivation(Resource):

    def __init__(self):
        # Initialize the table reference in the constructor
        self.org_hierarchy = Base.metadata.tables["db_nxtgen.Org_Hierarchy"]
        self.org_hier_mapping_table = Base.metadata.tables["db_nxtgen.Org_Hier_Mapping"]
        self.kpi_input = Base.metadata.tables["db_nxtgen.Kpi_Input"]
        self.org_process_mapping_helper = OrgProcessMappingHelper()
        self.org_hier_mapping_helper = OrgHierarchyMappingHelper()
        self.workflow_table = Base.metadata.tables["db_nxtgen.Workflow"]

    @user_or_admin_authentication_required
    def post(self):
        """Handles Mapping deactivation requests."""
        current_user = get_user_from_token()[1]
        try:
            data = request.get_json()
            print('request data....',data)
            response_messages = []
            for entry in data:
                if entry["action"] == "deactivateMapping":
                    if entry["id"]:
                        record = db.session.query(self.org_hier_mapping_table).filter(self.org_hier_mapping_table.c.id == entry["id"]).first()
                    if record:
                        org_mapping_date = {column.name: getattr(record, column.name)
                            for column in self.org_hier_mapping_table.columns
                            if column.name != 'record_id'}
                        
                        org_mapping_date['updated_date'] = func.now()
                        org_mapping_date['updated_by'] = current_user
                        org_mapping_date['rec_start_date'] = func.now()
                        org_mapping_date['rec_end_date'] = None
                        org_mapping_date['approval_1_by'] = None
                        org_mapping_date['approval_1_date'] = None
                        org_mapping_date['approval_2_by'] = None
                        org_mapping_date['approval_2_date'] = None
                        org_mapping_date['approval_1_status'] = 'Pending'
                        org_mapping_date['approval_2_status'] = 'Pending'

                        insert_stmt = self.org_hier_mapping_table.insert().values(**org_mapping_date)
                       
                        result = db.session.execute(insert_stmt)
                        # db.session.commit()
                        new_record_id = result.inserted_primary_key[0]

                        for hierarchy_data in entry.get("prop_val", []):

                            if (
                                "source_system_cd" not in hierarchy_data
                                or "process_area" not in hierarchy_data
                            ):
                                response_messages.append(
                                    "source_system_cd and process_area are required."
                                )
                                continue
                            
                            #   

                            

                            max_wid = db.session.execute(
                                select(func.max(func.cast(func.substring(self.workflow_table.c.wid, 4, 1000), Integer)))
                                .where(self.workflow_table.c.wid.like("wf_%"))
                            ).scalar()
 
                            new_wid = f"wf_{(max_wid + 1) if max_wid else 1}"
                            last_non_null_level = None 

                            for i in range(1, 8):
                                level_key = f"level{i}"
                            last_non_null_level = None
                            for i in range(1, 8):
                                level_key = f'level{i}'
                                if level_key in hierarchy_data and hierarchy_data[level_key]:
                                    last_non_null_level = hierarchy_data[level_key]
                            print('last_non_null_level:', last_non_null_level)
                            if last_non_null_level is None:
                                response_messages.append("No valid levels found.")
                                continue

                            print("Org", last_non_null_level)
                                
                            org_record = db.session.execute(
                                select(self.org_hierarchy).where(
                                    self.org_hierarchy.c.org_name
                                    == last_non_null_level
                                )
                            ).fetchone()
                            if not org_record:
                                response_messages.append(
                                    f"No organization found with name '{last_non_null_level}'."
                                )
                                continue

                            workflow_data_entries = []
                            for field_name, value in hierarchy_data.get(
                                "mapping", {}
                            ).items():
                                workflow_data_entries.append(
                                    {
                                        "wid": new_wid,
                                        "mapping_record_id": new_record_id,
                                        "dyn_col_1": field_name,
                                        "dyn_col_2": value,
                                        "created_date": db.func.now(),
                                        "email_id": get_user_from_token()[3],
                                        "is_deleted": 0,
                                        "wf_status": "Pending",
                                        "wf_reviewer_1_status": "Pending",
                                        "wf_reviewer_2_status": "Pending",
                                        "requested_by": literal(get_user_from_token()[1]),
                                        "typeof_action": "deactivateMapping",
                                        "typeof_cr": "single",
                                        "Comments": None,
                                        "depedent_workflow_id": None
                                    }
                                )

                            # Add process_area and source_system_cd entries
                            workflow_data_entries.append(
                                {
                                    "wid": new_wid,
                                    "mapping_record_id": new_record_id,
                                    "dyn_col_1": "process_area",
                                    "dyn_col_2": hierarchy_data["process_area"],
                                    "created_date": db.func.now(),
                                    "email_id": get_user_from_token()[3],
                                    "is_deleted": 0,
                                    "wf_status": "Pending",
                                    "wf_reviewer_1_status": "Pending",
                                    "wf_reviewer_2_status": "Pending",
                                    "requested_by": literal(get_user_from_token()[1]),
                                    "typeof_action": "deactivateMapping",
                                    "typeof_cr": "single",
                                    "Comments": None,
                                    "depedent_workflow_id": None
                                }
                            )
                            workflow_data_entries.append(
                                {
                                    "wid": new_wid,
                                    "mapping_record_id": new_record_id,
                                    "dyn_col_1": "source_system_cd",
                                    "dyn_col_2": hierarchy_data["source_system_cd"],
                                    "created_date": db.func.now(),
                                    "email_id": get_user_from_token()[3],
                                    "is_deleted": 0,
                                    "wf_status": "Pending",
                                    "wf_reviewer_1_status": "Pending",
                                    "wf_reviewer_2_status": "Pending",
                                    "requested_by": literal(get_user_from_token()[1]),
                                    "typeof_action": "deactivateMapping",
                                    "typeof_cr": "single",
                                    "Comments": None,
                                    "depedent_workflow_id": None
                                }
                            )

                            # Include levels from level1 to level7 in workflow entries
                            for i in range(1, 8):
                                level_key = f"level{i}"
                                if level_key in hierarchy_data and hierarchy_data[level_key]:
                                    workflow_data_entries.append(
                                        {
                                            "wid": new_wid,
                                            "mapping_record_id": new_record_id,
                                            "dyn_col_1": level_key,
                                            "dyn_col_2": hierarchy_data.get(level_key),
                                            "created_date": db.func.now(),
                                            "email_id": get_user_from_token()[3],
                                            "is_deleted": 0,
                                            "wf_status": "Pending",
                                            "wf_reviewer_1_status": "Pending",
                                            "wf_reviewer_2_status": "Pending",
                                            "requested_by": literal(get_user_from_token()[1]),
                                            "typeof_action": "deactivateMapping",
                                            "typeof_cr": "single",
                                            "Comments": None,
                                            "depedent_workflow_id": None
                                        }
                                )
                                    
                            # Insert all prepared workflow entries into the Workflow table
                            for workflow_data in workflow_data_entries:
                                db.session.execute(
                                    self.workflow_table.insert().values(workflow_data)
                                )
                        db.session.commit()
                        return {"message": "Deactivation request Submitted successfully"}, 201
                    else:
                            return {"message": "Record not found"}, 404
            
 
        except Exception as e:
            # Rollback the transaction in case of any errors
            db.session.rollback()
            return {"message": "An error occurred", "error": str(e)}, 500
        








class GetHierarchyMappingValueAPI(Resource):

    def __init__(self):
        self.org_hier_mapping = Base.metadata.tables["db_nxtgen.Org_Hier_Mapping"]
        self.process_area_mapping = Base.metadata.tables[
            "db_nxtgen.Process_Area_Mapping"
        ]

    @user_or_admin_authentication_required
    def get(self):
        try:
            process_areas = request.args.get("process_area")
            mapping_fields = request.args.get("mapping_field")

            if not process_areas or not mapping_fields:
                return {
                    "message": "Both process_area and mapping_field are required"
                }, 400

            # Split mapping_fields by ampersand to handle multiple fields
            mapping_fields = [field.strip() for field in mapping_fields.split("&")]

            # Split process_areas by ampersand to handle multiple process areas
            process_areas = [area.strip() for area in process_areas.split("&")]
            self.DEFAULT_REC_END_DATE = "9999-01-01 00:00:00.000"

            # Loop through dynamic fields and find matching ones
            dynamic_field_columns = {}
            for i in range(1, 13):
                field_name = f"dynamic_mapping_field_name_{i}"

                # Query Process_Area_Mapping to check if any dynamic mapping field matches one of the mapping_fields
                process_area_column = getattr(self.process_area_mapping.c, field_name)
                process_area_query = select(process_area_column).where(
                    self.process_area_mapping.c.process_area.in_(process_areas)
                )
                process_area_data = db.session.execute(process_area_query).fetchall()

                # Check if any of the provided mapping_fields match the dynamic field
                for field in process_area_data:
                    if field[0] in mapping_fields:
                        if field[0] not in dynamic_field_columns:
                            dynamic_field_columns[field[0]] = field_name
                        break

            if not dynamic_field_columns:
                return {
                    "message": f"No matching dynamic fields found for mapping_fields '{', '.join(mapping_fields)}' in process_areas '{', '.join(process_areas)}'"
                }, 404

            # Prepare query to retrieve data from Org_Hier_Mapping for all matched dynamic fields
            conditions = and_(
                self.org_hier_mapping.c.mapping_id
                == self.process_area_mapping.c.mapping_id,
                self.process_area_mapping.c.process_area.in_(process_areas),
            )

            response_data = {}
            for mapping_field, dynamic_field_column in dynamic_field_columns.items():
                org_hier_column = getattr(self.org_hier_mapping.c, dynamic_field_column)
                org_hier_query = select(org_hier_column).where(conditions, self.org_hier_mapping.c.rec_end_date == self.DEFAULT_REC_END_DATE).distinct()
                result = db.session.execute(org_hier_query).fetchall()

                # Add non-None results for each dynamic field
                response_data[mapping_field] = [
                    row[0] for row in result if row[0] is not None
                ]

            return {
                "message": "Data retrieved successfully",
                "data": response_data,
            }, 200

        except Exception as e:
            return {"message": "An error occurred", "error": str(e)}, 500


class OrgHierarchyDeactiveValidation(Resource):

    def __init__(self):
        # Initialize the table reference in the constructor
        self.org_hierarchy = Base.metadata.tables["db_nxtgen.Org_Hierarchy"]
        self.org_hier_mapping_table = Base.metadata.tables["db_nxtgen.Org_Hier_Mapping"]
        self.kpi_input = Base.metadata.tables["db_nxtgen.Kpi_Input"]
        self.org_process_mapping_helper = OrgProcessMappingHelper()
        self.org_hier_mapping_helper = OrgHierarchyMappingHelper()

    def get(self):
        """Fetching associated records for given org_id
        Params: org_id
        Returns:
            _type_: list of dictionaries which holds associated kpi input and process area
        """
        return self.org_hier_mapping_helper.fetch_associated_records(
            request.args.get("org_id")
        )


class ValidationAPI(Resource):

    def __init__(self):
        # Initialize constants and table references for DB interactions
        # self.DEFAULT_REC_END_DATE = "9999-01-01 00:00:00.000"
        self.org_hierarchy_table = Base.metadata.tables["db_nxtgen.Org_Hierarchy"]
        self.org_hier_mapping_table = Base.metadata.tables["db_nxtgen.Org_Hier_Mapping"]
        self.org_process_mapping_helper = OrgProcessMappingHelper()

    @user_or_admin_authentication_required
    def post(self):
        try:
            data = request.get_json()
            response_data = {"typeof_action": "name_change", "data": []}

            # Check for org name validation
            if "data" not in data and isinstance(data, list) and len(data) > 0:
                if data[0]["action"] == "create" and data[0]["prop_type"] == "org_name":
                    validation_result = self.org_process_mapping_helper.org_hierarchy_validation_service(
                        data[0], data
                    )
                    print("validation_result", validation_result)
                    data[0] = validation_result
                    return [validation_result]
                    # if validation_result == True:
                    #     return {
                    #         "is_validated": True,
                    #         "message": "Organization name validated successfully.",
                    #     }, 200
                    # else:
                    #     return {
                    #         "is_validated": False,
                    #         "message": validation_result,
                    #     }, 200

            if "data" in data:
                for entry in data["data"]:
                    entry["is_validated"] = True

                    existing_matches = self.org_process_mapping_helper.validation_organization_match_score(
                        entry["action_val"]
                    )
                    if existing_matches:
                        entry["is_validated"] = False

                    response_data["data"].append(entry)

            # Mapping validation check
            if isinstance(data, list):
                for item in data:
                    if (
                        item.get("action") == "create"
                        and item.get("prop_type") == "hierarchy"
                    ):
                        if item.get("prop_val", []):

                            mapping_validation_response = self.org_process_mapping_helper.org_hierarchy_mapping_validation_service(
                                item.get("prop_val", [])[0], request.args.get("org_id")
                            )

                            if mapping_validation_response.get("is_validated", False):
                                return {
                                    "is_validated": True,
                                    "message": "Mapping combination validated successfully.",
                                }, 200
                            else:
                                return {
                                    "is_validated": False,
                                    "message": "Mapping combination already exists. Try a different mapping combination.",
                                }, 200

            if "typeof_action" in data and data["typeof_action"] == "mapping_change":
                existing_matches = self.org_process_mapping_helper.org_hierarchy_mapping_validation_service(
                    data.get("action_val", [])[0], request.args.get("org_id")
                )
                if existing_matches.get("is_validated", False):
                    return {
                        "is_validated": True,
                        "message": "Mapping combination validated successfully.",
                    }, 200
                else:
                    return {
                        "is_validated": False,
                        "message": "Mapping combination already exists. Try a different mapping combination.",
                    }, 200

            return response_data, 200

        except Exception as e:
            return {
                "message": "Something went wrong",
                "data": None,
                "error": str(e),
            }, 500


class ApprovalWorkFlow(Resource):

    def __init__(self):
        # Initialize constants and table references for DB interactions
        self.workflow_table = Base.metadata.tables["db_nxtgen.Workflow"]
        self.common_helper = CommonHelper()
        self.org_hier_mapping_table = Base.metadata.tables["db_nxtgen.Org_Hier_Mapping"]
        self.org_hierarchy_table = Base.metadata.tables["db_nxtgen.Org_Hierarchy"]
        self.high_date = "9999-01-01 00:00:00.000"
        self.org_hierarchy_mapping_helper = OrgHierarchyMappingHelper()

    @user_or_admin_authentication_required
    def get(self):
        try:
            # Retrieve status from the query string (default is None)
            request_status = request.args.get("status", None)
            user_email = get_user_from_token()[3]
    
            # Check if the provided status is 'Pending' or 'Approved'
            if request_status in ["Pending", "Approved", "Rejected"]:
                # Prepare the filter conditions dynamically
                filter_condition = None

                if request_status == "Approved":
                    filter_condition = and_(
                        self.workflow_table.c.wf_reviewer_1_status == request_status,
                        self.workflow_table.c.wf_reviewer_2_status == request_status,
                    )
                else:
                    filter_condition = and_(
                            or_(
                                self.workflow_table.c.wf_reviewer_1_status == request_status,
                                self.workflow_table.c.wf_reviewer_2_status == request_status,
                        ), 
                                or_(
                                self.workflow_table.c.reviewer_1_email_id != user_email,
                                self.workflow_table.c.reviewer_1_email_id.is_(None)
                        )
                    )
                # Apply the filter condition if exists
                if filter_condition is not None:
                    query = db.session.execute(
                        select(self.workflow_table).where(
                            filter_condition
                        )  # Apply the filter condition
                    )

            # Fetch the filtered records from the database
            workflow_records = query.all()
            formatted_records = [
                self.common_helper.serialize_row(record._mapping)
                for record in workflow_records
            ]
            groupby_wid = self.common_helper.groupby_field(formatted_records)

            return groupby_wid, 200

        except Exception as e:
            return {
                "message": "Something went wrong",
                "data": None,
                "error": str(e),
            }, 500

    @user_or_admin_authentication_required
    def post(self):
        try:
            current_user = get_user_from_token()[1]
            data = request.get_json()

            new_work_flow_entry = db.session.execute(
                select(self.workflow_table).where(
                    self.workflow_table.c.wid == data.get("wid")
                )
            ).fetchall()
            if "dependent_wid" in data:

                dep_work_flow_entry = db.session.execute(
                    select(self.workflow_table).where(
                        self.workflow_table.c.wid == data.get("dependent_wid")
                    )
                ).fetchall()
                new_work_flow_entry.extend(dep_work_flow_entry)
            response = self.org_hierarchy_mapping_helper.approve_workflow(
                current_user, new_work_flow_entry, data
            )

            if not new_work_flow_entry:
                return {"error": "Workflow entry not found"}, 404
            else:
                return {"message": response}, 200

        except Exception as e:
            return {
                "message": "Something went wrong",
                "data": None,
                "error": str(e),
            }, 500


class GetHierarchyAllApprovedLevelDropdown(Resource):
    def __init__(self):
        # Initialize the table reference
        self.org_hierarchy = Base.metadata.tables["db_nxtgen.Org_Hierarchy"]
        self.default_date = "9999-01-01 00:00:00.000"

    @user_or_admin_authentication_required
    def get(self):
        """
        GET API to fetch all approved organizations based on org_name column.
        """
        try:
            subquery = (
                select(self.org_hierarchy.c.org_id)
                .where(
                    or_(
                        self.org_hierarchy.c.rec_end_date == self.default_date,
                        self.org_hierarchy.c.rec_end_date.is_(None),
                    )
                )
                .group_by(self.org_hierarchy.c.org_id)
                .having(func.count() > 1)
                .alias("duplicate_orgs")
            )

            # query to get approved organizations that are not in the subquery result
            query = select(
                self.org_hierarchy.c.org_id,
                self.org_hierarchy.c.h_id,
                self.org_hierarchy.c.org_name,
            ).where(
                and_(
                    or_(
                        self.org_hierarchy.c.rec_end_date == self.default_date,
                        self.org_hierarchy.c.rec_end_date.is_(None),
                    ),
                    not_(self.org_hierarchy.c.org_id.in_(subquery)),
                ),
                and_(
                    self.org_hierarchy.c.approval_1_status == "Approved",
                    self.org_hierarchy.c.approval_2_status == "Approved",
                ),
            )

            result = db.session.execute(query).fetchall()

            approved_organizations = {}
            for row in result:
                org_name = row.org_name
                if org_name and org_name not in approved_organizations:
                    approved_organizations[org_name] = {
                        "h_id": row.h_id,
                        "org_id": row.org_id,
                        "org_name": org_name,
                    }
            approved_organizations_list = list(approved_organizations.values())

            sorted_organizations = sorted(
                approved_organizations_list, key=lambda x: x["org_name"]
            )

            return {
                "message": "Data retrieved successfully",
                "data": sorted_organizations,
            }, 200

        except Exception as e:
            return {
                "message": "Something went wrong",
                "data": None,
                "error": str(e),
            }, 500


class GetHierarchyMappingViewHistory(Resource):

    def __init__(self):
        # Initialize table references using SQLAlchemy's metadata
        self.org_hierarchy = Base.metadata.tables["db_nxtgen.Org_Hierarchy"]
        self.org_hier_mapping = Base.metadata.tables["db_nxtgen.Org_Hier_Mapping"]
        self.process_area_mapping = Base.metadata.tables[
            "db_nxtgen.Process_Area_Mapping"
        ]
        self.org_hierarchy_mapping_helper = OrgHierarchyMappingHelper()
        self.org_process_mapping_helper = OrgProcessMappingHelper()

    @user_or_admin_authentication_required
    def get(self):
        try:
            # Retrieve ID from request parameters
            id = request.args.get("id")

            if not id:
                return {"message": "ID parameter is required", "data": []}, 400
            else:
                # Query to fetch hierarchy mapping data
                join_query = (
                    select(
                        self.org_hierarchy.c.level1,
                        self.org_hierarchy.c.level2,
                        self.org_hierarchy.c.level3,
                        self.org_hierarchy.c.level4,
                        self.org_hierarchy.c.level5,
                        self.org_hierarchy.c.level6,
                        self.org_hierarchy.c.level7,
                        self.org_hier_mapping.c.approval_1_status,
                        self.org_hier_mapping.c.approval_2_status,
                        self.org_hier_mapping.c.created_by,
                        self.org_hier_mapping.c.updated_by,
                        self.org_hier_mapping.c.updated_date,
                        self.org_hier_mapping.c.record_id,
                    )
                    .select_from(
                        self.org_hier_mapping.join(
                            self.org_hierarchy,
                            self.org_hier_mapping.c.org_id == self.org_hierarchy.c.org_id,
                        )
                    )
                    .where(self.org_hier_mapping.c.id == id)
                )

                result = db.session.execute(join_query).mappings().fetchall()

                if not result:
                    return {
                        "message": "No records found for the specified ID",
                        "data": [],
                    }, 404
                else:
                    # Fetch mapping_id from org_hier_mapping using the specified ID
                    mapping_id_query = select(self.org_hier_mapping.c.mapping_id).where(
                        self.org_hier_mapping.c.id == id
                    )
                    mapping_id_result = db.session.execute(mapping_id_query).fetchone()
                    mapping_id = mapping_id_result[0] if mapping_id_result else None

                    # Call to fetch dynamic fields using the mapping_id & id
                    org_mapping_history_records = (
                        self.org_process_mapping_helper._get_dynamic_fields_for_mapping(
                            mapping_id, id
                        )
                    )

                    response_data = []
                    for index, row in enumerate(result):
                        approval_1_status = row["approval_1_status"]
                        approval_2_status = row["approval_2_status"]

                        # Calculate status
                        status = self.org_hierarchy_mapping_helper.calculate_status(
                            approval_1_status, approval_2_status
                        )

                        # Initialize the row dictionary
                        row_dict = {
                            "Level_1": row["level1"],
                            "Level_2": row["level2"],
                            "Level_3": row["level3"],
                            "Level_4": row["level4"],
                            "Level_5": row["level5"],
                            "Level_6": row["level6"],
                            "Level_7": row["level7"],
                            "Created_By": row["created_by"],
                            "Updated_By": row["updated_by"],
                            "Updated_date": (
                                row["updated_date"].isoformat()
                                if isinstance(row["updated_date"], datetime)
                                else row["updated_date"]
                            ),
                            "approval_1_status": row["approval_1_status"],
                            "approval_2_status": row["approval_2_status"],
                            "Status": status,
                        }

                        # Only add dynamic fields if they are relevant
                        if index < len(org_mapping_history_records):
                            org_process_fields = org_mapping_history_records[index]
                            row_dict.update(
                                {k: v for k, v in org_process_fields.items() if v is not None}
                            )

                        response_data.append(row_dict)

                    return {
                        "message": "Data retrieved successfully",
                        "data": response_data,
                    }, 200

        except Exception as e:
            return {
                "message": "Something went wrong",
                "data": None,
                "error": str(e),
            }, 500


class GetHierarchyOrganizationHistory(Resource):

    def __init__(self):
        self.org_hierarchy = Base.metadata.tables["db_nxtgen.Org_Hierarchy"]

    @user_or_admin_authentication_required
    def get(self):
    # try:
        query_params = request.args.to_dict()
        if not query_params:
            return {
                "message": "Level Org Id in  parameter is required ",
                "data": [],
            }, 400

        all_org_id = list(query_params.values())
        query = select(self.org_hierarchy).where(
            self.org_hierarchy.c.org_id.in_(all_org_id)
        )
        result = db.session.execute(query).fetchall()
        cheraBichi = OrgHistorySchema.dump(result)
        grouped_data = defaultdict(list)

        for row in cheraBichi:
            row_dict = dict(row)
            for key, value in row_dict.items():
                if isinstance(value, datetime):
                    row_dict[key] = value.isoformat()
            org_level = row_dict.get("org_level")
            if org_level:
                level_key = f"level{org_level}"
                grouped_data[level_key].append(row_dict)

        return {
            "message": "Organiztaion History Data retrieved successfully",
            "data": grouped_data,
        }, 200

        # except Exception as e:
        #     return {
        #         "message": "Something went wrong",
        #         "data": None,
        #         "error": str(e),
        #     }, 500
