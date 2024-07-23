import factory
from django.utils import timezone
from factory.django import DjangoModelFactory
from faker import Faker

from apps.customers.factories import CompanyFactory
from .models import Container, ContainerTerminalVisit, ContainerImage, ContainerDocument

fake = Faker()


class ContainerFactory(DjangoModelFactory):
    class Meta:
        model = Container

    type = factory.Iterator(Container.ContainerType.values)
    name = factory.Sequence(lambda n: f"CONT{n:08}")


class ContainerTerminalVisitFactory(DjangoModelFactory):
    class Meta:
        model = ContainerTerminalVisit

    container = factory.SubFactory(ContainerFactory)
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
