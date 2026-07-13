from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAdminOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        print(
            f"DEBUG: Metoda {request.method}, Użytkownik {request.user}, IsStaff {request.user.is_staff}"
        )
        if request.method in SAFE_METHODS:
            return True
        return request.user and request.user.is_staff
