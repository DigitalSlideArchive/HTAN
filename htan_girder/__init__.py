from girder import plugin


class GirderPlugin(plugin.GirderPlugin):
    DISPLAY_NAME = 'HTAN'
    CLIENT_SOURCE_PATH = 'web_client'

    def load(self, info):
        # add plugin loading logic here
        pass
