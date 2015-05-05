
var noEntity = new (Backbone.Model.extend({_id: 'ENT', name: '', label: '', fields: []}))();

var StringFieldModel = Backbone.Model.extend({
    defaults: {
        field: {name: '', label: ''},
        entity: noEntity,
    },
    val: function () {
        return this.get('entity').get(this.get('field').name);
    },
});

var StringInputView = Backbone.View.extend({
    tagName: 'input',
    className: 'form-control',
    id: function () {
        return this.model.get('field').name + '-ctrl';
    },
    //template: _.template('<input class="form-control" type="text"/>'),
    events: {
        'click [type="text"]': 'onChange',
    },
    render: function () {
        this.$el.attr('type', 'text');
        this.$el.attr('value', this.model.val());
        return this;
    },
    onChange: function () {
        console.log(this.id(),'changed!');
    },
});





