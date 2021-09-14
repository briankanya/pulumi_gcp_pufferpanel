"""Main module."""

from typing import Optional

from pulumi import ComponentResource, ResourceOptions
from pulumi.asset import FileAsset
from pulumi_gcp.cloudfunctions import Function, FunctionIamMember
from pulumi_gcp.compute import AwaitableGetImageResult, Disk, get_image
from pulumi_gcp.config import zone
from pulumi_gcp.storage import Bucket, BucketObject


class PufferPanel(ComponentResource):
    AVAILABLE_MEMORY_MB = 128
    FUNCTION_RUNTIME = "python37"
    IMAGE_FAMILY = "debian-10"
    IMAGE_PROJECT = "debian-cloud"
    INGRESS_SETTINGS = "ALLOW_ALL"

    def __init__(
        self,
        name: str,
        dns_name: str,
        dns_zone: str,
        disk_size: Optional[int] = 30,
        disk_type: Optional[str] = "pd-standard",
        machine_type: Optional[str] = "e2-medium",
        opts: Optional[ResourceOptions] = None,
        server_name: Optional[str] = "pufferpanel-server",
    ) -> None:
        """
        Constructs the open source game server management tool PufferPanel.

        :param dns_name: The domain name to bind to
        :param dns_zone: The zone the dns_name falls into
        :param disk_size: The disk size to create for the preemptible compute instance
        :param disk_type: The disk type to create for the preemptible compute instance
        :param machine_type: The machine type to use for the preemptible compute instance
        :param server_name: The name to use for the preemptible compute instance
        """
        super().__init__(t="PufferPanel", name=name, opts=opts)
        self.code_bucket = self.__create_code_bucket()
        self.code_bucket_object = self.__create_code_bucket_object(bucket=self.code_bucket)
        self.dns_name = dns_name
        self.dns_zone = dns_zone
        self.disk_size = disk_size
        self.disk_type = disk_type
        self.machine_image = self.__get_image(
            image_family=self.IMAGE_FAMILY, image_project=self.IMAGE_PROJECT
        )
        self.machine_disk = self.__create_disk(
            disk_size=self.disk_size, disk_type=self.disk_type, image=self.machine_image
        )
        self.machine_type = machine_type
        self.server_name = server_name

        self.function = self.__create_function(
            available_memory_mb=self.AVAILABLE_MEMORY_MB,
            bucket=self.code_bucket,
            bucket_object=self.code_bucket_object,
            disk=self.machine_disk,
            dns_name=self.dns_name,
            dns_zone=self.dns_zone,
            function_runtime=self.FUNCTION_RUNTIME,
            ingress_settings=self.INGRESS_SETTINGS,
            machine_type=self.machine_type,
            server_name=self.server_name,
        )
        self.anonymous_function_access = self.__give_anonymous_function_access(self.function)

    def __get_image(self, image_family: str, image_project: str) -> AwaitableGetImageResult:
        return get_image(family=image_family, project=image_project)

    def __create_disk(
        self, disk_size: int, disk_type: str, image: AwaitableGetImageResult
    ) -> Disk:
        return Disk(
            resource_name="pufferpanel-disk",
            image=image.name,
            size=disk_size,
            type=disk_type,
        )

    def __create_code_bucket(self) -> Bucket:
        return Bucket("pufferpanel-bucket", force_destroy=True)

    def __create_code_bucket_object(self, bucket: Bucket) -> BucketObject:
        return BucketObject(
            "pufferpanel-bucket-object", bucket=bucket.name, source=FileAsset("cloud_function")
        )

    def __create_function(
        self,
        available_memory_mb: int,
        bucket: Bucket,
        bucket_object: BucketObject,
        disk: Disk,
        dns_name: str,
        dns_zone: str,
        function_runtime: str,
        ingress_settings: str,
        machine_type: str,
        server_name: str,
    ) -> Function:
        return Function(
            "pufferpanel-toggler",
            available_memory_mb=available_memory_mb,
            entry_point="http",
            environment_variables={
                "DISK_ID": disk.id,
                "DNS_NAME": dns_name,
                "DNS_ZONE": dns_zone,
                "MACHINE_TYPE": machine_type,
                "SERVER_NAME": server_name,
                "ZONE": zone,
            },
            ingress_settings=ingress_settings,
            max_instances=1,
            name="toggle-pufferpanel-server",
            runtime=function_runtime,
            source_archive_bucket=bucket.name,
            source_archive_object=bucket_object.name,
            trigger_http=True,
        )

    def __give_anonymous_function_access(self, function: Function) -> FunctionIamMember:
        return FunctionIamMember(
            "pufferpanel-server-toggler-public",
            cloud_function=function.name,
            role="roles/cloudfunctions.invoker",
            member="allUsers",
        )
