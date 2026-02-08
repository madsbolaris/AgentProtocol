#!/usr/bin/env node
/**
 * Check for ContentAnnotations model and usage
 */

const fs = require('fs');
const path = require('path');

const tspPath = path.join(__dirname, '../typespec/messages.tsp');
const content = fs.readFileSync(tspPath, 'utf-8');

console.log('Checking messages.tsp for ContentAnnotations...\n');

// Check if ContentAnnotations model exists
if (content.includes('model ContentAnnotations')) {
  console.log('✅ ContentAnnotations model FOUND');

  // Extract the model definition
  const modelRegex = /model ContentAnnotations\s*\{([^}]+)\}/s;
  const match = content.match(modelRegex);
  if (match) {
    console.log('\nContentAnnotations definition:');
    console.log(match[0]);
  }
} else {
  console.log('❌ ContentAnnotations model NOT FOUND in messages.tsp');
}

// Check for audience and encryption at message level
console.log('\n\nChecking ChatMessage for audience/encryption fields...\n');

const chatMessageRegex = /model ChatMessage\s*\{([\s\S]*?)\n\}/;
const chatMatch = content.match(chatMessageRegex);

if (chatMatch) {
  const messageBody = chatMatch[1];

  if (messageBody.includes('audience?:')) {
    console.log('✅ audience field FOUND at ChatMessage level');
  } else {
    console.log('❌ audience field NOT FOUND at ChatMessage level');
  }

  if (messageBody.includes('encryption?:')) {
    console.log('✅ encryption field FOUND at ChatMessage level');
  } else {
    console.log('❌ encryption field NOT FOUND at ChatMessage level');
  }
}

// Check if any content types reference ContentAnnotations
console.log('\n\nChecking if content types reference ContentAnnotations...\n');
const annotationsRefs = content.match(/annotations\?:\s*ContentAnnotations/g);

if (annotationsRefs) {
  console.log(`✅ Found ${annotationsRefs.length} references to ContentAnnotations in content types`);
} else {
  console.log('❌ NO references to ContentAnnotations found in content types');
}

// Check for EncryptedContent
console.log('\n\nChecking for EncryptedContent type...\n');
if (content.includes('model EncryptedContent')) {
  console.log('✅ EncryptedContent model FOUND');
} else {
  console.log('❌ EncryptedContent model NOT FOUND');
}
