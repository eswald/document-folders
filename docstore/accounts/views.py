from ..libs.views import ApiResponse, ApiView

from .forms import AccountRegistrationForm
from .models import Token
from .serializers import serialize_account, serialize_token


class AccountList(ApiView):
    auth_required = False
    
    def post(self, request):
        form = AccountRegistrationForm(request.POST)
        if not form.is_valid():
            return ApiResponse(
                status = 400,
                message = 'Invalid data',
                errors = form.errors,
            )
        
        account = form.save()
        token = Token.objects.create(account=account)
        return {
            'account': serialize_account(account),
            'token': serialize_token(token),
        }
