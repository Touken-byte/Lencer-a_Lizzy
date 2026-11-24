from django.shortcuts import render


def terminos(request):
    return render(request, 'frontend/terminos.html')


def privacidad(request):
    return render(request, 'frontend/privacidad.html')


def politica_cookies(request):
    return render(request, 'frontend/cookies.html')
