function beijingTimestamp(now = new Date()) {
  const parts = new Intl.DateTimeFormat("en-CA", {
    timeZone: "Asia/Shanghai",
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
    hourCycle: "h23",
  }).formatToParts(now);
  const values = Object.fromEntries(parts.map((part) => [part.type, part.value]));
  return `${values.year}-${values.month}-${values.day} ${values.hour}:${values.minute}:${values.second} +0800`;
}

function titleFromFilename(filename) {
  const withoutExtension = filename.replace(/\.md$/i, "");
  return withoutExtension.replace(/^\d{4}-\d{2}-\d{2}-/, "");
}

function yamlQuote(value) {
  return `"${value.replace(/\\/g, "\\\\").replace(/"/g, '\\"')}"`;
}

function createFrontMatter(filename, now = new Date()) {
  const title = titleFromFilename(filename);
  return [
    "---",
    "layout: post",
    `title: ${yamlQuote(title)}`,
    `date: ${beijingTimestamp(now)}`,
    "---",
    "",
    "",
  ].join("\n");
}

module.exports = { beijingTimestamp, titleFromFilename, createFrontMatter };
