from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.db import models
from django.utils.text import slugify

from apps.core.models import TimeStampedModel
from apps.users.models import CustomUser


class Company(TimeStampedModel):
    name = models.CharField(max_length=255, unique=True, db_index=True)
    validators = [RegexValidator(r"\S", "Name cannot be empty or just whitespace.")]
    address = models.TextField(blank=True)
    slug = models.SlugField(max_length=255, unique=True, db_index=True)

    class Meta:
        verbose_name_plural = "Companies"
        verbose_name = "Company"
        ordering = ["name"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class CompanyUser(TimeStampedModel):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)

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
