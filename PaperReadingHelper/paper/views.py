from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, render
from django.http import HttpRequest, JsonResponse
from django.views.generic import View
from django.core.files.storage import FileSystemStorage
from .models import Paper

import os, re
from datetime import datetime

class HomeView(LoginRequiredMixin, View):
    def get(self, request: HttpRequest, *args, **kwargs):
        context = {}

        return render(request, 'blank.html', context)

    def post(self, request: HttpRequest, *args, **kwargs):
        context = {}

        try:
            file = request.FILES.get('customFile')
            path = os.getcwd() + '/media/'

            # 저장받을 파일 경로를 추가합니다.
            fs = FileSystemStorage(location=path, base_url=path)

            # Media 폴더 경로에 파일을 저장합니다.
            filename = fs.save(file.name, file)

            # 파일 저장된 디렉터리 경로 저장
            uploaded_file_url = fs.url(filename)

            data_created = Paper.objects.create(
                user = request.user.id,
                file_name = filename,
                file_path = uploaded_file_url
            )

            context['success'] = True
            context['message'] = "업로드가 완료되었습니다."

            return JsonResponse(context, content_type='application/json')

        except Exception as e:
            context['success'] = True
            context['message'] = e

            return JsonResponse(context, content_type='application/json')