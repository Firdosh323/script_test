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

def get_all_regions():
    """Retrieves a list of all AWS regions"""
    ec2_client = boto3.client('ec2')
    regions = [region['RegionName'] for region in ec2_client.describe_regions()['Regions']]
    return regions

def get_ebs_details(account_id, region):
    """Fetches EBS details for a given account and region"""
    ec2_resource = boto3.resource('ec2', region_name=region)
    volumes = ec2_resource.volumes.all()

    volume_details = []
    for volume in volumes:
        volume_name = 'N/A'
        for tag in volume.tags or []:
            if tag['Key'] == 'Name':
                volume_name = tag['Value']
                break

        volume_details.append({
            'Account ID': account_id,
            'Volume Name': volume_name,
            'Volume ID': volume.id,
            'Size': volume.size,
            'Availability Zone': volume.availability_zone,
            'Tags': volume.tags or 'N/A'
        })

    return volume_details

def export_details_to_csv(data, filename='ebs_details.csv'):
    """Exports data to a CSV file"""
    if not data:
        print("No EBS volume details found.")
        return

    with open(filename, 'w', newline='') as csvfile:
        fieldnames = data[0].keys()
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)

if __name__ == '__main__':
    all_ebs_details = []

    all_accounts = get_all_accounts()
    all_regions = get_all_regions()

    for account_id in all_accounts:
        for region in all_regions:
            all_ebs_details.extend(get_ebs_details(account_id, region))

    export_details_to_csv(all_ebs_details)
