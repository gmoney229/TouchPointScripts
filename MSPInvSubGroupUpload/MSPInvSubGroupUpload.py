#!python3

#roles=Admin

# Imports
import csv
import datetime
import io
import re
import json

from xml.etree import cElementTree as ElementTree


# Variables
__author__ = "Gavin Murphy"
__email__ = "gmurphy@stannparish.org"


LOOKBACK_DAYS                   = 365
MSP_TP_ID_FIELDNAME             = 'TouchPoint ID'
MSP_ACTIVE_TIMING_FIELDNAME     = 'Last date used in a schedule'
MSP_REPLACEMENT_SUBGROUP_CODES  = {'CSH': 'Communion Sick and Homebound'}
MSP_IGNORE_SUBGROUP_CODES       = {'Welcome+'}
TP_MSP_INVOLVEMENT_ID           = 1308


# Classes


# Functions
def print_pgph(msg):
    print("<p>{}</p>".format(msg))


def process_get():
    html = model.Content('UploadFile')
    model.Form = model.RenderTemplate(html)


def process_post():
    csv_file = io.StringIO(model.Data.file)

    reader = csv.DictReader(csv_file)

    ministrs_loaded = set()

    for row in reader:
        ministr_tp_id = process_minister(row)
        if ministr_tp_id:
            ministrs_loaded.add(ministr_tp_id)

    unload_ministers_not_in_file(ministrs_loaded)


def process_minister(ministr):
    try:
        tp_id_field = ministr[MSP_TP_ID_FIELDNAME]
        if tp_id_field is None or tp_id_field == '':
            print_pgph("No touchpoint id defined in file for {}".format(ministr))
            return

        ministr['touchpoint_id']    = int(tp_id_field)
        ministr['name_2']           = '{} {}, ({})'.format(ministr['First name'], ministr['Last name'], ministr['touchpoint_id'])

    except Exception as err:
        print_pgph('ERROR Cannot find the TouchPoint Id field {} in record {}'.format(MSP_TP_ID_FIELDNAME, ministr))
        raise err

    if not active_minister(ministr):
        # TODO put in an archive involvement
        print_pgph('INFO: NOT_ACTIVE This is not an active minister {}'.format(ministr['name_2'] ))
        check_drop_from_org(ministr['touchpoint_id'], TP_MSP_INVOLVEMENT_ID)
        return

    if not model.InOrg(ministr['touchpoint_id'], TP_MSP_INVOLVEMENT_ID):
        model.JoinOrg(TP_MSP_INVOLVEMENT_ID, ministr['touchpoint_id'])
        print_pgph('INFO: added to involvement for person {} to org {}'.format(ministr['name_2'] , TP_MSP_INVOLVEMENT_ID))

    load_min_qual_subgroups(ministr, TP_MSP_INVOLVEMENT_ID)

    return ministr['touchpoint_id']


def active_minister(ministr):
    last_time_used = model.ParseDate(ministr[MSP_ACTIVE_TIMING_FIELDNAME])
    days_ago = datetime.datetime.now() - datetime.timedelta(days=LOOKBACK_DAYS)
    # convert for compareto TouchPoint model DateTime
    days_ago_tpdt = model.ParseDate(days_ago.strftime('%Y-%m-%d'))

    return not ((last_time_used < days_ago_tpdt) or (ministr['Inactive'].upper() == 'YES'))


def check_drop_from_org(people_id, org_id):
    if not model.InOrg(people_id, org_id):
        return
    drop_member_from_org(people_id, org_id)


def drop_member_from_org(people_id, org_id):
    print_pgph('WARNING: removing PeopleId {} from organization {}'.format(people_id, org_id))
    model.DropOrgMember(people_id, org_id)


def load_min_qual_subgroups(ministr, org_id):
    sub_groups_from_file = get_ministers_subgroups(ministr['Ministry qualifications'])

    # ADD
    for sub_group in sub_groups_from_file:
        if model.InSubGroup(ministr['touchpoint_id'], org_id, sub_group):
            continue

        print_pgph("INFO: adding PeopleId {} organization {}'s subgroup {}".format(ministr['name_2'] , org_id, sub_group))
        model.AddSubGroup(ministr['touchpoint_id'], org_id, sub_group)

    # REMOVE old
    exists_sg_query = '''
    SELECT
        mt.Name
    FROM dbo.OrgMemMemTags ommt
    LEFT JOIN dbo.MemberTags mt ON mt.Id = ommt.MemberTagId
    WHERE ommt.PeopleId = {} AND ommt.OrgId = {};
    '''.format(ministr['touchpoint_id'], org_id)

    existing_tp_sub_groups  = [r.Name for r in q.QuerySql(exists_sg_query)]

    for existing_sg in existing_tp_sub_groups:
        if existing_sg not in sub_groups_from_file:
            print_pgph("WARNING: removing PeopleId {} organization {} from subgroup {}".format(ministr['name_2'] , org_id, existing_sg))
            model.RemoveSubGroup(ministr['touchpoint_id'], org_id, existing_sg)


def get_ministers_subgroups(ministr_qual):
    sub_groups  = []
    pattern     = r"\s+\[(.*?)\]"

    groups_no_subcat = re.sub(pattern, "", ministr_qual)

    sub_groups_raw =  groups_no_subcat.split(',')

    for group in sub_groups_raw:
        group = group.strip()
        if group in MSP_IGNORE_SUBGROUP_CODES:
            continue
        elif group in MSP_REPLACEMENT_SUBGROUP_CODES:
            sub_groups.append(MSP_REPLACEMENT_SUBGROUP_CODES[group])
        else:
            sub_groups.append(group)

    return sub_groups


def unload_ministers_not_in_file(ministrs_loaded):
    org_in_question = TP_MSP_INVOLVEMENT_ID
    exists_members_query = '''
    SELECT
        PeopleId
    FROM dbo.OrganizationMembers
    WHERE OrganizationId={};
    '''.format(org_in_question)

    ids_in_org = [r.PeopleId for r in q.QuerySql(exists_members_query)]

    for people_id in ids_in_org:
        if people_id not in ministrs_loaded:
            drop_member_from_org(people_id, org_in_question)


if model.HttpMethod.lower() == 'get':
    process_get()

elif model.HttpMethod.lower() == 'post':
    process_post()
