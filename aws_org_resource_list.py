import boto3
import csv

def get_organization_accounts():
    """Retrieves a list of all AWS accounts within the organization"""
    org_client = boto3.client('organizations')
    accounts = []

    try:
        response = org_client.list_accounts()
        accounts.extend(response.get('Accounts', []))

        while 'NextToken' in response:
            response = org_client.list_accounts(NextToken=response['NextToken'])
            accounts.extend(response.get('Accounts', []))
    except Exception as e:
        print(f"An error occurred retrieving account details: {e}")

    return accounts

def get_account_tags(account_id):
    """Retrieves tags for a specific AWS account"""
    try:
        client = boto3.client('resourcegroupstaggingapi')
        tags_response = client.list_tags_for_resource(ResourceARN=f"arn:aws:organizations:::{account_id}")
        if 'ResourceTagMappingList' in tags_response:
            tags = tags_response['ResourceTagMappingList'][0].get('Tags', [])
        else:
            tags = []
    except Exception as e:
        print(f"An error occurred retrieving tags for account {account_id}: {e}")
        tags = []
    return tags

def export_accounts_to_csv(accounts, filename='organization_accounts.csv'):
    """Exports account details to a CSV file"""
    if not accounts:
        print("No account details found.")
        return

    with open(filename, 'w', newline='') as csvfile:
        fieldnames = ['Account ID', 'ARN', 'Email', 'Name', 'Status', 'Joined Timestamp', 'Tags']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for account in accounts:
            account_id = account['Id']
            arn = account['Arn']
            email = account['Email']
            name = account.get('Name', '')
            status = account['Status']
            joined_timestamp = account['JoinedTimestamp'].strftime("%Y-%m-%d %H:%M:%S")
            tags = get_account_tags(account_id)
            tags_str = ', '.join([f"{tag['Key']}: {tag['Value']}" for tag in tags])

            writer.writerow({
                'Account ID': account_id,
                'ARN': arn,
                'Email': email,
                'Name': name,
                'Status': status,
                'Joined Timestamp': joined_timestamp,
                'Tags': tags_str
            })

if __name__ == '__main__':
    organization_accounts = get_organization_accounts()
    export_accounts_to_csv(organization_accounts)
