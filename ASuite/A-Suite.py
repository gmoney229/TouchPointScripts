#!python3

#roles=Finance

# Imports
import re
import json

from xml.etree import cElementTree as ElementTree


# Variables
__author__ = "Gavin Murphy"
__email__ = "gmurphy@stannparish.org"


MY_CONFIGURATION = {
    "1091": {
        "description": "Stretch Goal: definition of what the report does",
        "content": {
            "id": 1091,
            "name": "ReturnedRefundTransAcct",
            "type_id": 4
        },
        "vars": {
            "StartDate": {
                "name": "StartDate",
                "type": "date",
                "default": "Most Recent Monday that was not this week",
                "min": "",
                "max": ""
            },
            "EndDate": {
                "name": "EndDate",
                "type": "date",
                "default": "Most Recent Sunday?",
                "min": "",
                "max": ""
            }
        }
    },
    "1119": {
        "description": "Stretch Goal: definition of what the report does",
        "content": {
            "id": 1119,
            "name": "MobileGivingReport",
            "type_id": 4
        },
        "vars": {
            "StartDate": {
                "name": "StartDate",
                "type": "date"
            },
            "EndDate": {
                "name": "EndDate",
                "type": "date"
            },
            "group_results": {
                "name": "group_results",
                "type": "str",
                "possible_values": [
                    "no",
                    "BY_FUND"
                ]
            }
        }
    },
    "1145": {
        "description": "Stretch Goal: definition of what the report does",
        "content": {
            "id": 1145,
            "name": "_TestingBox",
            "type_id": 4
        },
        "vars": {
            "StartDate": {
                "name": "StartDate",
                "type": "date"
            },
            "EndDate": {
                "name": "EndDate",
                "type": "date"
            },
            "group_results": {
                "name": "group_results",
                "type": "str",
                "possible_values": [
                    "no",
                    "BY_FUND"
                ]
            }
        }
    }
}


A_SUITE_HTML = """
<div class="box box-responsive"></div>
<div class="box-content">
    <h4>{{Title}}</h4>
    <form method="post" enctype="multipart/form-data">
        <div class="row">
            <div class="col-sm-3">
                <div class="form-group">
                    <label for="sdate" class="control-label">Start Date</label>
                    <div class="input-group date">
                        <input class="form-control" data-val="true"
                                data-val-date="The field DateTime must be a date."
                                data-val-required="The Deposit Date field is required."
                                id="sdate" name="sdate" type="text" value="">
                        <span class="input-group-addon hidden-xs hidden-sm"><i class="fa fa-calendar"></i></span>
                        <input disabled="disabled" id="dateIso" name="dateIso" type="hidden" value="">
                    </div>
                </div>
            </div>
            <div class="col-sm-3">
                <div class="form-group">
                    <label for="edate" class="control-label">End Date</label>
                    <div class="input-group date">
                        <input class="form-control" data-val="true"
                                data-val-date="The field DateTime must be a date."
                                data-val-required="The Deposit Date field is required."
                                id="edate" name="edate" type="text" value="">
                        <span class="input-group-addon hidden-xs hidden-sm"><i class="fa fa-calendar"></i></span>
                        <input disabled="disabled" id="dateIso" name="dateIso" type="hidden" value="">
                    </div>
                </div>
            </div>
        </div>
        <div class="row">
            <div class="col-sm-2">
                <div class="form-group">
                    <label for="runnableReport" class="control-label">Report Selection</label>
                    <select name="runnableReport" class="form-control">
                        <option value=0> -- select a Report -- </option>
                    {{#each runnable_reports}}
                        <option value="{{Id}}">{{Name}}</option>
                    {{/each}}
                    </select>
                </div>
            </div>
        </div>
        <button type="submit" class="btn btn-primary">Submit</button>
    </form>
</div>
</div>
"""

# Classes



# Functions
def print_pgph(msg):
    print("<p>{}</p>".format(msg))


def process_get():

    value_tbl = ""

    for reprt in MY_CONFIGURATION.values():
        if value_tbl == "":
            value_tbl = value_tbl + '''
                ({},'{}')
            '''.format(reprt['content']['id'], reprt['content']['name'])
        else:
            value_tbl = value_tbl + ''',
                ({},'{}')
            '''.format(reprt['content']['id'], reprt['content']['name'])

    # well I am sure there is a better way to do this... but kindah curious
    # https://www.sqlshack.com/the-table-variable-in-sql-server/
    # now I need the variables in here...
    temp_sql_for_dapper_rows = '''
        DECLARE @MyConfigurationReports TABLE(Id INT, Name VARCHAR(40))
        
        INSERT INTO @MyConfigurationReports
        VALUES 
        {}
        SELECT * FROM @MyConfigurationReports
    '''.format(value_tbl)
    Data.runnable_reports = q.QuerySql(temp_sql_for_dapper_rows)

    model.Form = model.RenderTemplate(A_SUITE_HTML)


def process_post():
    # TODO Format the url query params with native python dict format param method
    # maybe there is a way to directly call the SQL Report but for now this is good :)?
    # start_date = model.ParseDate(model.Data.sdate)
    # end_date = model.ParseDate(model.Data.edate)
    id_of_sql_script = model.Data.runnableReport
    # print('<pre>')
    # print(id_of_sql_script)
    # print('</pre>')
    print('REDIRECT=/RunScript/{0}'.format(MY_CONFIGURATION[id_of_sql_script]['content']['name']))

    # raise NotImplemented


if model.HttpMethod.lower() == 'get':
    process_get()

elif model.HttpMethod.lower() == 'post':
    process_post()
