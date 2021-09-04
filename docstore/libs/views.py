from django.core.exceptions import ValidationError
from django.http.response import HttpResponse, HttpResponseNotAllowed, JsonResponse


class ViewMeta(type):
    def __call__(self, request, *args, **kwargs):
        instance = super().__call__()
        return instance(request, *args, **kwargs)
    
    @property
    def func_name(self):
        return self.__name__
class SimpleView(metaclass=ViewMeta):
    # Simpler version of Django's generic View.

    http_method_names = ['get', 'post', 'put', 'patch', 'delete', 'head', 'options', 'trace']

    def __init__(self):
        from logging import getLogger
        self.log = getLogger('%s.%s' % (self.__class__.__module__, self.__class__.__name__))

    def __call__(self, request, *args, **kwargs):
        if hasattr(self, 'get') and not hasattr(self, 'head'):
            self.head = self.get

        self.request = request
        self.args = args
        self.kwargs = kwargs

        if request.method.lower() in self.http_method_names:
            handler = getattr(self, request.method.lower(), self.http_method_not_allowed)
        else:
            handler = self.http_method_not_allowed
        return handler(request, *args, **kwargs)

    def _allowed_methods(self):
        return [m.upper() for m in self.http_method_names if hasattr(self, m)]

    def http_method_not_allowed(self, request, *args, **kwargs):
        return HttpResponseNotAllowed(self._allowed_methods())

    def options(self, request, *args, **kwargs):
        response = HttpResponse()
        response['Allow'] = ', '.join(self._allowed_methods())
        response['Content-Length'] = '0'
        return response


class ApiException(Exception):
    def __init__(self, errors):
        self.errors = errors


class ApiResponse(JsonResponse):
    def __init__(self, result=None, errors=None, status=None, **kwargs):
        if errors:
            if not isinstance(errors, (list, dict)):
                errors = [errors]
            
            if status is None:
                status = 400
        
        return super().__init__({
            'result': result,
            'errors': errors,
        }, status=status, **kwargs)


class ApiView(SimpleView):
    auth_required = True
    
    def __call__(self, request, *args, **kwargs):
        # Check for an authorization token.
        if 'HTTP_AUTHORIZATION' in request.META:
            from ..accounts.models import Token
            auth = request.META['HTTP_AUTHORIZATION']
            prefix = "Bearer "
            if not auth.startswith(prefix):
                # Sometime, other types of authorization could be acceptable, or even preferable.
                return ApiResponse(status=401, errors='Unauthorized')
            try:
                token = Token.objects.select_related('account').get(uuid=auth[len(prefix):])
            except (Token.DoesNotExist, ValidationError):
                return ApiResponse(status=401, errors='Unauthorized')
            request.account = token.account
            request.csrf_processing_done = True
        elif self.auth_required:
            return ApiResponse(status=401, errors='Unauthorized')
        else:
            request.account = None

        # Translate JSON data in the request body.
        if request.META.get('CONTENT_TYPE', '').startswith('application/json'):
            from decimal import Decimal
            from json import loads as json_decode
            try:
                data = json_decode(request.body.decode('utf-8'), parse_float=Decimal)
            except ValueError:
                return ApiResponse(status=400, errors='Invalid JSON request')
            else:
                request.POST = data

        # Hide internal server errors.
        from django.core.exceptions import PermissionDenied
        try:
            result = super().__call__(request, *args, **kwargs)
        except PermissionDenied as err:
            message = str(err) or 'Permission Denied'
            return ApiResponse(errors=[message], status=403)
        except ApiException as err:
            return ApiResponse(errors=err.errors, status=400)
        except Exception as err:
            self.log.exception('API exception:')
            from django.conf import settings
            if settings.DEBUG:
                message = str(err)
            else:
                message = 'Internal server error'
            return ApiResponse(errors=message, status=500)

        # Translate results into responses.
        if not isinstance(result, HttpResponse):
            result = ApiResponse(result, status=200)

        return result
