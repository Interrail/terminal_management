from django.db.models import Count
from django.shortcuts import get_object_or_404

from apps.customers.filters import CompanyFilter
from apps.customers.models import Company


class CompanyService:
    def create_company(self, name, address):
        return Company.objects.create(name=name, address=address)

    def update_company(self, company_id, **data):
        company = get_object_or_404(Company, id=company_id)
        for key, value in data.items():
            setattr(company, key, value)
        company.save()
        return company

    def get_all_companies(self, filters):
        filters = filters or {}
        qs = Company.objects.annotate(
            containers_count=Count("container_visits")
        ).order_by("id")
        return CompanyFilter(filters, queryset=qs).qs

    def get_company_by_id(self, company_id):
        return get_object_or_404(Company, id=company_id)

    def get_company_by_name(self, name):
        return Company.objects.filter(name=name).first()

    def delete_company(self, company_id):
        company = get_object_or_404(Company, id=company_id)
        company.delete()
