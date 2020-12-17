import $ from 'jquery';
import _ from 'underscore';
import View from '@girder/core/views/View';

import PluginConfigBreadcrumbWidget from '@girder/core/views/widgets/PluginConfigBreadcrumbWidget';
import BrowserWidget from '@girder/core/views/widgets/BrowserWidget';
import { restRequest } from '@girder/core/rest';
import events from '@girder/core/events';
import router from '@girder/core/router';

import ConfigViewTemplate from 'ConfigView.pug';
import 'ConfigView.styl';

/**
 * Show the default quota settings for users and collections.
 */
var ConfigView = View.extend({
    events: {
        'click #g-htan-save': function (event) {
            this.$('#g-htan-error-message').text('');
            var settings = _.map(this.settingsKeys, (key) => {
                const element = this.$('#g-' + key.replace(/[_.]/g, '-'));
                var result = {
                    key,
                    value: element.val() || null
                };
                if (key === 'htan.import_folder') {
                    result.value = result.value ? result.value.split(' ')[0] : '';
                }
                return result;
            });
            this._saveSettings(settings);
        },
        'click #g-htan-cancel': function (event) {
            router.navigate('plugins', { trigger: true });
            router.navigate('plugins', { trigger: true });
        },
        'click .g-open-browser': '_openBrowser'
    },
    initialize: function () {
        this.breadcrumb = new PluginConfigBreadcrumbWidget({
            pluginName: 'HTAN',
            parentView: this
        });

        this.settingsKeys = [
            'htan.assetstore',
            'htan.import_path',
            'htan.import_folder'
        ];
        $.when(
            restRequest({
                method: 'GET',
                url: 'system/setting',
                data: {
                    list: JSON.stringify(this.settingsKeys),
                    default: 'none'
                }
            }).done((resp) => {
                this.settings = resp;
            }),
            restRequest({
                method: 'GET',
                url: 'system/setting',
                data: {
                    list: JSON.stringify(this.settingsKeys),
                    default: 'default'
                }
            }).done((resp) => {
                this.defaults = resp;
            })
        ).done(() => {
            this.render();
        });

        this._browserWidgetView = new BrowserWidget({
            parentView: this,
            titleText: 'Import Destination',
            helpText: 'Browse to a location to select it as the destination.',
            submitText: 'Select Destination',
            validate: function (model) {
                let isValid = $.Deferred();
                if (!model || model.get('_modelType') !== 'folder') {
                    isValid.reject('Please select a folder.');
                } else {
                    isValid.resolve();
                }
                return isValid.promise();
            }
        });
        this.listenTo(this._browserWidgetView, 'g:saved', function (val) {
            this.$('#g-htan-import-folder').val(val.id);
            restRequest({
                url: `resource/${val.id}/path`,
                method: 'GET',
                data: { type: val.get('_modelType') }
            }).done((result) => {
                // Only add the resource path if the value wasn't altered
                if (this.$('#g-htan-import-folder').val() === val.id) {
                    this.$('#g-htan-import-folder').val(`${val.id} (${result})`);
                }
            });
        });
    },

    render: function () {
        this.$el.html(ConfigViewTemplate({
            settings: this.settings,
            defaults: this.defaults
        }));
        this.breadcrumb.setElement(this.$('.g-config-breadcrumb-container')).render();
        return this;
    },

    _saveSettings: function (settings) {
        return restRequest({
            method: 'PUT',
            url: 'system/setting',
            data: {
                list: JSON.stringify(settings)
            },
            error: null
        }).done(() => {
            events.trigger('g:alert', {
                icon: 'ok',
                text: 'Settings saved.',
                type: 'success',
                timeout: 4000
            });
        }).fail((resp) => {
            this.$('#g-htan-error-message').text(
                resp.responseJSON.message
            );
        });
    },

    _openBrowser: function () {
        this._browserWidgetView.setElement($('#g-dialog-container')).render();
    }
});

export default ConfigView;
