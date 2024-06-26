from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from .models import Pacientes, DadosPaciente, Refeicao, Opcao
from datetime import datetime


@login_required(login_url='/auth/login/')
def pacientes(request):
    if request.method == 'GET':
        pacientes = Pacientes.objects.filter(nutri=request.user)
        return render(request, 'pacientes.html', {'pacientes': pacientes})


@login_required(login_url='/auth/login/')
def valida_paciente(request):
    if request.method == 'POST':
        nome = request.POST.get('nome')
        sexo = request.POST.get('sexo')
        idade = request.POST.get('idade')
        email = request.POST.get('email')
        telefone = request.POST.get('telefone')

        if (len(nome.strip()) == 0) or (len(sexo.strip()) == 0) or (len(idade.strip()) == 0) or (len(email.strip()) == 0) or (len(telefone.strip()) == 0):
            messages.add_message(request, messages.ERROR, 'Preencha todos os campos')
            return redirect('/pacientes/')

        if not idade.isnumeric():
            messages.add_message(request, messages.ERROR, 'Digite uma idade válida')
            return redirect('/pacientes/')

        pacientes = Pacientes.objects.filter(email=email)

        if pacientes.exists():
            messages.add_message(request, messages.ERROR, 'Já existe um paciente com esse E-mail')
            return redirect('/pacientes/')

        try:
            paciente = Pacientes(nome=nome,
                                 sexo=sexo,
                                 idade=idade,
                                 email=email,
                                 telefone=telefone,
                                 nutri=request.user)
            paciente.save()

            messages.add_message(request, messages.SUCCESS, 'Paciente registrado com sucesso!')
            return redirect('/pacientes/')
        
        except:
            messages.add_message(request, messages.ERROR, 'Erro interno do sistema! Por favor contate um administrador.')
            return redirect('/pacientes/')
        

@login_required(login_url='/auth/login/')
def dados_paciente_listar(request):
    if request.method == "GET":
        pacientes = Pacientes.objects.filter(nutri=request.user)
        return render(request, 'dados_paciente_listar.html', {'pacientes': pacientes})


@login_required(login_url='/auth/login/')
def dados_paciente(request, paciente_id):
    if request.method == 'GET':
        paciente = get_object_or_404(Pacientes, id=paciente_id)
        dados_paciente = DadosPaciente.objects.filter(paciente=paciente)

        if not paciente.nutri == request.user:
            messages.add_message(request, messages.ERROR, 'Esse paciente não é seu!')
            return redirect('/dados_paciente/')
        
        return render(request, 'dados_paciente.html', {'paciente': paciente,
                                                       'dados_paciente': dados_paciente})
        

@login_required(login_url='/auth/login/')
def valida_dados(request, paciente_id):
    if request.method == 'POST':
        paciente = get_object_or_404(Pacientes, id=paciente_id)
        peso = request.POST.get('peso')
        altura = request.POST.get('altura')
        gordura = request.POST.get('gordura')
        musculo = request.POST.get('musculo')

        hdl = request.POST.get('hdl')
        ldl = request.POST.get('ldl')
        colesterol_total = request.POST.get('ctotal')
        triglicerídios = request.POST.get('triglicerídios')

        if (len(peso.strip()) == 0) or (len(altura.strip()) == 0) or (len(gordura.strip()) == 0) or (len(musculo.strip()) == 0) or (len(hdl.strip()) == 0) or (len(ldl.strip()) == 0) or (len(colesterol_total.strip()) == 0) or (len(triglicerídios.strip()) == 0):
            messages.add_message(request, messages.ERROR, 'Preencha todos os campos')
            return redirect(f'/dados_paciente/{paciente_id}')
        
        if not peso.isnumeric() or not altura.isnumeric() or not gordura.isnumeric() or not musculo.isnumeric() or not hdl.isnumeric() or not ldl.isnumeric() or not colesterol_total.isnumeric() or not triglicerídios.isnumeric():
            messages.add_message(request, messages.ERROR, 'Os campos precisam ser números')
            return redirect(f'/dados_paciente/{paciente_id}')

        try:
            cadastrar_paciente = DadosPaciente(
                paciente=paciente,
                data=datetime.now(),
                peso=peso,
                altura=altura,
                percentual_gordura=gordura,
                percentual_musculo=musculo,
                colesterol_hdl=hdl,
                colesterol_ldl=ldl,
                colesterol_total=colesterol_total,
                trigliceridios=triglicerídios
            )
            cadastrar_paciente.save()

            messages.add_message(request, messages.SUCCESS, 'Dados do paciente cadastrados com sucesso!')
            return redirect(f'/dados_paciente/{paciente_id}')
        
        except:
            messages.add_message(request, messages.ERROR, 'Erro interno do sistema! Contate um administrador.')
            return redirect(f'/dados_paciente/{paciente_id}')


# API para o gráfico
@login_required(login_url='/auth/login/')
@csrf_exempt # isenta afunção de utilizar o csrf_token
def grafico_peso(request, paciente_id):
    paciente = get_object_or_404(Pacientes, id=paciente_id)
    dados_paciente = DadosPaciente.objects.filter(paciente=paciente).order_by("data")
    
    pesos = [dado.peso for dado in dados_paciente]
    labels = list(range(len(pesos)))
    data = {'peso': pesos,
            'labels': labels}
    
    return JsonResponse(data)


@login_required(login_url='/auth/login/')
def plano_alimentar_listar(request):
    if request.method == 'GET':
        pacientes = Pacientes.objects.filter(nutri=request.user)
        return render(request, 'plano_alimentar_listar.html', {'pacientes': pacientes})


@login_required(login_url='/auth/login/')
def plano_alimentar(request, paciente_id):
    if request.method == 'GET':
        paciente = get_object_or_404(Pacientes, id=paciente_id)
        refeicao = Refeicao.objects.filter(paciente=paciente).order_by('horario')
        opcao = Opcao.objects.all()

        if not paciente.nutri == request.user:
            messages.add_message(request, messages.ERROR, 'Esse paciente não é seu')
            return redirect('/plano_alimentar_listar/')

        return render(request, 'plano_alimentar.html', {'paciente': paciente,
                                                        'refeicao': refeicao,
                                                        'opcao': opcao})
    

@login_required(login_url='/auth/login/')
def refeicao(request, paciente_id):
    paciente = get_object_or_404(Pacientes, id=paciente_id)

    if not paciente.nutri == request.user:
        messages.add_message(request, messages.ERROR, 'Esse paciente não é seu')
        return redirect('/dados_paciente/')

    if request.method == 'POST':
        titulo = request.POST.get('titulo')
        horario = request.POST.get('horario')
        carboidratos = request.POST.get('carboidratos')
        proteinas = request.POST.get('proteinas')
        gorduras = request.POST.get('gorduras')

        try:
            refeicao = Refeicao(paciente=paciente,
                                titulo=titulo,
                                horario=horario,
                                carboidratos=carboidratos,
                                proteinas=proteinas,
                                gorduras=gorduras)
            refeicao.save()

            messages.add_message(request, messages.SUCCESS, 'Refeição cadastrada')
            return redirect(f'/plano_alimentar/{paciente_id}')
        
        except:
            messages.add_message(request, messages.ERROR, 'Erro interno do sistema! Contate um administrador.')
            return redirect(f'/plano_alimentar/{paciente_id}')


@login_required(login_url='/auth/login/')
def opcao(request, paciente_id):
    if request.method == 'POST':
        id_refeicao = request.POST.get('refeicao')
        imagem = request.FILES.get('imagem')
        descricao = request.POST.get("descricao")

        try:
            cadastrar_opcao = Opcao(refeicao_id=id_refeicao,
                                    imagem=imagem,
                                    descricao=descricao)
            cadastrar_opcao.save()

            messages.add_message(request, messages.SUCCESS, 'Opção cadastrada')
            return redirect(f'/plano_alimentar/{paciente_id}')

        except:
            messages.add_message(request, messages.ERROR, 'Erro interno do sistema! Contate um administrador')
            return redirect(f'/plano_alimentar/{paciente_id}')