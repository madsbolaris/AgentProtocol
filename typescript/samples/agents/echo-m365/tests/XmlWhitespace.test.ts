import * as fs from 'fs';
import * as path from 'path';

/**
 * Whitespace validation tests for XML result files.
 * Ensures proper indentation across all language implementations.
 */
describe('XML Results Whitespace Validation', () => {
  const testDataDir = findRepositoryRoot(process.cwd());
  const resultsBase = path.join(testDataDir, 'test-data', 'results', 'echom365');
  const xmlResultsDir = path.join(resultsBase, 'xml');
  const waitResultsDir = path.join(resultsBase, 'wait');

  function findRepositoryRoot(startPath: string): string {
    let current = startPath;
    while (current !== path.dirname(current)) {
      if (fs.existsSync(path.join(current, 'test-data'))) {
        return current;
      }
      current = path.dirname(current);
    }
    throw new Error('Could not find repository root with test-data directory');
  }

  function validateXmlIndentation(xmlFile: string) {
    const content = fs.readFileSync(xmlFile, 'utf-8');
    const lines = content.split('\n');
    const fileName = path.basename(xmlFile);

    lines.forEach((line, index) => {
      if (line.trim().startsWith('<?xml')) return;
      if (line.trim() === '') return;

      const lineNum = index + 1;

      // <thread> and </thread> should have no leading whitespace
      if (line.trim().startsWith('<thread') || line.trim().startsWith('</thread')) {
        if (!line.match(/^</)) {
          throw new Error(`${fileName}:${lineNum} - <thread> and </thread> tags should have no indentation\nLine: "${line}"`);
        }
      }
      // Direct children of <thread> should be indented with 2 spaces
      else if (line.trim().startsWith('<agent')) {
        if (!line.match(/^  [^ ]/)) {
          throw new Error(`${fileName}:${lineNum} - Direct children of <thread> should be indented with exactly 2 spaces\nLine: "${line}"`);
        }
      }
      // Children of <agent> should be indented with 4 spaces
      else if (line.trim().startsWith('<text')) {
        if (!line.match(/^    [^ ]/)) {
          throw new Error(`${fileName}:${lineNum} - Children of <agent> should be indented with exactly 4 spaces\nLine: "${line}"`);
        }
      }
      // Closing </agent> tag should be indented with 2 spaces
      else if (line.trim().startsWith('</agent')) {
        if (!line.match(/^  <\/agent>/)) {
          throw new Error(`${fileName}:${lineNum} - Closing </agent> tag should be indented with exactly 2 spaces\nLine: "${line}"`);
        }
      }
    });
  }

  it('should have proper indentation in xml results directory', () => {
    if (!fs.existsSync(xmlResultsDir)) {
      console.log('Skipping - xml results directory not found');
      return;
    }

    const xmlFiles = fs.readdirSync(xmlResultsDir)
      .filter(f => f.endsWith('.xml'))
      .map(f => path.join(xmlResultsDir, f));

    expect(xmlFiles.length).toBeGreaterThan(0);

    xmlFiles.forEach(xmlFile => {
      validateXmlIndentation(xmlFile);
    });
  });

  it('should have proper indentation in wait results directory', () => {
    if (!fs.existsSync(waitResultsDir)) {
      console.log('Skipping - wait results directory not found');
      return;
    }

    const xmlFiles = fs.readdirSync(waitResultsDir)
      .filter(f => f.endsWith('.xml'))
      .map(f => path.join(waitResultsDir, f));

    expect(xmlFiles.length).toBeGreaterThan(0);

    xmlFiles.forEach(xmlFile => {
      validateXmlIndentation(xmlFile);
    });
  });
});
