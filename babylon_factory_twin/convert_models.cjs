const fs = require('fs');
const path = require('path');

const modelsDir = path.join(__dirname, 'js/models');
const files = fs.readdirSync(modelsDir);

const injectCode = `\n  const size = machineMesh.metadata?.machineData?.size || {w:10, h:10, d:10};\n  const w = size.w; const h = size.h; const d = size.d;\n`;

files.forEach(file => {
  if (!file.endsWith('.js')) return;
  const filePath = path.join(modelsDir, file);
  let content = fs.readFileSync(filePath, 'utf-8');
  
  if (content.includes('const w = size.w')) {
    return; // Already processed
  }

  // 1. Inject w, h, d
  content = content.replace(/(function\s*\([^)]+\)\s*\{)/, `$1${injectCode}`);

  const replaceNumbers = (str) => {
      return str.replace(/(width|height|depth|diameter|size)\s*:\s*([0-9.]+)/g, (m, p1, p2) => {
          let factor = parseFloat(p2) / 10;
          let suffix = '';
          if (p1 === 'width') suffix = 'w';
          else if (p1 === 'height') suffix = 'h'; 
          else if (p1 === 'depth') suffix = 'd';
          else if (p1 === 'diameter') suffix = 'w'; 
          else if (p1 === 'size') suffix = 'w';
          return `${p1}: ${suffix} * ${factor}`;
      });
  };

  // Find all MeshBuilder.CreateXXXX options and replace
  content = content.replace(/(BABYLON\.MeshBuilder\.Create[A-Za-z]+\([^,]+,\s*\{)([^}]+)(\})/g, (m, start, options, end) => {
      const newOptions = replaceNumbers(options);
      return start + newOptions + end;
  });

  // 3. Replace .position.x/y/z = Number
  content = content.replace(/\.position\.(x|y|z)\s*=\s*([-]?[0-9.]+)(?!.*\s*\*\s*(w|h|d|Math\.PI))/g, (m, axis, val) => {
      const valF = parseFloat(val);
      if (isNaN(valF) || valF === 0) return m; 
      let factor = valF / 10;
      let suffix = '';
      if (axis === 'x') suffix = 'w';
      else if (axis === 'y') suffix = 'h';
      else if (axis === 'z') suffix = 'd';
      return `.position.${axis} = ${suffix} * ${factor}`;
  });

  fs.writeFileSync(filePath, content, 'utf-8');
});
console.log('Conversion complete');
