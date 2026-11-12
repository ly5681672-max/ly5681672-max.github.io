# frozen_string_literal: true

# Extend the existing al_search/ninja-keys index with Markdown body text.
# No changes to posts, pagination, or the upstream gem are required.
require "json"
require "cgi"

module ResearchNotesFullTextSearch
  MAX_BODY_CHARS = 20_000

  def render(context)
    original = super
    site = context.registers[:site]
    return original if original.empty? || !site || !site.config["posts_in_search"]

    searchable = {}
    site.posts.docs.each do |post|
      title = post.data["title"].to_s.strip
      next if title.empty?

      id = "post-#{Jekyll::Utils.slugify(CGI.escapeHTML(title))}"
      # Markdown source is sufficient for keyword matching, including Chinese.
      body = post.content.to_s
                 .gsub(/!\[[^\]]*\]\([^)]*\)/, " ")
                 .gsub(/\[([^\]]+)\]\([^)]*\)/, '\\1')
                 .gsub(/<[^>]+>/, " ")
                 .gsub(/[\r\n\t]+/, " ")
                 .gsub(/\s+/, " ")
                 .strip
                 .slice(0, MAX_BODY_CHARS)
      searchable[id] = body unless body.empty?
    end

    json = JSON.generate(searchable)
               .gsub("<", "\\u003c")
               .gsub(">", "\\u003e")
               .gsub("&", "\\u0026")
    original + <<~HTML
      <script>
        (() => {
          const ninja = document.querySelector("ninja-keys");
          if (!ninja || !Array.isArray(ninja.data)) return;
          const bodies = #{json};
          ninja.data = ninja.data.map((item) => {
            const body = bodies[item.id];
            return body ? { ...item, description: [item.description || "", body].join(" ").trim() } : item;
          });
        })();
      </script>
    HTML
  end
end

Jekyll::Hooks.register :site, :post_read do |_site|
  if defined?(AlSearch::SearchAssetsTag) &&
     !AlSearch::SearchAssetsTag.ancestors.include?(ResearchNotesFullTextSearch)
    AlSearch::SearchAssetsTag.prepend(ResearchNotesFullTextSearch)
  end
end
