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


NUM_LINES_TO_STRIP  = 6
MSP_TP_ID_FIELDNAME = 'TouchPoint ID'


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

        touchpoint_id = int(tp_id_field)

    except Exception as err:
        print_pgph('ERROR Cannot find the TouchPoint Id field {} in record {}'.format(MSP_TP_ID_FIELDNAME, ministr))
        raise err

    if not active_minister(ministr):
        print_pgph('INFO: NOT_ACTIVE This is not an active minister leaving them alone {}'.format(ministr))
        return


def active_minister(ministr):
    print_pgph("is this person still active?")



if model.HttpMethod.lower() == 'get':
    process_get()

elif model.HttpMethod.lower() == 'post':
    process_post()
