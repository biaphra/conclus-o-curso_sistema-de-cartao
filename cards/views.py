from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from .forms import CardForm, SignUpForm
from .models import Card
from .services import generate_card_data


@login_required
def request_card(request):
    if request.method == "POST":
        form = CardForm(request.POST)
        if form.is_valid():
            card_info = generate_card_data()

            card_request = form.save(commit=False)
            card_request.user = request.user
            card_request.name = card_info["name"]
            card_request.token = card_info["token"]
            card_request.last_four = card_info["last_four"]
            card_request.network = card_info["network"]
            card_request.expiration_date = card_info["expiration_date"]
            card_request.save()
            messages.success(request, "Solicitação enviada com sucesso. Acompanhe o status por aqui.")
            return redirect(reverse("cards:view_requests"))
    else:
        form = CardForm()
    return render(request, "cards/request_card.html", {"form": form})


@login_required
def view_requests(request):
    status = request.GET.get("status", "")
    requests = Card.objects.filter(user=request.user)
    if status in dict(Card.STATUS_CHOICES):
        requests = requests.filter(status=status)
    page = Paginator(requests, 6).get_page(request.GET.get("page"))
    return render(request, "cards/view_requests.html", {"user_requests": page, "status_filter": status, "statuses": Card.STATUS_CHOICES})


@login_required
def card_details(request, card_id):
    card = get_object_or_404(Card.objects.prefetch_related("history"), id=card_id, user=request.user)
    return render(request, "cards/card_details.html", {"card": card})


def signup(request):
    if request.user.is_authenticated:
        return redirect("home")
    form = SignUpForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        login(request, user)
        messages.success(request, "Conta criada com sucesso.")
        return redirect("home")
    return render(request, "registration/signup.html", {"form": form})


@require_GET
@login_required
def cards_api(request):
    cards = Card.objects.filter(user=request.user)
    return JsonResponse({"results": [{"id": card.id, "name": card.name, "last_four": card.last_four, "network": card.get_network_display(), "status": card.status, "status_label": card.get_status_display(), "created_at": card.created_at.isoformat()} for card in cards]})


@require_GET
def api_schema(request):
    return JsonResponse({"openapi": "3.0.3", "info": {"title": "DIO Bank API", "version": "1.0.0"}, "paths": {"/cards/api/": {"get": {"summary": "Lista os cartões do usuário autenticado", "responses": {"200": {"description": "Lista de cartões"}, "302": {"description": "Autenticação necessária"}}}}}})
