# frozen_string_literal: true

# Turn pasted plain https://... and [https://...] into clickable links after Markdown renders.
# This affects only blog posts and never rewrites the Markdown source.
require "nokogiri"

module ResearchAutoLinks
  LINK_CANDIDATE = /\[(https?:\/\/[^\]\s<>]+)\]|https?:\/\/[^\s<>"'，。！？；：、【】《》“”‘’]+/
  TRAILING_PUNCTUATION = /[.,!?;:，。！？；：、]/
  CONTENT_TAGS = %w[p li blockquote td th figcaption].freeze
  SKIP_TAGS = %w[a code pre script style kbd samp].freeze

  def self.convert(html)
    return html unless html.match?(%r{https?://})

    fragment = Nokogiri::HTML.fragment(html)
    changed = false
    fragment.xpath(".//text()").each do |node|
      value = node.text
      next unless value.match?(LINK_CANDIDATE)

      ancestors = node.ancestors.map(&:name)
      next if (ancestors & CONTENT_TAGS).empty?
      next unless (ancestors & SKIP_TAGS).empty?

      cursor = 0
      value.to_enum(:scan, LINK_CANDIDATE).each do
        match = Regexp.last_match
        prefix = value[cursor...match.begin(0)]
        node.add_previous_sibling(Nokogiri::XML::Text.new(prefix, node.document)) unless prefix.empty?

        url = match[1] || match[0]
        trailing = String.new
        unless match[1]
          while !url.empty? &&
                (url[-1].match?(TRAILING_PUNCTUATION) ||
                 (url.end_with?(")") && url.count(")") > url.count("(")) ||
                 (url.end_with?("]") && url.count("]") > url.count("[")) ||
                 (url.end_with?("}") && url.count("}") > url.count("{")))
            trailing.prepend(url[-1])
            url = url[0...-1]
          end
        end

        link = Nokogiri::XML::Node.new("a", node.document)
        link["href"] = url
        link.content = url
        node.add_previous_sibling(link)
        node.add_previous_sibling(Nokogiri::XML::Text.new(trailing, node.document)) unless trailing.empty?
        changed = true
        cursor = match.end(0)
      end

      suffix = value[cursor..]
      node.add_previous_sibling(Nokogiri::XML::Text.new(suffix, node.document)) unless suffix.empty?
      node.remove
    end

    changed ? fragment.to_html : html
  end
end

Jekyll::Hooks.register :posts, :post_convert do |post|
  post.content = ResearchAutoLinks.convert(post.content)
end
