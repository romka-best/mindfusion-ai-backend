class ReferenceImageGateway:
    def __init__(self, firebase):
        self.firebase = firebase

    async def get_public_link(self, user_id: str, filename: str) -> str:
        image_path = f"users/vision/{user_id}/{filename}"
        blob = await self.firebase.bucket.get_blob(image_path)

        return self.firebase.get_public_url(blob.name)
