from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse
import json
from django.views.decorators.csrf import csrf_exempt

from .forms import TodoForm
from .models import Todo

def index(request):

    item_list = Todo.objects.order_by("-date")
    if request.method == "POST":
        form = TodoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('todo')
    form = TodoForm()

    page = {
        "forms": form,
        "list": item_list,
        "title": "TODO LIST",
    }
    return render(request, 'todo/index.html', page)

def remove(request, item_id):
    item = Todo.objects.get(id=item_id)
    item.delete()
    messages.info(request, "Task Removed!")
    return redirect('todo')

def update_card(request):
    if request.method == "POST":
        data = json.loads(request.body)
        card_id = data.get("card_id")
        new_column = data.get("new_column")

        # Aqui você atualiza no banco
        card = Todo.objects.get(id=card_id)
        card.column = new_column
        card.save()

        return JsonResponse({"status": "ok"})