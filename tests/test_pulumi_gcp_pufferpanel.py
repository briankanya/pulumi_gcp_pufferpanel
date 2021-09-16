"""Tests for `pulumi_gcp_pufferpanel` module."""
from typing import Generator

import pulumi
import pytest

import pulumi_gcp_pufferpanel
from pulumi_gcp_pufferpanel.pulumi_gcp_pufferpanel import PufferPanel


@pytest.fixture
def version() -> Generator[str, None, None]:
    """Sample pytest fixture."""
    yield pulumi_gcp_pufferpanel.__version__


def test_version(version: str) -> None:
    """Sample pytest test function with the pytest fixture as an argument."""
    assert version == "0.4.2"


class MyMocks(pulumi.runtime.Mocks):
    """MyMocks."""

    def call(self, args: pulumi.runtime.MockCallArgs) -> dict:  # type: ignore
        """See https://www.pulumi.com/docs/reference/pkg/nodejs/pulumi/pulumi/runtime/#Mocks-call.

        Args:
            args (pulumi.runtime.MockCallArgs): Args for mock.

        Returns:
            dict: Needed provider implementation for this mock.
        """
        if args.token == "gcp:compute/getImage:getImage":
            return {"archive_size_bytes": 1180189056}
        return {}

    def new_resource(self, args: pulumi.runtime.MockResourceArgs) -> list:  # type: ignore
        """See https://www.pulumi.com/docs/reference/pkg/nodejs/pulumi/pulumi/runtime/#Mocks-newResource.

        Args:
            args (pulumi.runtime.MockResourceArgs): Args for mock.

        Returns:
            list: Unique identifier for this resource.
        """
        return [args.name + "_id", args.inputs]


pulumi.runtime.set_mocks(MyMocks())


@pulumi.runtime.test
def test_create_pufferpanel_server() -> None:
    """Test whether instantiating PufferPanel works."""
    _ = PufferPanel(
        name="PufferPanelServer", dns_name="bkanya.com", dns_zone="example-com-15fbd9a"
    )
