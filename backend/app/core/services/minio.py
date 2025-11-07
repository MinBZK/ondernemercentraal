import uuid
from dataclasses import dataclass, field
from io import BytesIO
from typing import BinaryIO

import urllib3
from minio import Minio

from ..settings import settings

client = Minio(
    endpoint=f"{settings.MINIO_HOST}:{settings.MINIO_HOST_PORT}",
    access_key=settings.MINIO_ACCESS_KEY,
    secret_key=settings.MINIO_SECRET_KEY,
    secure=settings.MINIO_HOST_PORT == 443,  # Set to True if you're using HTTPS
)


@dataclass
class MinioService:
    bucket_name: str
    host: str
    port: str
    access_key: str
    secret_key: str
    __client: Minio | None = field(default=None, init=False)

    def __connect(self):
        self.__client = Minio(
            endpoint=f"{self.host}:{self.port}",
            access_key=self.access_key,
            secret_key=self.secret_key,
            secure=settings.MINIO_HOST_PORT == 443,  # Set to True if you're using HTTPS
            http_client=urllib3.PoolManager(timeout=urllib3.Timeout(connect=2, read=5)),
        )

        # Make the bucket if it doesn't exist.
        found = self.__client.bucket_exists(self.bucket_name)
        if not found:
            self.__client.make_bucket(self.bucket_name)

    def check_initialization(self):
        self.__connect()
        assert self.__client
        assert self.__client.bucket_exists(self.bucket_name), "Bucket does not exist"

    @property
    def client(self):
        if self.__client is None:
            self.__connect()
        assert self.__client is not None
        return self.__client

    def __get_binaryio_length(self, file_obj: BinaryIO):
        """
        Gets the length of a BinaryIO file object using seek and tell.

        Args:
            file_obj: The BinaryIO file object.

        Returns:
            The length of the file in bytes.
        """
        # Store the current position
        current_pos = file_obj.tell()

        # Seek to the end of the file
        file_obj.seek(0, 2)  # 0 offset from the end (2)

        # Get the current position (which is the end, hence the length)
        length = file_obj.tell()

        # Seek back to the original position
        file_obj.seek(current_pos)

        return length

    def store_file(self, file: BinaryIO):
        """
        Returns the Minio object id.
        """
        object_name = str(uuid.uuid4())
        client = self.client
        assert client
        self.client.put_object(
            bucket_name=settings.MINIO_BUCKET_NAME,
            object_name=object_name,
            data=file,
            length=self.__get_binaryio_length(file),
        )
        return object_name

    def get_file(self, object_id: str):
        response = self.client.get_object(bucket_name=self.bucket_name, object_name=object_id)
        file_data_bytes = response.read()
        response.close()
        response.release_conn()
        return BytesIO(file_data_bytes)


minio_service = MinioService(
    bucket_name=settings.MINIO_BUCKET_NAME,
    host=settings.MINIO_HOST,
    port=str(settings.MINIO_HOST_PORT),
    access_key=settings.MINIO_ACCESS_KEY,
    secret_key=settings.MINIO_SECRET_KEY,
)
