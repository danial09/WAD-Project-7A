import sys

from random import randrange
from datetime import datetime
from dateutil.relativedelta import relativedelta

from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.utils import timezone

from sudokugame.forms import UserForm
from sudokugame.models import Game, Board

from sudokugame.sudoku_core import generate, flatten_join, difficulties, get_flattened_info


def home(request):
    return render(request, 'sudokugame/home.html')


def create_daily_challenge():
    board_check = Board.objects.filter(postedDate=timezone.now().date())
    if bool(board_check):
        return board_check[0]

    grid, solution = get_flattened_info(generate('M'))
    board = Board(grid=grid, solution=solution, postedDate=timezone.now().date())
    board.save()
    return board


def create_board(request):
    board_id = request.GET.get('id')
    if board_id is not None:
        return get_object_or_404(Board, pk=board_id)

    difficulty = request.GET.get('difficulty', 'M')
    # Sanity check to make sure difficulty passed does in fact exist.
    difficulty = difficulty if difficulty in difficulties else 'M'
    grid, solution = get_flattened_info(generate(difficulty))
    return Board.objects.get_or_create(grid=grid, solution=solution, difficulty=difficulty)[0]


def play(request):
    board = create_board(request)
    request.session['board'] = board.grid
    request.session['start_time'] = datetime.now().strftime("%H:%M:%S") 
    request.session['lives'] = 3
    request.session['hints'] = 3

    return render(request, 'sudokugame/play.html', context={'board': board})


# Create a registration view
def register(request):
    if request.method == 'POST':
        user_form = UserForm(request.POST)

        if user_form.is_valid():
            # Save the user's form data to the database
            user = user_form.save()

            # hash the password with the set_password method
            # then update the user object. 
            user.set_password(user.password)
            user.save()
            return redirect(reverse('sudokugame:login'))
        else:
            print(user_form.errors)
    else:
        # The request is not 'POST', we render our form. Its ready for user input. 
        user_form = UserForm()

    return render(request, 'sudokugame/register.html', context={'user_form': user_form})


def user_login(request):
    if request.user.is_authenticated:
        return redirect(reverse("sudokugame:home"))

    if request.method == 'POST':
        form = AuthenticationForm(request=request, data=request.POST)

        if form.is_valid():
            login(request, form.get_user())
            return redirect(reverse("sudokugame:home"))
        else:
            print(form.errors)
    else:
        form = AuthenticationForm()

    return render(request, 'sudokugame/login.html', context={'user_form': form})

@login_required
def user_logout(request):
    logout(request)
    return redirect(reverse('sudokugame:home'))

@login_required
def profile_page(request):
    current_user = request.user
    queryset = Game.objects.filter(user = current_user).order_by("-score")[:10]

    return render(request, "sudokugame/profile.html", {'games': queryset})

def leader_board(request):

    querysetE = Game.objects.filter(board__difficulty = "E").order_by("-score")[:10]
    querysetM = Game.objects.filter(board__difficulty = "M").order_by("-score")[:10]
    querysetH = Game.objects.filter(board__difficulty = "H").order_by("-score")[:10]
    querysetDCTemp = Game.objects.filter(board__postedDate__isnull = False)
    querysetDC = querysetDCTemp.order_by("board__postedDate").order_by("-score")[:10]

    context = {"Easygamelist": querysetE, "Mediumgamelist": querysetM, "Hardgamelist": querysetH, "Dailychallengelist": querysetDC}

    return render(request, "sudokugame/leaderboard.html", context)


def help_page(request):
    flattened_board = flatten_join(generate("M").board)
    board = Board(grid=flattened_board)
    return render(request, "sudokugame/help.html", context={"example_board": board})


def practice(request):
    return render(request, "sudokugame/practice.html")


def ajax_leaderboard(request):
    time = timezone.now()
    time_limit = request.GET.get("timeLimit", 'month')
    board_type = request.GET.get("boardType", 'M')
    if time_limit == 'day':
        time -= relativedelta(days=1)
    elif time_limit == 'week':
        time -= relativedelta(weeks=1)
    else:
        time -= relativedelta(months=1)

    queryset = Game.objects.filter(submissionDate__gt=time)

    if board_type != "DC":
        queryset = queryset.filter(board__difficulty=board_type)
    else:
        queryset = queryset.filter(board__postedDate__isnull=False)

    queryset = queryset.order_by("-score")[:10]

    data = [{'username': game.user.username, 'score': game.score} for game in queryset]

    response = JsonResponse(data, safe=False)
    return response
