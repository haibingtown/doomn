import { fabric } from 'fabric';

const extend = fabric.util.object.extend;

export const createFSVGClass = () => {
  // 创建自定义 FSVG 类
  fabric.Svg = fabric.util.createClass(fabric.Image, {
    type: 'svg',

    initialize: function(src, options) {
      options = options || {};
      this.callSuper('initialize', '', options);
      this._loadSVG(src, options.colors, options.stroke);
    },

    _loadSVG: function(src, fill, stroke) {
      fetch(src)
        .then(response => response.text())
        .then(svgText => {
          const parser = new DOMParser();
          const doc = parser.parseFromString(svgText, 'image/svg+xml');
          const svgElement = doc.querySelector('svg');
          if (svgElement) {
            this._applyColor(svgElement, fill, stroke);
            const serializer = new XMLSerializer();
            const newSvgUrl = 'data:image/svg+xml;base64,' + btoa(serializer.serializeToString(svgElement));
            fabric.Image.fromURL(newSvgUrl, (img) => {
              this.setElement(img.getElement());
              this.set({
                width: img.width,
                height: img.height
              });
              this.setCoords();
              this.canvas && this.canvas.renderAll();
            });
          }
        });
    },

    _applyColor: function(svgElement, colors, stroke) {
      if (colors) {
        Object.keys(colors).forEach(colorKey => {
          const colorValue = colors[colorKey];
          svgElement.querySelectorAll('*').forEach(el => {
            if (el.getAttribute('fill') === `var(${colorKey})`) {
              el.setAttribute('fill', colorValue);
            }
          });
        });
      }
      if (stroke) {
        svgElement.querySelectorAll('*').forEach(el => {
          el.setAttribute('stroke', stroke);
        });
      }
    },

  });

  // 静态方法 fromObject
  fabric.Svg.fromObject = (object, callback) => {
    const instance = new fabric.Svg(object.src, object);
    callback && callback(instance);
  };
}