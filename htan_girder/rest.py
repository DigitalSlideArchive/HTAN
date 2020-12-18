from girder.api import access
from girder.api.rest import Resource
from girder.api.describe import autoDescribeRoute, Description

from .reimport_job import reimportData


class HTANResource(Resource):
    def __init__(self):
        super().__init__()
        self.resourceName = 'htan'

        self.route('POST', ('reimport', ), self.reimportData)

    @autoDescribeRoute(
        Description('Reimport a folder to an assetstore based on settings.')
    )
    @access.public
    def reimportData(self):
        reimportData()
        return 'acknowledged'
