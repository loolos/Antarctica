const fs = require('fs');
const path = require('path');

function hasChinese(text) {
    return /[\u4e00-\u9fff]/.test(text);
}

function walkDir(dir, fileList = []) {
    const files = fs.readdirSync(dir);
    for (const file of files) {
        if (file.includes('venv') || file.includes('node_modules') || file.startsWith('.')) continue;
        const filePath = path.join(dir, file);
        const stat = fs.statSync(filePath);
        if (stat.isDirectory()) {
            walkDir(filePath, fileList);
        } else {
            if (file.endsWith('.bat')) {
                fileList.push(filePath);
            }
        }
    }
    return fileList;
}

const batFiles = walkDir(process.cwd());

batFiles.forEach(file => {
    try {
        const content = fs.readFileSync(file, 'utf8');
        if (hasChinese(content)) {
            console.log(`FOUND_CHINESE: ${file}`);
            const lines = content.split('\n');
            lines.forEach(line => {
                if (hasChinese(line)) {
                    console.log(`  Snippet: ${line.trim().substring(0, 60)}...`);
                }
            });
        }
    } catch (e) {
        console.log(`Error reading ${file}: ${e.message}`);
    }
});
