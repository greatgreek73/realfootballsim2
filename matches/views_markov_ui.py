from django.shortcuts import render

def markov_ui(request):
    # Простая страница с кнопкой и выводом сводки
    return render(request, "matches/markov_ui.html")
