import boto3

s3 = boto3.client('s3')

def audit_buckets():
    buckets = s3.list_buckets()['Buckets']
    for b in buckets:
        name = b['Name']
        try:
            region = s3.get_bucket_location(Bucket=name)['LocationConstraint'] or 'us-east-1'
        except Exception as e:
            region = f"error: {e}"
        try:
            versioning = s3.get_bucket_versioning(Bucket=name).get('Status', 'Disabled')
        except Exception as e:
            versioning = f"error: {e}"
        try:
            pab = s3.get_public_access_block(Bucket=name)['PublicAccessBlockConfiguration']
        except Exception as e:
            pab = f"error: {e}"
        print(f"{name} | region={region} | versioning={versioning} | public_access_block={pab}")

if __name__ == "__main__":
    audit_buckets()
