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


NUM_LINES_TO_STRIP              = 6
LOOKBACK_DAYS                   = 365
MSP_TP_ID_FIELDNAME             = 'TouchPoint ID'
MSP_ACTIVE_TIMING_FIELDNAME     = 'Last date used in a schedule'
MSP_REPLACEMENT_SUBGROUP_CODES  = {'CSH': 'Communion Sick and Homebound'}
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

    # NOTE would be way better do a find and replace but stripping lines is easier for now.
    #     thanks Google ?
    for _ in range(NUM_LINES_TO_STRIP):
        csv_file.readline()

    reader = csv.DictReader(csv_file)

    for row in reader:
        process_minister(row)


def process_minister(ministr):
    try:
        tp_id_field = ministr[MSP_TP_ID_FIELDNAME]
        if tp_id_field is None or tp_id_field == '':
            print_pgph("No touchpoint id defined in file for {}".format(ministr))
            return

        ministr['touchpoint_id'] = int(tp_id_field)

    except Exception as err:
        print_pgph('ERROR Cannot find the TouchPoint Id field {} in record {}'.format(MSP_TP_ID_FIELDNAME, ministr))
        raise err

    if not active_minister(ministr):
        print_pgph('INFO: NOT_ACTIVE This is not an active minister {}'.format(ministr))
        # check_drop_from_org(ministr['touchpoint_id'], TP_MSP_INVOLVEMENT_ID)
        print_pgph('WARNING: will drop if not active eventually for person {} in org {}'.format(ministr['touchpoint_id'], TP_MSP_INVOLVEMENT_ID))
        return

    # model.JoinOrg(ministr['touchpoint_id'], TP_MSP_INVOLVEMENT_ID)
    print_pgph('WARNING: will add to involvement eventually for person {} to org {}'.format(ministr['touchpoint_id'], TP_MSP_INVOLVEMENT_ID))

    load_subgroups(ministr, TP_MSP_INVOLVEMENT_ID)


def active_minister(ministr):
    last_time_used = model.ParseDate(ministr[MSP_ACTIVE_TIMING_FIELDNAME])
    days_ago = datetime.datetime.now() - datetime.timedelta(days=LOOKBACK_DAYS)
    # convert for compareto TouchPoint model DateTime
    days_ago_tpdt = model.ParseDate(days_ago.strftime('%Y-%m-%d'))

    return (last_time_used > days_ago_tpdt)


def check_drop_from_org(people_id, org_id):
    if not model.InOrg(people_id, org_id):
        return

    print_pgph('WARNING: removing PeopleId {} from organization {}'.format(people_id, org_id))
    model.DropOrgMember(people_id, org_id)


def load_subgroups(ministr, org_id):

    pattern = r"\s+\[(.*?)\]"

    groups_no_subcat = re.sub(pattern, "", ministr['Ministry qualifications'])

    for group in groups_no_subcat.split(","):
        print_pgph("WARNING: adding PeopleId {} organization {}'s subgroup {}".format(ministr['touchpoint_id'], org_id, group))
        # model.AddSubGroup(ministr['touchpoint_id'], org_id, group)


if model.HttpMethod.lower() == 'get':
    process_get()

elif model.HttpMethod.lower() == 'post':
    process_post()
