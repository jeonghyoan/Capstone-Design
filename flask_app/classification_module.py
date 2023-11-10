#!/usr/bin/env python
# coding: utf-8

# In[37]:


import urllib.request
import urllib.parse
from bs4 import BeautifulSoup as bs
import platform
from PIL import ImageFont, ImageDraw, Image
from matplotlib import pyplot as plt
import tensorflow as tf
import tensorflow_text
import re
import time
import pandas as pd
import numpy as np
import os
import uuid
import json
import requests
import sys


class ClassificationSystem:
    def __init__(self, reloadedModel = None, contents = None, threshold = 0.5, savedModelPath = None, excludeWordList = None, keyWordList = None, lastNum = 5):
        self.reloadedModel = reloadedModel
        self.contents = contents
        self.threshold = threshold
        self.savedModelPath = savedModelPath
        self.keyWordList = keyWordList
        self.excludeWordList = excludeWordList
        self.lastNum = lastNum
        #Initializing datas needed
        self.Setting()
        
    #methods for setting required data
    #setting keywords and reload trained text classification deep-learning model
    def Setting(self):
        #setting keywords
        keyWordData = pd.read_csv('./키워드&업체명_최종.csv')
        self.keyWordList = keyWordData['키워드'].tolist()
        self.excludeWordList = ["받지않고","100%내돈내산", "#체험단", "제공합", "체험할수", "제공하겠", "경험하니", "제공하기도", "뷰티블로거", "제공해드리며", "직접구매"]
        #load deeplearning model
        self.savedModelPath = './BlogPostClassifier'
        self.reloadedModel = tf.saved_model.load(self.savedModelPath)
        
    #used for data preprocessing
    #as a result, all the marks or blanks are removed from text
    def RemoveTrash(self, text):
        result = re.sub(r'[,. ]', '', text)
        return result
    
    
    #used for put newly inserted element in the tail of array, and let existing elements move forward once
    #as a result of this, existing first element(element of index 0) would be eliminated from the array
    #the reason why this method is defined is described in description of GetLastParagraph method which would be discussed further
    def MoveForward(self, array, newElement):
        for i in range(1, len(array)):
            array[i - 1] = array[i]
        array[-1] = newElement
        
    #used for altering transparent pixels to white pixels
    #this is because sometimes OCR do not works well if there is no background color in image
    def MakeBackWhite(self, image_file):
        try:
            img = Image.open(image_file)

            width, height = img.size

            #fill the transparent pixels with white pixels
            for x in range(width):
                for y in range(height):
                    pixel = img.getpixel((x, y))
                    if pixel[3] == 0:  #if alpha value is 0 --> if it is transparent pixel
                        img.putpixel((x, y), (255, 255, 255, 255))  

            #save altered image
            img.save(image_file)
        except IndexError: #Sometimes there are some image that do not have alpha value --> such files are usually have background color(not a transparent image), so just save it
            img.save(image_file)
        except TypeError:  # 'int' object is not subscriptable ... Sometimes there are some image that have only one int value for pixel value --> such files are usually have background color(not a transparent image), so just save it
            img.save(image_file)
        
    #Classification method : all you need in this entire class definition
    def Classification(self, link):
        print('----------------------Step 1 : Text Classification----------------------')
        #first, get last 5 paragraphs of the blog's contents
        #the contents(text, image) are given by accessing the blog link, and getting the html
        lastParagraphs = self.GetLastParagraph(link)
        #if returned last paragraph is 'Closed page', it is page that we cannot access
        if lastParagraphs != 'Closed page':
            #if returned last paragraph is not 'Closed page', it is valid classification target
            #this is mainly because the blogger deleted the page
            print('System : Valid page - Text Classification start')
            textClassificationResult = self.TextClassification(lastParagraphs)
            #if advertisement is detected in text contents, 1 is returned and classification would be terminated
            if textClassificationResult == 1:
                print('System : Ad detected in text')
                return 1
            #if advertisement is not detected in text contents, classification via image(OCR) starts
            else:
                print('System : Ad did not detected - OCR start')
                print('----------------------Step 2 : OCR----------------------')
                #get last 5 image of the blog's contents
                #all the images are converted into text data with OCR
                #if page is closed, returned OCR paragraph is 'Closed page'
                #but this condition should not be used since if it's invalid page, it would be filtered in upper condition(in test classification)
                ocrParagraphs = self.OCR(link)
                if ocrParagraphs == 'Closed page':
                    print('System : Page is not available for OCR now')
                    return -1
                #texts converted from images are also target of classification sequence which is same with text classification
                ocrClassificationResult = self.TextClassification(ocrParagraphs)
                #if advertisement is detected in image contents, 1 is returned and classification would be terminated
                if ocrClassificationResult == 1:
                    print('System : Ad detected in image')
                    return 1
                #if advertisement is not detected in image contents, classification via deep-learning model starts
                else:
                    print('System : Ad did not detected in image - text analysis start')
                    print('----------------------Step 3 : text analysis----------------------')
                    textAnalysisResult = self.TextAnalysis(self.contents)
                    #if advertisement is detected in text analysis, 1 is returned and classification would be terminated
                    if textAnalysisResult == 1:
                        print('System : Ad detected in text analysis')
                        return 1
                    #if advertisement is not detected in text analysis, it cans be seen as genuine review
                    #return 0(not advertisement)
                    else :
                        print('System : Ad did not detected at all')
                        return 0
        else:#in the case if we cannot access to page
            print('System : Cannot access to the page')
            return -1
        
    
    #this method is used for getting last 5 paragraphs from blog contents
    def GetLastParagraph(self, link):
        response = requests.get(link)
        
        if response.status_code == 200:
            try:
                soup = bs(response.text, 'html.parser')
                src = 'https://blog.naver.com/' + soup.iframe['src']

                response2 = requests.get(src)
                if response2.status_code == 200:
                    soup2 = bs(response2.text, 'html.parser')
                    main = soup2.find("div", attrs={'class':'se-main-container'}).text
            except TypeError: #if response is not valid, return 'Closed page'
                return 'Closed page'
        else: #if response is not valid, return 'Closed page'
            return 'Closed page'
        #text preprocessing phase
        main = main.replace('\u200b', '')
        main = re.sub('\n+', '\n', main)
        main = main.replace('\n \n', '\n')
        main = main.strip()
        #save whole contents for further text analysis phase
        self.contents = main
        #split contents for time efficiency
        #only last 5 paragraphs are candidates
        paragraphs = re.split(r'[.?!]\s|\n', main)
        paragraphs = self.DealWithHashtag(paragraphs)
        
        #initialize array with 5 elements of 'None'
        #it is very unusual case but sometimes there are some blog posts with less then 5 paragraphs
        #this is for avoid indexError
        lastParagraphs = ['None'] * self.lastNum
        
        for num in range(self.lastNum):
            try:
                #insert newly get paragraphs in lastParagraphs array, with MoveForward method mentioned above
                self.MoveForward(lastParagraphs, paragraphs[-1-num])
            except IndexError: #if the number of paragraph is less then 5
                break               

        for idx in range(len(lastParagraphs)):
            #remove blanks from paragraphs
            lastParagraphs[idx] = self.RemoveTrash(lastParagraphs[idx])

        print('lastParagraphs:')
        for idx in range(len(lastParagraphs)):
            print(lastParagraphs[idx])

        return lastParagraphs
        
    #this method is used for integrating all the hashtags included in blog post as one paragraphs
    #sometimes each hashtags are recognized as one paragraph
    #if this situation is not resolved, the last five paragraphs may all be hashtags
    #this situation will be obstacle for classification, so prevent that situation with this method
    def DealWithHashtag(self, arr):
        result = []
        current_concatenated = ''
        for item in arr:
            if item.startswith('#'):
                current_concatenated += item
            else:
                if current_concatenated:
                    result.append(current_concatenated)
                    current_concatenated = ''
                result.append(item)
        if current_concatenated:
            result.append(current_concatenated)
            
        return result
    
    #this method is text classification methods
    #to classify if there are keyword or exclude-word in text
    def TextClassification(self, lastParagraphs):
        resultArray = []
        for paragraph in lastParagraphs:
            keyWordFound = False

            for keyWord in self.keyWordList:
                #if keyword is included in paragraph, it is seen as advertisement
                if keyWord in paragraph:
                    keyWordFound = True
                    #if exclude-word is included in paragraph, with keyword, we cannot regard this as advertisement
                    #this should be candidate of text analysis(to detect any possible stealth advertisement)
                    for excludeWord in self.excludeWordList:
                        if excludeWord in paragraph:
                            keyWordFound = False
                            break
                    break
            #if keyword is found, append 1 in result array
            if keyWordFound:
                resultArray.append(1)
            #if keyword is not found or found with exclude-word, append 0 in result array
            else:
                resultArray.append(0)
        print(resultArray)
        #if any keyword is detected in any paragraph, it is advertisement post
        if 1 in resultArray:
            return 1
        #if not, return 0 and move on to next phase(image classification or text analysis)
        else:
            return 0
    
    #this method converts image data into text data
    def OCR(self, link):
        OCR_texts = []
        #get last 5 image source links
        sticker_sources = self.GetImageSource(link)
        #if it is valid target:
        if sticker_sources != 'Closed page':
            p = 0
            
            for img_url in sticker_sources:
                print('---------------------------',p,'th image---------------------------')
                if img_url == 'None':
                    continue
                else:
                    #encoding setting to deal with Korean
                    print('img url: ', img_url)

                    #decoded_url = urllib.parse.unquote(img_url)
                    encoded_url = urllib.parse.quote(img_url, safe=":/?=")
                    print('encoded_url: ', encoded_url)
                    #if blog advertisement agency's name is included in link, OCR is not needed
                    if 'revu' in encoded_url:
                        #append any keyword to OCR result, so that advertisement can be detected in OCR result
                        OCR_texts.append('무상지원')
                    elif 'reviewplace' in encoded_url:
                        OCR_texts.append('무상지원')
                    elif 'reviewnote' in encoded_url:
                        OCR_texts.append('무상지원')
                    elif 'storyn' in encoded_url:
                        OCR_texts.append('무상지원')
                    elif '%25EA%25B0%2595%25EB%2582%25A8%25EB%25A7%259B%25EC%25A7%2591' in encoded_url:#in the case of agency '강남맛집'
                        OCR_texts.append('무상지원')
                    elif 'tble' in encoded_url:
                        OCR_texts.append('무상지원')
                    else:
                        try:
                            #access to image source's url and save original image file
                            urllib.request.urlretrieve(encoded_url, "image" + str(p) + ".png")
                            image_file = "image" + str(p) + ".png"
                            
                            #in our experience, if the image source is not naver sticker or user's uploaded file, the image's background was usually transparent
                            #so check if the image is not both case
                            if 'storep-phinf' not in img_url: #if image is not naver sticker
                                if 'postfiles.pstatic.net' not in img_url: #if image is not user uploaded file
                                    self.MakeBackWhite(image_file) #transform transparent gackground to white background
                            #if image is naver sticker or user-uploaded file, upper condition is not used

                            #now, request NAVER CLOVA OCR API to get ocr result of the image
                            ocrResult = self.OCRAPI(image_file)
                            OCR_texts.append(ocrResult)
                        except urllib.error.URLError:
                            print('System : url is not available now... try again')
                            OCR_texts.append('Error - Try again')
                p+=1

            for idx in range(len(OCR_texts)):
                OCR_texts[idx] = self.RemoveTrash(OCR_texts[idx])

            print('OCR_texts:')
            for e in OCR_texts:
                print(e)

            return OCR_texts
        else: #if any sticker link is not valid, return 'Closed page'
            return 'Closed page'
    
    #this method is used for getting last 5 image source url link from the blog post
    def GetImageSource(self, link):
        response = requests.get(link)
    
        if response.status_code == 200:
            soup = bs(response.text, 'html.parser')
            src = 'https://blog.naver.com/' + soup.iframe['src']

            response2 = requests.get(src)
            if response2.status_code == 200:
                soup2 = bs(response2.text, 'html.parser')
        else:
            return 'Closed page'
        
        

        #this is sequence of getting only image source urls in whole html contents of the blog post link
        main = soup2.select_one('div.se-main-container')
        stickers = main.select('[class*=image]')
        img_stickers = [sticker for sticker in stickers if sticker.name in ['img', 'video']]
            
        #also initialize array with 5 'None' to avoid indexError, and use 'MoveForward' method
        sticker_sources = ['None'] * self.lastNum
        
        if len(img_stickers) == 0: # if there is not image in the blog post
                print('No sticker')
        else:
            for sticker in img_stickers:
                string = str(sticker)
                pattern = re.compile('"https://(.+?)"')
                match = pattern.search(string)
                if match:
                    src = match.group(1)
                else:
                    pattern = re.compile('"http://(.+?)"')
                    match = pattern.search(string)
                    if match:
                        src = match.group(1)
                    else:
                        print('Cannot find img source')

                if 'ssl.pstatic.net' in src:
                    continue
                if 'static.map' in src:
                    continue
                src = 'https://' + src
                self.MoveForward(sticker_sources, src)

        return sticker_sources
    
    #requesting OCR through NAVER CLOVA OCR API
    def OCRAPI(self, image_file):
        api_url = 'https://dc6wxilxz9.apigw.ntruss.com/custom/v1/25288/437b23172b9471714768d2e04f162ce60453c20b537138be6d23fbf9da95320a/general'
        secret_key = 'TERFRE51d1hqbWFwYVJBeEJMd2hVdHVocWhUSVdrbHI='
        
        #get request json
        request_json = {
            'images': [
                {
                    'format': 'jpg',
                    'name': 'demo'
                }
            ],
            'requestId': str(uuid.uuid4()),
            'version': 'V2',
            'timestamp': int(round(time.time() * 1000))
        }

        payload = {'message': json.dumps(request_json).encode('UTF-8')}
        files = [
          ('file', open(image_file,'rb'))
        ]
        headers = {
          'X-OCR-SECRET': secret_key
        }

        #send request and get response
        response = requests.request("POST", api_url, headers=headers, data = payload, files = files)

        ocr_response = response.text

        #JSON parsing
        parsed_response = json.loads(ocr_response)

        if parsed_response["images"][0]["inferResult"] == 'SUCCESS':
            #OCR result text is in "inferText" element in json file
            #save "inferText" in array
            infer_texts = []
            fields = parsed_response["images"][0]["fields"]
            for field in fields:
                infer_texts.append(field["inferText"])

            #if any line change is detected in image, there can be multiple inferTexts
            #so join them
            text = ' '.join(infer_texts)

            return text
        #if file type is gif, error occurs
        else:
            return 'gif'
    
    #this method is for text analysis
    #make classification with the deep-learning model
    def TextAnalysis(self, input):
        print('System : Text Analysis start')
        print(self.savedModelPath)
        analysisResult = tf.sigmoid(self.reloadedModel(tf.constant([input])))
        analysisResult = analysisResult.numpy()[0]
        print(analysisResult)
        if analysisResult >= 0.5:
            return 1
        else:
            return 0