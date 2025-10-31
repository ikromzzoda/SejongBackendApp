from django.http import JsonResponse
from .models import Book
from rest_framework.authtoken.models import Token


def check_token(request):
    auth_token = request.headers.get("token")
    if not auth_token:
        return JsonResponse({"error": "Token not provided"}, status=401)

    try:
        token = Token.objects.get(key=auth_token)
        user = token.user
    except Token.DoesNotExist:
        return JsonResponse({"error": "Invalid token"}, status=401)

    return user

def get_all_books(request):
    if request.method == "GET":
        user = check_token(request)
        if isinstance(user, JsonResponse):
            return user  # Возвращаем ошибку, если токен неверный
        
        books = Book.objects.all()
        data = []
        
        for book in books:
            data.append({
                'title': book.title,
                'author': book.author,
                'description': book.description,
                'cover': book.cover_id,
                'file': book.file_id,
                'genres': book.genres,
                'published_date': book.published_date,
                'created_at': book.created_at,
            })
        return JsonResponse(data, safe=False)




