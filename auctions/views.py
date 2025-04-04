from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.core.exceptions import ObjectDoesNotExist

from .models import *


def index(request):
    try:
        # Get list pokemon
        list_pokemons = Listing.objects.all()

        listings = []

        for pokemon in list_pokemons:
            categories = []
            for category in pokemon.category.all():
                categories.append(category)
            listing = {
                'id': pokemon.id,
                'title': pokemon.title,
                'price': "0" if pokemon.price is None else pokemon.price,
                'imageUrl':pokemon.imageUrl,
                'categories': categories,
                'watchlist': pokemon.watchlist.all(),
                'isActive': pokemon.isActive,
                'owner': pokemon.owner,
            }
            
            listings.append(listing)
    except Listing.DoesNotExist:
        HttpResponse("Objects do not exist")        
    except Listing.FieldError:
        HttpResponse("Field error in query")
    
    return render(request, "auctions/index.html", {
        "listings": listings,
    })


def login_view(request):
    if request.method == "POST":
        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(
                request,
                "auctions/login.html",
                {"message": "Invalid username and/or password."},
            )
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(
                request, "auctions/register.html", {"message": "Passwords must match."}
            )

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(
                request,
                "auctions/register.html",
                {"message": "Username already taken."},
            )
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")

# add_listing function
def add_listing(owner, title, imageUrl, description, categories, bid):
    try:
        price = Bid.objects.create(bid=bid, user=owner)
        listing = Listing.objects.create(
            title=title,
            description=description,
            imageUrl=imageUrl,
            owner=owner,
            price=price,
        )
        
        for id in categories:
            category = Category.objects.get(id=id)
            listing.category.add(category)
        
        listing.save()
        return 0
    
    except ObjectDoesNotExist as e:
        return HttpResponse(f"Object does not exist: {e}")


#@login_required
def create_listing(request):
    if request.method == "POST":
        try:
            title = request.POST["title"]
            imageUrl = request.POST["imageUrl"]
            description = request.POST["description"]
            categories = request.POST.getlist("category")
            bid = request.POST["bid"]
            owner = request.user

            add_listing(owner, title, imageUrl, description, categories, bid)


        except KeyError as e:
            missing_field = e.args[0]
            return HttpResponse(f"Missing field: {missing_field}")    
        except Exception as e:
            return HttpResponse(f"An error occurred: {e}")
        
        return HttpResponse("Form submitted")

    else:   
        cat = Category.objects.all()
        
        return render(request, "auctions/create.html", {
            "categories": cat,
        })

def detail_view(request, id):
    try:
        # get pokemon object follow id
        pokemon = Listing.objects.get(id=id)        
        
        categories = []
        for category in pokemon.category.all():
            categories.append(category)
        
        poke = {
            'id': pokemon.id,
            'title': pokemon.title,
            'price': "0" if pokemon.price is None else pokemon.price,
            'description': pokemon.description,
            'imageUrl':pokemon.imageUrl,
            'categories': categories,
        }
        

        return render(request, "auctions/details.html", {
            'poke':poke,
        })
    except ObjectDoesNotExist:
        return HttpResponse("Object does not exist")

def add_watchlist(request, id):
    try:
        # get pokemon object follow id
        pokemon = Listing.objects.get(id=id)

        user = request.user

        if pokemon.isActive:
            if user in pokemon.watchlist.all():
                pokemon.watchlist.remove(user)
                return JsonResponse({"message": "Removed Watchlist"})
            else:
                pokemon.watchlist.add(user)
                pokemon.save()  
        else:
            return JsonResponse({"message": "Not Active"})
        
        return JsonResponse({"message": "Added Watchlist"})
    except ObjectDoesNotExist:
        return HttpResponse("Object does not exist")

# get watchlist of user 
def get_watchlist(request):
    try:
        user = request.user
        
        # get all listings
        pokemons = Listing.objects.all()

        watchlist_of_user = []

        for pokemon in pokemons: 
            if user in pokemon.watchlist.all() and pokemon.isActive:
                categories = []
                for category in pokemon.category.all():
                    categories.append(category)
                
                watchlist_of_user.append({
                    'id': pokemon.id,
                    'title': pokemon.title,
                    'price': "0" if pokemon.price is None else pokemon.price,
                    'imageUrl':pokemon.imageUrl,
                    'categories': categories,
                    'watchlist': pokemon.watchlist.all(),
                    'isActive': pokemon.isActive,
                    'owner': pokemon.owner,
                })

        return render(request, "auctions/viewWatchlist.html", {
            "watchlists": watchlist_of_user,
        })
    except ObjectDoesNotExist:
        return HttpResponse("Object does not exist")
    except Listing.FieldError:
        return HttpResponse("Field error in query")
    except Exception as e:
        return HttpResponse(f"An error occurred: {e}")