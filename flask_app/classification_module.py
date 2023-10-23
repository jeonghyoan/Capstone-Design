#!/usr/bin/env python
# coding: utf-8

# In[25]:


import urllib.request
import urllib.parse
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import UnexpectedAlertPresentException
from selenium.common.exceptions import WebDriverException
from selenium import webdriver
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
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
import cv2
import requests
import sys

class ClassificationSystem:
    def __init__(self, contents = None, threshold = 0.5, savedModelPath = None, excludeWordList = None, keyWordList = None, lastNum = 10):
        self.contents = contents
        self.threshold = threshold
        self.savedModelPath = savedModelPath
        self.keyWordList = keyWordList
        self.excludeWordList = excludeWordList
        self.lastNum = lastNum
        # 생성시 한번 반드시 LoadKeyWords 실행
        self.LoadKeyWord()
        
    def LoadKeyWord(self):
        keyWordData = pd.read_csv('./키워드&업체명_최종.csv')
        self.keyWordList = keyWordData['키워드'].tolist()
        self.excludeWordList = ["받지않고","100%내돈내산", "#체험단", "제공합", "체험할수", "제공하겠", "경험하니", "제공하기도", "뷰티블로거", "제공해드리며", "직접구매"]
        self.savedModelPath = './BlogPostClassifier'
        
    def RemoveTrash(self, text):
        result = re.sub(r'[,. ]', '', text)
        return result
    
    def MoveForward(self, array, newElement):
        for i in range(1, len(array)):
            array[i - 1] = array[i]
        array[-1] = newElement
        
    def MakeBackWhite(self, image_file):
        try:
            img = Image.open(image_file)

            width, height = img.size

            # 투명한 부분을 흰색으로
            for x in range(width):
                for y in range(height):
                    pixel = img.getpixel((x, y))
                    if pixel[3] == 0:  # Alpha 값이 0(투명 픽셀)
                        img.putpixel((x, y), (255, 255, 255, 255))  

            # 바뀐 이미지 저장 
            img.save(image_file)
        except IndexError: # 알파값이 존재하지 않는 이미지
            img.save(image_file)
        except TypeError:  # 'int' object is not subscriptable ... 픽셀값 int 하나만 가진 이미지가 있는데 그경우 처리
            img.save(image_file)
        
    #실제 분류 코드 : 이 메소드만 호출하면 됨
    def Classification(self, link):
        while True:
            print('----------------------Step 1 : Text Classification----------------------')
            try:
                lastSentences = self.GetLastSentence(link)
                if lastSentences != 'Closed page':
                    print('System : Valid page - Text Classification start')
                    textClassificationResult = self.TextClassification(lastSentences)
                    if textClassificationResult == 1:
                        print('System : Ad detected in text')
                        return 1
                    else:
                        print('System : Ad did not detected - OCR start')
                        print('----------------------Step 2 : OCR----------------------')
                        ocrSentences = self.OCR(link)
                        if ocrSentences == 'Closed page':
                            print('System : Page is not available for OCR now')
                            return -1
                        ocrClassificationResult = self.TextClassification(ocrSentences)
                        if ocrClassificationResult == 1:
                            print('System : Ad detected in image')
                            return 1
                        else:
                            print('System : Ad did not detected in image - text analysis start')
                            print('----------------------Step 3 : text analysis----------------------')
                            textAnalysisResult = self.TextAnalysis(self.contents)
                            if textAnalysisResult == 1:
                                print('System : Ad detected in text analysis')
                                return 1
                            else :
                                print('System : Ad did not detected at all')
                                return 0
                else:#접근할 수 없는 페이지였을때 ex 구버전 or 삭제된 페이지
                    print('System : Cannot access to the page')
                    return -1
            except WebDriverException:
                print('System : Link unavailable temporarily : retry in 3 seconds')
                time.sleep(3)
        
    
    def GetLastSentence(self, link):
        #웹드라이버 설정
        options = webdriver.ChromeOptions()
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)
        
        client_id = "dEHbLikkg1UHv7x1qKPw" # 발급받은 id 입력
        client_secret = "ok2VRdqWEE" # 발급받은 secret 입력 
        
        driver = webdriver.Chrome(executable_path='./chromedriver-win64/chromedriver.exe', options=options)
        driver.implicitly_wait(1)
        try:
            #블로그 링크 접근
            driver.get(link)
            time.sleep(0.5)
            #블로그 안 본문이 있는 iframe에 접근하기
            driver.switch_to.frame("mainFrame")
            html = driver.page_source
            soup = bs(html, 'html.parser')

            lastSentences = ['None'] * self.lastNum
            try:
                mainContainerContents = driver.find_element(By.CSS_SELECTOR,'div.se-main-container').text
                #텍스트 이진분류용으로 전체 내용 저장
                self.contents = mainContainerContents
                #문장단위로 분리
                sentences = re.split(r'[.?!]\s|\n', mainContainerContents)
                sentences = self.DealWithHashtag(sentences)

                for num in range(self.lastNum):
                    try:
                        self.MoveForward(lastSentences, sentences[-1-num])
                    except IndexError:
                        break
            except NoSuchElementException:
                print('Old-Version')
                return 'Closed page'

            for idx in range(len(lastSentences)):
                lastSentences[idx] = self.RemoveTrash(lastSentences[idx])

            #------------------------------------------------------------------------------------
            #실험용 나중에 지울것

            print('lastSentences:')
            for e in lastSentences:
                print(e)
            #------------------------------------------------------------------------------------

            return lastSentences
        except UnexpectedAlertPresentException:
            print('Closed page')
            return 'Closed page'
        
    #Last Sentence 내에 해시태그들을 단일 요소로 합치는 메소드
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
    
    def TextClassification(self, lastSentences):
        resultArray = []
        for sentence in lastSentences:
            keyWordFound = False

            for keyWord in self.keyWordList:
                if keyWord in sentence:
                    keyWordFound = True

                    for excludeWord in self.excludeWordList:
                        if excludeWord in sentence:
                            keyWordFound = False
                            break
                    break
            if keyWordFound:
                resultArray.append(1)
            else:
                resultArray.append(0)
        print(resultArray)
        if 1 in resultArray:
            return 1
        else:
            return 0
    
    def OCR(self, link):
        OCR_texts = []
        #블로그 링크 접근
        sticker_sources = self.GetImageSource(link)
        if sticker_sources != 'Closed page':
            p = 0
            
            for img_url in sticker_sources:
                print('---------------------------',p,'th image---------------------------')
                if img_url == 'None':
                    continue
                else:
                    #한글 포함된 링크는 따로 인코딩 처리를 해줘야한다고 함
                    print('img url: ', img_url)

                    #decoded_url = urllib.parse.unquote(img_url)
                    encoded_url = urllib.parse.quote(img_url, safe=":/?=")
                    print('encoded_url: ', encoded_url)
                    if 'revu' in encoded_url:
                        OCR_texts.append('무상지원')
                    elif 'reviewplace' in encoded_url:
                        OCR_texts.append('무상지원')
                    elif 'reviewnote' in encoded_url:
                        OCR_texts.append('무상지원')
                    elif 'storyn' in encoded_url:
                        OCR_texts.append('무상지원')
                    elif '%25EA%25B0%2595%25EB%2582%25A8%25EB%25A7%259B%25EC%25A7%2591' in encoded_url:#강남맛집 인코딩 관련 처리
                        OCR_texts.append('무상지원')
                    elif 'tble' in encoded_url:
                        OCR_texts.append('무상지원')
                    else:#배경 하얗게 처리하는 부분
                        try:
                            urllib.request.urlretrieve(encoded_url, "image" + str(p) + ".png")
                            image_file = "image" + str(p) + ".png"
                            # 이미지 열기
                            # 스티커가 아닐경우
                            if 'storep-phinf' not in img_url:
                                if 'postfiles.pstatic.net' not in img_url:
                                    self.MakeBackWhite(image_file)

                            ocrResult = self.OCRAPI(image_file)
                            OCR_texts.append(ocrResult)
                        except urllib.error.URLError:
                            print('System : url is not available now... try again')
                            OCR_texts.append('Error - Try again')
                p+=1

            for idx in range(len(OCR_texts)):
                OCR_texts[idx] = self.RemoveTrash(OCR_texts[idx])
            #------------------------------------------------------------------------------------
            #실험용 나중에 지울것

            print('OCR_texts:')
            for e in OCR_texts:
                print(e)
            #------------------------------------------------------------------------------------

            return OCR_texts
        else:
            return 'Closed page'
    
    def GetImageSource(self, link):
        #웹드라이버 설정
        options = webdriver.ChromeOptions()
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)
        
        driver = webdriver.Chrome(executable_path='./chromedriver-win64/chromedriver.exe', options=options)
        driver.implicitly_wait(1)
        
        driver.get(link)
        time.sleep(1)
        p = 0
        #본문 내용 크롤링하기
        try:
            #블로그 안 본문이 있는 iframe에 접근하기
            driver.switch_to.frame("mainFrame")
            html = driver.page_source
            soup = bs(html, 'html.parser')
            main_container = soup.select_one('div.se-main-container')
            stickers = main_container.select('[class*=image]')
            img_stickers = [sticker for sticker in stickers if sticker.name in ['img', 'video']]
            

            if len(img_stickers) == 0:
                print('No sticker')
            else:
                sticker_sources = ['None'] * self.lastNum
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
                
        except AttributeError:
            print('The page is not available now. Please retry it later')
            return 'Closed page'
        #TextClassification 메소드에서 이미 걸러지기때문에 사실 쓰이지는 않음
        except NoSuchElementException:
            print('Closed page')
    
    #네이버 API를 통한 OCR
    def OCRAPI(self, image_file):
        api_url = 'https://dc6wxilxz9.apigw.ntruss.com/custom/v1/25288/437b23172b9471714768d2e04f162ce60453c20b537138be6d23fbf9da95320a/general'
        secret_key = 'TERFRE51d1hqbWFwYVJBeEJMd2hVdHVocWhUSVdrbHI='
        # 이미지에서 문자 추출
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

        response = requests.request("POST", api_url, headers=headers, data = payload, files = files)

        ocr_response = response.text

        # JSON 파싱
        parsed_response = json.loads(ocr_response)

        if parsed_response["images"][0]["inferResult"] == 'SUCCESS':
            # "inferText" 값을 추출하여 리스트에 저장
            infer_texts = []
            fields = parsed_response["images"][0]["fields"]
            for field in fields:
                infer_texts.append(field["inferText"])

            text = ' '.join(infer_texts)

            return text
        else:
            return 'gif'
    
    def TextAnalysis(self, input):
        print('System : Text Analysis start')
        print(self.savedModelPath)
        reloadedModel = tf.saved_model.load(self.savedModelPath)
        analysisResult = tf.sigmoid(reloadedModel(tf.constant([input])))
        print(analysisResult)
        if analysisResult >= 0.5:
            return 1
        else:
            return 0

