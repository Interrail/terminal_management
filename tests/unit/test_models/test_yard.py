import pytest

from apps.locations.models import Yard


class TestYard:
    @pytest.mark.django_db
    def test_yard_name(self):
        yard = Yard.objects.create(
            name="Test Yard", max_rows=5, max_columns=10, max_tiers=3
        )
        assert yard.name == "Test Yard"
