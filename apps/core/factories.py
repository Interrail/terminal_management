import factory
from django.utils import timezone
from django.utils.text import slugify
from factory.django import DjangoModelFactory
from faker import Faker

from apps.containers.models import (
    Container,
    ContainerStorage,
    ContainerImage,
    ContainerDocument,
)
from apps.customers.models import Company
from apps.locations.models import Yard, ContainerLocation

fake = Faker()


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


class YardFactory(DjangoModelFactory):
    class Meta:
        model = Yard

    container_type = factory.Iterator(Container.ContainerType.values)
    name = factory.Sequence(lambda n: f"Yard-{n}")
    max_rows = factory.LazyFunction(lambda: fake.random_int(min=10, max=15))
    max_columns = factory.LazyFunction(lambda: fake.random_int(min=10, max=15))
    max_tiers = factory.LazyFunction(lambda: fake.random_int(min=2, max=3))


class ContainerFactory(DjangoModelFactory):
    class Meta:
        model = Container

    type = factory.Iterator(Container.ContainerType.values)
    name = factory.Sequence(lambda n: f"CONT{n:07}")


class ContainerLocationFactory(DjangoModelFactory):
    class Meta:
        model = ContainerLocation

    container = factory.SubFactory(ContainerFactory)
    yard = factory.SubFactory(YardFactory)
    row = factory.LazyAttribute(lambda o: fake.random_int(min=1, max=o.yard.max_rows))
    column_start = factory.LazyAttribute(
        lambda o: fake.random_int(min=1, max=o.yard.max_columns)
    )
    column_end = factory.LazyAttribute(
        lambda o: fake.random_int(min=1, max=o.yard.max_columns)
    )
    tier = factory.LazyAttribute(lambda o: fake.random_int(min=1, max=o.yard.max_tiers))

    @factory.post_generation
    def ensure_unique_location(self, create, extracted, **kwargs):
        while (
            ContainerLocation.objects.filter(
                yard=self.yard,
                row=self.row,
                column_start=self.column_start,
                column_end=self.column_end,
                tier=self.tier,
            )
            .exclude(id=self.id)
            .exists()
        ):
            self.row = fake.random_int(min=1, max=self.yard.max_rows)
            self.column_start = fake.random_int(min=1, max=self.yard.max_columns)
            self.column_end = fake.random_int(min=1, max=self.yard.max_columns)
            self.tier = fake.random_int(min=1, max=self.yard.max_tiers)
            if create:
                self.save()


class ContainerTerminalVisitFactory(DjangoModelFactory):
    class Meta:
        model = ContainerStorage

    container_location = factory.SubFactory(ContainerLocationFactory)
    customer = factory.SubFactory(CompanyFactory)
    entry_time = factory.LazyFunction(timezone.now)
    exit_time = factory.LazyAttribute(
        lambda o: o.entry_time + timezone.timedelta(days=fake.random_int(min=1, max=30))
        if fake.boolean()
        else None
    )
    storage_days = factory.LazyAttribute(
        lambda o: (o.exit_time - o.entry_time).days if o.exit_time else 0
    )
    notes = factory.Faker("paragraph")
    is_empty = factory.Faker("boolean")


class ContainerImageFactory(DjangoModelFactory):
    class Meta:
        model = ContainerImage

    container = factory.SubFactory(ContainerTerminalVisitFactory)
    image = factory.django.ImageField(filename="container.jpg")
    name = factory.Faker("word")


class ContainerDocumentFactory(DjangoModelFactory):
    class Meta:
        model = ContainerDocument

    container = factory.SubFactory(ContainerTerminalVisitFactory)
    document = factory.django.FileField(filename="document.pdf")
    name = factory.Faker("word")
