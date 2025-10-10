"""Utilities for testing"""

from django.test import Client


class TestClient(Client):
    """Cliente personalizado para tests que agrega test_mode a las peticiones"""
    
    def get(self, *args, **kwargs):
        """Sobreescribe get para agregar test_mode"""
        response = super().get(*args, **kwargs)
        response.test_mode = True
        return response
    
    def post(self, *args, **kwargs):
        """Sobreescribe post para agregar test_mode"""
        response = super().post(*args, **kwargs)
        response.test_mode = True
        return response