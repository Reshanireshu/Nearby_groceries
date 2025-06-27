from db import db, Base

from sqlalchemy import Table, MetaData
from sqlalchemy import select, or_, func, case
from sqlalchemy.orm import aliased
from datetime import datetime
from fuzzywuzzy import fuzz
from sqlalchemy.sql import exists
from datetime import date


class OrgProcessMappingHelper:

    def __init__(self):
        super().__init__()
        self.org_hier_mapping = Base.metadata.tables["db_nxtgen.Org_Hier_Mapping"]
        self.process_area_mapping = Base.metadata.tables[
            "db_nxtgen.Process_Area_Mapping"
        ]
        self.org_hierarchy = Base.metadata.tables["db_nxtgen.Org_Hierarchy"]

        self.mapping_field_combo_table = Base.metadata.tables[
            "db_nxtgen.MappingField_Combo_Table"
        ]
        self.DEFAULT_REC_END_DATE = "9999-01-01 00:00:00.000"

    def _get_distinct_mapping_ids(self, source_system_cd=None, process_area=None,id=None):
        """Fetch distinct record IDs based on the source system code."""

        query = select(self.process_area_mapping.c.mapping_id).where(
            self.process_area_mapping.c.source_system_cd == source_system_cd,
            self.process_area_mapping.c.process_area == process_area,
            self.process_area_mapping.c.is_deleted == 0,
            or_(
                self.org_hier_mapping.c.rec_end_date == self.DEFAULT_REC_END_DATE,
                self.org_hier_mapping.c.rec_end_date
                == None,  # Use `None` for NULL in SQLAlchemy
            ),
        )

        distinct_record_ids = db.session.execute(query).fetchone()
        return distinct_record_ids._mapping if distinct_record_ids else None

    def _get_org_record(self, org_id):
        """Fetch the organization record by its ID."""
        org_record = db.session.execute(
            select(*[col for col in self.org_hierarchy.c if col.name != 'updated_date' and col.name != 'created_date' and col.name != 'record_id'] ).where(
                self.org_hierarchy.c.org_id == org_id,
                self.org_hierarchy.c.is_deleted == 0,
                or_(
                    self.org_hierarchy.c.rec_end_date == self.DEFAULT_REC_END_DATE,
                    self.org_hierarchy.c.rec_end_date
                    == None,  # Use `None` for NULL in SQLAlchemy
                ),
            )
        ).fetchone()
        return org_record._mapping if org_record else None

    def _get_org_process_area_records(self, mapping_id, org_id=None):
        """Fetch process area mappings for the specified source system code."""
        mapping_record_query = None
        mapping_record = ""
        if mapping_id is not None:
            mapping_record_query = select(self.process_area_mapping).where(
                self.process_area_mapping.c.mapping_id == mapping_id
            )
            mapping_record = db.session.execute(mapping_record_query).fetchone()

            org_hier_subq = (
                                select(
                                    self.org_hier_mapping,
                                    func.row_number().over(
                                        partition_by=self.org_hier_mapping.c.org_id,
                                        order_by=[
                                            case(
                                                (self.org_hier_mapping.c.rec_end_date == None, 0),
                                                else_=1
                                            ),
                                            self.org_hier_mapping.c.id.desc()
                                        ]
                                    ).label("rn")
                                )
                                .where(
                                    self.org_hier_mapping.c.mapping_id == mapping_id,
                                    or_(
                                        self.org_hier_mapping.c.rec_end_date == self.DEFAULT_REC_END_DATE,
                                        self.org_hier_mapping.c.rec_end_date == None,
                                    )
                                )
                                .subquery()
                            )
            mapping_col_record_query = select(org_hier_subq).where(org_hier_subq.c.rn == 1)
            mapping_col_record = db.session.execute(mapping_col_record_query).fetchall()
            org_process_mapping_vals = []
            for each_row in mapping_col_record:
                each_row_Dict = dict()
                for k, v in dict(each_row._mapping).items():
                    if (
                        k.startswith("dynamic")
                        or k == "record_id"
                        or k == "org_id"
                        or k == "id"
                        or k == "approval_1_status"
                        or k == "approval_2_status"
                        or k == "updated_date"
                        or k == "created_date"
                    ):
                        if k == "updated_date" or k == "created_date" and isinstance(v, datetime):
                            v = v.isoformat() if v else None

                    each_row_Dict.update({k: v})
                org_process_mapping_vals.append(each_row_Dict)
            mapping_rcd_title = {
                k: v
                for k, v in dict(mapping_record._mapping).items()
                if (
                    k.startswith("dynamic")
                    or k == "process_area"
                    or k == "record_id"
                    or k == "org_id"
                    or k == "id"
                )
                and v is not None
            }

            # Create a new list of dictionaries with keys replaced by the values from the title dictionary
            return [
                {
                    "org_id": record["org_id"],
                    "record_id": record["record_id"],
                    "id": record["id"],
                    "updated_date": record["updated_date"],
                    "created_date": record["created_date"],
                    "status": (
                        "Approved"
                        if record["approval_1_status"] == "Approved"
                        and record["approval_2_status"] == "Approved"
                        else (
                            "Rejected"
                            if "Rejected"
                            in [record["approval_1_status"], record["approval_2_status"]]
                            else (
                                "Pending"
                                if "Pending"
                                in [
                                    record["approval_1_status"],
                                    record["approval_2_status"],
                                ]
                                else None
                            )
                        )
                    ),
                    "process_area": mapping_rcd_title["process_area"],
                    **{
                        mapping_rcd_title[k]: v
                        for k, v in record.items()
                        if k in mapping_rcd_title
                    },  # Merge the dynamic field mappings
                }
                for record in org_process_mapping_vals
            ]

    def _merge_records(self, org_record, process_area_records):
        """Merge organization record with each process area record."""
        
        merged_item = {**process_area_records, **org_record}   
        merged_item["org_hier_status"] = merged_item["status"]
       
        merged_item = {key: value.isoformat() if isinstance(value, datetime) else value
            for key, value in merged_item.items()
            
        }
        return merged_item

    def _get_mapping_field_combo(self, process_area, source_system_cd):
        mapping_col_record = db.session.execute(
            select(self.mapping_field_combo_table).where(
                self.mapping_field_combo_table.c.process_area == process_area,
                self.mapping_field_combo_table.c.source_system_cd == source_system_cd
            )
        ).fetchall()

        mapping_combo = [
            " & ".join(
                str(mapping_combo_val)
                for mapping_combo_key, mapping_combo_val in item._mapping.items()
                if "mapping_field" in mapping_combo_key
                and mapping_combo_val is not None
            )
            for item in mapping_col_record
        ]
        return {"mapping_field_combination": mapping_combo}
    
    def _update_status_in_list_of_records(self, list_parent_org_records):
        # Format the record if one is found

        formatted_records = []

        for parent_org_record in list_parent_org_records:
            # record_dict = dict(parent_org_record._mapping)

            # record_dict.update({'org_name': value for key, value in record_dict.items() if key.startswith('level')})
            # Determine the status based on approval statuses
            approval_1_status = parent_org_record.get("approval_1_status")
            approval_2_status = parent_org_record.get("approval_2_status")

            if approval_1_status == "Approved" and approval_2_status == "Approved":
                status = "Approved"
            elif "Rejected" in [approval_1_status, approval_2_status]:
                status = "Rejected"
            elif "Pending" in [approval_1_status, approval_2_status]:
                status = "Pending"
            else:
                status = None

            # Add the status to the record
            parent_org_record["status"] = status
            parent_org_record["record_id"] = parent_org_record.get("record_id")

            formatted_records.append(parent_org_record)
        return formatted_records

    def build_base_query(self, include_pending):
        
        query = (
                        select(
                            self.org_hierarchy,
                            func.row_number().over(
                                partition_by=self.org_hierarchy.c.org_id,
                                order_by=[
                                    case(
                                        (self.org_hierarchy.c.rec_end_date == None, 0),
                                        else_=1
                                    ),
                                    self.org_hierarchy.c.org_id.desc()
                                ]
                            ).label("rn")
                        )
                        .where(
                            or_(
                                self.org_hierarchy.c.rec_end_date == self.DEFAULT_REC_END_DATE,
                                self.org_hierarchy.c.rec_end_date == None,
                            )
                        )
                        .subquery()
                            )
        query = select(query).where(query.c.rn == 1)

        if include_pending == "false":
            query = query.where(
                self.org_hierarchy.c.approval_1_status == "Approved",
                self.org_hierarchy.c.approval_2_status == "Approved",
            )

        return query


    def org_hierarchy_validation_service(self, request_org_data,req_data=None):
        # Extract org names and parent names to query in batch
        org_names = [
            each_org["org_name"].lower() if each_org.get("org_name") else None
            for each_org in request_org_data["prop_val"]
        ]

        parent_names = [
            each_org["parent_name"].lower() if each_org.get("parent_name") else None
            for each_org in request_org_data["prop_val"]
        ]

        # Filter out None values
        org_names = [name for name in org_names if name]
        parent_names = [name for name in parent_names if name]

        # Batch query for org names and parent names
        existing_orgs = {
            org.org_name.lower()
            for org in db.session.query(self.org_hierarchy.c.org_name)
            .filter(
                self.org_hierarchy.c.org_name.in_(org_names),
                self.org_hierarchy.c.approval_2_status != "Rejected",
                self.org_hierarchy.c.approval_1_status != "Rejected",
            )
            .all()
        }
        approved_parents = {
            org.org_name.lower()
            for org in db.session.query(self.org_hierarchy.c.org_name)
            .filter(
                self.org_hierarchy.c.org_name.in_(parent_names),
                self.org_hierarchy.c.approval_2_status == "Approved",
                self.org_hierarchy.c.approval_1_status == "Approved",
            )
            .all()
        }

        all_filtered_orgs = []
        message = []
        response = {}

        for each_org in request_org_data["prop_val"]:
            org_name = each_org.get("org_name")
            if org_name:  # Ensure org_name is not None before calling lower()
                filtered_orgs = self.validation_organization_match_score(
                    org_name.lower()
                )
                
                if filtered_orgs:
                    print(each_org,'each org')
                    each_org['is_validated'] = False
                    # all_filtered_orgs.extend(filtered_orgs)
                    
                elif not filtered_orgs:
                    each_org['is_validated'] = True

                if each_org.get("org_level", 0) > 7:  # Default to 0 if not specified
                    message.append(
                        {
                            "message": f"Invalid organization level found for organization {org_name}. The level should not exceed 7."
                        }
                    )

                parent_name = each_org.get("parent_name")
                if parent_name:
                    exists_parent = (
                        db.session.query(self.org_hierarchy)
                        .filter(self.org_hierarchy.c.org_name == parent_name.lower())
                        .limit(1)
                        .first()
                    )

                    if exists_parent and parent_name.lower() not in approved_parents:
                        message.append(
                            {
                                "message": f"Parent organization has not been approved for {org_name}"
                            }
                        )

        response["message"] = message
        return request_org_data
        # print('all_filtered_orgs',all_filtered_orgs)
        # if len(all_filtered_orgs) > 0:
        #     response["org_name_exists"] = {
        #         "message": "Organization name already exists, Try a different name",
        #         "match_percentage": all_filtered_orgs,
        #     }
        # if len(message) > 0 or len(all_filtered_orgs) > 0:
        #     return request_org_data
        # else:
        #     return request_org_data

    def validation_organization_match_score(self, org_name_data):
        # print('orgname',org_name_data)
        org_names = [
            org_name[0]
            for org_name in db.session.query(self.org_hierarchy.c.org_name).all()
        ]
        seen = set()
        filtered_orgs = []
        for  org in org_names:
           
            if fuzz.ratio(org.lower() ,org_name_data.lower()) > 80 :
                if org_name_data not in seen:
                    seen.add(org_name_data)
                    filtered_orgs.append({
                        "org_name": org_name_data,
                        "match_percentage": fuzz.ratio(org.lower(),org_name_data.lower()),
                    })   
                
        return filtered_orgs

    def construct_hier_org_records(self, list_of_org_hier_records):

        # Deduplicate by keeping the highest `org_level` for each unique level reference
        level_to_record = {}
        for each_org_hier_record in list_of_org_hier_records:
            for level_key in [
                "level1",
                "level2",
                "level3",
                "level4",
                "level5",
                "level6",
                "level7",
            ]:
                level_value = each_org_hier_record[level_key]
                if level_value:
                    if level_value not in level_to_record or int(
                        each_org_hier_record["org_level"]
                    ) > int(level_to_record[level_value]["org_level"]):

                        level_to_record[level_value] = each_org_hier_record

        # Deduplicate by `org_id` to ensure only unique `org_id` records
        unique_records = {}
        for record in level_to_record.values():
            org_id = record["org_id"]
            if org_id not in unique_records or int(record["org_level"]) > int(
                unique_records[org_id]["org_level"]
            ):
                unique_records[org_id] = record

        # Extract the final list of unique records
        final_records = list(unique_records.values())
        # Sort the final filtered records by `org_level` for clarity
        return final_records

    def construct_org_name_and_org_id(self):
        # Query to fetch all org_id and org_name in ascending order of org_level
        org_id_level_query = (
            db.session.query(self.org_hierarchy.c.org_name, self.org_hierarchy.c.org_id)
            .order_by(self.org_hierarchy.c.org_level.asc())
            .all()
        )
        org_id_isparent_pending_query = (
            db.session.query(
                self.org_hierarchy.c.org_name,
                self.org_hierarchy.c.approval_1_status,
                self.org_hierarchy.c.approval_2_status,
            )
            .order_by(self.org_hierarchy.c.org_level.asc())
            .all()
        )

        # Create a dictionary with org_name as key and org_id as value
        return {org_name: org_id for org_name, org_id in org_id_level_query}, {
            org_name: (
                True
                if approval_1_status == "Pending" or approval_2_status == "Pending"
                else False
            )
            for org_name, approval_1_status, approval_2_status in org_id_isparent_pending_query
        }

    def org_hierarchy_mapping_validation_service(self, hierarchy_data, org_id):
        # Ensure required keys exist in hierarchy_data
        if (
            "source_system_cd" not in hierarchy_data
            or "process_area" not in hierarchy_data
        ):
            return {"is_validated": False, "message": "Required keys are missing."}

        last_non_null_level = None
        for i in range(1, 8):
            level_key = f"level{i}"
            if level_key in hierarchy_data and hierarchy_data[level_key]:
                last_non_null_level = hierarchy_data[level_key]
        # Check if mapping exists for the provided process_area and source_system_cd
        mapping_record = db.session.execute(
            select(self.process_area_mapping).where(
                self.process_area_mapping.c.source_system_cd
                == hierarchy_data["source_system_cd"],
                self.process_area_mapping.c.process_area
                == hierarchy_data["process_area"],
            )
        ).fetchone()
        get_org_id = (
            db.session.execute(
                select(self.org_hierarchy).where(
                    self.org_hierarchy.c.org_name == last_non_null_level
                )
            )
            .fetchone()
            ._mapping
        )
        # if mapping_record:
        #     return {"is_validated": False}

        # if not mapping_record:
        #     return {"is_validated": True}

        # Continue processing dynamic columns only if mapping_record exists
        # Convert mapping to a dictionary for dynamic column processing
        mapping_dict = dict(mapping_record._mapping)
        dynamic_columns = {}
        is_hier_mapping_combo_exists = db.session.execute(
            select(self.org_hier_mapping).where(
                self.org_hier_mapping.c.mapping_id == mapping_dict["mapping_id"],
                self.org_hier_mapping.c.org_id == get_org_id["org_id"],
            )
        ).fetchall()
        for each_hier_mapping in is_hier_mapping_combo_exists:
            for i in range(1, 13):
                dynamic_field_name = f"dynamic_mapping_field_name_{i}"
                if (
                    dynamic_field_name in each_hier_mapping._mapping
                    and each_hier_mapping._mapping[dynamic_field_name] is not None
                ):
                    key = mapping_dict[dynamic_field_name]
                    if key in hierarchy_data.get("mapping", {}):

                        if each_hier_mapping._mapping[dynamic_field_name] == hierarchy_data["mapping"][key]:
                            print(each_hier_mapping._mapping[dynamic_field_name],hierarchy_data["mapping"][key],'no change')
                        dynamic_columns[key] = each_hier_mapping._mapping[
                            dynamic_field_name
                        ]
                    else:
                        print('equal not')
                else:
                    print('outter if else',each_hier_mapping._mapping[dynamic_field_name])
        
        # # Validate dynamic column values
        if dynamic_columns == hierarchy_data["mapping"]:
            return {"is_validated": False}

        else:
            return {"is_validated": True}

    def forming_mapping_title_val(self, mapping_record):
        """_summary_: forming the hierarchy mapping title and respective value in the dictionary form"""
        return self._get_org_process_area_records(mapping_record["mapping_id"])[0]

    def replace_org_name_by_org_id(self, list_of_dict):
        """_summary_: generate all level org_id in a array"""
        construct_org_name_and_org_id, construct_org_name_and_org_id_status = (
            self.construct_org_name_and_org_id()
        )

        for each_org_record in list_of_dict:

            level_org_id = {}
            leaf_org_id = ""
            for level in [
                "level1",
                "level2",
                "level3",
                "level4",
                "level5",
                "level6",
                "level7",
            ]:
                if each_org_record.get(level):
                    level_org_id[f"{level}_org_id"] = construct_org_name_and_org_id.get(
                        each_org_record.get(level)
                    )
                    # leaf_org_id = construct_org_name_and_org_id.get(each_org_record.get(level))
            each_org_record["each_org_id"] = level_org_id
            each_org_record["leaf_org_id"] = list(level_org_id.items())[-1][-1]
        return list_of_dict
    
    def _get_dynamic_fields_for_mapping(self, mapping_id, id=None, org_id=None):
        """Fetch process area mappings for the specified source system code."""
        mapping_record_query = None
        mapping_record = ""
        if mapping_id is not None:
            mapping_record_query = select(self.process_area_mapping).where(
                self.process_area_mapping.c.mapping_id == mapping_id,
            )
            mapping_record = db.session.execute(mapping_record_query).fetchone()

        # Main query to fetch the record with the latest record_id
        if org_id is not None:
            mapping_col_record_query = select(self.org_hier_mapping).where(
                self.org_hier_mapping.c.mapping_id == mapping_id,
                self.org_hier_mapping.c.org_id == org_id,
                # or_(
                #     self.org_hier_mapping.c.rec_end_date == self.DEFAULT_REC_END_DATE,
                #     self.org_hier_mapping.c.rec_end_date.is_(None),
                # ),  # Use `None` for NULL in SQLAlchemy
            )
            mapping_col_record = db.session.execute(mapping_col_record_query).fetchall()
        else:
            mapping_col_record_query = select(self.org_hier_mapping).where(
                self.org_hier_mapping.c.mapping_id == mapping_id,
		self.org_hier_mapping.c.id == id,
                # or_(
                #     self.org_hier_mapping.c.rec_end_date == self.DEFAULT_REC_END_DATE,
                #     self.org_hier_mapping.c.rec_end_date.is_(None),
                # ),  # Use `None` for NULL in SQLAlchemy
            )
            mapping_col_record = db.session.execute(mapping_col_record_query).fetchall()
        org_process_mapping_vals = []
        for each_row in mapping_col_record:
            each_row_Dict = {k: (v.isoformat() if isinstance(v, datetime) else v)
                            for k, v in dict(each_row._mapping).items() if k.startswith("dynamic")}
            org_process_mapping_vals.append(each_row_Dict)

        if mapping_record is None:
            raise ValueError("Mapping record not found.")

        dynamic_fields = {
            k: v
            for k, v in dict(mapping_record._mapping).items()
            if k.startswith("dynamic") and v is not None
        }
        return [
            {k: v for k, v in {
                **{
                    dynamic_fields[k]: v
                    for k, v in record.items() if k in dynamic_fields
                }
            }.items() if v is not None}
            for record in org_process_mapping_vals
        ]
    
    def _get_org_hierarchy_mapping_records(self, mapping_id, org_id=None):
        """Fetch process area and hierarchy mappings."""
        mapping_record_query = None
        mapping_record = ""
        if mapping_id is not None:
            mapping_record_query = select(self.process_area_mapping).where(
                self.process_area_mapping.c.mapping_id == mapping_id,
            )
            mapping_record = db.session.execute(mapping_record_query).fetchone()

        if org_id is not None:
            mapping_col_record_query = select(self.org_hier_mapping).where(
                self.org_hier_mapping.c.mapping_id == mapping_id,
                self.org_hier_mapping.c.org_id == org_id,
                or_(
                    self.org_hier_mapping.c.rec_end_date == self.DEFAULT_REC_END_DATE,
                    self.org_hier_mapping.c.rec_end_date.is_(None),
                ),  
            )
            mapping_col_record = db.session.execute(mapping_col_record_query).fetchall()
        else:
            mapping_col_record_query = select(self.org_hier_mapping).where(
                self.org_hier_mapping.c.mapping_id == mapping_id,
                or_(
                    self.org_hier_mapping.c.rec_end_date == self.DEFAULT_REC_END_DATE,
                    self.org_hier_mapping.c.rec_end_date.is_(None),
                ),  
            )
            mapping_col_record = db.session.execute(mapping_col_record_query).fetchall()
        org_process_mapping_vals = []
        for each_row in mapping_col_record:
            each_row_Dict = dict()
            for k, v in dict(each_row._mapping).items():
                if (
                    k.startswith("dynamic")
                    or k == "record_id"
                    or k == "org_id"
                    or k == "id"
                    or k == "approval_1_status"
                    or k == "approval_2_status"
                    or k == "updated_date"
                    or k == "created_date"
                ):
                    if k == "updated_date" or k == "created_date" and isinstance(v, datetime):
                        v = v.isoformat() if v else None
                    # if k == "record_id":
                    #     k = "mapping_record_id"

                each_row_Dict.update({k: v})
            org_process_mapping_vals.append(each_row_Dict)
        mapping_rcd_title = {
            k: v
            for k, v in dict(mapping_record._mapping).items()
            if (
                k.startswith("dynamic")
                or k == "process_area"
                or k == "record_id"
                or k == "org_id"
                or k == "id"
            )
            and v is not None
        }
        # Create a new list of dictionaries with keys replaced by the values from the title dictionary
        return [
            {
                "org_id": record["org_id"],
                "record_id": record["record_id"],
                "id": record["id"],
                "updated_date": record["updated_date"],
                "created_date": record["created_date"],
                "status": (
                    "Approved"
                    if record["approval_1_status"] == "Approved"
                    and record["approval_2_status"] == "Approved"
                    else (
                        "Rejected"
                        if "Rejected"
                        in [record["approval_1_status"], record["approval_2_status"]]
                        else (
                            "Pending"
                            if "Pending"
                            in [
                                record["approval_1_status"],
                                record["approval_2_status"],
                            ]
                            else None
                        )
                    )
                ),
                "process_area": mapping_rcd_title["process_area"],
                **{
                    mapping_rcd_title[k]: v
                    for k, v in record.items()
                    if k in mapping_rcd_title
                },  # Merge the dynamic field mappings
            }
            for record in org_process_mapping_vals
        ]
