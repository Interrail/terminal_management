from django.http import HttpResponse
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.containers.services.container_storage_report import (
    ContainerStorageReportService,
)


class ContainerStorageReportAPI(APIView):
    def get(self, request, company_id):
        try:
            container_storage_report_service = ContainerStorageReportService()
            transport_type = request.query_params.get("transport_type", None)
            month = request.query_params.get("month", None)
            dispatched = request.query_params.get("dispatched", None)

            workbook = container_storage_report_service.get_report(
                company_id,
                dispatched=dispatched,
                month=month,
                transport_type=transport_type,
            )

            response = HttpResponse(
                content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
            response["Content-Disposition"] = (
                "attachment; filename=container_storage_report.xlsx"
            )

            # Save the workbook directly to the response
            # Save workbook to response and verify
            print("Saving workbook to response...")
            workbook.save(response)

            print("Response size:", len(response.content))
            return response
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
