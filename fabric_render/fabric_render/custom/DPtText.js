const fabric = require('fabric').fabric;


/**
 * d-pt-text 是个行为与group一致
 */

fabric.DPtText = fabric.util.createClass(fabric.Group, {
  type: 'd-pt-text',
  initialize(objects, options) {
    const alreadyGrouped = true
    this.callSuper('initialize', objects, {...options, alreadyGrouped});
  },
});

fabric.DPtText.fromObject = (object, callback) => {
  fabric.util.enlivenObjects(object.objects, function (enlivenedObjects) {
    var options = fabric.util.object.clone(object);
    delete options.objects;
    var instance = new fabric.DPtText(enlivenedObjects, options);
    callback && callback(instance);
  });
};