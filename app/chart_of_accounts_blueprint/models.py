from app import app
from apiclient import discovery
import httplib2


def update_chart_of_accounts(qbo, qbo_company_id, gsuite_credentials, sheet_id):
    skip_list = [u'Unapplied Cash Bill Payment Expenditure', u'Unapplied Cash Payment Revenue', u'Retained Earnings', u'Sales of Product Income', u'Services', u'Uncategorized Asset', u'Uncategorized Expense', u'Uncategorized Income', u'Undeposited Funds', u'Opening Balance Equity']

    # important! delete accounts furthest from the root first, closer later, so that we don't try to delete an account with sub accounts
    accounts = list(
        reversed(
            sorted(
                qbo.get("{0}/v3/company/{1}/query?query=select%20%2A%20from%20account&minorversion=4".format(app.config["QBO_ACCOUNTING_API_BASE_URL"], qbo_company_id), headers={'Accept': 'application/json'}).data['QueryResponse']['Account'],
                key=lambda a: a['FullyQualifiedName'].count(':')
            )
        )
    )

    # delete existing accounts, except un-delete-ables
    for account in accounts:
        if account['FullyQualifiedName'] not in skip_list:
            account['Active'] = False
            response = qbo.post("{0}/v3/company/{1}/account?operation=update".format(app.config["QBO_ACCOUNTING_API_BASE_URL"], qbo_company_id), format='json', headers={'Accept': 'application/json', 'Content-Type': 'application/json', 'User-Agent': 'wfbot'}, data=account)
            if response.status != 200:
                raise LookupError, "update {0} {1} {2}".format(response.status, response.data, account)

    # get chart of accounts from google sheet
    http_auth = gsuite_credentials.authorize(httplib2.Http())
    sheets = discovery.build('sheets', 'v4', http_auth)
    result = sheets.spreadsheets().values().get(spreadsheetId=sheet_id, range='A:Z').execute()
    rows = result.get('values', [])
    header = rows.pop(0)
    accounts = []
    for row in rows:
        a = {};
        for i, value in enumerate(row):
            a[header[i]] = value
        accounts.append(a)

    # important! create accounts closer to the root of the tree first, further away later, so the latter can reference the former
    accounts = sorted(accounts, key=lambda a: a['FullyQualifiedName'].count(':'))

    for i, account in enumerate(accounts):
        if account['FullyQualifiedName'] not in skip_list:
            fqn = account['FullyQualifiedName']
            if fqn.count(':') > 0:
                parent_fully_qualified_name, name = fqn.rsplit(":", 1)
                accounts[i]['Name'] = name
                parent_account = next(a for a in accounts if a["FullyQualifiedName"] == parent_fully_qualified_name)
                accounts[i]['ParentRef'] = {"value": parent_account["Id"]}
            else:
                accounts[i]['Name'] = fqn

            response = qbo.post("{0}/v3/company/{1}/account".format(app.config["QBO_ACCOUNTING_API_BASE_URL"], qbo_company_id), format='json', headers={'Accept': 'application/json', 'Content-Type': 'application/json', 'User-Agent': 'wfbot'}, data=accounts[i])
            if response.status != 200:
                raise LookupError, "create {0} {1} {2}".format(response.status, response.data, account)
            accounts[i]['Id'] = response.data['Account']['Id']
