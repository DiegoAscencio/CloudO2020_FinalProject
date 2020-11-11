#Needed permissions:
# Translate Access

import json
import boto3

def lambda_handler(event, context):
    translate = boto3.client(service_name='translate', region_name='us-east-1', use_ssl=True)
    
    result = translate.translate_text(Text="Hello, World. This is a test of the translate service", 
                SourceLanguageCode="en", TargetLanguageCode="es")
    print('TranslatedText: ' + result.get('TranslatedText'))
    print('SourceLanguageCode: ' + result.get('SourceLanguageCode'))
    print('TargetLanguageCode: ' + result.get('TargetLanguageCode'))
