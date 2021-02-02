import $ from 'jquery';
import View from '@girder/core/views/View';

import PluginConfigBreadcrumbWidget from '@girder/core/views/widgets/PluginConfigBreadcrumbWidget';
import BrowserWidget from '@girder/core/views/widgets/BrowserWidget';
import { restRequest } from '@girder/core/rest';
import events from '@girder/core/events';
import router from '@girder/core/router';

import ConfigViewTemplate from './ConfigView.pug';
import './ConfigView.styl';

/**
 * Show the default quota settings for users and collections.
 */
var ConfigView = View.extend({
    events: {
        'click #g-htan-save': '_recordSettings',
        'click #g-htan-cancel': function (event) {
            router.navigate('plugins', { trigger: true });
            router.navigate('plugins', { trigger: true });
        },
        'click .g-open-browser': '_openBrowser',
        'click .g-htan-add': '_addRow',
        'click .g-htan-delete': '_removeRow'
    },
    initialize: function () {
        this.breadcrumb = new PluginConfigBreadcrumbWidget({
            pluginName: 'HTAN',
            parentView: this
        });

        this.settingsKeys = [
            'htan.import_list'
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
            this._browserTarget.val(val.id);
            restRequest({
                url: `resource/${val.id}/path`,
                method: 'GET',
                data: { type: val.get('_modelType') }
            }).done((result) => {
                // Only add the resource path if the value wasn't altered
                if (this._browserTarget.val() === val.id) {
                    this._browserTarget.val(`${val.id} (${result})`);
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

    _openBrowser: function (el) {
        this._browserTarget = $(el.target).closest('td').find('input');
        this._browserWidgetView.setElement($('#g-dialog-container')).render();
    },

    _addRow: function () {
        let newrow = this.$('tr.htan-empty-row').clone();
        let parent = this.$('tr.htan-empty-row').parent();
        this.$('tr.htan-empty-row').removeClass('htan-empty-row');
        parent.append(newrow);
    },
    _removeRow: function (evt) {
        $(evt.target).closest('tr').remove();
    },
    _recordSettings: function (event) {
        this.$('#g-htan-error-message').text('');
        let importList = [];
        this.$('tr').each(function () {
            let entry = {};
            $(this).find('[htan_prop]').each(function () {
                let input = $(this);
                let key = input.attr('htan_prop');
                let value = input.val().trim();
                if (value) {
                    if (key === 'destinationId') {
                        value = value.split(' ')[0];
                    }
                    entry[key] = value;
                }
            });
            if (Object.keys(entry).length) {
                importList.push(entry);
            }
        });
        this._saveSettings([{
            key: 'htan.import_list',
            value: JSON.stringify(importList)
        }]);
    }
});

export default ConfigView;
