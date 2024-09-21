#!python3

#roles=Finance

# Imports
import datetime
import json
import re

# Variables
__author__ = "Gavin Murphy"
__email__ = "gmurphy@stannparish.org"


DEFAULT_CONTRIBUTION_TYPE = "Tax deductible"

CHOOSE_JSON_FILE_HTML = """
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
    model.Form = model.RenderTemplate(CHOOSE_JSON_FILE_HTML)

def process_post():
    find_sql = '''
    SELECT Body FROM dbo.Content WHERE Id = @text_content_id
    '''
    selected_text_content_id = int(model.Data.textContentJson)
    params = {"text_content_id": selected_text_content_id}
    cont = q.QuerySqlTop1(find_sql, None, params)

    if cont.Body is not None:
        batches = process_batch_json(cont.Body)
    else:
        print("<p>NOTICE: Content body is none: {}</p>".format(selected_text_content_id))
        return

    for id in batches:
        # NOTE I had a rough time getting the f string working here
        batch_link = "{}/Batches/Detail/{}".format(model.CmsHost, id)
        anchor = "<a href=\"{}\">{}</a>".format(batch_link, batch_link)
        print(anchor)


def process_batch_json(raw_json):
    batch_ids = []

    try:
        parsed_bdy = json.loads(raw_json)
        # TODO would be nice to make sure the json is good at this point
        #    plus I think you can run the data through a json schema checker and catch Exception

    except Exception as e:
        print("<p>ERROR: Failed to load json {}</p>".format(e))
        raise e

    # NOTE I think this could go away once jsonschema is in place
    if parsed_bdy is None or len(parsed_bdy) == 0:
        print("<p>NOTICE: json is empty not doing anything: {}</p>".format(parsed_bdy))
        return

    for batch in parsed_bdy.values():
        # NOTE TouchPoint does not like walrus operator either
        batch_id = make_the_batch(batch)

        if batch_id:
            batch_ids.append(batch_id)
        else:
            print("<p>NOTICE: Batch was not created in make_the_batch(): {}</p>".format(parsed_bdy))

    return batch_ids


def make_the_batch(bundle):
    # NOTE shoudn't lookup data be callable with out writing SQL in Python???
    #     (4, 5, 6) = (Online, Online Pledge, Pledge)
    batch_type_sql = '''
        SELECT Id, Description FROM lookup.BundleHeaderTypes WHERE Id NOT IN (4,5,6)
    '''
    bundle_header_types = {r.Description: r.Id for r in q.QuerySql(batch_type_sql)}

    batch_defaults = bundle['defaults']

    default_date = model.ParseDate(batch_defaults['date'])
    estimated_amount = bundle['estimated_amt']
    batch_type = bundle['batch_type']

    if batch_type not in bundle_header_types:
        print("<p>NOTICE: bundle_header_type NOT FOUND: {}</p>".format(batch_type))
        return

    batch_type_id = bundle_header_types[batch_type]

    bundle_header = model.GetBundleHeader(default_date, model.DateTime.Now, batch_type_id)

    bundle_contribs = bundle.get("contributions", [])

    if len(bundle_contribs) > 0:
        make_contributions_for_batch(bundle_header, bundle_contribs, batch_defaults)

    model.FinishBundle(bundle_header)
    return bundle_header.BundleHeaderId


def make_contributions_for_batch(bundle_header, contributions, batch_defaults):

    fund_id = batch_defaults['fund_id']
    default_date = model.ParseDate(batch_defaults['date'])
    default_batch_contrib_type = batch_defaults.get("contribution_type", DEFAULT_CONTRIBUTION_TYPE)

    if contributions is None or len(contributions) == 0:
        print("<p>NOTICE: No preloaded contributions configured for this batch: {}</p>".format(bundle_header))
        return None

    # TODO just make this whole thing a class so I don't have to do this every-single time...
    contrib_type_sql = '''
        SELECT Id, Description FROM lookup.ContributionType
    '''
    contrib_types = {r.Description: r.Id for r in q.QuerySql(contrib_type_sql)}
    
    if default_batch_contrib_type in contrib_types:
        contrib_type_id = contrib_types[batch_defaults['contribution_type']]
    else:
        print("<p>ERROR: Batch Default Contribution type not found {}</p>".format(default_batch_contrib_type))

    for contrib in contributions:
        people_id = contrib.get("people_id", 1)
        check_no = contrib.get("check_no", "")
        amount = contrib.get("amount", 0.00)
        type = contrib.get("type", default_batch_contrib_type)

        if type in contrib_types:
            contrib_type_id = contrib_types[type]
        else:
            print("<p>ERROR: contribution type INVALID CONTRIBUTION TYPE str: {}</p>".format(type))
            return

        bundle_detail = model.AddContributionDetail(default_date, fund_id, amount, check_no, None, contrib_type_id)
        bundle_detail.Contribution.MetaInfo = "Imported at time (utc){}".format(datetime.datetime.now(datetime.timezone.utc))

        try:
            p = model.GetPerson(people_id)
            bundle_detail.Contribution.PeopleId = p.pid
        except Exception as e:
            bundle_detail.Contribution.ContributionDesc = "person with TouchPoint Id {} not found".format(people_id)
            print("<p>ERROR: cannot find person with ID: {}</p>".format(people_id))
            print("<p>EXCEPTION: unable to find person with ID {}</p>".format(e))

        bundle_header.BundleDetails.Add(bundle_detail)


if model.HttpMethod.lower() == 'get':
    process_get()

elif model.HttpMethod.lower() == 'post':
    process_post()
