from girder import plugin
from girder.models.assetstore import Assetstore
from girder.models.folder import Folder
from girder.utility import setting_utilities

from .constants import PluginSettings


@setting_utilities.validator(PluginSettings.HTAN_ASSETSTORE)
def validateHTANAssetstore(doc):
    if not doc.get('value', None):
        doc['value'] = None
    else:
        Assetstore().load(doc['value'], force=True, exc=True)


@setting_utilities.validator(PluginSettings.HTAN_IMPORT_PATH)
def validateHTANImportPath(doc):
    if not doc.get('value', None):
        doc['value'] = None
    else:
        doc['value'] = str(doc['value'])


@setting_utilities.validator(PluginSettings.HTAN_IMPORT_FOLDER)
def validateHTANImportFolder(doc):
    if not doc.get('value', None):
        doc['value'] = None
    else:
        Folder().load(doc['value'], force=True, exc=True)


class GirderPlugin(plugin.GirderPlugin):
    DISPLAY_NAME = 'HTAN'
    CLIENT_SOURCE_PATH = 'web_client'

    def load(self, info):
        # add plugin loading logic here
        pass
