from django.apps import apps


class TestPageToursConfig:
    def test_the_app_is_installed_under_its_label(self):
        config = apps.get_app_config("page_tours")
        assert config.name == "page_tours"
