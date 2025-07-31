  // Helper function to modify image URLs to use the proxy
  export const modifyImageUrls = (objects) => {
    objects.forEach(obj => {
      if (obj.type === 'image' && obj.src) {
        obj.src = `https://api.doomn.com/_proxy/${obj.src}`;
      }
    });
  }

  // 增加 cross
  export const _from_z = (obj) => {
    if (Array.isArray(obj)) {
      obj.forEach(item => _from_z(item));
    } else if (obj.type === 'group') {
      _from_z(obj.objects)
    } else if (obj.type === 'image') {
        // obj.crossOrigin = 'anonymous';
        // obj.src = `https://api.doomn.com/_proxy/${obj.src}`;
    }

    delete obj['clipPath'];
  }

  export const convert = (json, source) => {
    if (source == 'z') {
      return from_z(json)
    } 

    return json
  }

  const from_z = (json) => {
     json.objects.splice(0, 0,{
        type: "rect",
        version: "5.3.0",
        originX: "left",
        originY: "top",
        left: 0,
        top: 0,
        width: json.clipPath.width,
        height: json.clipPath.height,
        fill: "#ffffff",
        id: "workspace",
        selectable: false,
        hasControls: false
      })
    _from_z(json.objects)
    console.dir(json)
    return json
  }