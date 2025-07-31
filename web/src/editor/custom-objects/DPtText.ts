import { fabric } from 'fabric';


/**
 * pt-text 是个图层组，包含一个文字图层和一个背景图片层
 */

export const createPicTransTextClass = () => {
  // @ts-ignore custom d-pt-text
  fabric.DPtText = fabric.util.createClass(fabric.Group, {
    type: 'd-pt-text',

    initialize(objects, options) {
      const alreadyGrouped = true
      // 寻找最后一个 type 为 'text' 的 object
      this.textLayer = objects.slice().reverse().find(obj => obj.type === 'text' || obj.type === 'f-text' || obj.type === 'i-text');
      this.originText = fabric.util.object.clone(this.textLayer)
      let extra = this.textLayer.extra || {'from_text': 'unknown', 'from_lan': 'unknown'}
      this.originText.text = "原文: "+extra.from_text
      this.originText.fill = 'rgb(160, 160, 160)'
      this.originText.fontSize=20
      this.originText.fontFamily = "AlibabaPuHuiTi"
      this.originText.top=0
      this.originText.left=0
      this.originText.linethrough=true
      this.originText.angle=0
      this.originText.visible=true
      // this.originTextCover=this.originText.toDataURL()
      

      this.callSuper('initialize', objects, {...options, alreadyGrouped});

      this.transable = options.transable ?? true;

      // this._cover = this.toDataURL()
      // 根据 transable 属性设置子对象的可见性
      this._updateVisibility();
    },

    getTextLayer() {
      return this.textLayer
    },

    // 增加 set 方法的扩展，监听 transable 属性的变化
    set(property, value) {
      this.callSuper('set', property, value);

      if (property === 'transable') {
        this.transable = value;
        this._updateVisibility();
      }

      return this;
    },
    setTransable(a) {
      this.set('transable', a)
    },
    toObject() {
      return fabric.util.object.extend(this.callSuper('toObject'), {
        transable: this.transable
      });
    },
    
    // 自定义方法，根据 transable 属性更新子对象的可见性
    _updateVisibility() {
        this._objects.forEach(obj => {
          obj.visible = this.transable;
        });
      },

    // 自定义 toDataURL 方法
    toCover(options) {
      if (this.transable) {
        return this.toDataURL(options);
      } else {
        return this.originText.toDataURL({
          // visible:true,
          ...options
        });
      }
    }
  });

  // @ts-ignore custom d-pt-text
  fabric.DPtText.fromObject = (object, callback) => {
    fabric.util.enlivenObjects(object.objects, function (enlivenedObjects) {
      var options = fabric.util.object.clone(object);
      delete options.objects;
      var instance = new fabric.DPtText(enlivenedObjects, options);
      callback && callback(instance);
    });
  };

  // 扩展 fabric.IText.prototype.toObject 方法
  fabric.IText.prototype.toObject = (function (toObject) {
    return function () {
      // 调用原始的 toObject 方法，并扩展自定义属性
      return fabric.util.object.extend(toObject.call(this), {
        extra: this.extra || {}, // 添加 extra 属性，默认为 null
      });
    };
  })(fabric.IText.prototype.toObject);

  fabric.IText.fromObject = (function (fromObject) {
    return function (object, callback) {
      return fromObject.call(this, object, function (instance) {
        instance.extra = object.extra || {}; // 恢复 extra 属性
        callback && callback(instance);
      });
    };
  })(fabric.IText.fromObject);
};