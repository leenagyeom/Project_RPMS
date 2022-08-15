import os
import warnings
os.environ['KMP_DUPLICATE_LIB_OK'] = 'True'
warnings.filterwarnings("ignore", category=UserWarning)
import time
import re

import torch
from PIL import Image, ImageFilter

import easyocr
from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from azure.cognitiveservices.vision.computervision.models import OperationStatusCodes
from azure.cognitiveservices.vision.computervision.models import VisualFeatureTypes
from msrest.authentication import CognitiveServicesCredentials

def easy_ocr(path):
    reader = easyocr.Reader(['ko', 'en'], gpu=True)
    result = reader.readtext(path)
    read_result = result[0][1]
    read_confid = int(round(result[0][2], 2) * 100)
    return read_result, read_confid

def azure_ocr(path):
    ##### Azure Cognitive Service Info
    subscription_key = "8d06cd8651fd43f2bf392c71478a6d67"
    endpoint = "https://platestr.cognitiveservices.azure.com/"
    computervision_client = ComputerVisionClient(endpoint, CognitiveServicesCredentials(subscription_key))

    ##### OCR start ...
    img = open(path, "rb")
    
    read_response = computervision_client.read_in_stream(img, language="ko", raw=True)
    read_operation_location = read_response.headers["Operation-Location"]
    operation_id = read_operation_location.split("/")[-1]

    while True:
        read_result = computervision_client.get_read_result(operation_id)
        if read_result.status not in ['notStarted', 'running']:
            break
        time.sleep(1)

    if read_result.status == OperationStatusCodes.succeeded:
        for text_result in read_result.analyze_result.read_results:
            for line in text_result.lines:
                print(f'Azure OCR 결과    : {line.text}')
                ocr_result = re.sub(r'[^\w\s]', '', line.text)
                ocr_result = ocr_result.replace(' ', '')
                
            return ocr_result
                # print(line.bounding_box)
