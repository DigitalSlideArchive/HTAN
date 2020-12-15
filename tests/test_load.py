import pytest

from girder.plugin import loadedPlugins


@pytest.mark.plugin('htan_girder')
def test_import(server):
    assert 'htan_girder' in loadedPlugins()
