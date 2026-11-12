/* Site-only enhancement for al_search 1.0.3. Keeps ninja-keys navigation and keyboard shortcuts. */
(() => {
  "use strict";

  const SEARCH_PARAM = "search_hit";
  const BEFORE_PARAM = "search_before";
  const AFTER_PARAM = "search_after";
  const MAX_HITS_PER_POST = 12;
  const CONTEXT_CHARS = 45;
  const normal = (value) =>
    String(value || "")
      .replace(/\s+/g, "")
      .toLocaleLowerCase();
  // ninja-action renders titles as HTML; never pass untrusted Markdown markup to it.
  const safeText = (value) =>
    String(value || "")
      .replace(/[<>&]/g, " ")
      .replace(/[\r\t]/g, " ");

  function findHits(entry, keyword) {
    const hits = [];
    const needle = keyword.toLocaleLowerCase();
    let globalOrdinal = 0;
    for (const section of entry.sections || []) {
      const body = section.text || "";
      const lower = body.toLocaleLowerCase();
      let from = 0;
      while (from < body.length) {
        const pos = lower.indexOf(needle, from);
        if (pos < 0) break;
        const before = body.slice(Math.max(0, pos - CONTEXT_CHARS), pos);
        const after = body.slice(pos + keyword.length, pos + keyword.length + CONTEXT_CHARS);
        const snippet = `${pos > CONTEXT_CHARS ? "…" : ""}${before}${body.slice(pos, pos + keyword.length)}${after}${pos + keyword.length + CONTEXT_CHARS < body.length ? "…" : ""}`;
        hits.push({ section: section.title || "正文", snippet: safeText(snippet), before, after, ordinal: globalOrdinal++ });
        from = pos + Math.max(needle.length, 1);
      }
    }
    return hits;
  }

  function buildTargetUrl(url, query, hit) {
    const target = new URL(url, window.location.href);
    target.searchParams.set(SEARCH_PARAM, query);
    target.searchParams.set(BEFORE_PARAM, normal(hit.before).slice(-24));
    target.searchParams.set(AFTER_PARAM, normal(hit.after).slice(0, 24));
    target.searchParams.set("search_ordinal", String(hit.ordinal));
    return target.href;
  }

  async function setupSearchResults() {
    const ninja = document.querySelector("ninja-keys");
    const index = window.researchFullTextIndex;
    if (!ninja || !index || !Object.keys(index).length) return;
    if (!window.customElements || !window.customElements.whenDefined) return;
    await customElements.whenDefined("ninja-keys");
    await ninja.updateComplete;
    const root = ninja.shadowRoot;
    const header = root?.querySelector("ninja-header");
    if (!header) return;

    const original = ninja.data.slice();
    ninja.placeholder = "搜索文章标题或正文关键词";

    function update(query) {
      const keyword = String(query || "").trim();
      if (!keyword) {
        ninja.data = original;
        return;
      }
      const results = [];
      for (const item of original) {
        const entry = index[item.id];
        if (!entry) {
          results.push(item); // Preserve navigation, news, theme and social commands.
          continue;
        }
        const hits = findHits(entry, keyword);
        if (!hits.length) {
          results.push(item); // Preserve title-only and fuzzy matches.
          continue;
        }
        for (const hit of hits.slice(0, MAX_HITS_PER_POST)) {
          results.push({
            ...item,
            id: `${item.id}-hit-${hit.ordinal}`,
            title: `${safeText(entry.title)}\n${safeText(hit.section)} · ${hit.snippet}`,
            // Retain the upstream full-text ranking path for Ninja Keys.
            description: item.description,
            handler: () => {
              window.location.href = buildTargetUrl(entry.url, keyword, hit);
            },
          });
        }
        if (hits.length > MAX_HITS_PER_POST) {
          const hit = hits[MAX_HITS_PER_POST];
          results.push({
            ...item,
            id: `${item.id}-more`,
            title: `${safeText(entry.title)}\n另有 ${hits.length - MAX_HITS_PER_POST} 处匹配，点击进入下一处`,
            description: item.description,
            handler: () => {
              window.location.href = buildTargetUrl(entry.url, keyword, hit);
            },
          });
        }
      }
      ninja.data = results;
      // The native component draws each row in an isolated shadow root.
      // Make the existing title support a second line instead of ellipsizing it.
      void ninja.updateComplete.then(formatRows);
    }

    function formatRows() {
      for (const action of root.querySelectorAll("ninja-action")) {
        void action.updateComplete.then(() => {
          const title = action.shadowRoot?.querySelector(".ninja-title");
          if (title && !title.dataset.researchWrap) {
            title.dataset.researchWrap = "1";
            title.style.whiteSpace = "pre-line";
            title.style.overflowWrap = "anywhere";
            title.style.textOverflow = "clip";
          }
        });
      }
    }
    header.addEventListener("change", (event) => update(event.detail?.search));
    const watcher = new MutationObserver(formatRows);
    watcher.observe(root, { childList: true, subtree: true });
    formatRows();
  }

  function getVisibleArticleText(root) {
    const walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT, {
      acceptNode(node) {
        const parent = node.parentElement;
        if (!parent || !node.nodeValue.trim()) return NodeFilter.FILTER_REJECT;
        if (parent.closest("script, style, noscript, nav, footer, textarea, svg, .MathJax, .mjx-container")) {
          return NodeFilter.FILTER_REJECT;
        }
        return NodeFilter.FILTER_ACCEPT;
      },
    });
    const parts = [];
    let fullText = "";
    while (walker.nextNode()) {
      const node = walker.currentNode;
      parts.push({ node, from: fullText.length, to: fullText.length + node.nodeValue.length });
      fullText += node.nodeValue;
    }
    return { fullText, parts };
  }

  function commonSuffixLength(a, b) {
    let i = 0;
    while (i < a.length && i < b.length && a[a.length - 1 - i] === b[b.length - 1 - i]) i++;
    return i;
  }
  function commonPrefixLength(a, b) {
    let i = 0;
    while (i < a.length && i < b.length && a[i] === b[i]) i++;
    return i;
  }

  function chooseMatch(text, query, before, after, ordinal) {
    const lower = text.toLocaleLowerCase();
    const needle = query.toLocaleLowerCase();
    const matches = [];
    let at = 0;
    while (at < text.length) {
      at = lower.indexOf(needle, at);
      if (at < 0) break;
      const preceding = normal(text.slice(Math.max(0, at - 150), at)).slice(-before.length);
      const following = normal(text.slice(at + query.length, at + query.length + 150)).slice(0, after.length);
      const score = commonSuffixLength(preceding, before) + commonPrefixLength(following, after);
      matches.push({ at, score, index: matches.length });
      at += Math.max(needle.length, 1);
    }
    if (!matches.length) return -1;
    const ordinalIndex = Number.isInteger(ordinal) && ordinal >= 0 && ordinal < matches.length ? ordinal : 0;
    if (!before && !after) return matches[ordinalIndex].at;
    matches.sort((a, b) => b.score - a.score || Math.abs(a.index - ordinalIndex) - Math.abs(b.index - ordinalIndex));
    return matches[0].at;
  }

  function showTargetHighlight() {
    const params = new URLSearchParams(window.location.search);
    const query = params.get(SEARCH_PARAM);
    if (!query || query.length > 120) return;
    const article = document.querySelector("article") || document.querySelector("main");
    if (!article) return;
    const { fullText, parts } = getVisibleArticleText(article);
    const before = params.get(BEFORE_PARAM) || "";
    const after = params.get(AFTER_PARAM) || "";
    const ordinal = Number.parseInt(params.get("search_ordinal") || "0", 10);
    const offset = chooseMatch(fullText, query, before, after, ordinal);
    if (offset < 0) return;
    const start = parts.find((part) => part.from <= offset && offset < part.to);
    const endOffset = offset + query.length - 1;
    const end = parts.find((part) => part.from <= endOffset && endOffset < part.to);
    if (!start || !end) return;
    const range = document.createRange();
    range.setStart(start.node, offset - start.from);
    range.setEnd(end.node, endOffset - end.from + 1);
    const style = document.createElement("style");
    style.textContent =
      "::highlight(research-search-hit) { background: #ffdf5a; color: #171717; } mark.research-search-hit { background: #ffdf5a; color: #171717; }";
    document.head.appendChild(style);
    if (window.CSS?.highlights && window.Highlight) {
      CSS.highlights.set("research-search-hit", new Highlight(range));
    } else if (start.node === end.node) {
      const mark = document.createElement("mark");
      mark.className = "research-search-hit";
      range.surroundContents(mark);
    }
    const target = start.node.parentElement;
    if (target) {
      requestAnimationFrame(() => target.scrollIntoView({ block: "center", behavior: "smooth" }));
    }
  }

  void setupSearchResults();
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", showTargetHighlight, { once: true });
  } else {
    showTargetHighlight();
  }
})();
