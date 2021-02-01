from girder.api import access
from girder.api.rest import Resource
from girder.api.describe import autoDescribeRoute, Description

from .reimport_job import reimportData


class HTANResource(Resource):
    def __init__(self):
        super().__init__()
        self.resourceName = 'htan'

        self.route('POST', ('reimport', ':key'), self.reimportData)

    @autoDescribeRoute(
        Description('Reimport a folder to an assetstore based on settings.')
        .param('key', 'The key to reimport.', paramType='path')
    )
    @access.public
    def reimportData(self, key):
        reimportData(key)
        return 'acknowledged'
