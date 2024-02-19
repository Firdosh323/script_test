import boto3
import csv

def get_organization_accounts():
    """
    Retrieve AWS organization account details.
    """
    # Initialize the AWS Organizations client
    org_client = boto3.client('organizations')

    # Retrieve a list of accounts in the organization
    response = org_client.list_accounts()

    return response['Accounts']

def extract_account_details(account):
    """
    Extract relevant details from an AWS account object.
    """
    account_id = account['Id']
    arn = account['Arn']
    email = account['Email']
    name = account['Name']
    status = account['Status']
    joined_timestamp = str(account['JoinedTimestamp'])
    tags = get_account_tags(account_id)
    
    return [account_id, arn, email, name, status, joined_timestamp, tags]

def get_account_tags(account_id):
    """
    Retrieve tags associated with an AWS account.
    """
    # Initialize the AWS Resource Groups Tagging client
    tagging_client = boto3.client('resourcegroupstaggingapi')

    # Retrieve tags for the specified resource
    response = tagging_client.get_resources(
        ResourceARNList=[f'arn:aws:organizations:::{account_id}']
    )
    
    tags = response['ResourceTagMappingList'][0]['Tags'] if response['ResourceTagMappingList'] else []
    
    # Convert tags to a dictionary format for easy handling
    tags_dict = {tag['Key']: tag['Value'] for tag in tags}
    
    return tags_dict

def export_to_csv(accounts):
    """
    Export account details to a CSV file.
    """
    with open('aws_organization_accounts.csv', 'w', newline='') as csvfile:
        fieldnames = ['Account ID', 'ARN', 'Email', 'Name', 'Status', 'Joined Timestamp', 'Tags']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        for account in accounts:
            account_details = extract_account_details(account)
            writer.writerow({fieldnames[i]: account_details[i] for i in range(len(fieldnames))})

def main():
    accounts = get_organization_accounts()
    export_to_csv(accounts)
    print("AWS organization account details exported successfully to 'aws_organization_accounts.csv'.")

if __name__ == "__main__":
    main()
