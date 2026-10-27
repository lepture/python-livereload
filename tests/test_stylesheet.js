// Run with `node tests/test_stylesheet.js`.
const assert = require('assert');
const fs = require('fs');
const path = require('path');
const vm = require('vm');

// Load the shipped Browserify modules without starting its WebSocket client.
const source = fs.readFileSync(path.join(__dirname, '../livereload/vendors/livereload.js'), 'utf8');
const load = vm.runInNewContext(source.replace('[8]);', '[]);'), {
  CSSRule: { CHARSET_RULE: 2, IMPORT_RULE: 3 }
});
const Reloader = load(7).Reloader;
const requests = [];
const callbacks = [];
const sheets = [];
const parent = {
  insertBefore(link) { requests.push(link.href); }
};
const links = ['first', 'second'].map(name => {
  const sheet = {
    href: 'http://example.test/' + name + '/style.css',
    cssRules: [],
    insertRule(text, index) { this.cssRules.splice(index, 0, { media: [] }); },
    deleteRule(index) { this.cssRules.splice(index, 1); }
  };
  const imported = { href: 'http://example.test/' + name + '/import.css?v=1#part', cssRules: [] };
  const rule = { type: 3, href: 'import.css?v=1#part', styleSheet: imported, parentStyleSheet: sheet, media: [] };
  sheet.cssRules.push(rule);
  sheets.push(sheet);
  return { rel: 'stylesheet', href: sheet.href, sheet, parentNode: parent };
});
const document = {
  getElementsByTagName(tag) { return tag === 'link' ? links : []; },
  createElement() { return {}; }
};
const reloader = new Reloader({ document }, { log() {} }, {
  start(delay, callback) { callbacks.push(callback); }
});
reloader.reload('/second/import.css', { liveCSS: true });
assert.strictEqual(requests.length, 1);
const requested = new URL(requests[0], 'http://example.test/page.html');
assert.strictEqual(requested.pathname, '/second/import.css');
assert.strictEqual(requested.searchParams.get('v'), '1');
assert.ok(requested.searchParams.has('livereload'));
assert.strictEqual(requested.hash, '#part');
callbacks.shift()();
assert.strictEqual(sheets[0].cssRules.length, 1);
assert.strictEqual(sheets[0].cssRules[0].href, 'import.css?v=1#part');
callbacks.shift()();
console.log('Imported stylesheet matching and prefetch URL regression passed');
