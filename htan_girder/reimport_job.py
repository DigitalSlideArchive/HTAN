import json
from threading import RLock

from girder import logger
from girder.models.assetstore import Assetstore
from girder.models.folder import Folder
from girder.models.setting import Setting
from girder.models.user import User
from girder.utility.progress import ProgressContext

from girder_jobs.constants import JobStatus
from girder_jobs.models.job import Job

from .constants import PluginSettings

_reimportStatus = {
    'lock': RLock(),
    'running': None,
    'rerun': set(),
}


def reimportData(key):
    with _reimportStatus['lock']:
        if not _reimportStatus['running']:
            startReimportJob(key)
        else:
            if key not in _reimportStatus['rerun']:
                logger.info('Adding future HTAN reimport job for %s.', key)
            else:
                logger.info('Already have a future HTAN reimport job for %s.', key)
            _reimportStatus['rerun'] |= {key}


def startReimportJob(key):
    with _reimportStatus['lock']:
        job = Job().createLocalJob(
            module='htan_girder.reimport_job',
            function='reimportJob',
            title='Reimport to the HTAN assetstore',
            type='htan_reimport',
            public=True,
            asynchronous=True,
            kwargs=dict(key=key),
        )
        _reimportStatus['running'] = True
        _reimportStatus['rerun'] -= {key}
        logger.info('Scheduling HTAN reimport job.')
        Job().scheduleJob(job)


def reimportJob(job):
    key = job['kwargs']['key']
    job = Job().updateJob(
        job, log='Started HTAN reimport job for %s\n' % key,
        status=JobStatus.RUNNING)
    try:
        importList = Setting().get(PluginSettings.HTAN_IMPORT_LIST)
        if not importList:
            return
        record = {}
        for entry in json.loads(importList):
            if entry.get('key') == key:
                record = entry
        assetstoreId = record.get('assetstoreId')
        importFolderId = record.get('destinationId')
        if not assetstoreId or not importFolderId:
            logger.info(
                'HTAN reimport job for key %s not configured.  An assetstore '
                'and folder must be set.', key)
            return
        assetstore = Assetstore().load(assetstoreId)
        folder = Folder().load(importFolderId, force=True)
        if not assetstore or not folder:
            logger.info(
                'HTAN reimport job not configured properly.  There is '
                'invalid or nonexistant assetstore or folder.')
            return
        admin = User().findOne({'admin': True})
        logger.info('Starting HTAN reimport job for %s.', key)
        with ProgressContext(True, user=admin, title='Importing data') as ctx:
            Assetstore().importData(
                assetstore, parent=folder, parentType='folder',
                params=dict(
                    importPath=record.get('importPath', ''),
                    fileIncludeRegex=record.get('fileIncludeRegex'),
                    fileExcludeRegex=record.get('fileExcludeRegex'),
                ), progress=ctx, user=admin,
                leafFoldersAsItems=False)
        if record.get('endFunction'):
            logger.info(
                'Should now run function %s, but doing so it not implemented',
                record['endFunction'])
        logger.info('Finished HTAN reimport job for %s.' % key)
        job = Job().updateJob(
            job, log='Finished HTAN reimport job for %s.' % key,
            status=JobStatus.SUCCESS)
    except Exception:
        job = Job().updateJob(
            job, log='Error running HTAN reimport job for %s\n' % key,
            status=JobStatus.ERROR)
        logger.exception('Error running HTAN reimport job for %s', key)
        return
    finally:
        with _reimportStatus['lock']:
            _reimportStatus['running'] = False
            if len(_reimportStatus['rerun']):
                startReimportJob(sorted(_reimportStatus['rerun'])[0])
