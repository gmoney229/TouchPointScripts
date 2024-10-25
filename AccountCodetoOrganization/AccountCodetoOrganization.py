#!python3

#roles=Finance

# Imports
import re
import json

from xml.etree import cElementTree as ElementTree


# Variables
__author__ = "Gavin Murphy"
__email__ = "gmurphy@stannparish.org"


# Classes
class XmlListConfig(list):
    # https://stackoverflow.com/questions/2148119/how-to-convert-an-xml-string-to-a-dictionary
    def __init__(self, aList):
        for element in aList:
            if element:
                # treat like dict
                if len(element) == 1 or element[0].tag != element[1].tag:
                    self.append(XmlDictConfig(element))
                # treat like list
                elif element[0].tag == element[1].tag:
                    self.append(XmlListConfig(element))
            elif element.text:
                text = element.text.strip()
                if text:
                    self.append(text)


class XmlDictConfig(dict):
    # https://stackoverflow.com/questions/2148119/how-to-convert-an-xml-string-to-a-dictionary
    def __init__(self, parent_element):
        if parent_element.items():
            self.update(dict(parent_element.items()))
        for element in parent_element:
            if element:
                # treat like dict - we assume that if the first two tags
                # in a series are different, then they are all different.
                if len(element) == 1 or element[0].tag != element[1].tag:
                    aDict = XmlDictConfig(element)
                # treat like list - we assume that if the first two tags
                # in a series are the same, then the rest are the same.
                else:
                    # here, we put the list in dictionary; the key is the
                    # tag name the list elements all share in common, and
                    # the value is the list itself 
                    aDict = {element[0].tag: XmlListConfig(element)}
                # if the tag has attributes, add those to the dict
                if element.items():
                    aDict.update(dict(element.items()))
                self.update({element.tag: aDict})
            # this assumes that if you've got an attribute in a tag,
            # you won't be having any text. This may or may not be a 
            # good idea -- time will tell. It works for the way we are
            # currently doing XML configuration files...
            elif element.items():
                self.update({element.tag: dict(element.items())})
            # finally, if there are no child tags and no attributes, extract
            # the text
            else:
                self.update({element.tag: element.text})


# Functions
def f_remove_accents(old):
    """
    https://stackoverflow.com/a/69099798
    https://stackoverflow.com/questions/517923/what-is-the-best-way-to-remove-accents-normalize-in-a-python-unicode-string
    Removes common accent characters
    Uses: regex.
    """
    new = re.sub(r'[àáâãäå]', 'a', old)
    new = re.sub(r'[ÀÁÂÃ]', 'A', new)
    new = re.sub(r'[èéêë]', 'e', new)
    # new = re.sub(r'[èéêë]', 'E', new)
    new = re.sub(r'[ìíîï]', 'i', new)
    # new = re.sub(r'[ìíîï]', 'I', new)
    new = re.sub(r'[òóôõö]', 'o', new)
    # new = re.sub(r'[òóôõö]', 'O', new)
    new = re.sub(r'[ùúûü]', 'u', new)
    # new = re.sub(r'[ùúûü]', 'U', new)
    new = re.sub(r'[ñńņň]', 'n', new)
    new = re.sub(r'[ÑŃŅŇ]', 'N', new)
    return new


def print_pgph(msg):
    print("<p>{}</p>".format(msg))


def process_get():
    
    account_codes = get_account_codes()

    # New Registration Forms
    get_new_org_settings(account_codes)

    # Old Join Involvement + OnlineReg (TODO test for twebb)?
    get_old_org_settings(account_codes)

    print('<pre>')
    print(json.dumps(account_codes, indent=4))
    print('</pre>')


def get_account_codes():
    account_codes_def = {}

    account_codes_sql = '''
        SELECT
            Id,
            Code,
            Description,
            Active,
            AccountManagementRoleId
        FROM lookup.AccountCode
    '''
    
    for r in q.QuerySql(account_codes_sql):
        account_codes_def[r.Id] = {
            "Id": r.Id,
            "Code": r.Code,
            "Description": r.Description,
            "Active": r.Active,
            "AccountManagementRoleId": r.AccountManagementRoleId,
            "Involvements": {}
        }
    return account_codes_def


def get_new_org_settings(accnt_codes):
    organization_reg_codes_sql = '''
        SELECT
            OrganizationId,
            OrganizationName,
            RegAccountCodeId
        FROM dbo.Organizations
        WHERE RegAccountCodeId IS NOT NULL
    '''
    for r in q.QuerySql(organization_reg_codes_sql):
        check_add_account_code(r, r.RegAccountCodeId, accnt_codes)


def get_old_org_settings(accnt_codes):
    organization_settings_sql = '''
        SELECT
            OrganizationId,
            OrganizationName,
            RegSettingXml
        FROM dbo.Organizations
        WHERE RegSettingXml IS NOT NULL
    '''
    for r in q.QuerySql(organization_settings_sql):
        reg_acct_code = get_acct_code_from_xml(r)
        check_add_account_code(r, reg_acct_code, accnt_codes)


def get_acct_code_from_xml(row):
    ret_acct_code = None

    # The row.RegSettingXml holds some crazy characters/images so trying to make the value normalized with codec
    try:
        content = row.RegSettingXml.encode('utf-8').strip()
    except Exception as e:
        print_pgph("EXCEPTION: this is a problem need to parse with codec and ignore errors:")
        print('<pre>')
        print("type of variable = {}".format(type(row.RegSettingXm)))
        print(row.RegSettingXml)
        print('</pre>')
        return None

    ret_acct_code = get_acct_code_from_xml_str(content)

    return ret_acct_code


def get_acct_code_from_xml_str(xml_str):
    row_xml_str = xml_str

    root = ElementTree.XML(row_xml_str)
    xml_dict = XmlDictConfig(root)

    fees_def = xml_dict.get("Fees", {})
    if not fees_def:
        print_pgph("INFO: no fees definition found in RegSettingXml")
        return

    ret_acct_code = fees_def.get("AccountingCode", None)
    if ret_acct_code:
        try:
            ret_acct_code = int(ret_acct_code)
            return ret_acct_code
        except Exception as e:
            print_pgph("ERROR: tried to make AccountingCode({}) an int and failed with e = {}".format(ret_acct_code, e))

        # covers for description that is not an ID ex. 4291.01-MYC
        try:
            ret_acct_code = str(ret_acct_code)
            return ret_acct_code
        except Exception as e:
            print_pgph("ERROR: tried to make AccountingCode({}) a string failed with e = {}".format(ret_acct_code, e))

    return


def check_add_account_code(row, accting_code, acct_codes):

    if accting_code is None:
        # print_pgph("DEBUG: Not adding information for account code: {}".format(accting_code))
        return

    if accting_code not in acct_codes and type(accting_code) == int:
        print_pgph("WARNING: New account code for account_codes dictionary not adding new int AccountCodeId's at this point: {}".format(accting_code))
        return

    if accting_code not in acct_codes:
        print_pgph("INFO: Adding this account code to the list = {}".format(accting_code))
        acct_codes[accting_code] = {
            "Code": accting_code,
            "Involvements": {}
        }

    print_pgph("INFO: New Involvement({}) to account code def {}".format(row.OrganizationId, accting_code))

    acct_codes[accting_code]["Involvements"][row.OrganizationId] = {
        "OrganizationId": row.OrganizationId,
        # NOTE: this covers json.dumps from blowing up when accented n with tilde is being printed
        "OrganizationName": f_remove_accents(row.OrganizationName)
    }


def process_post():
    raise NotImplemented


if model.HttpMethod.lower() == 'get':
    process_get()

elif model.HttpMethod.lower() == 'post':
    process_post()
