from mongoengine import Document, StringField, ListField


class OAuth2ClientDocument(Document):
    name: str = StringField()
    website_url: str = StringField(db_field="websiteUrl")
    logo_url: str = StringField(db_field="logoUrl")
    author: str = StringField()
    redirect_uris: list[str] = ListField(StringField(), db_field="redirectUris")
    meta = {"collection": "oauth2-client"}
