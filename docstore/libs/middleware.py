class ErrorLoggingMiddleware(object):
    def __init__(self, get_response):
        from logging import getLogger
        self.log = getLogger('docstore')
        self.get_response = get_response
    
    def __call__(self, request):
        try:
            return self.get_response(request)
        except Exception:
            url = request.build_absolute_uri()
            self.log.exception('Error handling %s to %s:', request.method, url)
            raise
    
    def process_exception(self, request, exception):
        from django.core.exceptions import PermissionDenied
        if not isinstance(exception, PermissionDenied):
            url = request.build_absolute_uri()
            self.log.exception('Error handling %s to %s:', request.method, url)


class SecurityPolicyMiddleware(object):
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        response = self.get_response(request)
        response['Referrer-Policy'] = 'never'
        response['Content-Security-Policy'] = '; '.join([
            "referrer no-referrer",
            "script-src 'self'",
        ])
        return response
