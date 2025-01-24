from PIL import Image
import requests,datetime

from minio import Minio
from minio.error import S3Error

# 'http://10.83.190.87:9000/zhgd/test.mp4'
def download_by_requests(path,download_path):
    result = requests.get(path)
    with open(download_path, 'wb') as f:
        f.write(result.content)

class MyMinio:
    def __init__(self,bucketname) -> None:
        minio_endpoint = "10.83.190.141:9000"
        minio_access_key = "miniozhgd"
        minio_secret_key = "miniozhgd"
        self.bucket_name = bucketname

        self.minio_client = Minio(
            minio_endpoint,
            access_key=minio_access_key,
            secret_key=minio_secret_key,
            secure=False  # 如果使用HTTPS，请将其设置为True
        )

    # 创建存储桶
    def create(self,bucket_name):
        try:
            self.minio_client.make_bucket(bucket_name)
            print(f"Bucket '{bucket_name}' created successfully.")
        except S3Error as e:
            print(f"Error creating bucket: {e}")

    # 删除存储桶
    def remove_bucket(self,bucket_name):
        try:
            self.minio_client.remove_bucket(bucket_name)
            print(f"Bucket '{bucket_name}' deleted successfully.")
        except S3Error as e:
            print(f"Error deleting bucket: {e}")

    def update(self,minio_object_name,local_file_path):
        try:
            self.minio_client.fput_object(self.bucket_name, minio_object_name, local_file_path)
            print(f"File '{minio_object_name}' uploaded successfully.")
        except S3Error as e:
            print(f"Error uploading file: {e}")

    def down_load(self,minio_object_name,download_path):
        try:
            self.minio_client.fget_object(self.bucket_name, minio_object_name, download_path)
            print(f"File '{minio_object_name}' downloaded successfully to '{download_path}'.")
        except S3Error as e:
            print(f"Error downloading file: {e}")
# 删除对象
    def delete(self,minio_object_name):
        try:
            self.minio_client.remove_object(self.bucket_name, minio_object_name)
            print(f"Object '{minio_object_name}' deleted successfully.")
        except S3Error as e:
            print(f"Error deleting object: {e}")


if __name__=='__main__':
    minio_db = MyMinio('zhgd')
    local_file_path = 'data/videos/test.mp4'
    # minio_object_name = 'detection/faces/'+str(datetime.date.today().day)+'/'+local_file_path.split('/')[-1]
    minio_object_name = 'test.mp4'
    minio_object_name = 'detection/fired/2024-06-20/frame_19.jpg'
    local_file_path = 'data\objdetect\othors\dog1.jpg'
    minio_db.update(minio_object_name,local_file_path)
    # minio_db.down_load()
    
