# frozen_string_literal: true

require "minitest/autorun"
begin
  require "jekyll"
rescue LoadError
  # Plain-Ruby local tests remain available; CI installs Jekyll.
end
require_relative "../_plugins/research_math_guard"

class ResearchMathGuardTest < Minitest::Test
  BOXED = '\\boxed{\\tau=\\frac{1}{|\\lambda|}}'

  def test_bare_boxed_formula_is_delimited_before_markdown_table_parsing
    result = ResearchMathGuard.normalize("松弛时间：\n\n#{BOXED}\n\n下一段。\n")
    assert_equal 1, result.wrapped_count
    assert_includes result.text, "\n$$\n#{BOXED}\n$$\n"
    assert_includes result.text, "下一段。"
    assert_equal result.text, ResearchMathGuard.normalize(result.text).text
  end

  def test_bare_fraction_standalone
    source = "\\frac{d\\theta}{dt}\n"
    assert_equal "$$\n#{source}$$\n", ResearchMathGuard.normalize(source).text
  end

  def test_standalone_math_variable_equation
    source = "\\theta_R+\\theta_P+\\theta_*=1\n"
    assert_equal "$$\n#{source}$$\n", ResearchMathGuard.normalize(source).text
  end

  def test_variable_assignment_with_fraction
    source = "J=\\frac{d\\theta}{dt}\n"
    assert_equal "$$\n#{source}$$\n", ResearchMathGuard.normalize(source).text
  end

  def test_aligned_environment_is_wrapped_as_a_whole
    source = "\\begin{aligned}\na &= b \\\\\nc &= d\n\\end{aligned}\n"
    result = ResearchMathGuard.normalize(source)
    assert_equal 1, result.wrapped_count
    assert_equal "$$\n#{source}$$\n", result.text
  end

  def test_preserve_explicit_math_fenced_code_and_inline_code
    source = <<~MD
      $$
      #{BOXED}
      $$
      ```latex
      #{BOXED}
      ```
      ~~~math
      #{BOXED}
      ~~~
      `#{BOXED}`
      Here is $\\lambda$ and \\(\\theta\\).
    MD
    assert_equal source, ResearchMathGuard.normalize(source).text
  end

  def test_preserve_indented_code_html_code_and_plain_text
    source = "    #{BOXED}\n<pre>\n#{BOXED}\n</pre>\n说明 \\boxed{a} 的语法。\n"
    assert_equal source, ResearchMathGuard.normalize(source).text
  end

  def test_preserve_liquid_code_block
    source = "{% highlight latex %}\n#{BOXED}\n{% endhighlight %}\n"
    assert_equal source, ResearchMathGuard.normalize(source).text
  end

  def test_ambiguous_prose_and_latex_fails_without_rewriting
    assert_raises(ResearchMathGuard::FormulaError) do
      ResearchMathGuard.normalize("\\boxed{x} 后面是解释。\n")
    end
  end

  def test_unclosed_display_math_delimiter_fails
    assert_raises(ResearchMathGuard::FormulaError) do
      ResearchMathGuard.normalize("$$\n\\frac{1}{2}\n")
    end
  end

  def test_invalid_strong_formula_fails_loudly
    error = assert_raises(ResearchMathGuard::FormulaError) do
      ResearchMathGuard.normalize("\\boxed{\\frac{1}{|\\lambda|}\n", source: "demo.md")
    end
    assert_includes error.message, "demo.md:1"
  end

  def test_incomplete_environment_fails_loudly
    assert_raises(ResearchMathGuard::FormulaError) do
      ResearchMathGuard.normalize("\\begin{aligned}\na &= b\n")
    end
  end

  def test_jekyll_markdown_math_and_hook
    begin
      require "kramdown"
      require "kramdown-parser-gfm"
    rescue LoadError
      skip "Jekyll and Kramdown are verified in GitHub Actions (bundle exec)"
    end
    post = Struct.new(:content, :relative_path, :path).new("#{BOXED}\n", "_posts/demo.md", "_posts/demo.md")
    Jekyll::Hooks.trigger(:posts, :pre_render, post)
    html = Kramdown::Document.new(post.content, input: "GFM").to_html
    assert_includes html, "\\[#{BOXED}\\]"
    refute_match(/<table[\s>]/, html)
    assert_equal 1, post.content.scan(/^\$\$$/).length / 2
  end
end
