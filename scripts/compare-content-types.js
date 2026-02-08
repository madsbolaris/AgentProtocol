#!/usr/bin/env node
/**
 * Compare content types in TypeSpec vs Documentation
 */

const fs = require('fs');
const path = require('path');

// Read current TypeSpec types
const tspTypesPath = path.join(__dirname, '../.workspace/content-types-current.txt');
const tspTypes = new Set(
  fs.readFileSync(tspTypesPath, 'utf-8')
    .split('\n')
    .filter(Boolean)
);

// Read content-types.md
const docsPath = path.join(__dirname, '../api-reference/content-types.md');
const docsContent = fs.readFileSync(docsPath, 'utf-8');

// Extract types mentioned in docs (look for **TypeName** patterns)
const docTypeRegex = /\*\*(\w+Content)\*\*/g;
const docTypes = new Set();
let match;
while ((match = docTypeRegex.exec(docsContent)) !== null) {
  docTypes.add(match[1]);
}

console.log('TypeSpec Types:', tspTypes.size);
console.log('Documented Types:', docTypes.size);
console.log('');

// Find differences
const inTspNotInDocs = [...tspTypes].filter(t => !docTypes.has(t));
const inDocsNotInTsp = [...docTypes].filter(t => !tspTypes.has(t));

if (inTspNotInDocs.length > 0) {
  console.log('❌ In TypeSpec but NOT in docs:');
  inTspNotInDocs.forEach(t => console.log(`  - ${t}`));
  console.log('');
}

if (inDocsNotInTsp.length > 0) {
  console.log('❌ In docs but NOT in TypeSpec:');
  inDocsNotInTsp.forEach(t => console.log(`  - ${t}`));
  console.log('');
}

if (inTspNotInDocs.length === 0 && inDocsNotInTsp.length === 0) {
  console.log('✅ All types match!');
}

// Write report
const report = {
  tspCount: tspTypes.size,
  docCount: docTypes.size,
  inTspNotInDocs,
  inDocsNotInTsp,
  tspTypes: [...tspTypes].sort(),
  docTypes: [...docTypes].sort()
};

const reportPath = path.join(__dirname, '../.workspace/content-type-comparison.json');
fs.writeFileSync(reportPath, JSON.stringify(report, null, 2));
console.log('\nReport written to:', reportPath);
