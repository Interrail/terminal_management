import factory
from django.utils.text import slugify
from factory.django import DjangoModelFactory

from .models import Company


class CompanyFactory(DjangoModelFactory):
    class Meta:
        model = Company

    name = factory.Faker("company")
    address = factory.Faker("address")
    slug = factory.LazyAttribute(lambda obj: slugify(obj.name))

    @factory.post_generation
    def ensure_unique_name(self, create, extracted, **kwargs):
        while Company.objects.filter(name=self.name).exclude(id=self.id).exists():
            self.name = factory.Faker("company").generate({})
            self.slug = slugify(self.name)
            if create:
                self.save()
