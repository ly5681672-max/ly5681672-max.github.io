# frozen_string_literal: true

# Turn pasted [https://...] text into a clickable link after Markdown renders.
# This affects only blog posts and never rewrites the Markdown source.
require "nokogiri"

module ResearchAutoLinks
  BRACKETED_URL = /\[(https?:\/\/[^\]\s<>]+)\]/
  CONTENT_TAGS = %w[p li blockquote td th figcaption].freeze
  SKIP_TAGS = %w[a code pre script style kbd samp].freeze

  def self.convert(html)
    return html unless html.match?(/\[https?:\/\//)

    fragment = Nokogiri::HTML.fragment(html)
    fragment.xpath(".//text()").each do |node|
      value = node.text
      next unless value.match?(BRACKETED_URL)

      ancestors = node.ancestors.map(&:name)
      next if (ancestors & CONTENT_TAGS).empty?
      next unless (ancestors & SKIP_TAGS).empty?

      cursor = 0
      value.to_enum(:scan, BRACKETED_URL).each do
        match = Regexp.last_match
        prefix = value[cursor...match.begin(0)]
        node.add_previous_sibling(Nokogiri::XML::Text.new(prefix, node.document)) unless prefix.empty?

        link = Nokogiri::XML::Node.new("a", node.document)
        link["href"] = match[1]
        link.content = match[1]
        node.add_previous_sibling(link)

        cursor = match.end(0)
      end

      suffix = value[cursor..]
      node.add_previous_sibling(Nokogiri::XML::Text.new(suffix, node.document)) unless suffix.empty?
      node.remove
    end

    fragment.to_html
  end
end

Jekyll::Hooks.register :posts, :post_convert do |post|
  post.content = ResearchAutoLinks.convert(post.content)
end
