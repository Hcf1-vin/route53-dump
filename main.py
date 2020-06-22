import boto3
import yaml
import os

def s3_put(s3_bucket,s3_body):
    s3_key = str(s3_body["zone_info"]["name"]).replace(".","-") + "zone.yml"
    s3_body = yaml.dump(s3_body)
    response = s3_client.put_object(
        Body=str.encode(s3_body),
        Bucket=s3_bucket,
        Key=s3_key
    )
    print(response)

def get_zone_info(zone_id):
    response = r53_client.get_hosted_zone(
        Id=zone_id
    )
    zone_info = {}
    vpc_list = []

    zone_info["name"] = response["HostedZone"]["Name"]
    zone_info["private"] = response["HostedZone"]["Config"]["PrivateZone"]
    zone_info["record_count"] = response["HostedZone"]["ResourceRecordSetCount"]


    if zone_info["private"] == True:
        for a in response["VPCs"]:
            vpc_list.append(a["VPCId"])

    zone_info["vpc_list"] = vpc_list

    return zone_info

def get_records(zone_id):
    is_truncated = True
    marker = None
    record_list = []
    while is_truncated != False:
        if marker == None:
            response = r53_client.list_resource_record_sets(
                HostedZoneId=zone_id
            )
        else:
            response = r53_client.list_resource_record_sets(
                HostedZoneId=zone_id,
                StartRecordName=marker,
            )
        if "NextRecordName" in response:
            marker = response["NextRecordName"]
        else:
            marker = None

        if "IsTruncated" in response:
            is_truncated = response["IsTruncated"]
        else:
            is_truncated = False
       
        for a in response["ResourceRecordSets"]:

            record_dict = {}
            if a["Type"] == "A" or a["Type"] == "CNAME":
                record_value = []
                record_dict["name"] = a["Name"]
                
                if "AliasTarget" in a:
                    record_dict["type"] = "CNAME"
                    record_value.append(a["AliasTarget"]["DNSName"])
                else:
                    record_dict["type"] = a["Type"]
                    for b in a["ResourceRecords"]:
                        record_value.append(b["Value"])
                
                record_dict["value"] = record_value
                record_list.append(record_dict)

    return record_list

def get_zone_ids():
    is_truncated = True
    marker = None
    zone_list = []
    while is_truncated != False:
        if marker == None:
            response = r53_client.list_hosted_zones()
        else:
            response = r53_client.list_hosted_zones(
                Marker=marker,
            )
        if "NextMarker" in response:
            marker = response["NextMarker"]
        else:
            marker = None

        if "IsTruncated" in response:
            is_truncated = response["IsTruncated"]
        else:
            is_truncated = False

        for a in response["HostedZones"]:
            zone_list.append(a["Id"])

    return zone_list
def main():
    for a in get_zone_ids():
        zone_data = {}
        zone_data["records"] = get_records(a)
        zone_data["zone_info"] = get_zone_info(a)
        s3_put(s3_bucket,zone_data)

if __name__ == "__main__":
    s3_bucket = os.environ("s3_bucket")
    r53_client = boto3.client("route53")
    s3_client = boto3.client("s3")
    main()