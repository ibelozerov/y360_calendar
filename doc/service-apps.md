Request: POST https://oauth.yandex.ru/token

content-type:application/x-www-form-urlencoded

client_id=f0bb5b131d7147c0a358313fc9644143&client_secret=394fe11a0d99438894e391a79779e4f0&subject_token=abugrin%40myandex360.ru&subject_token_type=urn%3Ayandex%3Aparams%3Aoauth%3Atoken-type%3Aemail&grant_type=urn%3Aietf%3Aparams%3Aoauth%3Agrant-type%3Atoken-exchange




Response example
{
  "access_token": "2.1130000065953636.737750.1773238212.1773234612463.1.0.11770638.0UGCtOZb46IPg4yy.J5k8Aqg56Q3lGdJDQ-IlxeCu7u2_xb6g5J3IwM8aUj2ixn2fe9RFxPkCMQTEEsKup8DTaURz2Xv-9GRdFL6o7Ag.ZDCl51h3PKDKgNBANDIlEg",
  "expires_in": 3600,
  "issued_token_type": "urn:ietf:params:oauth:token-type:access_token",
  "scope": "addressbook:all yadisk:disk cloud_api:disk.app_folder cloud_api:disk.read cloud_api:disk.write cloud_api:disk.info telemost-api:conferences.read mail:imap_full mail:imap_ro telemost-api:conferences.delete mail:smtp telemost-api:conferences.create telemost-api:conferences.update calendar:all",
  "token_type": "bearer"
}