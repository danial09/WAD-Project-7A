import sys
from random import randrange

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse

from sudoku import Sudoku

from sudokugame.forms import UserForm
from sudokugame.models import Game, Board

from sudokugame.sudoku_core import generate, flatten_join


def test(request):
    puzzle = Sudoku(3, 3, seed=randrange(sys.maxsize)).difficulty(0.7)
    flattened = [str(cell) if cell is not None else '0' for row in puzzle.board for cell in row]

    return render(request, 'sudokugame/test.html', context={'board': flattened})

def home(request):
    return render(request, 'sudokugame/home.html')


def play(request):
    #TODO: Add the ability to create boards of varying difficulties
    #TODO: Change this so that it can access existing boards as well as create new ones
    flattened_grid = flatten_join(generate('M').board)

    board_filter = Board.objects.filter(grid=flattened_grid)

    if board_filter.exists():
        board = board_filter[0]
    else:
        board = Board()
        board.grid = flattened_grid
        board.difficulty = "M"
        board.save()

    return render(request, 'sudokugame/play.html', context={'board': board})



# Create a registration view
def register(request):
    registered = False

    if request.method == 'POST':
        user_form = UserForm(request.POST)

        if user_form.is_valid():
            # Save the user's form data to the database
            user = user_form.save()

            # hash the password with the set_password method
            # then update the user object. 
            user.set_password(user.password)
            user.save()
            registered =True
        else:
            print(user_form.errors)
    else:
        # The request is not 'POST', we render our form. Its ready for user input. 
        user_form = UserForm()

    return render(request, 'sudokugame/register.html', context={'user_form': user_form, 'registered': registered})


def user_login(request):
    if request.method == 'POST':
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(username=username, password=password)

        if user:
            if user.is_active:
                login(request, user)
                # Redirects to the Home page
                return redirect(reverse("sudokugame:home"))
            else:
                return HttpResponse("Your account is disabled")
        else:
            print(f"Invalid login details: {username}, {password}")
            return HttpResponse("Invalid login details supplied")

    else:
        return render(request, "sudokugame/login.html")

@login_required
def user_logout(request):
    logout(request)
    return redirect(reverse('sudokugame:home'))

@login_required
def profile_page(request):

    current_user = request.user
    queryset = Game.objects.filter(user = current_user).order_by("-score")[:10]

    context = {"users_games": queryset, "user": current_user}

    return render(request, "sudokugame/profile.html", context)

def leader_board(request):

    querysetE = Game.objects.filter(board__difficulty = "E").order_by("-score")[:10]
    querysetM = Game.objects.filter(board__difficulty = "M").order_by("-score")[:10]
    querysetH = Game.objects.filter(board__difficulty = "H").order_by("-score")[:10]
    querysetDCTemp = Game.objects.filter(board__postedDate__isnull = False)
    querysetDC = querysetDCTemp.order_by("board__postedDate").order_by("-score")[:10]

    context = {"Easygamelist": querysetE, "Mediumgamelist": querysetM, "Hardgamelist": querysetH, "Dailychallengelist": querysetDC}

    return render(request, "sudokugame/leaderboard.html", context)



