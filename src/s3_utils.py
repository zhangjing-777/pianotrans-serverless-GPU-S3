import boto3
import os
from datetime import datetime
import uuid

def upload_to_s3(file_path: str, bucket_name: str, aws_access_key_id: str, 
                 aws_secret_access_key: str, region_name: str = "us-east-1",
                 prefix: str = "midi") -> str:
    """
    上传文件到S3并返回公开访问的URL
    
    Args:
        file_path: 本地文件路径
        bucket_name: S3 bucket名称
        aws_access_key_id: AWS访问密钥ID
        aws_secret_access_key: AWS访问密钥
        region_name: AWS区域
        prefix: S3中的文件夹前缀
    
    Returns:
        文件的公开访问URL
    """
    try:
        # 创建S3客户端
        s3_client = boto3.client(
            's3',
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            region_name=region_name
        )
        
        # 生成唯一的文件名
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        unique_id = str(uuid.uuid4())[:8]
        file_extension = os.path.splitext(file_path)[1]
        s3_key = f"{prefix}/{timestamp}_{unique_id}{file_extension}"
        
        # 上传文件
        print(f"Uploading to S3: {bucket_name}/{s3_key}")
        s3_client.upload_file(
            file_path,
            bucket_name,
            s3_key,
            ExtraArgs={'ContentType': 'audio/midi'}
        )
        
        # 生成公开访问URL
        if region_name == "us-east-1":
            url = f"https://{bucket_name}.s3.amazonaws.com/{s3_key}"
        else:
            url = f"https://{bucket_name}.s3.{region_name}.amazonaws.com/{s3_key}"
        
        print(f"Upload successful: {url}")
        return url
        
    except Exception as e:
        print(f"S3 upload error: {str(e)}")
        raise
