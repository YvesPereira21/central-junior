from rest_framework.permissions import BasePermission


class IsCustomerUser(BasePermission):
    message = "Apenas usuários podem fazer essa ação"

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        return request.user.groups.filter(name='Customer profile')

class IsOwner(BasePermission):
    message = "Você não tem permissão para isso"

    def has_object_permission(self, request, view, obj):
        if hasattr(obj, 'profile'):
            return obj.profile.user == request.user

        if hasattr(obj, 'user'):
            return obj.user == request.user

        if hasattr(obj, 'author'):
            return obj.author.user == request.user

class IsOwnerQuestion(BasePermission):
    message = "Apenas o dono da pergunta pode realizar essa ação"

    def has_object_permission(self, request, view, obj):
        if not hasattr(obj, 'question') or not obj.question:
            return False

        if not hasattr(obj.question, 'profile') or not obj.question.profile:
            return False

        return obj.question.profile.user == request.user
