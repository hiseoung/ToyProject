from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, render
from django.http import HttpRequest, JsonResponse
from django.views.generic import View
from django.core.files.storage import FileSystemStorage
from .models import Paper
from django.contrib.auth.models import User

import os
import re
import requests
from datetime import datetime
from pdf2image import convert_from_path, convert_from_bytes
from ast import literal_eval


class HomeView(LoginRequiredMixin, View):
    def get(self, request: HttpRequest):
        context = {}

        context['user_id'] = request.user.id
        context['user_name'] = User.objects.filter(id=request.user.id).values_list('username', flat=True)[0]

        return render(request, 'main.html', context)

    def post(self, request: HttpRequest, *args, **kwargs):
        context = {}
        paper_text = []

        try:
            file = request.FILES.get('customFile')
            sep = os.sep
            path = os.getcwd() + sep + 'media' + sep

            # 저장받을 파일 경로를 추가합니다.
            fs = FileSystemStorage(location=path, base_url=path)

            # Media 폴더 경로에 파일을 저장합니다.
            filename = fs.save(file.name, file)

            # 파일 저장된 디렉터리 경로 저장
            uploaded_file_url = fs.url(filename)

            # data = Paper.objects.filter(file_name=filename).values_list('file_name')[0]            
            # context['file_name'] = data

            print(path + filename)
            # images = convert_from_path(path + filename)
            images = convert_from_path(path + filename)
            
            file_str_name = filename[:-4]
            os.mkdir(path + sep + file_str_name)

            for i, page in enumerate(images):
                page.save(path+file_str_name + sep + file_str_name+str(i)+".png", "PNG")
                image_path = path + file_str_name

            for idx, i in enumerate(os.listdir(image_path)):

                path = image_path + sep + i
                print(image_path + sep + i)

                files = {
                    'image_file': (f'{path}', open(f'{path}', 'rb')),
                }

                response = requests.post('http://127.0.0.1:49180/predict', files=files)    
                text = response.json()
                text = ' '.join(text)

                # t = response.text.encode('utf-8')
                # t = t.decode('utf-8')                
                # t = literal_eval(t)['text']
                # text = response.json()
                # print("===============================")
                # print(text['text'])
                # print("===============================")
                # text = ' '.join(str(_) for _ in t)

                data_created = Paper.objects.create(
                    user=request.user.id,
                    file_name=filename,
                    file_path=path,
                    file_text=text,
                    page_number = idx
                )

            filetext = list(Paper.objects.filter(file_name=filename).values_list('file_text', flat=True))
            filename = Paper.objects.filter(file_name=filename).values_list('file_name', flat=True)[0]

            context['paper_text'] = filetext
            context['file_name'] = filename
            context['success'] = True
            context['message'] = "업로드가 완료되었습니다."
            # serializers.serialize('json', qs)
            return JsonResponse(context, content_type='application/json')

        except Exception as e:
            context['success'] = False
            context['message'] = e

            return JsonResponse(context, content_type='application/json')
