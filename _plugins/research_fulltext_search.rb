# frozen_string_literal: true

# Keep al_search/ninja-keys, but add searchable Markdown sections and location data.
# The site-specific JavaScript provides excerpts and navigates to the exact match.
require "json"
require "cgi"

module ResearchNotesFullTextSearch
  def search_plaintext(source)
    CGI.unescapeHTML(source.to_s)
       .gsub(/!\[[^\]]*\]\([^)]*\)/, " ")
       .gsub(/\[([^\]]+)\]\([^)]*\)/, '\\1')
       .gsub(%r{https?://\S+}, " ")
       .gsub(/<[^>]+>/, " ")
       .gsub(/[\r\n\t]+/, " ")
       .gsub(/`/, "")
       .gsub(/\s+/, " ")
       .strip
  end

  def search_sections(post)
    blocks = []
    heading = "正文"
    lines = []
    flush = lambda do
      text = search_plaintext(lines.join(" "))
      blocks << { title: search_plaintext(heading), text: text } unless text.empty?
    end

    # Jekyll may have already converted post.content to HTML at render time.
    # Restore block boundaries so numbered learning-note items keep their titles.
    source = post.content.to_s
                 .gsub(/<(?:p|h[1-6]|li|br)\b[^>]*>/i, "\n")
                 .gsub(%r{</(?:p|h[1-6]|li)>}i, "\n")
    source.each_line do |line|
      stripped = line.strip
      section_heading = if stripped.match?(/^\#{1,6}\s+\S/)
                          stripped.sub(/^\#{1,6}\s+/, "")
                        elsif stripped.match?(/^\d{1,3}[.、]\s*\S/) && stripped.length <= 160
                          stripped
                        end
      if section_heading
        flush.call
        heading = section_heading
        lines = [stripped] # The heading itself remains searchable.
      else
        lines << stripped
      end
    end
    flush.call
    blocks
  end

  def render(context)
    original = super
    site = context.registers[:site]
    return original if original.empty? || !site || !site.config["posts_in_search"]

    searchable = {}
    site.posts.docs.each do |post|
      title = post.data["title"].to_s.strip
      next if title.empty?

      id = "post-#{Jekyll::Utils.slugify(CGI.escapeHTML(title))}"
      sections = search_sections(post)
      next if sections.empty?

      searchable[id] = {
        title: title,
        url: "#{site.config['baseurl'].to_s.sub(%r{/$}, '')}#{post.url}",
        sections: sections,
        body: sections.map { |section| section[:text] }.join(" ")
      }
    end

    json = JSON.generate(searchable)
               .gsub("<", "\\u003c")
               .gsub(">", "\\u003e")
               .gsub("&", "\\u0026")
               .gsub("\u2028", "\\u2028")
               .gsub("\u2029", "\\u2029")
    baseurl = site.config["baseurl"].to_s.sub(%r{/$}, "")
    original + <<~HTML
      <script>
        (() => {
          const ninja = document.querySelector("ninja-keys");
          const index = #{json};
          window.researchFullTextIndex = index;
          if (!ninja || !Array.isArray(ninja.data)) return;
          ninja.data = ninja.data.map((item) => {
            const post = index[item.id];
            return post ? { ...item, description: [item.description || "", post.body].join(" ").trim() } : item;
          });
        })();
      </script>
      <script defer src="#{baseurl}/assets/js/research-search.js"></script>
    HTML
  end
end

Jekyll::Hooks.register :site, :post_read do |_site|
  if defined?(AlSearch::SearchAssetsTag) &&
     !AlSearch::SearchAssetsTag.ancestors.include?(ResearchNotesFullTextSearch)
    AlSearch::SearchAssetsTag.prepend(ResearchNotesFullTextSearch)
  end
end
