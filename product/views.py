from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from .models import collection
from django.views.decorators.csrf import requires_csrf_token
from datetime import datetime
from bson import ObjectId


# Create your views here.
# @requires_csrf_token
def index(request):
    return render(request, "index.html")


def get_all_product(request):
    products = collection.find()
    context = {"products": products}
    return render(request, "seed_list.html", context)


def insert_product(request):
    if request.method == "POST":

        data = request.POST.get("seed_repDate")
        date_obj = datetime.strptime(data, "%Y-%m-%d")
        thai_year = date_obj.year + 543
        thai_date_str = f"{thai_year:04d}{date_obj.month:02d}{date_obj.day:02d}"

        yearWeek = request.POST.get("seeds_yearWeek")
        varity = request.POST.get("seed_varity")
        RDCSD = request.POST.get("seed_RDCSD")
        stock2Sale = request.POST.get("seed_stock2Sale")
        season = request.POST.get("seed_season")
        crop_year = request.POST.get("seed_crop_year")

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

        # print(document)
        collection.insert_one(document)
        return redirect("/")
    return render(request, "insert_product.html")


def edit_product(request, product_id):
    if request.method == "POST":
        condition = int(product_id)
        data = request.POST.get("seed_repDate")
        date_obj = datetime.strptime(data, "%Y-%m-%d")
        thai_year = date_obj.year + 543
        thai_date_str = f"{thai_year:04d}{date_obj.month:02d}{date_obj.day:02d}"

        yearWeek = request.POST.get("seeds_yearWeek")
        varity = request.POST.get("seed_varity")
        RDCSD = request.POST.get("seed_RDCSD")
        stock2Sale = request.POST.get("seed_stock2Sale")
        season = request.POST.get("seed_season")
        crop_year = request.POST.get("seed_crop_year")

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

        return redirect("/")

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


def delete_product(request, product_id):
    condition = int(product_id)
    collection.delete_one({"_id": condition})
    return redirect("/")
