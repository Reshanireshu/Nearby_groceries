from sqlalchemy import (
    select,
    func,
    Integer,
    cast,
    insert,
    literal,
    or_,
    distinct,
    text,
    update,
)
from db import db, Base
from datetime import date
from datetime import datetime
from authentication import get_user_from_token
from common_helper.common_helper import CommonHelper
from .org_process_mapping_helper import OrgProcessMappingHelper
from constants.request_parser import keys_to_remove_org_proc_mapping


class OrgHierarchyMappingHelper:

    def __init__(self):
        # Initialize constants and table references for DB interactions
        self.DEFAULT_REC_END_DATE = "9999-01-01 00:00:00.000"
        self.org_hierarchy_table = Base.metadata.tables["db_nxtgen.Org_Hierarchy"]
        self.workflow_table = Base.metadata.tables["db_nxtgen.Workflow"]
        self.workflow_static_table = Base.metadata.tables["db_nxtgen.Workflow_Static"]
        self.org_hier_mapping_table = Base.metadata.tables["db_nxtgen.Org_Hier_Mapping"]
        self.process_area_mapping_table = Base.metadata.tables[
            "db_nxtgen.Process_Area_Mapping"
        ]
        self.kpi_input = Base.metadata.tables["db_nxtgen.Kpi_Input"]
        self.kpi_master = Base.metadata.tables["db_nxtgen.Kpi_Master"]
        self.common_helper = CommonHelper()
        self.org_process_mapping_helper = OrgProcessMappingHelper()

    def calculate_status(self, approval_1_status, approval_2_status):
        """Calculate the status based on the approval statuses."""
        if approval_1_status == "Approved" and approval_2_status == "Approved":
            return "Approved"
        elif "Rejected" in [approval_1_status, approval_2_status]:
            return "Rejected"
        elif "Pending" in [approval_1_status, approval_2_status]:
            return "Pending"
        else:
            return None

    def work_flow_creation(self, record_id, copy_org_data, request_from_user):

        max_wid = db.session.execute(
            select(
                func.max(
                    func.cast(
                        func.substring(self.workflow_table.c.wid, 4, 1000), Integer
                    )
                )
            ).where(self.workflow_table.c.wid.like("wf_%"))
        ).scalar()
        new_wid = f"wf_{(max_wid + 1) if max_wid else 1}"
        workflow_entry = db.session.execute(
            select(self.workflow_static_table).where(
                self.workflow_static_table.c.action == "update",
                self.workflow_static_table.c.type == "single",
                self.workflow_static_table.c.prop_type == "organization",
                self.workflow_static_table.c.is_new == 0,
            )
        ).fetchone()
        # Inserting the record in workflow Table

        workflow_data = {
            "wid": new_wid,
            "prop_id": workflow_entry.prop_id,
            "org_hierarchy_record_id": record_id,
            "dyn_col_1": "Organization",
            "dyn_col_2": copy_org_data["org_name"],
            "dyn_col_3": None,
            "dyn_col_4": None,
            "created_date": db.func.now(),
            "email_id": get_user_from_token()[3],
            "updated_date": db.func.now(),
            "is_deleted": 0,
            "wf_status": "Pending",
            "wf_reviewer_1_name": None,
            "wf_reviewer_2_name": None,
            "requested_by": copy_org_data["updated_by"],
            "wf_reviewer_1_status": "Pending",
            "wf_reviewer_1_status_date": None,
            "wf_reviewer_2_status": "Pending",
            "wf_reviewer_2_status_date": None,
            "typeof_action": request_from_user["action"],
            "typeof_cr": (
                "Single" if len(request_from_user["prop_val"]) == 1 else "Multiple"
            ),
            "Comments": None,
        }
        db.session.execute(self.workflow_table.insert().values(workflow_data))
        db.session.commit()

    def handle_deactivate_mapping(self, deactivation_record):
        """Processes the deactivation mapping workflow."""
        org_names = []
        org_names_str = ""

        if deactivation_record["prop_type"] == "mapping_record_id":

            for hierarchy_data in deactivation_record.get("prop_val", []):
                # Check if a deactivation request is already under review
                is_deactivation_requested = (
                    db.session.query(self.org_hier_mapping_table)
                    .filter(
                        self.org_hier_mapping_table.c.approval_1_status == "Pending",
                        self.org_hier_mapping_table.c.record_id
                        == hierarchy_data["record_id"],
                        self.org_hier_mapping_table.c.approval_2_status == "Pending",
                    )
                    .first()
                )
                is_deactivation_approved = (
                    db.session.query(self.org_hier_mapping_table)
                    .filter(
                        self.workflow_table.c.wf_status == "Approved",
                        self.workflow_table.c.mapping_record_id
                        == hierarchy_data["record_id"],
                        self.workflow_table.c.typeof_action == "deactivate",
                    )
                    .first()
                )
                if is_deactivation_requested:
                    return {
                        "message": "The request to deactivate the organization is currently under review."
                    }, 200
                if is_deactivation_approved:
                    return {
                        "message": "The request to deactivate the organization is already approved."
                    }, 200

                new_wid = self.generate_workflow_id()
                self.prepare_mapping_workflow_records(hierarchy_data, new_wid)

        else:
            for each_record in deactivation_record["prop_val"]:

                # Check if a deactivation request is already under review
                is_exists = db.session.execute(
                    select(self.org_hierarchy_table).where(
                        self.org_hierarchy_table.c.org_id == each_record["org_id"]
                    )
                ).fetchone()
                is_deactivation_requested = (
                    db.session.query(self.workflow_table)
                    .filter(
                        self.workflow_table.c.wf_status == "Pending",
                        self.workflow_table.c.dyn_col_2
                        == is_exists._mapping["org_name"],
                        self.workflow_table.c.typeof_action == "deactivate",
                    )
                    .first()
                )

                if is_deactivation_requested:
                    return {
                        "message": "The request to deactivate the organization is currently under review."
                    }, 200

                # Fetch and copy the original record
                original_record = (
                    db.session.query(self.org_hierarchy_table)
                    .filter(self.org_hierarchy_table.c.org_id == each_record["org_id"])
                    .first()
                )

                org_names.append(original_record._mapping.get("org_name"))
                if original_record:
                    record_copy = self.prepare_record_copy(original_record)

                    # Insert the copied record and retrieve its ID
                    result = db.session.execute(
                        self.org_hierarchy_table.insert()
                        .values(record_copy)
                        .returning(self.org_hierarchy_table.c.record_id)
                    )
                    record_id = result.scalar()

            # Commit the transaction
            org_names_str = ", ".join(org_names)
            db.session.commit()
            self.work_flow_creation(record_id, record_copy, deactivation_record)
        return {
            "status": "success",
            "message": f"Deactivation request for deactivating {org_names_str} has been sent to approver",
        }, 200

    def handle_check_associations(self, deactivation_record):
        """Checks for associations in the hierarchy."""
        for each_record in deactivation_record["prop_val"]:

            # Fetch organization hierarchy record
            return self.fetch_associated_records(each_record["org_id"])
        return {"message": "No associations found."}, 200

    def fetch_associated_records(self, org_id):
        # Fetch organization hierarchy record
        org_hierarchy_record = db.session.execute(
            select(
                self.org_hierarchy_table.c.org_level,
                self.org_hierarchy_table.c.org_name,
            ).where(self.org_hierarchy_table.c.org_id == org_id)
        ).fetchone()

        if org_hierarchy_record:
            org_hierarchy_record = dict(org_hierarchy_record._mapping)
            column_name = f"level{org_hierarchy_record['org_level']}"
            column = getattr(self.org_hierarchy_table.c, column_name)

            # Query child organizations
            child_orgs_query = select(self.org_hierarchy_table.c.org_name).where(
                column == org_hierarchy_record["org_name"]
            )
            child_orgs = db.session.execute(child_orgs_query).fetchall()
            child_orgs = [
                dict(org._mapping)["org_name"]
                for org in child_orgs
                if dict(org._mapping)["org_name"] != org_hierarchy_record["org_name"]
            ]
        else:
            # If no hierarchy record exists, return early
            return {
                "org_id": org_id,
                "associated_child_organizations": None,
                "mapping_association": None,
                "KPI Input Association": None,
            }, 404

        # Query KPI input records
        kpi_input_query = select(
            self.kpi_input.c.kpi_id, self.kpi_input.c.reporting_period
        ).where(self.kpi_input.c.org_id == org_id)

        # Convert date objects to strings and prepare KPI records
        kpi_records = [
            {
                key: (value.isoformat() if isinstance(value, date) else value)
                for key, value in dict(record._mapping).items()
            }
            for record in db.session.execute(kpi_input_query).fetchall()
        ]

        # Query related KPI master data for each KPI record
        for each_kpi_record in kpi_records:
            kpi_master_query = select(
                self.kpi_master.c.kpi_name, self.kpi_master.c.sector
            ).where(self.kpi_master.c.kpi_id == each_kpi_record["kpi_id"])

            # Fetch KPI master record
            kpi_master_record = db.session.execute(kpi_master_query).fetchone()
            if kpi_master_record:
                # Update each KPI record with master data
                each_kpi_record.update(dict(kpi_master_record._mapping))

        # # Query hierarchy mapping associations
        # mapping_query = select(self.org_hier_mapping_table.c.mapping_id).where(
        #     self.org_hier_mapping_table.c.org_id == org_id
        # )
        # mapping_assoc = db.session.execute(mapping_query).fetchall()
        # # Process mapping associations
        if org_id is not None:
            get_mapping_id = [
                each_record._mapping["mapping_id"]
                for each_record in db.session.execute(
                    select(distinct(self.org_hier_mapping_table.c.mapping_id)).where(
                        self.org_hier_mapping_table.c.org_id == org_id
                    )
                ).fetchall()
            ]
        mapping_association = []
        for each_mapping_id in get_mapping_id:
            mapping_association.extend(
                self.org_process_mapping_helper._get_org_hierarchy_mapping_records(
                    each_mapping_id, org_id
                )
            )

        return {
            "org_id": org_id,
            "associated_child_organizations": child_orgs,
            "mapping_association": mapping_association,
            "KPI Input Association": kpi_records,
        }, 200

    def prepare_record_copy(self, original_record):
        """Prepares a copy of the original record with updated values."""
        record_copy = (
            original_record._asdict()
            if hasattr(original_record, "_asdict")
            else dict(original_record)
        )
        record_copy.pop("record_id", None)  # Remove identity column
        record_copy.update(
            {
                "rec_end_date": None,
                "rec_start_date": date.today(),
                "approval_1_by": None,
                "approval_1_status": "Pending",
                "approval_1_date": None,
                "approval_2_by": None,
                "approval_2_status": "Pending",
                "approval_2_date": None,
                "created_date": date.today(),
                "updated_date": date.today(),
                "record_cut_over_date": None,
                "updated_by": get_user_from_token()[1],
            }
        )
        return record_copy

    def construct_hier_table_response(self, record, approval_status):
        # Create a dictionary for the current record
        org_hierarchy_table_data = {
            "org_id": record.org_id,
            "record_id": record.record_id,
            "org_name": record.org_name,
            "hier_type": record.hier_type,
            "org_level": record.org_level,
            "is_deleted": record.is_deleted,
            "h_id": record.h_id,
            "status": approval_status,
        }

        # Dynamically handle levels and their corresponding org_id mappings
        for level in range(1, 8):  # Levels 1 through 7
            level_key = f"level{level}"
            org_hierarchy_table_data[level_key] = getattr(record, level_key, "") or ""
            # if level <= 2:  # Add org_id mapping for level1 and level2 only
            org_hierarchy_table_data[f"{level_key}_org_id"] = (
                self.org_process_mapping_helper.replace_org_name_by_org_id(
                    getattr(record, level_key, "") or ""
                )
            )

    def approval_all_parent_and_leaf(
        self, org_id_prev_rcd, new_record, approval_status_key
    ):

        for (each_parent_level,) in range(1, org_id_prev_rcd._mapping.get("org_level")):
            level_pt_org = f"level{each_parent_level}"
            exists = db.session.execute(
                select(self.org_hierarchy_table).where(
                    self.org_hierarchy_table.c.org_name == level_pt_org,
                    self.org_hierarchy_table.c.is_deleted == 0,
                    getattr(self.org_hierarchy_table.c, f"{approval_status_key}")
                    == approval_status_key,  # condition 3
                )
            ).fetchone()  # count() returns the number of matching rows
            if not exists:
                db.session.execute(
                    self.org_hierarchy_table.update()
                    .where(
                        self.org_hierarchy_table.c.org_name == level_pt_org,
                        self.org_hierarchy_table.c.is_deleted == 0,
                        getattr(self.org_hierarchy_table.c, f"{approval_status_key}")
                        == approval_status_key,  # condition 3
                    )
                    .values(new_record)
                )
        return True

    def prepare_mapping_workflow_records(self, hierarchy_data, new_wid):
        all_wf_columns = [c.name for c in self.workflow_table.columns if c.name != "id"]
        all_mpg_columns = [
            c.name for c in self.org_hier_mapping_table.columns if c.name != "record_id"
        ]
        new_id = int(self.generate_hier_mapping_id())
        modified_wf_columns = {
            "wid": literal(new_wid),
            "wf_status": literal("Pending"),
            "wf_reviewer_1_status_date": None,
            "wf_reviewer_1_status": literal("Pending"),
            "wf_reviewer_1_name": None,
            "wf_reviewer_2_status_date": None,
            "wf_reviewer_2_status": literal("Pending"),
            "wf_reviewer_2_name": None,
            "created_date": literal(date.today()),
            "email_id": literal(get_user_from_token()[3]),
            "updated_date": literal(date.today()),
            "requested_by": literal(get_user_from_token()[1]),
            "updated_by": literal(get_user_from_token()[1]),
        }
        modified_mpg_columns = {
            "id": literal(new_id),
            "rec_end_date": None,
            "rec_start_date": literal(date.today()),
            "approval_1_by": None,
            "approval_1_status": literal("Pending"),
            "approval_1_date": None,
            "approval_2_by": None,
            "approval_2_status": literal("Pending"),
            "approval_2_date": None,
            "created_date": literal(date.today()),
            "updated_date": literal(date.today()),
            "updated_by": literal(get_user_from_token()[1]),
        }

        slected_wf_records = select(
            *[
                modified_wf_columns.get(col, self.workflow_table.c[col])
                for col in all_wf_columns
            ]
        ).where(
            self.workflow_table.c.mapping_record_id == hierarchy_data.get("record_id")
        )
        slected_mpg_records = select(
            *[
                modified_mpg_columns.get(col, self.org_hier_mapping_table.c[col])
                for col in all_mpg_columns
            ]
        ).where(
            self.org_hier_mapping_table.c.record_id == hierarchy_data.get("record_id")
        )
        insert_st_wf_records = insert(self.workflow_table).from_select(
            all_wf_columns, slected_wf_records
        )
        insert_st_mpg_records = insert(self.org_hier_mapping_table).from_select(
            all_mpg_columns, slected_mpg_records
        )
        db.session.execute(insert_st_wf_records)
        db.session.execute(insert_st_mpg_records)
        db.session.commit()

    def generate_workflow_id(self):

        max_wid = db.session.execute(
            select(
                func.max(
                    func.cast(
                        func.substring(self.workflow_table.c.wid, 4, 1000), Integer
                    )
                )
            ).where(self.workflow_table.c.wid.like("wf_%"))
        ).scalar()
        return f"wf_{(max_wid + 1) if max_wid else 1}"

    def generate_hier_mapping_id(self):

        mx_id_result = db.session.execute(
            select(func.max(self.org_hier_mapping_table.c.id))
        ).scalar()
        return mx_id_result + 1 if mx_id_result != None else 1

    def approve_workflow(self, current_user, new_work_flow_entry, data):

        new_record = {"updated_date": datetime.now(), "updated_by": current_user}
        old_record ={}
        response_message = []
        for each_work_flow in new_work_flow_entry:
            wid = each_work_flow._mapping.get("wid")
            # Handle approval 1 and 2 statuses
            for approval in [("approval_1"), ("approval_2")]:
                approval_status_key = f"{approval}_status"

                if approval_status_key in data:
                    if (
                        data[f"{approval}_status"] == "Rejected"
                        and ("Comments" not in data or data["Comments"] == "" )
                    ):
                        print('rejection')
                        response_message.append(
                            {
                                each_work_flow._mapping.get(
                                    "wid"
                                ): f"Comments , this field cannot be blank"
                            }
                        )
                        return response_message

                    digits = "".join(
                        char for char in approval_status_key if char.isdigit()
                    )

                    new_record[f"{approval}_status"] = data[f"{approval}_status"]
                    new_record[f"{approval}_date"] = datetime.now()
                    new_record[f"{approval}_by"] = current_user

                    # Update mapping record if provided

                    if (
                        each_work_flow._mapping["wf_reviewer_1_status"] == "Approved"
                        and "approval_2_status" in data
                        and data[f"{approval}_status"] == "Approved"
                    ):
                        new_record["rec_end_date"] = self.DEFAULT_REC_END_DATE
                        old_record["rec_end_date"] = func.now()
                  
                    if each_work_flow._mapping.get("mapping_record_id") != None:
                        exists = db.session.execute(
                            select(self.org_hier_mapping_table).where(
                                self.org_hier_mapping_table.c.record_id
                                == each_work_flow._mapping.get(
                                    "mapping_record_id"
                                ),  # condition 1
                                getattr(
                                    self.org_hier_mapping_table.c,
                                    f"{approval_status_key}",
                                )
                                == data[f"{approval_status_key}"],  # condition 3
                            )
                        ).fetchone()  # count() returns the number of matching rows
                        if  (each_work_flow._mapping["wf_status"] == "Approved" or  each_work_flow._mapping["wf_status"] == "Rejected") == True:
                            response_message = f'{  each_work_flow._mapping.get("wid")} already {each_work_flow._mapping["wf_status"]}'
                            return response_message
                        elif not exists and approval_status_key == "approval_1_status" and each_work_flow._mapping.get("typeof_action") != "deactivate" and  data[f"{approval_status_key}"] == "Approved":
                            

                            db.session.execute(
                            self.org_hier_mapping_table.update()
                            .where(
                                self.org_hier_mapping_table.c.id
                                == exists._mapping("id"),
                                self.org_hier_mapping_table.c.rec_end_date
                                ==self.DEFAULT_REC_END_DATE, 
                            )
                            .values(old_record)
                            )

                            
                                # Commit the transaction
                            db.session.commit()
                            response_message = f'{ each_work_flow._mapping.get("wid")} has been sent for approval 1'
                        elif exists and approval_status_key == "approval_1_status":
                            response_message = f'{ each_work_flow._mapping.get("wid")} already sent for approval 1'
                            return response_message
                        elif (
                            each_work_flow._mapping["wf_reviewer_1_status"] == 'Pending'
                            and approval == "approval_2" 
                         and each_work_flow._mapping["wf_status"] == 'Pending'):

                            response_message = f"Approval 2 Cant proceed because Approval 1 has not been processed for  {each_work_flow._mapping.get('wid')}"
                            
                            return response_message
                        elif (each_work_flow._mapping["wf_status"] == "Approved" or each_work_flow._mapping["wf_status"] == "Rejected") == True:
                            response_message = f'{  each_work_flow._mapping.get("wid")} updatation already {each_work_flow._mapping["wf_status"]}'
                            
                            return response_message
                        
                        elif ("approval_2_status" in data and (data[f"{approval}_status"] == "Approved" and each_work_flow._mapping["wf_status"] != "Approved") 
                              and  each_work_flow._mapping.get("typeof_action") != "deactivate" and  each_work_flow._mapping.get("typeof_action") != "update"):
                            response_message = f'{  each_work_flow._mapping.get("wid")} has been successfully Approved'

                        elif ("approval_2_status" in data and (data[f"{approval}_status"] == "Approved" and each_work_flow._mapping["wf_status"] != "Approved") 
                              and  each_work_flow._mapping.get("typeof_action") == "update"):
                            
                            org_id_prev_rcd = db.session.execute(
                            select(self.org_hier_mapping_table).where(
                                self.org_hier_mapping_table.c.record_id
                                == each_work_flow._mapping.get(
                                    "mapping_record_id"
                                ),  # condition 1
                                )
                            ).fetchone()
                            new_record["rec_end_date"] = self.DEFAULT_REC_END_DATE
                            new_prev_record = {"rec_end_date": datetime.now()}
                            # new_prev_record = {"is_deleted": 1}
                            db.session.execute(
                                self.org_hier_mapping_table.update()
                                .where(
                                    self.org_hier_mapping_table.c.org_id
                                    == org_id_prev_rcd._mapping.get("org_id"),
                                    self.org_hier_mapping_table.c.record_id
                                    != each_work_flow._mapping.get(
                                        "mapping_record_id"
                                    ),
                                    self.org_hierarchy_table.c.is_deleted == 0,
                                )
                                .values(new_prev_record)
                            )

                            # Commit the transaction
                            db.session.commit()
                            response_message = f'{ each_work_flow._mapping.get("wid")} has been successfully deactivated'
                            
                        elif ("approval_2_status" in data and data[f"{approval}_status"] == "Rejected" and each_work_flow._mapping["wf_status"] != "Rejected"):

                            new_record["rec_end_date"] = datetime.now()
                            new_record["is_deleted"] = 1
                            response_message = f'{  each_work_flow._mapping.get("wid")} has been successfully Rejected'
                            

                        elif (
                            "approval_1_status" in data
                            and data[f"{approval}_status"] == "Rejected" and each_work_flow._mapping["wf_status"] != "Rejected"
                        ):
                            new_record["rec_end_date"] = datetime.now()
                            new_record[f"approval_2_status"] = None
                            new_record[f"approval_2_date"] = None
                            new_record["is_deleted"] = 1
                            print('approval 1')
                            response_message = f'{  each_work_flow._mapping.get("wid")} has been successfully Rejected'
                            
                        elif (
                            (each_work_flow._mapping.get("typeof_action") == "deactivate" or each_work_flow._mapping.get("typeof_action") == "update")
                            and each_work_flow._mapping["org_hierarchy_record_id"] is None
                            and "approval_2_status" in data and (data["approval_2_status"] == "Approved")
                        ) :
                            org_id_prev_rcd = db.session.execute(
                            select(self.org_hier_mapping_table).where(
                                self.org_hier_mapping_table.c.record_id
                                == each_work_flow._mapping.get(
                                    "mapping_record_id"
                                ),  # condition 1
                                )
                            ).fetchone()
                            new_record["rec_end_date"] = self.DEFAULT_REC_END_DATE
                            new_prev_record = {"rec_end_date": datetime.now()}
                            # new_prev_record = {"is_deleted": 1}
                            db.session.execute(
                                self.org_hier_mapping_table.update()
                                .where(
                                    self.org_hier_mapping_table.c.org_id
                                    == org_id_prev_rcd._mapping.get("org_id"),
                                    self.org_hier_mapping_table.c.record_id
                                    != each_work_flow._mapping.get(
                                        "mapping_record_id"
                                    ),
                                    self.org_hierarchy_table.c.is_deleted == 0,
                                )
                                .values(new_prev_record)
                            )

                            # Commit the transaction
                            db.session.commit()
                            response_message = f'{ each_work_flow._mapping.get("wid")} has been successfully deactivated'
                       
                        db.session.execute(
                            self.org_hier_mapping_table.update()
                            .where(
                                self.org_hier_mapping_table.c.record_id
                                == each_work_flow._mapping.get("mapping_record_id"),
                                self.org_hier_mapping_table.c.is_deleted == 0,
                            )
                            .values(new_record)
                        )
                            # Commit the transaction
                        db.session.commit()
                      
                    elif each_work_flow._mapping.get("org_hierarchy_record_id") != None:
                      
                        exists = db.session.execute(
                            select(self.org_hierarchy_table).where(
                                self.org_hierarchy_table.c.record_id
                                == each_work_flow._mapping.get(
                                    "org_hierarchy_record_id"
                                ),  # condition 1
                                getattr(
                                    self.org_hierarchy_table.c,
                                    f"{approval_status_key}",
                                )
                                == data[f"{approval_status_key}"],  # condition 3
                            )
                        ).fetchone()  # count() returns the number of matching rows

                        # if exists is not None:

                        if exists is not None and approval == "approval_1":
                            response_message = f'{ each_work_flow._mapping.get("wid")} updatation already {"sent for approval 1" if each_work_flow._mapping["wf_status"] == "Pending" else each_work_flow._mapping["wf_status"]}'
                            
                            return response_message
                        if (each_work_flow._mapping["wf_reviewer_1_status"] == "Pending" ) and approval == "approval_2"  and each_work_flow._mapping["wf_status"] == 'Pending':
                            response_message.append(
                                f"Approval 2 Cant proceed because Approval 1 has not been processed for  {each_work_flow._mapping.get('wid')}"
                            )
                            return response_message
                        if exists is None and approval == "approval_1" and data[f"{approval_status_key}"] == "Approved" :

                            if (
                                each_work_flow._mapping["wf_status"] == "Pending"
                                or each_work_flow._mapping["wf_reviewer_1_status"]
                                == "Pending"
                                and approval == "approval_1" and  each_work_flow._mapping.get("typeof_action") != "deactivate"
                            ):
                                response_message = f'{ each_work_flow._mapping.get("wid")} has been sent for approval 1'
                                

                        if (
                            exists is None
                            and each_work_flow._mapping["wf_status"] == "Pending"
                            and each_work_flow._mapping["wf_reviewer_1_status"]
                            == "Approved"
                            and approval == "approval_2"
                            and data[f"{approval_status_key}"] == "Approved"
                        ):

                            response_message.append(
                                f'{ each_work_flow._mapping.get("wid")} has been successfully Approved'
                            )
                       
                        if ("approval_2_status" in data and data[f"{approval}_status"] == "Rejected" and each_work_flow._mapping["wf_status"] != "Rejected"):

                            new_record["rec_end_date"] = datetime.now()
                            new_record["is_deleted"] = 1
                            response_message = f'{  each_work_flow._mapping.get("wid")} has been successfully Rejected'

                        if each_work_flow._mapping.get("typeof_action") == "update" and ("approval_2_status" in data and data["approval_2_status"] == "Rejected" 
                                                                                              or "approval_1_status" in data and data["approval_1_status"] == "Rejected" ):
                            
                            print("Got into block 2")
                            org_id_prev_rcd = db.session.execute(
                            select(self.org_hierarchy_table).where(
                                self.org_hierarchy_table.c.record_id
                                == each_work_flow._mapping.get(
                                    "org_hierarchy_record_id"
                                ),  # condition 1
                            )
                        ).fetchone()
                            org_level = org_id_prev_rcd._mapping.get("org_level") 
                            level_column = f"level{org_level}"
                            print("org level", level_column)
                            print("old org_name", each_work_flow._mapping.get("dyn_col_2"))
                            db.session.execute(            
                                self.org_hierarchy_table.update()            
                                .where(                
                                    getattr(self.org_hierarchy_table.c, level_column) == each_work_flow._mapping.get("dyn_col_2"), 
                                    self.org_hierarchy_table.c.org_level >= org_level, 
                                    # self.org_hierarchy_table.c.org_id != sindata["Org_id"], 
                                    self.org_hierarchy_table.c.is_deleted == 0 
                                    ) 
                                .values(is_parent_pending='False') 
                                ) 
                            print("successful)")
                            db.session.commit()

                            

                        if (
                            "approval_1_status" in data
                            and data[f"{approval}_status"] == "Rejected" and each_work_flow._mapping["wf_status"] != "Rejected"
                        ):
                            new_record["rec_end_date"] = datetime.now()
                            new_record[f"approval_2_status"] = None
                            new_record[f"approval_2_date"] = None
                            new_record["is_deleted"] = 1
                            response_message = f'{  each_work_flow._mapping.get("wid")} has been successfully Rejected'
                            
                        if (each_work_flow._mapping["wf_status"] == "Approved" or each_work_flow._mapping["wf_status"] == "Rejected") == True:
                            response_message = f'{  each_work_flow._mapping.get("wid")} updatation already {each_work_flow._mapping["wf_status"]}'
                        
                            return response_message
                        org_id_prev_rcd = db.session.execute(
                            select(self.org_hierarchy_table).where(
                                self.org_hierarchy_table.c.record_id
                                == each_work_flow._mapping.get(
                                    "org_hierarchy_record_id"
                                ),  # condition 1
                            )
                        ).fetchone()

                        if (
                            each_work_flow._mapping.get("typeof_action") == "deactivate"
                            and "approval_2_status" in data and data[f"{approval}_status"] == "Approved" 
                        ) :

                            new_record["record_cut_over_date"] = datetime.now()
                            new_record["rec_end_date"] = self.DEFAULT_REC_END_DATE
                            new_prev_record = {"rec_end_date": datetime.now()}
                            # new_prev_record = {"is_deleted": 1}

                            db.session.execute(
                                self.org_hierarchy_table.update()
                                .where(
                                    self.org_hierarchy_table.c.org_id
                                    == org_id_prev_rcd._mapping.get("org_id"),
                                    self.org_hierarchy_table.c.record_id
                                    != each_work_flow._mapping.get(
                                        "org_hierarchy_record_id"
                                    ),
                                    self.org_hierarchy_table.c.is_deleted == 0,
                                )
                                .values(new_prev_record)
                            )

                            # Commit the transaction
                            db.session.commit()
                            response_message.append(f'{ each_work_flow._mapping.get("wid")} has been successfully deactivated')

                        if (
                            "approval_2_status" in data
                            and each_work_flow._mapping.get("typeof_action") == "update"
                            and data[f"approval_2_status"] == "Approved"
                        ):

                            new_record["record_cut_over_date"] = (
                                self.DEFAULT_REC_END_DATE
                            )
                            new_record["rec_end_date"] = self.DEFAULT_REC_END_DATE
                            new_record["rec_start_date"] = datetime.now()
                            new_prev_record = {"rec_end_date": datetime.now()}

                            db.session.execute(
                                self.org_hierarchy_table.update()
                                .where(
                                    self.org_hierarchy_table.c.org_id
                                    == org_id_prev_rcd._mapping.get("org_id"),
                                    self.org_hierarchy_table.c.record_id
                                    != each_work_flow._mapping.get(
                                        "org_hierarchy_record_id"
                                    ),
                                    self.org_hierarchy_table.c.rec_end_date
                                    == self.DEFAULT_REC_END_DATE,
                                    self.org_hierarchy_table.c.is_deleted == 0,
                                )
                                .values(new_prev_record)
                            )

                            level_column = (
                                f"level{org_id_prev_rcd._mapping.get('org_level')}"
                            )
                            db.session.execute(
                                self.org_hierarchy_table.update()
                                .where(
                                    getattr(self.org_hierarchy_table.c, level_column)
                                    == each_work_flow._mapping.get("dyn_col_2"),
                                    self.org_hierarchy_table.c.org_level
                                    > org_id_prev_rcd._mapping.get("org_level"),
                                    # self.org_hierarchy_table.c.org_id != sindata["Org_id"],
                                    self.org_hierarchy_table.c.is_deleted == 0,
                                    
                                )
                                .values(
                                    is_parent_pending=None,
                                    **{
                                        level_column: org_id_prev_rcd._mapping.get(
                                            "org_name"
                                        )
                                    },
                                )
                            )

                            # # Commit the transaction
                            db.session.commit()
                            response_message.append(f'{ each_work_flow._mapping.get("wid")} has been successfully updated')
                        db.session.execute(
                            self.org_hierarchy_table.update()
                            .where(
                                self.org_hierarchy_table.c.record_id
                                == each_work_flow._mapping.get(
                                    "org_hierarchy_record_id"
                                ),
                                self.org_hierarchy_table.c.is_deleted == 0,
                            )
                            .values(new_record)
                        )
                        # Define the update statement

                    update_stmt = (
                        update(self.workflow_table)
                        .where(
                            self.workflow_table.c.wid == wid
                        )  
                        .values(
                            **{
                                f"wf_reviewer_{digits}_status": data[
                                    f"{approval}_status"
                                ],
                                f"reviewer_{digits}_email_id" : get_user_from_token()[3],
                                f"wf_reviewer_{digits}_status_date": datetime.now(),
                                f"wf_reviewer_{digits}_name": current_user,
                                "updated_date": datetime.now(),
                                "Comments": data["Comments"] if "Comments" in data else None,
                                "wf_status": (
                                    "Approved"
                                    if each_work_flow._mapping.get(
                                        "wf_reviewer_1_status"
                                    )
                                    == "Approved"
                                    and "approval_2_status" in data
                                    and data[f"approval_2_status"] == "Approved"
                                
                                    else "Pending"
                                ) if data[f"{approval}_status"] != 'Rejected' else 'Rejected',
                            }
                        )
                    )
                    # Execute the update statement
                    db.session.execute(update_stmt)
                    # Commit the transaction
                    db.session.commit()
        return response_message
