# frozen_string_literal: true

require "minitest/autorun"
require "jekyll"
require "nokogiri"
require_relative "../_plugins/research_auto_links"

class ResearchAutoLinksTest < Minitest::Test
  def html_for(value)
    Nokogiri::HTML.fragment(ResearchAutoLinks.convert(value))
  end

  def test_plain_pasted_url_becomes_a_link
    html = html_for("<p>https://chatgpt.com/s/t_example</p>")
    link = html.at_css("p > a")
    refute_nil link
    assert_equal "https://chatgpt.com/s/t_example", link["href"]
    assert_equal "https://chatgpt.com/s/t_example", link.text
  end

  def test_bracketed_link_keeps_legacy_behavior
    html = html_for("<p>[https://example.org/note]</p>")
    assert_equal "https://example.org/note", html.at_css("a")["href"]
    assert_equal "https://example.org/note", html.at_css("a").text
  end

  def test_multiple_links_preserve_surrounding_text
    html = html_for("<p>来源：https://example.org/one 及 http://example.com/two。</p>")
    assert_equal ["https://example.org/one", "http://example.com/two"], html.css("a").map { |link| link["href"] }
    assert_includes html.text, "来源："
    assert_includes html.text, "。"
    assert_equal "http://example.com/two", html.css("a").last.text
  end

  def test_punctuation_is_not_included_in_href
    html = html_for("<p>(https://example.org/docs?q=1&amp;lang=zh), 下一条。</p>")
    assert_equal "https://example.org/docs?q=1&lang=zh", html.at_css("a")["href"]
    assert_match(/\), 下一条。/, html.text)
  end

  def test_balanced_parentheses_in_valid_url_are_preserved
    url = "https://en.wikipedia.org/wiki/Function_(mathematics)"
    html = html_for("<p>#{url}.</p>")
    assert_equal url, html.at_css("a")["href"]
    assert_match(/\.$/, html.text)
  end

  def test_existing_markdown_anchor_and_code_are_not_changed
    fragment = '<p><a href="https://example.org/already">已有链接</a> ' \
               '<code>https://example.org/code</code></p><pre><code>https://example.org/pre</code></pre>'
    result = ResearchAutoLinks.convert(fragment)
    doc = Nokogiri::HTML.fragment(result)
    assert_equal ["https://example.org/already"], doc.css("a").map { |link| link["href"] }
    assert_equal "https://example.org/code", doc.at_css("p code").text
    assert_equal "https://example.org/pre", doc.at_css("pre code").text
  end

  def test_already_linked_url_is_idempotent
    once = ResearchAutoLinks.convert("<p>https://example.org/hi</p>")
    twice = ResearchAutoLinks.convert(once)
    assert_equal once, twice
    assert_equal 1, Nokogiri::HTML.fragment(twice).css("a").length
  end

  def test_do_not_change_code_only_fragment
    source = "<pre><code>https://example.org/code</code></pre>"
    assert_equal source, ResearchAutoLinks.convert(source)
  end

  def test_do_not_rewrite_math_or_image_alt_content
    source = '<p><img src="/a.png" alt="https://example.org/image"></p>'
    assert_equal source, ResearchAutoLinks.convert(source)
  end

  def test_unsafe_schemes_remain_text
    source = "<p>javascript:alert(1) mailto:hi@example.org</p>"
    assert_equal source, ResearchAutoLinks.convert(source)
  end

  def test_jekyll_hook_converts_plain_url_from_real_post
    post = Struct.new(:content).new("<p>https://chatgpt.com/s/t_demo</p>")
    Jekyll::Hooks.trigger(:posts, :post_convert, post)
    assert_equal "https://chatgpt.com/s/t_demo", Nokogiri::HTML.fragment(post.content).at_css("a")["href"]
  end
end
