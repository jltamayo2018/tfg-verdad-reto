from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from .models import Pack
from .forms import PackForm, ActionForm
from .models import Action, Pack
from django.http import Http404, HttpResponseForbidden
import random
import qrcode
import io
from django.urls import reverse
from django.views.decorators.http import require_POST
from django.contrib import messages

def home(request):
    return render(request, 'home.html')

def registro(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')  # a /accounts/login/
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {"form": form})

@login_required
def dashboard(request):
    # Solo los packs del usuario actual
    packs = (Pack.objects
                  .filter(owner=request.user)
                  .order_by('-creation_date'))
    return render(request, 'dashboard.html', {'packs': packs})

@login_required
def pack_create(request):
    if request.method == "POST":
        form = PackForm(request.POST)
        if form.is_valid():
            pack = form.save(commit=False)
            pack.owner = request.user  # asignar el usuario actual como owner
            pack.save() # genera también los tokens
            messages.success(request, "Pack creado correctamente.")
            return redirect('pack_detail', pk=pack.pk)
    else:
        form = PackForm()
    
    return render(request, 'pack_form.html', {
    'form': form,
    'page_title': 'Crear pack',
    'submit_label': 'Guardar',
    'cancel_url': reverse('dashboard'),
    })

@login_required
def pack_rename(request, pk):
    pack = get_object_or_404(Pack, pk=pk, owner=request.user)
    if request.method == 'POST':
        form = PackForm(request.POST, instance=pack)
        if form.is_valid():
            form.save()
            messages.success(request, "Nombre del pack actualizado.")
            return redirect('pack_detail', pk=pack.pk)
    else:
        form = PackForm(instance=pack)

    # podemos reutilizar tu pack_form.html cambiando el título
    return render(request, 'pack_form.html', {
    'form': form,
    'pack': pack,
    'page_title': 'Editar pack',
    'submit_label': 'Guardar',
    'cancel_url': reverse('dashboard'),
    })

@login_required
def pack_delete(request, pk):
    pack = get_object_or_404(Pack, pk=pk, owner=request.user)
    if request.method == 'POST':
        nombre = pack.name
        pack.delete()
        messages.success(request, f'Pack "{nombre}" eliminado.')
        return redirect('dashboard')
    
    return render(request, 'pack_confirm_delete.html', {'pack': pack})

@login_required
def pack_detail(request, pk):
    pack = get_object_or_404(Pack, pk=pk, owner=request.user)
    verdades = Action.objects.filter(pack=pack, type=Action.Type.VERDAD).order_by('-created_at')
    retos = Action.objects.filter(pack=pack, type=Action.Type.RETO).order_by('-created_at')
    return render(request, 'pack_detail.html', {
        'pack': pack,
        'verdades': verdades,
        'retos': retos,
    })

@login_required
def action_create(request, pk, tipo):
    pack = get_object_or_404(Pack, pk=pk, owner=request.user)
    # Normalizamos el tipo
    tipo = tipo.upper()
    if tipo not in (Action.Type.VERDAD, Action.Type.RETO):
        raise Http404("Tipo inválido")

    if request.method == 'POST':
        form = ActionForm(request.POST)
        if form.is_valid():
            accion = form.save(commit=False)
            accion.pack = pack
            # Forzamos el tipo al de la URL para evitar manipulación del form
            accion.type = tipo
            accion.save()
            messages.success(request, f"{'Verdad' if tipo == Action.Type.VERDAD else 'Reto'} creada correctamente.")
            return redirect('pack_detail', pk=pack.pk)
    else:
        form = ActionForm(initial={'type': tipo})

    return render(request, 'action_form.html', {
    'form': form,
    'pack': pack,
    'modo': 'nueva',
    'tipo_legible': 'Verdad' if tipo == Action.Type.VERDAD else 'Reto',
    'page_title': f"Nuev{'a Verdad' if tipo == Action.Type.VERDAD else 'o Reto'}",
    'submit_label': 'Guardar',
    })

@login_required
def action_edit(request, pk, accion_id):
    pack = get_object_or_404(Pack, pk=pk, owner=request.user)
    accion = get_object_or_404(Action, pk=accion_id, pack=pack)

    if request.method == 'POST':
        form = ActionForm(request.POST, instance=accion)
        if form.is_valid():
            # bloqueamos que cambien el tipo desde el form, mantiene el actual
            obj = form.save(commit=False)
            obj.type = accion.type
            obj.save()
            messages.success(request, "Acción actualizada.")
            return redirect('pack_detail', pk=pack.pk)
    else:
        form = ActionForm(instance=accion)

    return render(request, 'action_form.html', {
    'form': form,
    'pack': pack,
    'modo': 'editar',
    'tipo_legible': 'Verdad' if accion.type == Action.Type.VERDAD else 'Reto',
    'page_title': f"Editar {'Verdad' if accion.type == Action.Type.VERDAD else 'Reto'}",
    'submit_label': 'Guardar',
    })

@login_required
def action_toggle(request, pk, accion_id):
    if request.method != 'POST':
        return HttpResponseForbidden("Método no permitido")
    pack = get_object_or_404(Pack, pk=pk, owner=request.user)
    accion = get_object_or_404(Action, pk=accion_id, pack=pack)
    accion.active = not accion.active
    accion.save()
    messages.info(request, f"Acción {'activada' if accion.active else 'desactivada'}.")
    return redirect('pack_detail', pk=pack.pk)

@login_required
def action_delete(request, pk, accion_id):
    pack = get_object_or_404(Pack, pk=pk, owner=request.user)
    accion = get_object_or_404(Action, pk=accion_id, pack=pack)

    if request.method == 'POST':
        accion.delete()
        messages.success(request, "Acción borrada.")
        return redirect('pack_detail', pk=pack.pk)

    return render(request, 'action_confirm_delete.html', {
        'pack': pack,
        'accion': accion,
    })

def publico_por_token(request, token):
    # 1) Buscar el pack por el token único
    pack = get_object_or_404(Pack, token=token)
    
    # 2) Determinar el tipo según el parámetro GET (?t=verdad o ?t=reto)
    tipo_param = (request.GET.get('t') or '').lower()
    if tipo_param == 'reto':
        tipo = Action.Type.RETO
    else:
        # por defecto mostramos 'Verdad'
        tipo = Action.Type.VERDAD

    # 3) Elegir una acción aleatoria activa del tipo correspondiente
    acciones = list(Action.objects.filter(pack=pack, type=tipo, active=True))
    accion = random.choice(acciones) if acciones else None

    # 4) Renderizar la plantilla pública
    return render(request, 'publico.html', {
        'pack': pack,
        'tipo': 'Verdad' if tipo == Action.Type.VERDAD else 'Reto',
        'accion': accion,
        'token': pack.token,  # usamos siempre el nuevo token unificado
    })

# Opción copilot, muestra el QR en el navegador y lo tienes que guardar tú manualmente
'''
@login_required
def qr_image(request, pk, kind):
    pack = get_object_or_404(Pack, pk=pk, owner=request.user)
    kind = kind.lower()
    if kind == 'verdad':
        token = pack.token_verdad
    elif kind == 'reto':
        token = pack.token_reto
    else:
        raise Http404("Tipo de QR inválido")

    url = request.build_absolute_uri(f'/q/{token}/')

    # Generar el código QR
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")

    # Guardar la imagen en un buffer en memoria
    buffer = BytesIO()
    img.save(buffer)
    buffer.seek(0)

    return HttpResponse(buffer.getvalue(), content_type="image/png")
'''

@login_required
def qr_image(request, pk):
    # pack debe pertenecer al usuario logueado
    pack = get_object_or_404(Pack, pk=pk, owner=request.user)

    # URL pública con el token único
    public_url = request.build_absolute_uri(reverse('publico_por_token', args=[pack.token]))

    # Generar QR en memoria con control de parámetros
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=8,
        border=4,
    )
    qr.add_data(public_url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")

    # Guardar en buffer en memoria
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    buf.seek(0)

    # Devolver PNG como descarga (Content-Disposition sugiere nombre de archivo)
    resp = HttpResponse(buf.getvalue(), content_type='image/png')
    resp['Content-Disposition'] = f'attachment; filename="qr_pack{pack.pk}.png"'
    return resp

@require_POST
@login_required
def link_regenerate(request, pk):

    pack = get_object_or_404(Pack, pk=pk, owner=request.user)
    pack.regenerate_unified()  # invalida el anterior y crea un token nuevo
    messages.success(request, "Enlace del pack regenerado.")
    return redirect('pack_detail', pk=pack.pk)

def handler400(request, exception):
    return render(request, 'errors/400.html', status=400)

def handler403(request, exception):
    return render(request, 'errors/403.html', status=403)

def handler404(request, exception):
    return render(request, 'errors/404.html', status=404)

def handler500(request):
    return render(request, 'errors/500.html', status=500)