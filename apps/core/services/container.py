from django.shortcuts import get_object_or_404

from apps.core.models import Container


class ContainerService:
    def get_all_containers(self):
        return Container.objects.all()

    def create_container(self, data):
        return Container.objects.create(**data)

    def get_or_create_container(self, container_name, container_size):
        if container := Container.objects.filter(name=container_name).first():
            return container
        else:
            return Container.objects.create(name=container_name, size=container_size)

    def exists_container(self, container_name):
        return Container.objects.filter(name=container_name).exists()

    def get_container(self, container_id):
        return get_object_or_404(Container, id=container_id)

    def get_container_by_name(self, container_name):
        return get_object_or_404(Container, name=container_name)

    def update_container(self, container_id, data):
        container = self.get_container(container_id)
        for key, value in data.items():
            setattr(container, key, value)
        container.save()
        return container

    def delete_container(self, container_id):
        container = self.get_container(container_id)
        container.delete()
