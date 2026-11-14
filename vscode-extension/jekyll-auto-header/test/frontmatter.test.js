const test = require("node:test");
const assert = require("node:assert/strict");
const { createFrontMatter, titleFromFilename, beijingTimestamp } = require("../src/frontmatter");

test("extracts title from a dated filename", () => {
  assert.equal(titleFromFilename("2026-11-14-catmap-08.md"), "catmap-08");
});

test("accepts arbitrary Chinese filename", () => {
  assert.equal(titleFromFilename("OOH吸附能分析.md"), "OOH吸附能分析");
});

test("accepts arbitrary filename without date prefix", () => {
  assert.equal(titleFromFilename("任意名称测试.md"), "任意名称测试");
});

test("uses Asia/Shanghai time with +0800 offset", () => {
  assert.match(beijingTimestamp(new Date("2026-11-14T08:42:03.000Z")), /^2026-11-14 16:42:03 \\+0800$/);
});

test("generates complete front matter", () => {
  assert.equal(
    createFrontMatter("OOH吸附能分析.md", new Date("2026-11-14T08:42:03.000Z")),
    '---\\nlayout: post\\ntitle: "OOH吸附能分析"\\ndate: 2026-11-14 16:42:03 +0800\\n---\\n\\n\\n'
  );
});
