import os
import json
import base64
import logging
from google.cloud import storage
from google.api_core.exceptions import NotFound
class CaesarAIGCP:
    def __init__(self) -> None:
        dir_path = os.path.dirname(os.path.realpath(__file__))
        with open(f"{dir_path}/creds.txt") as f:
            service_base64 = f.read()
        service_info = json.loads(base64.b64decode(service_base64.encode()).decode())
        self._client = storage.Client.from_service_account_info(service_info)

    def make_blob_public(self,blob_name,bucket_name:str="revisioncardimages"):
        """Makes a blob publicly accessible."""
        # bucket_name = "your-bucket-name"
        # blob_name = "your-object-name"
        bucket = self._client.bucket(bucket_name)
        blob = bucket.blob(blob_name)

        blob.make_public()

        #print(
        #    f"Blob {blob.name} is publicly accessible at {blob.public_url}"
        #)

    def upload_to_bucket(self,  file_bytes,blob_name:str,bucket_name:str="revisioncardimages"):
        """ Upload data to a bucket"""
        
        # Explicitly use service account credentials by specifying the private key
        # file.


        #print(buckets = list(client.list_buckets())
        bucket = self._client.get_bucket(bucket_name)
        blob = bucket.blob(blob_name)
        blob.upload_from_file(file_bytes) #upload_from_filename(path_to_file)
        
        #returns a public url
        self.make_blob_public(blob_name,bucket_name)
        return blob.public_url
    def rename_blob(self,blob_name, new_blob_name:str,bucket_name:str="revisioncardimages"):
        
        """
        Function for renaming file in a bucket buckets.

        inputs
        -----
        bucket_name: name of bucket
        blob_name: str, name of file 
            ex. 'data/some_location/file_name'
        new_blob_name: str, name of file in new directory in target bucket 
            ex. 'data/destination/file_name'
        """


        bucket = self._client.bucket(bucket_name)
        blob = bucket.blob(blob_name)
        new_blob = bucket.rename_blob(blob, str(new_blob_name))
        self.make_blob_public(new_blob_name,bucket_name)
        return new_blob.public_url
    def get_media(self,blob_name:str,bucket_name:str="revisioncardimages"):
        try:
            bucket =self._client.get_bucket(bucket_name)
            blob = bucket.blob(blob_name)
            self.make_blob_public(blob_name)


            return{"title":blob.name,"url":blob.public_url}
        except NotFound as nof:
            logging.warning("Delete - Object does not exist.")
            pass
    def get_all_media(self,bucket_name:str="revisioncardimages"):
        bucket =self._client.get_bucket(bucket_name)
        blobs = bucket.list_blobs()
        return [{"title":blob.name,"url":blob.public_url,"public_callback":self.make_blob_public(blob.name)} for blob in blobs]
    def gen_get_all_media(self,bucket_name:str="revisioncardimages"):
        bucket =self._client.get_bucket(bucket_name)
        blobs = bucket.list_blobs()
        for blob in blobs:
            self.make_blob_public(blob.name)
            yield {"title":blob.name,"url":blob.public_url}

    def delete_media(self,blob_name:str,bucket_name:str="revisioncardimages"):
        try:
            bucket =self._client.get_bucket(bucket_name)
            blob = bucket.blob(blob_name)
            generation_match_precondition = None

            # Optional: set a generation-match precondition to avoid potential race conditions
            # and data corruptions. The request to delete is aborted if the object's
            # generation number does not match your precondition.
            blob.reload()  # Fetch blob metadata to use in generation_match_precondition.
            generation_match_precondition = blob.generation

            blob.delete(if_generation_match=generation_match_precondition)
        except NotFound as nof:
            logging.warning("Delete - Object does not exist.")
            pass
    def delete_subset_media(self,blob_suffix:str,bucket_name:str="revisioncardimages"):
        bucket = self._client.get_bucket(bucket_name)
        # list all objects in the directory
        blobs = bucket.list_blobs()
        for blob in blobs:
            if blob_suffix in blob.name:
                blob.delete()



if __name__ == "__main__":
    caesaraigcp = CaesarAIGCP()

    caesaraigcp.get_media("caer2.jpeg")
    #for media in media:
    #    print(media)
    