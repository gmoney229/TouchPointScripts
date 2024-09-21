#!python3

#roles=Finance

# Imports
import datetime
import json
import re

# Variables
__author__ = "Gavin Murphy"
__email__ = "gmurphy@stannparish.org"


HTML = """
<div class="box box-responsive"></div>
<div class="box-content">
    <h4>{{Title}}</h4>
    <form method="post" enctype="multipart/form-data">
        <div class="row">
            <div class="col-sm-2">
                <div class="form-group">
                    <label for="textContentJson" class="control-label">Text Content with batch json</label>
                    <select name="textContentJson" class="form-control">
                        <option value=0> -- select a Text Content -- </option>
                        {{#each text_contents}}
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


def process_get():
    txt_cont_sql = '''
        SELECT Id, Name
        FROM dbo.Content
        WHERE TypeID != 0
            AND Name LIKE '%.json%'
        ORDER BY DateCreated DESC
    '''
    Data.text_contents = q.QuerySql(txt_cont_sql)
    model.Form = model.RenderTemplate(HTML)

def process_post():
    find_sql = '''
    SELECT Body FROM dbo.Content WHERE Id = @text_content_id
    '''

    params = {"text_content_id": int(model.Data.textContentJson)}
    cont = q.QuerySqlTop1(find_sql, None, params)

    print('<pre>')
    print(cont)

    print('</pre>')


if model.HttpMethod.lower() == 'get':
    process_get()

elif model.HttpMethod.lower() == 'post':
    process_post()
