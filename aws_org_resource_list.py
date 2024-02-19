import boto3
import csv
import datetime

def get_account_details():
    """Retrieves details of all AWS accounts within the organization."""
    org_client = boto3.client('organizations')
    tagging_client = boto3.client('resourcegroupstaggingapi')

    accounts = []
    paginator = org_client.get_paginator('list_accounts')
    for page in paginator.paginate():
        for account in page['Accounts']:
            try:
                tags_response = tagging_client.get_resources(
                    ResourceARNList=[account['Arn']]
                )
                tags = tags_response['ResourceTagMappingList'][0].get('Tags', [])
            except Exception:
                tags = []

            accounts.append({
                'Account ID': account['Id'],
                'Name': account.get('Name', 'No Alias'),
                'ARN': account['Arn'],
                'Email': account['Email'],
                'Created Date': account['JoinedTimestamp'].strftime('%Y-%m-%d'),
                'Tags': tags
            })

    return accounts

def export_details_to_csv(data, filename='core_resource_details.csv'):
    """Exports data to a CSV file."""
    with open(filename, 'w', newline='') as csvfile:
        fieldnames = ['Account ID', 'Name', 'ARN', 'Email', 'Created Date', 'Tags']  # Include 'ARN' field
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)

if __name__ == '__main__':
    all_account_details = get_account_details()
    export_details_to_csv(all_account_details)
