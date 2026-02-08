#!/usr/bin/env node
/**
 * Extract AIContent types from messages.tsp
 * Outputs: List of all content types in the union
 */

const fs = require('fs');
const path = require('path');

const tspPath = path.join(__dirname, '../typespec/messages.tsp');
const content = fs.readFileSync(tspPath, 'utf-8');

// Find the AIContent union definition
const unionRegex = /@discriminator\("kind"\)\s*union\s+AIContent\s*\{([^}]+)\}/s;
const match = content.match(unionRegex);

if (!match) {
  console.error('Could not find AIContent union in messages.tsp');
  process.exit(1);
}

const unionBody = match[1];

// Extract content type names (excluding comments)
const lines = unionBody.split('\n');
const types = [];

for (const line of lines) {
  const trimmed = line.trim();
  // Skip empty lines and comments
  if (!trimmed || trimmed.startsWith('//')) continue;

  // Extract type name (before comma)
  const typeMatch = trimmed.match(/^(\w+),?$/);
  if (typeMatch) {
    types.push(typeMatch[1]);
  }
}

console.log('AIContent Types Found:', types.length);
console.log('');
console.log(types.join('\n'));

// Write to output file
const outputPath = path.join(__dirname, '../.workspace/content-types-current.txt');
fs.mkdirSync(path.dirname(outputPath), { recursive: true });
fs.writeFileSync(outputPath, types.join('\n'));

console.log('\nOutput written to:', outputPath);
