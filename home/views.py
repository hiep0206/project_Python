from django.shortcuts import render

def index(request):
    return render(request, 'page/home.html')

def thong_tin(request):
    return render(request, 'page/infor.html')

def bai_viet(request):
    return render(request, 'page/write.html')

def lien_he(request):
    return render(request, 'page/contact.html')

# Thêm vào cuối file home/views.py
def contact(request):
    return render(request, 'home/contact.html')