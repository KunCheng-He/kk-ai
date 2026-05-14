import { marked } from 'marked';
import { codeToHtml } from 'shiki';
import puppeteer from 'puppeteer';
import { readFile } from 'fs/promises';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';

const __dirname = dirname(fileURLToPath(import.meta.url));

const THEMES = ['github', 'github-dark', 'notion', 'carbon', 'minimal'];
const DEFAULT_THEME = 'github';
const DEFAULT_WIDTH = 400;
const SHIKI_THEMES = {
  'github': 'github-light',
  'github-dark': 'github-dark',
  'notion': 'github-light',
  'carbon': 'github-dark',
  'minimal': 'github-light'
};

let browser = null;
let highlighter = null;

async function getHighlighter() {
  if (!highlighter) {
    const { createHighlighter } = await import('shiki');
    highlighter = await createHighlighter({
      themes: ['github-light', 'github-dark'],
      langs: ['javascript', 'typescript', 'python', 'go', 'rust', 'java', 'c', 'cpp', 'css', 'html', 'json', 'yaml', 'bash', 'sql', 'markdown', 'jsx', 'tsx']
    });
  }
  return highlighter;
}

async function getBrowser() {
  if (!browser) {
    browser = await puppeteer.launch({
      headless: 'new',
      args: ['--no-sandbox', '--disable-setuid-sandbox']
    });
  }
  return browser;
}

export async function closeBrowser() {
  if (browser) {
    await browser.close();
    browser = null;
  }
}

async function loadTheme(theme) {
  const themePath = join(__dirname, 'themes', `${theme}.css`);
  return readFile(themePath, 'utf-8');
}

async function loadTemplate() {
  const templatePath = join(__dirname, 'templates', 'base.html');
  return readFile(templatePath, 'utf-8');
}

async function highlightCode(code, lang, theme) {
  const hl = await getHighlighter();
  const shikiTheme = SHIKI_THEMES[theme] || 'github-light';
  
  let html;
  try {
    html = await hl.codeToHtml(code, {
      lang: lang || 'text',
      theme: shikiTheme
    });
  } catch {
    html = await hl.codeToHtml(code, {
      lang: 'text',
      theme: shikiTheme
    });
  }
  
  return addLineNumbers(html);
}

function addLineNumbers(html) {
  const preMatch = html.match(/<pre[^>]*>([\s\S]*?)<\/pre>/);
  if (!preMatch) return html;
  
  const preTag = html.match(/<pre[^>]*>/)[0];
  const codeContent = preMatch[1];
  
  const parts = codeContent.split(/<span class="line">/);
  const lines = parts.slice(1);
  const totalLines = lines.length;
  const lineNumberWidth = String(totalLines).length;
  
  let result = preTag + '<code>';
  lines.forEach((line, index) => {
    const lineNum = index + 1;
    const paddedNum = String(lineNum).padStart(lineNumberWidth, ' ');
    const cleanLine = line.replace(/<\/code>$/, '').replace(/<\/span>$/, '');
    result += `<span class="line"><span class="line-number">${paddedNum}</span><span class="line-content">${cleanLine}</span></span>`;
  });
  result += '</code></pre>';
  
  return result;
}

function wrapCodeInWindow(codeHtml, theme) {
  if (theme !== 'carbon') {
    return codeHtml;
  }
  
  return `<div class="code-window">
  <div class="code-window-header">
    <span class="code-window-dot red"></span>
    <span class="code-window-dot yellow"></span>
    <span class="code-window-dot green"></span>
  </div>
  <div class="code-window-body">
    ${codeHtml}
  </div>
</div>`;
}

async function renderMarkdown(markdown, options = {}) {
  const { theme = DEFAULT_THEME, codeLang } = options;
  
  const renderer = new marked.Renderer();
  const originalCode = renderer.code.bind(renderer);
  
  renderer.code = async function({ text, lang }) {
    const language = lang || codeLang;
    const highlighted = await highlightCode(text, language, theme);
    return wrapCodeInWindow(highlighted, theme);
  };
  
  marked.setOptions({ renderer });
  
  const tokens = marked.lexer(markdown);
  const htmlParts = [];
  
  for (const token of tokens) {
    if (token.type === 'code') {
      const highlighted = await highlightCode(token.text, token.lang || codeLang, theme);
      htmlParts.push(wrapCodeInWindow(highlighted, theme));
    } else {
      htmlParts.push(marked.parser([token]));
    }
  }
  
  return htmlParts.join('\n');
}

async function buildHtml(content, theme) {
  const [template, themeCss] = await Promise.all([
    loadTemplate(),
    loadTheme(theme)
  ]);
  
  return template
    .replace(/\{\{content\}\}/g, content)
    .replace(/\{\{theme\}\}/g, theme)
    .replace(/\{\{theme_css\}\}/g, themeCss);
}

async function captureScreenshot(html, options = {}) {
  const { format = 'png', outputPath, scale = 2 } = options;
  const browser = await getBrowser();
  const page = await browser.newPage();
  
  try {
    await page.setViewport({ width: 1200, height: 100, deviceScaleFactor: scale });
    await page.setContent(html, { waitUntil: 'networkidle0' });
    
    const container = await page.$('.container');
    const boundingBox = await container.boundingBox();
    
    const contentWidth = Math.ceil(boundingBox.width);
    const contentHeight = Math.ceil(boundingBox.height);
    
    await page.setViewport({ 
      width: Math.max(100, contentWidth + 32), 
      height: Math.max(100, contentHeight + 32), 
      deviceScaleFactor: scale 
    });
    
    const screenshotOptions = {
      path: outputPath,
      type: format,
      clip: {
        x: boundingBox.x,
        y: boundingBox.y,
        width: contentWidth,
        height: contentHeight
      },
      fullPage: false
    };
    
    if (format === 'png') {
      screenshotOptions.omitBackground = true;
    }
    
    await page.screenshot(screenshotOptions);
    
    return outputPath;
  } finally {
    await page.close();
  }
}

export async function convertMarkdownToImage(markdown, options = {}) {
  const {
    theme = DEFAULT_THEME,
    format = 'png',
    outputPath
  } = options;
  
  if (!THEMES.includes(theme)) {
    throw new Error(`Unknown theme: ${theme}. Available themes: ${THEMES.join(', ')}`);
  }
  
  const html = await renderMarkdown(markdown, { theme });
  const fullHtml = await buildHtml(html, theme);
  
  return captureScreenshot(fullHtml, { format, outputPath });
}

export async function convertCodeToImage(code, options = {}) {
  const {
    theme = DEFAULT_THEME,
    format = 'png',
    outputPath,
    lang
  } = options;
  
  const language = lang || 'text';
  const highlighted = await highlightCode(code, language, theme);
  const wrapped = wrapCodeInWindow(highlighted, theme);
  const fullHtml = await buildHtml(wrapped, theme);
  
  return captureScreenshot(fullHtml, { format, outputPath });
}

export async function batchConvert(files, options = {}) {
  const results = [];
  
  for (const file of files) {
    try {
      const content = await readFile(file, 'utf-8');
      const outputPath = file.replace(/\.md$/, `.${options.format || 'png'}`);
      await convertMarkdownToImage(content, { ...options, outputPath });
      results.push({ file, success: true, outputPath });
    } catch (error) {
      results.push({ file, success: false, error: error.message });
    }
  }
  
  return results;
}

export { THEMES, DEFAULT_THEME, DEFAULT_WIDTH };
