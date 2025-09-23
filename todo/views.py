from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Max, F
from django.utils import timezone
import json


from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from .forms import TodoForm
from .models import Todo

def index(request):
    today = timezone.now().date()
###
    columns = {
        'column1': {
            'name': 'To Do',
            'cards': Todo.objects.filter(column='column1').order_by('position')
        },
        'column2': {
            'name': 'Doing', 
            'cards': Todo.objects.filter(column='column2').order_by('position')
        },
        'column3': {
            'name': 'Done',
            'cards': Todo.objects.filter(column='column3').order_by('position')
        },
    }
###
    page = {
        "columns": columns,
        "title": "Trellado", 
        "today": today,
    }
    return render(request, 'todo/index.html', page)

def remove(request, id):
    item = Todo.objects.get(id=id)
    item.delete()
    messages.info(request, "Task Removed!")
    return redirect('todo')

def create(request):
    if request.method == 'POST':
        form = TodoForm(request.POST)
        if form.is_valid():
            todo = form.save(commit=False)
            todo.column = 'column1'
            
            # Garantir que created_in tenha um valor
            if not todo.created_in:
                todo.created_in = timezone.now()
                
            # A posição será o próximo número disponível
            last_position = Todo.objects.filter(column='column1').aggregate(Max('position'))['position__max']
            todo.position = (last_position or 0) + 1
            todo.save()
            return redirect('todo')
    else:
        form = TodoForm()
    return render(request, 'todo/create_card.html', {'form': form})

def edit_card(request, id):
    todo = get_object_or_404(Todo, id=id)
    if request.method == 'POST':
        form = TodoForm(request.POST, instance=todo)
        if form.is_valid():
            edited_todo = form.save(commit=False)
            edited_todo.save()  # Salva sem alterar column e position
            return redirect('todo')
    else:
        form = TodoForm(instance=todo)
    return render(request, 'todo/edit_card.html', {'form': form})

@csrf_exempt
@require_POST
def update_card_position(request):
    try:
        data = json.loads(request.body)
        card_id = data.get('card_id')
        new_column = data.get('column')
        new_position = int(data.get('position'))
        
        card = Todo.objects.get(id=card_id)
        old_column = card.column
        old_position = card.position
        
        # Se é movimento dentro da mesma coluna
        if old_column == new_column:
            if new_position > old_position:
                # Movendo para baixo
                Todo.objects.filter(
                    column=old_column,
                    position__gt=old_position,
                    position__lte=new_position
                ).update(position=F('position') - 1)
            else:
                # Movendo para cima
                Todo.objects.filter(
                    column=old_column,
                    position__lt=old_position,
                    position__gte=new_position
                ).update(position=F('position') + 1)
        else:
            # Movendo entre colunas
            # Ajustar coluna original
            Todo.objects.filter(
                column=old_column,
                position__gt=old_position
            ).update(position=F('position') - 1)
            
            # Abrir espaço na coluna destino
            Todo.objects.filter(
                column=new_column,
                position__gte=new_position
            ).update(position=F('position') + 1)
        
        # Atualizar o card movido
        Todo.objects.filter(id=card_id).update(
            column=new_column,
            position=new_position
        )
        
        return JsonResponse({'status': 'success'})
    
    except Exception as e:
        print(f"Erro: {e}")
        return JsonResponse({'status': 'error', 'message': str(e)})