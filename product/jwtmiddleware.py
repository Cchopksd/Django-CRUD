from django.conf import settings
from django.http import JsonResponse
import jwt


class JWTMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Exclude paths that don't require authentication
        excluded_paths = [
            "/accounts/login",
            "",
        ]  # Add paths that don't require authentication
        if request.path in excluded_paths:
            return self.get_response(request)

        # Get the token from the request headers
        token = request.headers.get("Authorization", "").split("Bearer ")[-1]

        if not token:
            return JsonResponse({"error": "Authorization header missing"}, status=401)

        try:
            # Decode the token using the secret key
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])

            # You can perform additional validation here, like checking if the user exists in the database

            # Attach the payload to the request for later use
            request.user = payload["user"]
        except jwt.ExpiredSignatureError:
            return JsonResponse({"error": "Token has expired"}, status=401)
        except jwt.InvalidTokenError:
            return JsonResponse({"error": "Invalid token"}, status=401)

        return self.get_response(request)
