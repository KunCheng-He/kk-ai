#!/usr/bin/env node

import { program } from 'commander';
import { readFile, mkdir } from 'fs/promises';
import { glob } from 'glob';
import { convertMarkdownToImage, convertCodeToImage, batchConvert, closeBrowser, THEMES, DEFAULT_THEME } from './converter.mjs';
import { detectLanguage } from './detector.mjs';

program
  .name('markdown-to-image')
  .description('Convert Markdown text to beautiful images')
  .version('1.0.0')
  .argument('[input]', 'Input Markdown file (supports glob patterns)')
  .option('-o, --output <path>', 'Output file path or directory (for batch)')
  .option('-t, --theme <theme>', `Theme: ${THEMES.join(', ')} (default: ${DEFAULT_THEME})`, DEFAULT_THEME)
  .option('-f, --format <format>', 'Output format: png, svg', 'png')
  .option('--text <text>', 'Markdown text to convert (instead of file)')
  .option('--code <code>', 'Code snippet to convert (wraps in code block)')
  .option('--lang <lang>', 'Programming language for code highlighting')
  .option('--detect', 'Auto-detect language for code snippets', false)
  .action(async (input, options) => {
    try {
      await run(input, options);
    } catch (error) {
      console.error(`Error: ${error.message}`);
      process.exit(1);
    } finally {
      await closeBrowser();
    }
  });

async function run(input, options) {
  const { text, code, lang, detect, theme, format, output } = options;
  
  if (code) {
    const language = lang || (detect ? detectLanguage(code) : 'text');
    const outputPath = output || `code.${format}`;
    await convertCodeToImage(code, {
      theme,
      format,
      outputPath,
      lang: language
    });
    console.log(`Created: ${outputPath}`);
    return;
  }
  
  if (text) {
    const outputPath = output || `output.${format}`;
    await convertMarkdownToImage(text, {
      theme,
      format,
      outputPath
    });
    console.log(`Created: ${outputPath}`);
    return;
  }
  
  if (!input) {
    program.help();
    return;
  }
  
  const files = await glob(input);
  
  if (files.length === 0) {
    throw new Error(`No files found matching: ${input}`);
  }
  
  if (files.length === 1) {
    const content = await readFile(files[0], 'utf-8');
    const outputPath = output || files[0].replace(/\.md$/, `.${format}`);
    await convertMarkdownToImage(content, {
      theme,
      format,
      outputPath
    });
    console.log(`Created: ${outputPath}`);
    return;
  }
  
  const outputDir = output || '.';
  if (output !== '.') {
    await mkdir(outputDir, { recursive: true });
  }
  
  const results = await batchConvert(files, {
    theme,
    format,
    output: outputDir
  });
  
  for (const result of results) {
    if (result.success) {
      console.log(`Created: ${result.outputPath}`);
    } else {
      console.error(`Failed: ${result.file} - ${result.error}`);
    }
  }
  
  const successCount = results.filter(r => r.success).length;
  console.log(`\nConverted ${successCount}/${results.length} files`);
}

program.parse();
