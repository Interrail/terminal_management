from django.db import transaction, IntegrityError
from django.db.models import Count, Subquery, OuterRef, Prefetch
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import ValidationError

from apps.core.models import TerminalService
from apps.customers.filters import CompanyFilter, CompanyServiceFilter, FreeDaysFilter
from apps.customers.models import (
    Company,
    CompanyContract,
    ContractService,
    ContractFreeDay,
)


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
        qs = (
            Company.objects.annotate(
                containers_count=Count("container_visits"),
                active_contract=Subquery(
                    CompanyContract.objects.filter(
                        company=OuterRef("pk"), is_active=True
                    ).values("pk")[:1]
                ),
            )
            .prefetch_related(
                Prefetch(
                    "contracts",
                    queryset=CompanyContract.objects.filter(is_active=True),
                    to_attr="active_contract_list",
                )
            )
            .order_by("-id")
        )

        return CompanyFilter(filters, queryset=qs).qs

    def get_company_by_id(self, company_id):
        return get_object_or_404(Company, id=company_id)

    def get_company_by_name(self, name):
        return Company.objects.filter(name__iexact=name).first()

    def delete_company(self, company_id):
        company = get_object_or_404(Company, id=company_id)
        company.delete()


class CompanyContractService:
    @transaction.atomic
    def create_contract(self, company_id, data):
        try:
            customer_contract = CompanyContract.objects.create(
                company_id=company_id, **data
            )
            services = TerminalService.objects.all()
            for service in services:
                ContractServiceService().create(
                    customer_contract.id, service.id, service.base_price
                )
            return customer_contract
        except Exception as e:
            # Log the exception if needed
            raise e

    def get_by_id(self, contract_id):
        return get_object_or_404(CompanyContract, id=contract_id)

    def update_contract(self, contract_id, data):
        contract = get_object_or_404(CompanyContract, id=contract_id)

        # Store the original name
        original_name = contract.name

        for key, value in data.items():
            setattr(contract, key, value)

        try:
            # Attempt to save the contract
            contract.full_clean()  # This will check for model validation
            contract.save()
        except IntegrityError as e:
            # Check if the error is due to a duplicate name
            if "unique constraint" in str(e).lower() and "name" in str(e).lower():
                # If the name hasn't changed, we can ignore this error
                if data.get("name") == original_name:
                    pass  # The name hasn't changed, so we can ignore this error
                else:
                    # If the name has changed and there's a conflict, raise an error
                    raise ValidationError("A contract with this name already exists.")
            else:
                # If it's a different integrity error, re-raise it
                raise
        except ValidationError:
            # Re-raise any other validation errors
            raise

        return contract

    def delete_contract(self, contract_id):
        contract = get_object_or_404(CompanyContract, id=contract_id)
        contract.delete()

    def get_all_by_company(self, company_id):
        return CompanyContract.objects.filter(company_id=company_id)


class ContractServiceService:
    def create(self, contract_id, service_id, price=0):
        return ContractService.objects.create(
            contract_id=contract_id, service_id=service_id, price=price
        )

    def get_services_by_contract(self, contract_id, filters=None):
        filters = filters or {}
        qs = ContractService.objects.filter(contract_id=contract_id)
        return CompanyServiceFilter(filters, queryset=qs).qs

    def update_service(self, contract_id, service_id, data):
        service = get_object_or_404(
            ContractService, contract_id=contract_id, id=service_id
        )
        for key, value in data.items():
            setattr(service, key, value)
        service.save()
        return service

    def get_active_services_by_company(self, company_id, filters):
        filters = filters or {}
        qs = ContractService.objects.filter(
            contract__company_id=company_id,
            contract__is_active=True,
        )
        return CompanyServiceFilter(filters, queryset=qs).qs


class ContractFreeDayService:
    def get_free_days_by_contract(self, contract_id, filters=None):
        filters = filters or {}
        qs = ContractFreeDay.objects.filter(contract_id=contract_id)
        return FreeDaysFilter(filters, queryset=qs).qs

    def update_free_day(self, contract_id, free_day_id, data):
        free_day = get_object_or_404(
            ContractFreeDay, id=free_day_id, contract_id=contract_id
        )
        for key, value in data.items():
            setattr(free_day, key, value)
        free_day.save()
        return free_day
