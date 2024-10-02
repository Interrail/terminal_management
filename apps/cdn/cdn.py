from minio import Minio
from minio.error import S3Error
from terminal_management.settings.production import CDN_URL, CDN_ACCESS_KEY, CDN_SECRET_KEY, MTT_BUCKET
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
import time

class CDNService:
    def __init__(self):
        self.base_url = CDN_URL
        self.access_key = CDN_ACCESS_KEY
        self.secret_key = CDN_SECRET_KEY

    def generate_unique_filename(self, filename):
        return f"{int(time.time())}_{filename}"

    def upload( self, file):
        client = Minio(self.base_url,
                    access_key=self.access_key,
                    secret_key=self.secret_key,
                    secure=True)

        found = client.bucket_exists(MTT_BUCKET)
        if not found:
            client.make_bucket(MTT_BUCKET)
        else:
            print("Bucket", MTT_BUCKET, "already exists")
        
        filename = self.generate_unique_filename(file.name)
        try:
            client.put_object(
                MTT_BUCKET,
                filename,
                file,
                length=-1,  # MinIO will calculate the length
                part_size=5 * 1024 * 1024  # 10MB part size
            )

            # Construct the full file path
            file_url = f"http://{CDN_URL}/{MTT_BUCKET}/{filename}"
            print(f"File uploaded to MinIO: {file_url   }")
            return file_url
        except S3Error as e:
            print(f"Error occurred while uploading to MinIO: {e}")
            return ""


class UploadFileApi(APIView):
    def post(self, request):
        file = request.FILES['file']
        CDNService().upload(file)
        return Response(status=status.HTTP_202_ACCEPTED)
