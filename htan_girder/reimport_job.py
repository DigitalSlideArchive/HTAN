from threading import RLock

from girder import logger
from girder.models.assetstore import Assetstore
from girder.models.folder import Folder
from girder.models.setting import Setting
from girder.models.user import User
from girder.utility.progress import ProgressContext

from girder_jobs.models.job import Job

from .constants import PluginSettings

_reimportStatus = {
    'lock': RLock(),
    'running': None,
    'rerun': False,
}


def reimportData():
    with _reimportStatus['lock']:
        if not _reimportStatus['running']:
            startReimportJob()
        else:
            _reimportStatus['rerun'] = True


def startReimportJob():
    with _reimportStatus['lock']:
        job = Job().createLocalJob(
            module='htan_girder.reimport_job',
            function='reimportJob',
            title='Reimport to the HTAN assetstore',
            type='htan_reimport',
            public=True,
            asynchronous=True,
        )
        _reimportStatus['running'] = True
        _reimportStatus['rerun'] = False
        logger.info('Scheduling HTAN reimport job.')
        Job().scheduleJob(job)


def reimportJob(*args, **kwargs):
    try:
        assetstoreId = Setting().get(PluginSettings.HTAN_ASSETSTORE)
        importPath = Setting().get(PluginSettings.HTAN_IMPORT_PATH) or ''
        importFolderId = Setting().get(PluginSettings.HTAN_IMPORT_FOLDER)
        if not assetstoreId or not importFolderId:
            logger.info('HTAN reimport job not configured.  An assetstore and folder must be set.')
            return
        assetstore = Assetstore().load(assetstoreId)
        folder = Folder().load(importFolderId, force=True)
        if not assetstore or not folder:
            logger.info(
                'HTAN reimport job not configured properly.  There is '
                'invalid or nonexistant assetstore or folder.')
            return
        admin = User().findOne({'admin': True})
        logger.info('Starting HTAN reimport job.')
        with ProgressContext(True, user=admin, title='Importing data') as ctx:
            Assetstore().importData(
                assetstore, parent=folder, parentType='folder',
                params=dict(importPath=importPath), progress=ctx, user=admin,
                leafFoldersAsItems=False)
        logger.info('Finished HTAN reimport job.')
    finally:
        with _reimportStatus['lock']:
            _reimportStatus['running'] = False
            if _reimportStatus['rerun']:
                startReimportJob()
