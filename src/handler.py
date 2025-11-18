import runpod
import base64
import tempfile
import os
from predict import transcribe_piano
from s3_utils import upload_to_s3

def handler(event):
    """
    RunPod Serverless Entry
    Expected input:
    {
        "input": {
            "audio_base64": "<base64 audio>",
            "s3_bucket": "your-bucket-name",
            "aws_access_key_id": "your-access-key",
            "aws_secret_access_key": "your-secret-key",
            "aws_region": "us-east-1" (optional, default: us-east-1),
            "s3_prefix": "midi" (optional, default: midi)
        }
    }
    """
    try:
        print("Received request")
        
        # 获取输入参数
        input_data = event["input"]
        audio_b64 = input_data["audio_base64"]
        
        # S3配置 - 优先使用环境变量
        s3_bucket = input_data.get("s3_bucket", os.environ.get("S3_BUCKET_NAME"))
        aws_access_key_id = input_data.get("aws_access_key_id", os.environ.get("AWS_ACCESS_KEY_ID"))
        aws_secret_access_key = input_data.get("aws_secret_access_key", os.environ.get("AWS_SECRET_ACCESS_KEY"))
        aws_region = input_data.get("aws_region", os.environ.get("AWS_REGION", "ap-southeast-1"))
        s3_prefix = input_data.get("s3_prefix", "qiupupu/PianoTrans")
        
        # 解码音频
        audio_bytes = base64.b64decode(audio_b64)
        print(f"Decoded audio: {len(audio_bytes)} bytes")

        # 保存上传的音频
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as f:
            f.write(audio_bytes)
            audio_path = f.name
        
        print(f"Saved audio to {audio_path}")

        # 转录
        midi_path = transcribe_piano(audio_path)

        # 检查是否需要上传到S3
        if s3_bucket and aws_access_key_id and aws_secret_access_key:
            # 上传到S3
            midi_url = upload_to_s3(
                file_path=midi_path,
                bucket_name=s3_bucket,
                aws_access_key_id=aws_access_key_id,
                aws_secret_access_key=aws_secret_access_key,
                region_name=aws_region,
                prefix=s3_prefix
            )
            
            # 清理临时文件
            try:
                os.unlink(audio_path)
                os.unlink(midi_path)
            except:
                pass
            
            print("Request completed successfully with S3 upload")
            return {"midi_url": midi_url}
        else:
            # 回退到返回base64（如果没有提供S3配置）
            with open(midi_path, "rb") as f:
                midi_b64 = base64.b64encode(f.read()).decode()
            
            # 清理临时文件
            try:
                os.unlink(audio_path)
                os.unlink(midi_path)
            except:
                pass
            
            print("Request completed successfully with base64 response")
            return {"midi_base64": midi_b64}
    
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return {"error": str(e)}

# 关键：启动 RunPod serverless
if __name__ == "__main__":
    print("Starting RunPod serverless handler...")
    runpod.serverless.start({"handler": handler})
