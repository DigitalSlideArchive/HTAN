import events from '@girder/core/events';
import router from '@girder/core/router';

import { registerPluginNamespace } from '@girder/core/pluginUtils';
import { exposePluginConfig } from '@girder/core/utilities/PluginUtils';

// expose symbols under girder.plugins
import * as htan from '@girder/htan_girder';

import ConfigView from './views/ConfigView';

const pluginName = 'htan_girder';
const configRoute = `plugins/${pluginName}/config`;

registerPluginNamespace(pluginName, htan);

exposePluginConfig(pluginName, configRoute);

router.route(configRoute, 'HTANConfig', function () {
    events.trigger('g:navigateTo', ConfigView);
});
