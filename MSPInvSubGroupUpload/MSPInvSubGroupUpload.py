#!python3

#roles=Admin

# Imports
import csv
import io


# Variables
__author__ = "Gavin Murphy"
__email__ = "gmurphy@stannparish.org"


NUM_LINES_TO_STRIP = 6


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
        print_pgph(row)


if model.HttpMethod.lower() == 'get':
    process_get()

elif model.HttpMethod.lower() == 'post':
    process_post()
