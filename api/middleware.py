from django.conf import settings


class CORSMiddleware(object):
    """
       Middleware to provide temporary access to the API from another domain
       It may be removed in the future
    """
    CORS_ALLOWED_ORIGINS = settings.CLIENT_ORIGIN
    CORS_ALLOWED_METHODS = ['POST', 'GET', 'OPTIONS', 'PUT', 'DELETE', 'PATCH']
    CORS_ALLOWED_HEADERS = ['Content-Type', 'X-CSRFToken']
    # ['Origin', 'X-Requested-With', 'Set-Cookie', 'Content-Type', 'Accept']

    def process_request(self, request):

        if 'HTTP_ACCESS_CONTROL_REQUEST_METHOD' in request.META:
            response = http.HttpResponse()
            response['Access-Control-Allow-Origin'] = self.CORS_ALLOWED_ORIGINS
            response['Access-Control-Allow-Methods'] = ",".join(self.CORS_ALLOWED_METHODS)
            response['Access-Control-Allow-Headers'] = ",".join(self.CORS_ALLOWED_HEADERS)
            response['Access-Control-Allow-Credentials'] = 'true'
            # response['Access-Control

            return response

        return None

    def process_response(self, request, response):
        if response.has_header('Access-Control-Allow-Origin'):
            return response

        response['Access-Control-Allow-Origin'] = self.CORS_ALLOWED_ORIGINS
        response['Access-Control-Allow-Methods'] = ",".join(self.CORS_ALLOWED_METHODS)
        response['Access-Control-Allow-Headers'] = ",".join(self.CORS_ALLOWED_HEADERS)
        response['Access-Control-Allow-Credentials'] = 'true'
        return response

