from epilepsy12.models import Epilepsy12User


# Middleware to capture user information in request
class CurrentUserMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            Epilepsy12User.created_by = request.user
            Epilepsy12User.updated_by = request.user
        response = self.get_response(request)
        return response
