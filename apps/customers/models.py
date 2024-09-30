from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator, MinValueValidator
from django.db import models, transaction
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.text import slugify

from apps.core.models import BaseModel, TerminalService, FreeDayCombination
from apps.users.models import CustomUser


class Company(BaseModel):
    name = models.CharField(
        max_length=255,
        unique=True,
        db_index=True,
        validators=[RegexValidator(r"\S", "Name cannot be empty or just whitespace.")],
    )
    address = models.TextField(blank=True)
    slug = models.SlugField(max_length=255, unique=True, db_index=True)

    class Meta:
        verbose_name_plural = "Companies"
        verbose_name = "Company"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class CompanyUser(BaseModel):
    company = models.ForeignKey(
        Company, on_delete=models.CASCADE, related_name="company_users"
    )
    user = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name="company_users"
    )

    class Meta:
        verbose_name_plural = "Company Users"
        verbose_name = "Company User"
        ordering = ["company", "user"]

    def clean(self):
        """
        Custom validation to ensure the relationship is unique and valid.
        """
        super().clean()
        if CompanyUser.objects.filter(company=self.company, user=self.user).exists():
            raise ValidationError("This user is already associated with this company.")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.company} - {self.user}"


class CompanyContract(BaseModel):
    name = models.CharField(max_length=255, unique=True)
    company = models.ForeignKey(
        Company, on_delete=models.CASCADE, related_name="contracts"
    )
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    file = models.FileField(upload_to="contracts/", blank=True)
    free_days = models.PositiveIntegerField(blank=True, null=True)

    class Meta:
        ordering = ["-id"]
        constraints = [
            models.UniqueConstraint(
                fields=["company", "start_date"], name="unique_company_start_date"
            )
        ]
        db_table = "customer_contract"
        verbose_name = "Customer Contract"
        verbose_name_plural = "Customer Contracts"

    def __str__(self):
        return f"Contract with {self.company} from {self.start_date}"


@receiver(post_save, sender=CompanyContract)
def link_free_day_combinations(sender, instance, created, **kwargs):
    if created:
        with transaction.atomic():
            free_day_combinations = FreeDayCombination.objects.all()
            for combination in free_day_combinations:
                ContractFreeDay.objects.get_or_create(
                    contract=instance,
                    free_day_combination=combination,
                    defaults={"free_days": instance.free_days or 0},
                )


class ContractService(BaseModel):
    contract = models.ForeignKey(
        CompanyContract, on_delete=models.CASCADE, related_name="services"
    )
    service = models.ForeignKey(TerminalService, on_delete=models.CASCADE)
    price = models.DecimalField(
        max_digits=12, decimal_places=2, validators=[MinValueValidator(0)]
    )
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        ordering = ["-id"]
        unique_together = ("contract", "service")
        db_table = "contract_service"
        verbose_name = "Contract Service"
        verbose_name_plural = "Contract Services"

    def __str__(self):
        return f"{self.service} for {self.contract.company} at {self.price}"


class ContractFreeDay(BaseModel):
    contract = models.ForeignKey(
        CompanyContract, on_delete=models.CASCADE, related_name="contract_free_days"
    )
    free_day_combination = models.ForeignKey(
        FreeDayCombination, on_delete=models.CASCADE, related_name="contract_free_days"
    )
    free_days = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ("contract", "free_day_combination")
        verbose_name = "Contract Free Day"
        verbose_name_plural = "Contract Free Days"

    def __str__(self):
        return f"{self.contract.name} - {self.free_day_combination} - {self.free_days} days"
