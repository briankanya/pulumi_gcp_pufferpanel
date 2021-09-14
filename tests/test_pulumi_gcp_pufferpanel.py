"""Tests for `pulumi_gcp_pufferpanel` module."""
from typing import Generator

import pytest

import pulumi_gcp_pufferpanel


@pytest.fixture
def version() -> Generator[str, None, None]:
    """Sample pytest fixture."""
    yield pulumi_gcp_pufferpanel.__version__


def test_version(version: str) -> None:
    """Sample pytest test function with the pytest fixture as an argument."""
    assert version == "0.4.2"
