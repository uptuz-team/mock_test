from django.apps import AppConfig


class MockWritingConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'mock_writing'
