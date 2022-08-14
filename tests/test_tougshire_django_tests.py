from django.test import TestCase
from django.apps import apps
from django.contrib import admin

class TestGeneralModelParams(TestCase):
    def setUp(self):
        pass

    def test_check_models_registered(self):
        exempted_models=['Person_positions']
        # Make sure all models except those listed in excepted_models are registered
        app_label = __package__.replace('.tests','')
        for label, model in apps.all_models[app_label].items():
            if not model.__name__ in exempted_models:
                self.assertTrue(admin.site.is_registered(model),msg=model.__name__ + ' is not registered')

    def test_check_models_str(self):
        exempted_models=['Person_positions']
        # Make sure all models except those listed in excepted_models have __str__ defined
        app_label = __package__.replace('.tests','')
        for label, model in apps.all_models[app_label].items():
            if not model.__name__ in exempted_models:
                m = model()
                default_str_substring = type(m).__name__ + ' object ('
                self.assertFalse(m.__str__()[:len(default_str_substring)] == default_str_substring, msg="No __str__ defined for " + type(m).__name__)

    def test_check_models_ordering(self):
        exempted_models=[]
        # Make sure all models except those listed in excepted_models have __str__ defined
        app_label = __package__.replace('.tests','')
        for label, model in apps.all_models[app_label].items():
            if not model in exempted_models:
                m = model()
                self.assertTrue(hasattr(m._meta, "ordering"))



