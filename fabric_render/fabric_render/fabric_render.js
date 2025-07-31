// fabric_script.js
const fabric = require('fabric').fabric;
const fs = require('fs');
const out = fs.createWriteStream(process.argv[2]);
require('./custom/DPtText')

// createPicTransTextClass()

// 字体
if (process.argv[6].length > 1) {
    const font_families = process.argv[6].split(",");
    const font_paths = process.argv[7].split(",");
    for (let i = 0; i < font_families.length; i++) {
        fabric.nodeCanvas.registerFont(font_paths[i], {family: font_families[i]});
    }
} else {
    const path = require('path');
    // 获取当前目录的绝对路径
    const currentDir = __dirname;
    // 获取当前目录的上一级目录
    // const parentDir = path.dirname(currentDir);
    // 相对路径（从当前目录的上一级目录开始）
    const relativePath = 'assets/font/YouSheBiaoTiHei.ttf';
    // 将相对路径转换为绝对路径
    const absolutePath = path.resolve(currentDir, relativePath);
    fabric.nodeCanvas.registerFont(absolutePath, {family: 'YouSheBiaoTiHei'});
}

// 画布大小
const canvas = new fabric.StaticCanvas(null,
    {width: parseInt(process.argv[4]), height: parseInt(process.argv[5])}
);

fs.readFile(process.argv[3], 'utf8', (err, data) => {
    if (err) throw err;
    canvas.loadFromJSON(data, function () {
        canvas.renderAll();
        const stream = canvas.createPNGStream();
        stream.on('data', function (chunk) {
            out.write(chunk);
        });
    });
});
