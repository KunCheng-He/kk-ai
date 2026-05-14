const LANGUAGE_PATTERNS = {
  javascript: [
    /\b(const|let|var|function|return|if|else|for|while|class|extends|import|export|from|async|await|try|catch|throw|new|this)\b/,
    /=>/,
    /console\.(log|error|warn|info)/,
    /\b(document|window|Array|Object|String|Number|Boolean|Promise|Map|Set)\b/,
    /require\s*\(/,
    /\.then\s*\(/,
    /\.catch\s*\(/
  ],
  typescript: [
    /\b(interface|type|enum|namespace|implements|declare|abstract|readonly|keyof|infer)\b/,
    /:\s*(string|number|boolean|void|any|never|unknown|object)\b/,
    /<.*>/,
    /\bas\s+(string|number|boolean|any)/,
    /@types\//
  ],
  python: [
    /\b(def|class|if|elif|else|for|while|return|import|from|as|try|except|finally|with|lambda|yield|raise|pass|break|continue)\b/,
    /\bself\b/,
    /\b(print|len|range|str|int|float|list|dict|set|tuple|bool|None|True|False)\b/,
    /:\s*$/,
    /^\s{4}/m,
    /__\w+__/
  ],
  go: [
    /\b(package|import|func|var|const|type|struct|interface|map|chan|go|defer|select|case|default|fallthrough|range|go)\b/,
    /\bfmt\.(Print|Println|Printf|Sprintf)\b/,
    /\bmake\s*\(/,
    /\bgo\s+\w+\s*\(/,
    /:=/,
    /\berror\b/
  ],
  rust: [
    /\b(fn|let|mut|const|static|pub|mod|use|crate|self|super|impl|trait|struct|enum|match|if|else|for|while|loop|break|continue|return|unsafe|async|await)\b/,
    /\bprintln!|print!|format!|vec!|hashmap!/,
    /::\w+/,
    /<.*>/,
    /&mut\s+/,
    /Option|Result|Vec|String|Box/
  ],
  java: [
    /\b(public|private|protected|class|interface|extends|implements|static|final|void|int|long|double|float|boolean|char|byte|short|new|return|if|else|for|while|do|switch|case|break|continue|try|catch|finally|throw|throws|import|package)\b/,
    /\bSystem\.(out|err|in)\b/,
    /\b(String|Integer|Boolean|Double|Float|Long|Object|Class|Exception)\b/,
    /@Override|@Deprecated|@SuppressWarnings/,
    /\bnull\b/
  ],
  c: [
    /\b(int|char|float|double|void|long|short|unsigned|signed|const|static|extern|register|volatile|struct|union|enum|typedef|sizeof|return|if|else|for|while|do|switch|case|break|continue|goto)\b/,
    /\bprintf|scanf|malloc|free|calloc|realloc/,
    /#include\s*<.*>/,
    /#define\s+\w+/,
    /\bNULL\b/,
    /\*\w+/
  ],
  cpp: [
    /\b(class|public|private|protected|virtual|override|friend|namespace|using|template|typename|new|delete|this|operator|const_cast|static_cast|dynamic_cast|reinterpret_cast)\b/,
    /\b(std::|cout|cin|endl|vector|string|map|set|list|queue|stack|pair)\b/,
    /::\w+/,
    /<.*>/,
    /#include\s*<.*>/,
    /\bnullptr\b/
  ],
  css: [
    /^\s*\.[\w-]+\s*\{/m,
    /^\s*#[\w-]+\s*\{/m,
    /^\s*[\w-]+\s*:\s*[\w-]+;/m,
    /@media|@keyframes|@import|@font-face/,
    /\b(px|em|rem|%|vh|vw|deg|s|ms)\b/,
    /rgba?\(|hsl?\(/
  ],
  html: [
    /<(!DOCTYPE|html|head|body|div|span|p|a|img|ul|ol|li|table|tr|td|th|form|input|button|script|style|link|meta|title|header|footer|nav|section|article|aside|main)\b/i,
    /<\/[\w-]+>/i,
    /<[\w-]+[^>]*\/>/i,
    /\bclass\s*=/i,
    /\bid\s*=/i
  ],
  json: [
    /^\s*\{/m,
    /^\s*\[/m,
    /"[\w-]+"\s*:/,
    /:\s*"[^"]*"/,
    /:\s*(true|false|null|\d+)/,
    /^\s*"[\w-]+"\s*:/m
  ],
  yaml: [
    /^[\w-]+:\s*$/m,
    /^[\w-]+:\s+[\w-]+/m,
    /^\s+-\s+/m,
    /^---\s*$/m,
    /^\s{2}[\w-]+:/m,
    /\$\{[\w-]+\}/
  ],
  bash: [
    /^#!/,
    /\b(if|then|else|fi|for|do|done|while|case|esac|function|return|exit|echo|read|export|source|alias|unset)\b/,
    /\$\w+/,
    /\$\{[\w-]+\}/,
    /\|\s*\w+/,
    /&&|\|\|/,
    /\b(git|npm|yarn|pip|python|node|cat|ls|cd|mkdir|rm|cp|mv|chmod|chown|grep|sed|awk|find|curl|wget)\b/
  ],
  sql: [
    /\b(SELECT|FROM|WHERE|JOIN|LEFT|RIGHT|INNER|OUTER|ON|AND|OR|NOT|IN|LIKE|BETWEEN|IS|NULL|AS|ORDER|BY|ASC|DESC|LIMIT|OFFSET|GROUP|HAVING|INSERT|INTO|VALUES|UPDATE|SET|DELETE|CREATE|TABLE|DROP|ALTER|INDEX|VIEW|DATABASE|GRANT|REVOKE)\b/i,
    /\b(INT|VARCHAR|TEXT|BOOLEAN|DATE|DATETIME|TIMESTAMP|FLOAT|DOUBLE|DECIMAL|BIGINT|SMALLINT|CHAR|BLOB)\b/i,
    /;\s*$/m,
    /--.*$/,
    /\/\*[\s\S]*\*\//
  ]
};

const LANGUAGE_PRIORITY = [
  'typescript', 'javascript', 'python', 'rust', 'go', 'java', 
  'cpp', 'c', 'sql', 'bash', 'json', 'yaml', 'css', 'html'
];

function countMatches(code, patterns) {
  let count = 0;
  for (const pattern of patterns) {
    const matches = code.match(pattern);
    if (matches) {
      count += matches.length;
    }
  }
  return count;
}

export function detectLanguage(code) {
  const scores = {};
  
  for (const [lang, patterns] of Object.entries(LANGUAGE_PATTERNS)) {
    scores[lang] = countMatches(code, patterns);
  }
  
  let maxScore = 0;
  let detectedLang = 'text';
  
  for (const lang of LANGUAGE_PRIORITY) {
    if (scores[lang] > maxScore) {
      maxScore = scores[lang];
      detectedLang = lang;
    }
  }
  
  if (maxScore === 0) {
    return 'text';
  }
  
  if (detectedLang === 'javascript' && scores['typescript'] > 0) {
    const tsSpecific = LANGUAGE_PATTERNS.typescript.filter(p => 
      !LANGUAGE_PATTERNS.javascript.some(jp => jp.source === p.source)
    );
    const tsScore = countMatches(code, tsSpecific);
    if (tsScore > 0) {
      return 'typescript';
    }
  }
  
  return detectedLang;
}

export function getSupportedLanguages() {
  return Object.keys(LANGUAGE_PATTERNS);
}
