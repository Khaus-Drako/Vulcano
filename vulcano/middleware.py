"""Middleware for Vulcano platform"""

class TestModeMiddleware:
    """Middleware para agregar atributo test_mode a las peticiones en tests"""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        """Procesa la petición"""
        test_mode = getattr(request, 'test_mode', False)
        request.test_mode = test_mode
        response = self.get_response(request)
        if hasattr(response, 'test_mode'):
            request.test_mode = response.test_mode
        return response