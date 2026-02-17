"use strict";
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || (function () {
    var ownKeys = function(o) {
        ownKeys = Object.getOwnPropertyNames || function (o) {
            var ar = [];
            for (var k in o) if (Object.prototype.hasOwnProperty.call(o, k)) ar[ar.length] = k;
            return ar;
        };
        return ownKeys(o);
    };
    return function (mod) {
        if (mod && mod.__esModule) return mod;
        var result = {};
        if (mod != null) for (var k = ownKeys(mod), i = 0; i < k.length; i++) if (k[i] !== "default") __createBinding(result, mod, k[i]);
        __setModuleDefault(result, mod);
        return result;
    };
})();
Object.defineProperty(exports, "__esModule", { value: true });
const fs = __importStar(require("fs"));
const path = __importStar(require("path"));
/**
 * Whitespace validation tests for XML result files.
 * Ensures proper indentation across all language implementations.
 */
describe('XML Results Whitespace Validation', () => {
    const testDataDir = findRepositoryRoot(process.cwd());
    const resultsBase = path.join(testDataDir, 'test-data', 'results', 'samples', 'echo-m365');
    const xmlResultsDir = path.join(resultsBase, 'xml');
    const waitResultsDir = path.join(resultsBase, 'wait');
    function findRepositoryRoot(startPath) {
        let current = startPath;
        while (current !== path.dirname(current)) {
            if (fs.existsSync(path.join(current, 'test-data'))) {
                return current;
            }
            current = path.dirname(current);
        }
        throw new Error('Could not find repository root with test-data directory');
    }
    function validateXmlIndentation(xmlFile) {
        const content = fs.readFileSync(xmlFile, 'utf-8');
        const lines = content.split('\n');
        const fileName = path.basename(xmlFile);
        lines.forEach((line, index) => {
            if (line.trim().startsWith('<?xml'))
                return;
            if (line.trim() === '')
                return;
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
//# sourceMappingURL=XmlWhitespace.test.js.map