from django.shortcuts import render, redirect
from .models import Categoria, Flashcard, Desafio, FlashcardDesafio
from django.contrib.messages import constants
from django.contrib import messages
from django.http import Http404

# Create your views here.
def novo_flashcard(request):
    if not request.user.is_authenticated:
        return redirect('/usuarios/logar')
    if request.method == 'GET':
        categoria = Categoria.objects.all()
        dificuldades = Flashcard.DIFICULDADE_CHOICES
        flashcards = Flashcard.objects.filter(user=request.user)
        categoria_filtrar = request.GET.get('categoria')
        dificuldade_filtrar = request.GET.get('dificuldade')

        if categoria_filtrar:
            flashcards = flashcards.filter(categoria__id=categoria_filtrar)
        print(dificuldade_filtrar)
        if dificuldade_filtrar:
            flashcards = flashcards.filter(dificuldade=dificuldade_filtrar)
        return render(request, 'novo_flashcard.html', {'categorias': categoria, 'dificuldades': dificuldades, 'flashcards': flashcards})
    elif request.method == 'POST':
        pergunta = request.POST.get('pergunta')
        resposta = request.POST.get('resposta')
        categoria = request.POST.get('categoria')
        dificuldade = request.POST.get('dificuldade')

        if len(pergunta.strip()) == 0 or len(resposta.strip()) == 0:
            messages.add_message(request, constants.ERROR, 'Preencha os campos de resposta e pergunta')
            return redirect('/flashcard/novo_flashcard')
        
        flashcard = Flashcard(user=request.user, pergunta=pergunta, resposta=resposta, categoria_id=categoria, dificuldade=dificuldade)

        flashcard.save()
        messages.add_message(request, constants.SUCCESS, 'Cadastrado com sucesso')
        return redirect('/flashcard/novo_flashcard')
    
def deletar_flashcard(request, id):
    flashcard = Flashcard.objects.get(id=id)
    flashcard.delete()
    messages.add_message(request, constants.SUCCESS, 'Flashcard deletado com sucesso')
    return redirect('/flashcard/novo_flashcard/')

def iniciar_desafio(request):
    if request.method == 'GET':
        categoria = Categoria.objects.all()
        dificuldades = Flashcard.DIFICULDADE_CHOICES
        return render(request, 'iniciar_desafio.html', {'categorias': categoria, 'dificuldades': dificuldades})
    elif request.method == 'POST':
        titulo = request.POST.get('titulo')
        categorias = request.POST.getlist('categoria')
        dificuldade = request.POST.get('dificuldade')
        qtd_perguntas = request.POST.get('qtd_perguntas')
        desafio = Desafio(
                            user=request.user,
                            titulo=titulo,
                            quantidade_perguntas=qtd_perguntas,
                            dificuldade=dificuldade,
                        )
        desafio.save()

        for categoria in categorias:
            desafio.categoria.add(categoria)

        flashcard = Flashcard.objects.filter(user=request.user).filter(dificuldade=dificuldade).filter(categoria_id__in=categorias).order_by('?')
        if flashcard.count() < int(qtd_perguntas):
            qtd_perguntas = flashcard.count()
        flashcard = flashcard[0:int(qtd_perguntas)]

        for flash in flashcard:
            flashcard_desafio = FlashcardDesafio(flashcard=flash)
            flashcard_desafio.save()
            desafio.flashcards.add(flashcard_desafio)

        desafio.save()

        return redirect(f'/flashcard/desafio/{desafio.id}')
    
def listar_desafio(request):
    if request.method == 'GET':
        desafios = Desafio.objects.filter(user=request.user)
        categorias = Categoria.objects.all()
        dificuldades = Flashcard.DIFICULDADE_CHOICES
        filtro_categorias = request.GET.get('categoria')
        filtro_dificuldades = request.GET.get('dificuldade')
        print(filtro_categorias)
        if filtro_categorias:
            desafios = Desafio.objects.filter(categoria=filtro_categorias)
        if filtro_dificuldades:
            desafios = Desafio.objects.filter(dificuldade=filtro_dificuldades)
        return render(request, 'listar_desafio.html', {'desafios': desafios, 'categorias': categorias, 'dificuldades': dificuldades})
    
def desafio(request, id):
    desafio = Desafio.objects.get(id=id)
    if not desafio.user == request.user:
        raise Http404()

    if request.method == 'GET':
        acertos = desafio.flashcards.filter(respondido=True).filter(acertou=True)
        erros = desafio.flashcards.filter(respondido=False).filter(acertou=False)
        faltantes = desafio.flashcards.filter(respondido=False).count()
        return render(request, 'desafio.html', {'desafio': desafio, 'acertos': acertos.count(), 'erros': erros.count(), 'faltantes': faltantes})
    
def responder_flashcard(request, id):
    flashcard_desafio = FlashcardDesafio.objects.get(id=id)
    acertou = request.GET.get('acertou')
    desafio_id = request.GET.get('desafio_id')
    if not flashcard_desafio.flashcard.user == request.user:
        return Http404()
    flashcard_desafio.respondido = True
    if acertou == '1':
        flashcard_desafio.acertou = True
    elif acertou == '0':
        flashcard_desafio.acertou = False
    flashcard_desafio.save()
    return redirect(f'/flashcard/desafio/{desafio_id}')

def relatorio(request, id):
    desafio = Desafio.objects.get(id=id)
    acertos = desafio.flashcards.filter(acertou=True).count()
    erros = desafio.flashcards.filter(acertou=False).count()
    dados = [acertos, erros]
    categorias = desafio.categoria.all()
    name_categoria = []
    dados2 = []
    for categoria in categorias:
        dados2.append(desafio.flashcards.filter(flashcard__categoria=categoria).filter(acertou=True).count())
        name_categoria.append(categoria.nome)

    return render(request, 'relatorio.html', {'desafio': desafio,
                                                'dados':dados,
                                                'categorias': name_categoria,
                                                'dados2': dados2})

