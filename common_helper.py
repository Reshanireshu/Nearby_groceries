import requests
from datetime import datetime
import pandas as pd
import numpy as np
from itertools import groupby
from sqlalchemy import or_

from constants.azure_auth_urls import graph_url
from flask import current_app
from db import db, Base
from sqlalchemy import select, case, desc, select

from helper.org_process_mapping_helper import OrgProcessMappingHelper


class CommonHelper:

    def __init__(self):
        self.org_hier_mapping_table = Base.metadata.tables["db_nxtgen.Org_Hier_Mapping"]
        self.org_hierarchy_table = Base.metadata.tables["db_nxtgen.Org_Hierarchy"]
        self.high_date = "9999-01-01 00:00:00.000"
        self.workflow_table = Base.metadata.tables["db_nxtgen.Workflow"]
        self.org_process_mapping_helper = OrgProcessMappingHelper()

    def get_user_details(self, headers):
        user_details = requests.get(graph_url, headers=headers)

        return user_details

    def find_max_length(self, obj):
        return len(max(obj.values(), key=lambda x: len(x)))

    def cleaned_dict(self, list_dict):
        cleaned_data = []
        for item in list_dict:
            cleaned_item = {k: v for k, v in item.items() if v}
            cleaned_data.append(cleaned_item)
        return cleaned_data

    def build_tree_view_json(self, list_of_dict):
        hierarchy = []
        # print('data .....',list_of_dict)
        for item in list_of_dict:
            # print('item.....',item)
            org_id = item["org_id"]
            org_name = item["org_name"]
            org_level = int(item["org_level"])
            # orgName = item[f"level{org}"]
            # Start from the top level
            current_level = hierarchy

            # Traverse through each level and build the hierarchy
            for level in range(1, org_level + 1):
                level_key = f"level{level}"
                level_value = item.get(level_key)
                if not level_value:
                    break

                # Find or create the node for the current level
                # print('current_level.....',current_level['org_id'])
                existing_node = next(
                    (node for node in current_level if node["orgName"] == level_value),
                    None,
                )
                #     # Once we've traversed all levels, make sure the org_name node has the org_id
                if level_value == org_name:
                    # print('current level....',current_level)
                    existing_node = next(
                        (node for node in current_level if node["orgName"] == org_name),
                        None,
                    )
                    if existing_node:
                        existing_node["org_id"] = org_id

                if not existing_node:
                    new_node = {
                        "org_id": item.get(
                            "org_id"
                        ),  # Set org_id only if label matches org_name
                        "orgName": level_value,
                        "parentOrgName": (
                            item.get(f"level{level-1}") if level > 1 else level_value
                        ),
                        "children": [],
                    }
                    current_level.append(new_node)
                    current_level = new_node["children"]
                else:
                    current_level = existing_node["children"]

        return hierarchy

    def remove_unnecessary_keys_in_list_of_dict(self, list_of_dict, keys_to_remove):
        for record in list_of_dict:

            for key in keys_to_remove:
                record.pop(key, None)  # Use pop with default None to avoid KeyError
        return list_of_dict

    def serialize_row(self, row):
        """
        Helper function to convert datetime objects to strings for JSON serialization.
        Additionally, remap keys as needed.
        """
        # Key mapping dictionary
        key_mapping = {
            "dyn_col_1": "request_details",
            "dyn_col_2": "from",
            "dyn_col_3": "to",
        }

        # Serialize the row and handle datetime objects
        serialized = {}
        for key, value in row.items():
            # Rename keys based on the key_mapping dictionary
            new_key = key_mapping.get(key, key)

            if isinstance(value, datetime):
                # Convert datetime to string (ISO 8601 format)
                serialized[new_key] = value.isoformat() if value else None
            else:
                serialized[new_key] = value

        return serialized

    def groupby_field(self, list_of_dict):
        if not list_of_dict:
            return []
        group_by_record = pd.DataFrame(list_of_dict)
        group_by_cols = ["wid", "typeof_action", "typeof_cr", "wf_status"]

        group_by_cols = [col for col in group_by_cols if col in group_by_record.columns]
        grouped_records = (
            group_by_record.groupby(group_by_cols, dropna=False)
            .apply(self.process_group)
            .tolist()
        )
        return grouped_records

    def process_group(self, x):
        
        x = x.replace({np.nan: None})
        mapping_info = []

        if x["depedent_workflow_id"].iloc[0] is not None:
            depedent_workflow_obj = (
                db.session.execute(
                    select(self.workflow_table).where(
                        self.workflow_table.c.wid
                        == str(x["depedent_workflow_id"].iloc[0])
                    )
                )
                .fetchone()
            )
            if depedent_workflow_obj is not None:
                depedent_workflow_obj = depedent_workflow_obj._mapping
        response = {
            "wid": x["wid"].iloc[0],
            "typeof_action": x["typeof_action"].iloc[0],
            "typeof_cr": x["typeof_cr"].iloc[0],
            "approver_1_name": x["wf_reviewer_1_name"].iloc[0],
            "approver_1_Date": x["wf_reviewer_1_status_date"].iloc[0],
            "approver_1_status": x["wf_reviewer_1_status"].iloc[0],
            "approver_2_name": x["wf_reviewer_2_name"].iloc[0],
            "approver_2_Date": x["wf_reviewer_2_status_date"].iloc[0],
            "approver_2_status": x["wf_reviewer_2_status"].iloc[0],
            "requested_by": x["requested_by"].iloc[0],
            "requested_on": x["created_date"].iloc[0],
            "Comments": x["Comments"].iloc[0],
            "depedent_workflow_id": (
                {
                    "status": depedent_workflow_obj["wf_status"],
                    "wid": depedent_workflow_obj["wid"],
                }
                if x["depedent_workflow_id"].iloc[0]
                else []
            ),
        }
        formatted_mapping_records = {}
        get_org_record = {}
        for index,row in x.iterrows():
            if 'level' not in  row.to_dict()['request_details'] :
                formatted_mapping_records[row.to_dict()['request_details']] = {'from':row.to_dict()['from'],'to':row.to_dict()['to']} if row.to_dict()['to'] is not None else row.to_dict()['from']
                
        if x["mapping_record_id"].iloc[0] is not None:
            
            formatted_mapping_record = {**formatted_mapping_records , **self.formatted_org_mapping_records(int(x["mapping_record_id"].iloc[0]))
            }
            mapping_info.append(formatted_mapping_record)
            
            
            
            get_org_record =  db.session.execute(
                    select(self.org_hierarchy_table).where(
                        self.org_hierarchy_table.c.org_id
                        == formatted_mapping_record.get('org_id')
                    )
                    ).fetchone()._mapping
            
        elif  x["org_hierarchy_record_id"].iloc[0] is not None:
            length_org_rcd = len(x["org_hierarchy_record_id"])
            if length_org_rcd>1:
                get_org_record =  db.session.execute(
                  select(self.org_hierarchy_table).where(
                        self.org_hierarchy_table.c.record_id
                        == int(x["org_hierarchy_record_id"].iloc[length_org_rcd-1] )
                    )
                    ).fetchone()._mapping
            else:
                get_org_record =  db.session.execute(
                    select(self.org_hierarchy_table).where(
                            self.org_hierarchy_table.c.record_id
                            == int(x["org_hierarchy_record_id"].iloc[0] )
                        )
                        ).fetchone()._mapping
            
        org_info = []
        org_level_name = {}
        # for each_level_ix in range(1,int(get_org_record.get('org_level'))+1):
           
        #     each_org_hier_level = f'level{each_level_ix}'


        #     org_record_prev = db.session.execute(
        #         select(self.org_hierarchy_table)
        #         .where(
        #             self.org_hierarchy_table.c.org_name == get_org_record.get(each_org_hier_level)
        #         )
        #         .order_by(
        #             case(
        #                 (self.org_hierarchy_table.c.rec_end_date == None, 0),
        #                 else_=1
        #             ),
        #             desc(self.org_hierarchy_table.c.rec_end_date)
        #         )
        #     ).fetchone()

        #     org_record = db.session.execute(
        #         select(self.org_hierarchy_table)
        #         .where(
        #             self.org_hierarchy_table.c.org_id == org_record_prev._mapping.get('org_id')
        #         )
        #         .order_by(
        #             case(
        #                 (self.org_hierarchy_table.c.rec_end_date == None, 0),
        #                 else_=1
        #             ),
        #             desc(self.org_hierarchy_table.c.rec_end_date)
        #         )
        #     ).fetchone()


        #     formatted_org_record = self.formatted_org_records(org_record)
        #     if x["typeof_action"].iloc[0] == "update" and x["mapping_record_id"].iloc[0] is None:
                
        #         formatted_org_record["from_orgname"] = x["from"].iloc[0]
        #         formatted_org_record["to_orgname"] = x["to"].iloc[0]
        #         del formatted_org_record["org_name"]
        #     org_info.append(formatted_org_record)
        #     org_level_name[each_org_hier_level] = (
        #             get_org_record.get(each_org_hier_level)
        #         )

        
        org_names = [get_org_record.get(f'level{ix}') for ix in range(1, int(get_org_record.get('org_level')) + 1)]

    
        org_name_records = db.session.execute(
            select(self.org_hierarchy_table)
            .where(self.org_hierarchy_table.c.org_name.in_(org_names))
            .order_by(
                case((self.org_hierarchy_table.c.rec_end_date == None, 0), else_=1),
                desc(self.org_hierarchy_table.c.rec_end_date)
            )
        ).fetchall()

     
        org_ids = list({record._mapping['org_id'] for record in org_name_records})

     
        org_id_records = db.session.execute(
            select(self.org_hierarchy_table)
            .where(self.org_hierarchy_table.c.org_id.in_(org_ids))
            .order_by(
                case((self.org_hierarchy_table.c.rec_end_date == None, 0), else_=1),
                desc(self.org_hierarchy_table.c.rec_end_date)
            )
        ).fetchall()

       
        org_name_map = {}
        for record in org_name_records:
            org_name = record._mapping['org_name']
            if org_name not in org_name_map:
                org_name_map[org_name] = record

        org_id_map = {}
        for record in org_id_records:
            org_id = record._mapping['org_id']
            if org_id not in org_id_map:
                org_id_map[org_id] = record

      
        for each_level_ix in range(1, int(get_org_record.get('org_level')) + 1):
            each_org_hier_level = f'level{each_level_ix}'
            org_name = get_org_record.get(each_org_hier_level)

            org_record_prev = org_name_map.get(org_name)
            org_record = org_id_map.get(org_record_prev._mapping['org_id']) if org_record_prev else None

            if org_record:
                formatted_org_record = self.formatted_org_records(org_record)
                if x["typeof_action"].iloc[0] == "update" and x["mapping_record_id"].iloc[0] is None:
                    formatted_org_record["from_orgname"] = x["from"].iloc[0]
                    formatted_org_record["to_orgname"] = x["to"].iloc[0]
                    del formatted_org_record["org_name"]
                org_info.append(formatted_org_record)
                org_level_name[each_org_hier_level] = org_name


    
        response["mapping_info"] = mapping_info if mapping_info else []
        response["org_hierarchy_info"] = org_info if org_info else []
        response["org_level_name"] = org_level_name if org_level_name else []
        return response

    def formatted_org_mapping_records(self, record_id):

        mapping_record = db.session.execute(
            select(self.org_hier_mapping_table).where(
                self.org_hier_mapping_table.c.record_id == record_id
            )
        ).fetchone()
        formatted_mapping_record = {}
        if mapping_record is not None:

            mapping_record = mapping_record._mapping
           
           
            # formatted_mapping_record = (
            #     self.org_process_mapping_helper.forming_mapping_title_val(
            #         mapping_record
            #     )
            # )
           
            # # del formatted_mapping_record["org_id"]
            # del formatted_mapping_record["id"]
            # del formatted_mapping_record["status"]

            formatted_mapping_record["isDeactivated"] = (
                mapping_record["rec_end_date"] is not None
                and mapping_record["rec_end_date"] < datetime.now()
            )
            formatted_mapping_record["org_id"] = mapping_record["org_id"]
            formatted_mapping_record["record_id"] = mapping_record["record_id"]
            formatted_mapping_record["updated_date"] = mapping_record["updated_date"].isoformat() if mapping_record["updated_date"] else None
            formatted_mapping_record["created_date"] = mapping_record["created_date"].isoformat() if mapping_record["created_date"] else None
            print('record id',record_id)
            print('formatted_mapping_record',formatted_mapping_record)               
            return formatted_mapping_record
    def formatted_org_records(self,org_record):

        org_record = org_record._mapping
        formatted_org_record = {}

        formatted_org_record["org_name"] = org_record["org_name"]
        formatted_org_record["org_id"] = org_record["org_id"]
        formatted_org_record["org_level"] = org_record.get(
            "org_level"
        )
        ct_key = int(org_record.get("org_level"))
        formatted_org_record["parent_org_name"] = (
            org_record[f"level{ct_key-1}"] if ct_key > 1 else None
        )

        formatted_org_record["mapping_record_id"] = None
        formatted_org_record["org_hierarchy_record_id"] = (
            org_record["record_id"]
        )
        formatted_org_record["isDeactivated"] = (
            org_record["record_cut_over_date"] <= datetime.now()
            if org_record["record_cut_over_date"]
            else False
        )
        return formatted_org_record
