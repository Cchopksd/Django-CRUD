from django.http import JsonResponse
from functools import wraps
import jwt
from .models import users_collection
from django.conf import settings

def jwt_token_required(func):
    @wraps(func)
    def wrapper(request, *args, **kwargs):
        token = request.COOKIES.get("access_token")

        if not token:
            return JsonResponse({"error": "JWT token is missing"}, status=401)

        try:
            payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=["HS256"])
            user_id = payload["user_id"]

            user = users_collection.find_one({"_id": user_id})

            if not user:
                return JsonResponse({"error": "User not found"}, status=404)

            if user.get("role") == "admin":
                return func(request, *args, **kwargs)
            else:
                return JsonResponse({"error": "Unauthorized"}, status=403)

        except jwt.ExpiredSignatureError:
            return JsonResponse({"error": "JWT token has expired"}, status=401)

        except jwt.InvalidTokenError:
            return JsonResponse({"error": "Invalid JWT token"}, status=401)

    return wrapper
