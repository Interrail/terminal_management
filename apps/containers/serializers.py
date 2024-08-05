from rest_framework import serializers


class StorageStatisticsSerializer(serializers.Serializer):
    total_containers = serializers.IntegerField()
    empty_containers = serializers.IntegerField()
    laden_containers = serializers.IntegerField()
    avg_storage_days = serializers.IntegerField()
    turnover_rate = serializers.FloatField()
    storage_utilization = serializers.FloatField()


class ContainerTypeSerializer(serializers.Serializer):
    type = serializers.CharField()
    count = serializers.IntegerField()


class CustomerSerializer(serializers.Serializer):
    customer_name = serializers.CharField()
    visit_count = serializers.IntegerField()


class ContainerStatisticsSerializer(serializers.Serializer):
    common_types = serializers.ListField(child=ContainerTypeSerializer())


class CustomerStatisticsSerializer(serializers.Serializer):
    busiest_customers = serializers.ListField(child=CustomerSerializer())


class AllStatisticsSerializer(serializers.Serializer):
    storage = StorageStatisticsSerializer()
    common_types = serializers.ListField(child=ContainerTypeSerializer())
    busiest_customers = serializers.ListField(child=CustomerSerializer())
