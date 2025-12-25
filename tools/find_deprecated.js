const fs = require('fs');
const path = require('path');

const searchStr = 'util._extend';
const rootDir = 'frontend/node_modules';

function searchFile(filePath) {
    try {
        const content = fs.readFileSync(filePath, 'utf8');
        if (content.includes(searchStr)) {
            console.log(`Found in: ${filePath}`);
        }
    } catch (e) {
        // ignore errors
    }
}

function walkDir(dir) {
    if (!fs.existsSync(dir)) return;
    const files = fs.readdirSync(dir);
    for (const file of files) {
        const fullPath = path.join(dir, file);
        const stat = fs.statSync(fullPath);
        if (stat.isDirectory()) {
            walkDir(fullPath);
        } else if (file.endsWith('.js')) {
            searchFile(fullPath);
        }
    }
}

console.log('Searching...');
walkDir(rootDir);
console.log('Done.');
