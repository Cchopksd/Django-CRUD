from django.shortcuts import render, redirect
from django.http import JsonResponse
from .models import collection, users_collection
from datetime import datetime, timedelta
import jwt
from django.conf import settings
from rest_framework.decorators import api_view
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from functools import wraps


def index(request):
    return render(request, "index.html")


def generate_tokens(user_id):
    access_token = jwt.encode(
        {
            "user_id": str(user_id),
            "exp": datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRY),
        },
        settings.JWT_SECRET_KEY,
        algorithm="HS256",
    ).decode("utf-8")

    refresh_token = jwt.encode(
        {
            "user_id": str(user_id),
            "exp": datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRY),
        },
        settings.REFRESH_TOKEN_SECRET_KEY,
        algorithm="HS256",
    ).decode("utf-8")

    return access_token, refresh_token


@api_view(["GET", "POST"])
def login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = users_collection.find_one({"username": username})
        if user is None or user.get("password") != password:
            return JsonResponse({"error": "Invalid username or password"}, status=400)

        user_id = str(user["_id"])

        access_token, refresh_token = generate_tokens(user_id)
        response = redirect("/product-list")
        response.set_cookie("username", username)
        response.set_cookie("access_token", access_token)
        response.set_cookie("refresh_token", refresh_token)
        return response

    return render(request, "login.html")


def check_permission(view_func):
    @wraps(view_func)
    def wrapped_view(request, *args, **kwargs):
        auth_token = request.COOKIES.get("access_token")

        if not auth_token:
            return JsonResponse(
                {"error": "Authentication credentials were not provided."}, status=401
            )

        try:
            payload = jwt.decode(
                auth_token, settings.JWT_SECRET_KEY, algorithms=["HS256"]
            )
            request.user_id = payload["user_id"]
        except jwt.ExpiredSignatureError:
            if "text/html" in request.headers.get("Accept", ""):
                return redirect("/accounts/login")
            else:
                return JsonResponse({"error": "Token has expired"}, status=401)

        except (jwt.InvalidTokenError, KeyError):
            return JsonResponse({"error": "Invalid token"}, status=401)

        return view_func(request, *args, **kwargs)

    return wrapped_view


@api_view(["GET"])
@check_permission
def get_all_product(request):
    """
    Retrieve all products.
    """
    products = list(collection.find())

    if "text/html" in request.headers.get("Accept", ""):
        context = {"products": products}
        return render(request, "seed_list.html", context)
    else:
        return JsonResponse(products, safe=False)


@swagger_auto_schema(
    methods=["POST"],
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=[
            "seed_repDate",
            "seeds_yearWeek",
            "seed_varity",
            "seed_RDCSD",
            "seed_stock2Sale",
            "seed_season",
            "seed_crop_year",
        ],
        properties={
            "seed_repDate": openapi.Schema(type=openapi.TYPE_STRING, format="date"),
            "seeds_yearWeek": openapi.Schema(type=openapi.TYPE_INTEGER),
            "seed_varity": openapi.Schema(type=openapi.TYPE_STRING),
            "seed_RDCSD": openapi.Schema(type=openapi.TYPE_STRING),
            "seed_stock2Sale": openapi.Schema(type=openapi.TYPE_STRING),
            "seed_season": openapi.Schema(type=openapi.TYPE_INTEGER),
            "seed_crop_year": openapi.Schema(type=openapi.TYPE_STRING),
        },
    ),
    responses={200: "Success"},
)
@api_view(["GET", "POST"])
@check_permission
def insert_product(request):
    if request.method == "POST":
        data = request.data
        repDate = data.get("seed_repDate")
        print(data)
        date_obj = datetime.strptime(repDate, "%Y-%m-%d")
        thai_year = date_obj.year + 543
        thai_date_str = f"{thai_year:04d}{date_obj.month:02d}{date_obj.day:02d}"

        yearWeek = data.get("seeds_yearWeek")
        varity = data.get("seed_varity")
        RDCSD = data.get("seed_RDCSD")
        stock2Sale = data.get("seed_stock2Sale")
        season = data.get("seed_season")
        crop_year = data.get("seed_crop_year")

        last_document = collection.find_one(sort=[("_id", -1)])
        new_id = last_document["_id"] + 1
        document = {
            "_id": new_id,
            "Seed_RepDate": str(thai_date_str),
            "Seed_Year": int(thai_year),
            "Seeds_YearWeek": int(yearWeek),
            "Seed_Varity": varity,
            "Seed_RDCSD": RDCSD,
            "Seed_Stock2Sale": stock2Sale,
            "Seed_Season": int(season),
            "Seed_Crop_Year": crop_year,
        }

        collection.insert_one(document)
        return redirect("/product-list/")
    else:
        return render(request, "insert_product.html")


@swagger_auto_schema(
    methods=["PUT"],
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=[
            "seed_repDate",
            "seeds_yearWeek",
            "seed_varity",
            "seed_RDCSD",
            "seed_stock2Sale",
            "seed_season",
            "seed_crop_year",
        ],
        properties={
            "seed_repDate": openapi.Schema(type=openapi.TYPE_STRING, format="date"),
            "seeds_yearWeek": openapi.Schema(type=openapi.TYPE_INTEGER),
            "seed_varity": openapi.Schema(type=openapi.TYPE_STRING),
            "seed_RDCSD": openapi.Schema(type=openapi.TYPE_STRING),
            "seed_stock2Sale": openapi.Schema(type=openapi.TYPE_STRING),
            "seed_season": openapi.Schema(type=openapi.TYPE_INTEGER),
            "seed_crop_year": openapi.Schema(type=openapi.TYPE_STRING),
        },
    ),
    responses={200: "Success"},
)
@api_view(["GET", "PUT"])
@check_permission
def edit_product(request, product_id):
    if request.method == "PUT":
        data = request.data
        condition = int(product_id)
        seed_repDate = data.get("seed_repDate")
        yearWeek = data.get("seeds_yearWeek")
        varity = data.get("seed_varity")
        RDCSD = data.get("seed_RDCSD")
        stock2Sale = data.get("seed_stock2Sale")
        season = data.get("seed_season")
        crop_year = data.get("seed_crop_year")

        date_obj = datetime.strptime(seed_repDate, "%Y-%m-%d")
        thai_year = date_obj.year + 543
        thai_date_str = f"{thai_year:04d}{date_obj.month:02d}{date_obj.day:02d}"

        document = {
            "$set": {
                "Seed_RepDate": thai_date_str,
                "Seed_Year": int(thai_year),
                "Seeds_YearWeek": int(yearWeek),
                "Seed_Varity": varity,
                "Seed_RDCSD": RDCSD,
                "Seed_Stock2Sale": stock2Sale,
                "Seed_Season": int(season),
                "Seed_Crop_Year": crop_year,
            }
        }

        filter = {"_id": condition}

        collection.update_one(filter, document)

        if "text/html" in request.headers.get("Accept", ""):
            return redirect("/product-list/")
        else:
            return JsonResponse({"success"}, status=201)

    else:
        condition = int(product_id)
        payload = collection.find_one({"_id": condition})

        gregorian_year = int(payload["Seed_RepDate"][:4]) - 543
        thai_month_day = int(payload["Seed_RepDate"][4:])
        gregorian_date = datetime.strptime(
            f"{gregorian_year}{thai_month_day}", "%Y%m%d"
        )
        payload["gregorian_date"] = gregorian_date.strftime("%Y-%m-%d")
        return render(request, "edit_seed.html", payload)


@swagger_auto_schema(
    methods=["delete"], responses={204: "No Content", 404: "Not Found"}
)
@api_view(["DELETE"])
@check_permission
def delete_product(request, product_id):
    condition = int(product_id)
    collection.delete_one({"_id": condition})

    if "text/html" in request.headers.get("Accept", ""):
        return redirect("/")
    else:
        return JsonResponse("Delete Successful", status=200, safe=False)
