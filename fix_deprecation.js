const fs = require('fs');
const path = require('path');

const filesToFix = [
    'frontend/node_modules/spdy/test/client-test.js'
];

const target = 'util._extend';
const replacement = 'Object.assign';

filesToFix.forEach(filePath => {
    const fullPath = path.join(process.cwd(), filePath);
    if (fs.existsSync(fullPath)) {
        try {
            let content = fs.readFileSync(fullPath, 'utf8');
            if (content.includes(target)) {
                content = content.split(target).join(replacement);
                fs.writeFileSync(fullPath, content, 'utf8');
                console.log(`Fixed ${filePath}`);
            } else {
                console.log(`Target not found in ${filePath}`);
            }
        } catch (e) {
            console.error(`Error processing ${filePath}:`, e);
        }
    } else {
        console.log(`File not found: ${fullPath}`);
    }
});
