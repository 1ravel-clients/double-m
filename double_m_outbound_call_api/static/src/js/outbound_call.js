odoo.define('double_m_outbound_call_api.outbound_call', function(require) {
    "use strict";
    var FieldChar = require('web.basic_fields').FieldChar;
    var fieldRegistry  = require('web.field_registry');
    var CustomPhoneField= FieldChar.extend({
        _renderReadonly: function () {
            // Override this function to modify your field on readonly mode
            this._super.apply(this, arguments);
            var phoneNumber = this.$el.html();
            // this.$el.attr('data-phone', phoneNumber);

            var $clickToCall = $('<button>', {class: 'btn btn-link mb-1 clicktocall-gcalls'}).attr('data-phone', phoneNumber).html('<i class="fa fa-mobile"> Call</i>');
            this.$el.append($clickToCall);
        },
    });

    // This is the name of your new widget field extending
    fieldRegistry.add('outbound_call', CustomPhoneField);

    return {
        CustomPhoneField: CustomPhoneField,
    };
});
