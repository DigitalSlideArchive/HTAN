import json

from girder import plugin
from girder.exceptions import ValidationException
from girder.models.assetstore import Assetstore
from girder.models.folder import Folder
from girder.utility import setting_utilities

from .constants import PluginSettings
from .rest import HTANResource


@setting_utilities.validator(PluginSettings.HTAN_IMPORT_LIST)
def validateHTANImportList(doc):
    val = doc.get('value', None)
    try:
        if isinstance(val, list):
            doc['value'] = json.dumps(val)
        elif not val or val.strip() == '':
            doc['value'] = None
        else:
            parsed = json.loads(val)
            if not isinstance(parsed, list):
                raise ValueError
            doc['value'] = val.strip()
    except (ValueError, AttributeError):
        raise ValidationException('%s must be a JSON list.' % doc['key'], 'value')
    keys = {}
    for entry in json.loads(doc['value']):
        if not entry.get('key') or entry.get('key') in keys:
            raise ValidationException('Each entry must have a unique name', 'value')
        try:
            Assetstore().load(entry.get('assetstoreId'), exc=True)
        except Exception:
            raise ValidationException(
                'Invalid assetstore ID %s.' % entry.get('assetstoreId'), 'value')
        try:
            Folder().load(entry.get('destinationId'), exc=True, force=True)
        except Exception:
            raise ValidationException(
                'Invalid import folder ID %s.' % entry.get('destinationId'), 'value')


class GirderPlugin(plugin.GirderPlugin):
    DISPLAY_NAME = 'HTAN'
    CLIENT_SOURCE_PATH = 'web_client'

    def load(self, info):
        info['apiRoot'].htan = HTANResource()
