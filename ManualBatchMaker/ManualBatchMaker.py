#!python3

#roles=Finance

# Imports
import datetime
import json

from collections import OrderedDict


# Variables
__author__ = "Gavin Murphy"
__email__ = "gmurphy@stannparish.org"


DEFAULT_CONTRIBUTION_TYPE = "Tax deductible"
DEFAULT_BATCH_TYPE = "Loose Checks and Cash"

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


def print_pgph(msg):
    print("<p>{}</p>".format(msg))


def process_get():
    txt_cont_sql = '''
        SELECT Id, Name
        FROM dbo.Content
        WHERE TypeID != 0
            AND Name LIKE '%.json%'
        ORDER BY DateCreated DESC
    '''
    # TODO add a cancel button
    Data.text_contents  = q.QuerySql(txt_cont_sql)
    model.Form          = model.RenderTemplate(CHOOSE_JSON_FILE_HTML)


def process_post():
    # TODO test no selection '-- select a Text Content --'
    find_sql = '''
    SELECT Body FROM dbo.Content WHERE Id = @text_content_id
    '''
    selected_text_content_id    = int(model.Data.textContentJson)
    params                      = {"text_content_id": selected_text_content_id}
    cont                        = q.QuerySqlTop1(find_sql, None, params)

    if cont.Body is not None:
        processed_batches = process_batches_json(cont.Body)
    else:
        print_pgph("NOTICE: Content body is none: {}".format(selected_text_content_id))
        return

    for batch_info in processed_batches:
        anchor = "<a href=\"{}\">{} -- {}</a>".format(batch_info["link"], batch_info["short_name"], batch_info["link"])
        print_pgph(anchor)


def process_batches_json(raw_json):
    batches_processed = []

    try:
        parsed_bdy = json.loads(raw_json, object_pairs_hook=OrderedDict)
        batches_def = parsed_bdy["batches"]
        # TODO would be nice to make sure the json is good at this point
        #    plus I think you can run the data through a json schema checker and catch Exception

    except Exception as e:
        print_pgph("ERROR: Failed to load json {}".format(e))
        raise e

    # NOTE I think this could go away once jsonschema is in place
    if batches_def is None or len(batches_def) == 0:
        print_pgph("NOTICE: json is empty not doing anything: {}".format(batches_def))
        return

    for batch_short_name, batch in batches_def.items():
        batch_id = make_the_batch(batch)

        if batch_id:
            batches_processed.append({
                "id": batch_id,
                "link": "{}/Batches/Detail/{}".format(model.CmsHost, batch_id),
                "short_name": batch_short_name
            })
        else:
            print_pgph("NOTICE: Batch was not created in make_the_batch(): {}".format(batch))

    return batches_processed


def make_the_batch(batch_def):
    # NOTE shoudn't lookup data be callable with out writing SQL in Python???
    #     (4, 5, 6) = (Online, Online Pledge, Pledge)
    batch_type_sql = '''
        SELECT Id, Description FROM lookup.BundleHeaderTypes WHERE Id NOT IN (4,5,6)
    '''
    bundle_header_types = {r.Description: r.Id for r in q.QuerySql(batch_type_sql)}

    # NOTE model.ResolveFundId(fundName) might do what I need
    #    (2) = (No longer Active/Closed)
    funds_sql = '''
        SELECT FundId, FundName FROM dbo.ContributionFund WHERE FundStatusId != 2
    '''
    funds = {r.FundId: r.FundName for r in q.QuerySql(funds_sql)}

    batch_defaults      = batch_def['defaults']
    batch_deposit_info  = batch_def['deposit']

    default_date        = model.ParseDate(batch_defaults['date'])
    batch_type          = batch_def.get('batch_type', DEFAULT_BATCH_TYPE)

    if batch_type not in bundle_header_types:
        print_pgph("NOTICE: bundle_header_type NOT FOUND: {}".format(batch_type))
        return

    batch_type_id   = bundle_header_types[batch_type]

    bundle_header   = model.GetBundleHeader(default_date, model.DateTime.Now, batch_type_id)
    fund_id         = batch_defaults.get("fund_id", None)

    if fund_id not in funds:
        print_pgph("NOTICE: Batch Default FUND not found using: {}".format(bundle_header.FundId))
    else:
        bundle_header.FundId = fund_id

    bundle_contribs = batch_def.get("contributions", [])

    if len(bundle_contribs) > 0:
        make_contributions_for_batch(bundle_header, bundle_contribs, batch_defaults)

    # TODO figure out how to not call this function
    #    it is not allowing me to set the estimated amt
    model.FinishBundle(bundle_header)

    bundle_header.BundleTotal = batch_def.get('estimated_amt', 0)
    bundle_header.BundleCount = batch_def.get("estimated_count", 0)

    bundle_header.DepositDate = model.ParseDate(batch_deposit_info['date'])
    bundle_header.ReferenceId = batch_deposit_info.get("reference_#", None)
    # NOTE not sure if ReferenceIdType needs to be set as well?

    return bundle_header.BundleHeaderId


def make_contributions_for_batch(bundle_header, contributions, batch_defaults):
    fund_id                     = batch_defaults['fund_id']
    default_date                = batch_defaults['date']
    default_batch_contrib_type  = batch_defaults.get("contribution_type", DEFAULT_CONTRIBUTION_TYPE)

    if contributions is None or len(contributions) == 0:
        print_pgph("NOTICE: No preloaded contributions configured for this batch: {}".format(bundle_header))
        return None

    # TODO just make this whole thing a class so I don't have to do this every-single time...
    contrib_type_sql = '''
        SELECT Id, Description FROM lookup.ContributionType
    '''
    contrib_types = {r.Description: r.Id for r in q.QuerySql(contrib_type_sql)}
    
    if default_batch_contrib_type in contrib_types:
        contrib_type_id = contrib_types[batch_defaults['contribution_type']]
    else:
        print_pgph("ERROR: Batch Default Contribution type not found {}".format(default_batch_contrib_type))

    for contrib in contributions:
        # NOTE here non-contributions will be fund
        # TODO need to allow fundid at contribution level and contribution date
        people_id   = contrib.get("people_id", None)
        check_no    = contrib.get("check_#", "")
        amount      = contrib.get("amount", 0.00)  # TODO make sure my code doesn't break for int or not 2 decimals
        type        = contrib.get("type", default_batch_contrib_type)  # TODO breaking out fund_description breaks here
        date        = model.ParseDate(contrib.get("date", default_date))
        description = contrib.get("notes", "")
        fund        = contrib.get("fund", fund_id)  # TODO break this out into a fund_description dict?

        if type in contrib_types:
            contrib_type_id = contrib_types[type]
        else:
            print_pgph("ERROR: contribution type INVALID CONTRIBUTION TYPE str: {}".format(type))
            return

        if amount == 0:
            print_pgph("ERROR: amount cannot be zero: {}".format(amount))
            return

        # TODO maybe call a function here? make_str_amount()
        #    or change the type in the json?
        amount = str(amount)
        # NOTE just try PeopleId as string
        # people_id = str(people_id)

        bundle_detail = model.AddContributionDetail(date, fund, amount, check_no, None, None, contrib_type_id)
        # Use time in UTC? datetime.datetime.now(datetime.timezone.utc)
        bundle_detail.Contribution.MetaInfo = "Imported at time {}".format(datetime.datetime.now().strftime("%x %X"))

        if people_id is not None:
            try:
                p = model.GetPerson(people_id)
                bundle_detail.Contribution.PeopleId = p.PeopleId
            except Exception as e:
                description = "person with TouchPoint Id {} not found".format(people_id) if description == "" else description
                print_pgph("ERROR: trying to assign contribution to person with ID: {}".format(people_id))
                print_pgph("EXCEPTION: did not contribute person with ID {}".format(e))

        # TODO test and make sure description is not too long...
        bundle_detail.Contribution.ContributionDesc = description

        bundle_header.BundleDetails.Add(bundle_detail)


if model.HttpMethod.lower() == 'get':
    process_get()

elif model.HttpMethod.lower() == 'post':
    process_post()
