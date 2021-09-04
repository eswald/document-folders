from ..libs.views import ApiResponse, ApiView

from .forms import DocumentCreationForm
from .serializers import serialize_document


class DocumentList(ApiView):
    def post(self, request):
        form = DocumentCreationForm(request.POST)
        if not form.is_valid():
            return ApiResponse(
                status = 400,
                message = 'Invalid data',
                errors = form.errors,
            )
        
        document = form.save(account=request.account)
        return {
            'document': serialize_document(document),
        }
