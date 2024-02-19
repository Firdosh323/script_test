import boto3
import csv

def get_all_accounts():
    """Retrieves a list of all AWS account IDs within the organization"""
    org_client = boto3.client('organizations')
    accounts = []

    try:
        response = org_client.list_accounts()
        accounts.extend(response.get('Accounts', []))

        while 'NextToken' in response:
            response = org_client.list_accounts(NextToken=response['NextToken'])
            accounts.extend(response.get('Accounts', []))
    except Exception as e:
        print(f"An error occurred retrieving account IDs: {e}")

    return [account['Id'] for account in accounts]

def get_vpc_details(account_id, region):
    """Fetches VPC details for a given account and region"""
    ec2_client = boto3.client('ec2', region_name=region)
    vpcs = []

    try:
        response = ec2_client.describe_vpcs()
        for vpc in response['Vpcs']:
            vpc_id = vpc['VpcId']
            vpc_name = ''
            for tag in vpc.get('Tags', []):
                if tag['Key'] == 'Name':
                    vpc_name = tag['Value']
                    break
            
            vpc_arn = ec2_client.describe_vpcs(VpcIds=[vpc_id])['Vpcs'][0]['VpcArn']

            vpcs.append({
                'Account ID': account_id,
                'VPC Name': vpc_name,
                'VPC ID': vpc_id,
                'VPC ARN': vpc_arn,
                'CIDR Block': vpc['CidrBlock'],
                'Region': region,
                'State': vpc['State']
            })
    except Exception as e:
        print(f"Error listing VPCs for account {account_id} in region {region}: {e}")

    return vpcs

def get_all_regions():
    """Retrieves a list of all AWS regions"""
    ec2_client = boto3.client('ec2')
    regions = [region['RegionName'] for region in ec2_client.describe_regions()['Regions']]
    return regions

def export_details_to_csv(data, filename='vpc_details.csv'):
    """Exports data to a CSV file"""
    if not data:
        print("No resource details found.")
        return

    with open(filename, 'w', newline='') as csvfile:
        fieldnames = data[0].keys()
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)

if __name__ == '__main__':
    all_vpc_details = []

    all_accounts = get_all_accounts()
    all_regions = get_all_regions()

    for account_id in all_accounts:
        for region in all_regions:
            all_vpc_details.extend(get_vpc_details(account_id, region))

    export_details_to_csv(all_vpc_details)
