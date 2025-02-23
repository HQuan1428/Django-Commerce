from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.core.exceptions import ObjectDoesNotExist

from .models import *


def index(request):
    # Get list pokemon
    list_pokemons = Listing.objects.all()

    listings = []

    for pokemon in list_pokemons:
        if not pokemon.isActive:
            continue 
        categories = []
        for category in pokemon.category.all():
            categories.append(category)
        listing = {
            'id': pokemon.id,
            'title': pokemon.title,
            'imageUrl':pokemon.imageUrl,
            'categories': categories,
        }
        
        listings.append(listing)
        
    
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