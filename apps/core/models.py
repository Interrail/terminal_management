from django.core.validators import MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.db.models.signals import post_save
from django.dispatch import receiver
from apps.core.choices import ContainerSize, ContainerState, MeasurementUnit


class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Container(models.Model):
    name = models.CharField(
        max_length=12, unique=True, db_index=True, verbose_name=_("Container Name")
    )
    size = models.CharField(
        max_length=4, choices=ContainerSize.choices, verbose_name=_("Container Type")
    )

    class Meta:
        db_table = "container"
        verbose_name = _("Container")
        verbose_name_plural = _("Containers")

    def __str__(self):
        return f"{self.name} ({self.get_size_display()})"

    @property
    def in_storage(self):
        return self.storages.filter(exit_time__isnull=True).exists()

    @property
    def teu(self):
        size = self.size
        if size == ContainerSize.TWENTY:
            return 1
        else:
            return 2


class TerminalServiceType(BaseModel):
    name = models.TextField(unique=True)
    unit_of_measure = models.CharField(max_length=50, choices=MeasurementUnit.choices)

    class Meta:
        db_table = "terminal_service_type"
        verbose_name = "Terminal Service Type"
        verbose_name_plural = "Terminal Service Types"

    def __str__(self):
        return self.name


class TerminalService(BaseModel):
    name = models.TextField()
    service_type = models.ForeignKey(
        TerminalServiceType,
        on_delete=models.PROTECT,
        related_name="services",
        null=True,
    )
    container_size = models.CharField(
        max_length=50, choices=ContainerSize.choices, default="ANY"
    )
    container_state = models.CharField(
        max_length=6, choices=ContainerState.choices, default="ANY"
    )
    base_price = models.DecimalField(
        max_digits=12, decimal_places=2, validators=[MinValueValidator(0)]
    )
    description = models.TextField(blank=True)
    multiple_usage = models.BooleanField(default=False)

    class Meta:
        unique_together = ["name", "container_size", "container_state"]
        verbose_name = "Terminal Service"
        verbose_name_plural = "Terminal Services"

    def __str__(self):
        return f"{self.name} ({self.get_container_size_display()} - {self.get_container_state_display()})"


class FreeDayCombination(BaseModel):
    container_size = models.CharField(max_length=50, choices=ContainerSize.choices)
    container_state = models.CharField(max_length=50, choices=ContainerState.choices)
    category = models.CharField(
        max_length=50,
        choices=(("import", "Import"), ("export", "Export"), ("transit", "Transit")),
    )
    default_free_days = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ("container_size", "container_state", "category")
        verbose_name = "Free Day Combination"
        verbose_name_plural = "Free Day Combinations"

    def __str__(self):
        return f"{self.get_container_size_display()} - {self.get_container_state_display()} - {self.get_category_display()}"


@receiver(post_save, sender=TerminalService)
def create_contract_services(sender, instance, created, **kwargs):
    if created:
        from apps.customers.models import CompanyContract, ContractService

        # Get all company contracts
        company_contracts = CompanyContract.objects.all()
        contract_services = []

        for contract in company_contracts:
            contract_services.append(
                ContractService(
                    contract=contract,
                    service=instance,
                    price=instance.base_price,
                    quantity=1,
                )
            )

        # Bulk create the ContractService instances
        ContractService.objects.bulk_create(contract_services)
