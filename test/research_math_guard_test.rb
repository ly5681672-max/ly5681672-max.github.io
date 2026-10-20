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

  def test_multiline_boxed_formula_is_delimited_as_a_whole
    source = "\\boxed{\nX_i=-k_{\\mathrm B}T\n\\frac{\\partial\\ln(\\mathrm{TOF})}{\\partial G_i}\n}\n"
    result = ResearchMathGuard.normalize(source)
    assert_equal 1, result.wrapped_count
    assert_equal "$" + "$\n" + source + "$" + "$\n", result.text
    assert_equal result.text, ResearchMathGuard.normalize(result.text).text
  end

  def test_inline_math_delimiters_are_normalized_for_kramdown
    source = "需要注意：直接使用 \\(k_{\\mathrm B}T\\)，不需要直接代入普朗克常数 \\(h\\)。\n"
    result = ResearchMathGuard.normalize(source)
    assert_equal 2, result.wrapped_count
    assert_includes result.text, "$$k_{\\mathrm B}T$$"
    assert_includes result.text, "$$h$$"
    assert_equal result.text, ResearchMathGuard.normalize(result.text).text
  end

  def test_parenthesized_raw_latex_and_scientific_symbol_are_wrapped
    source = "热活化因子 (k_{\\mathrm B}T)，普朗克常数 (h)。\n"
    result = ResearchMathGuard.normalize(source)
    assert_equal 2, result.wrapped_count
    assert_includes result.text, "$$(k_{\\mathrm B}T)$$"
    assert_includes result.text, "$$(h)$$"
  end

  def test_normal_parentheses_and_markdown_link_destinations_are_preserved
    source = "普通说明（例如示例）和英文 (e.g. example)，链接 [文件](notes_v1.md)。\n"
    assert_equal source, ResearchMathGuard.normalize(source).text
  end

  def test_inline_math_is_rendered_by_kramdown
    begin
      require "kramdown"
      require "kramdown-parser-gfm"
    rescue LoadError
      skip "Kramdown is verified in GitHub Actions (bundle exec)"
    end
    source = "直接使用 \\(k_{\\mathrm B}T\\)，常数为 \\(h\\)。\n"
    normalized = ResearchMathGuard.normalize(source).text
    html = Kramdown::Document.new(normalized, input: "GFM").to_html
    assert_includes html, "\\(k_{\\mathrm B}T\\)"
    assert_includes html, "\\(h\\)"
  end

  def test_split_fraction_equation_is_kept_in_one_display_math_block
    source = "公式推导\n\\frac{d\\ln(\\mathrm{TOF})}{d(\\mathrm{TOF})}\n=\\frac{1}{\\mathrm{TOF}}\n"
    result = ResearchMathGuard.normalize(source, source: "_posts/catmap.md")
    equation = "\\frac{d\\ln(\\mathrm{TOF})}{d(\\mathrm{TOF})}\n=\\frac{1}{\\mathrm{TOF}}\n"
    assert_equal 1, result.wrapped_count
    assert_includes result.text, "$$\n#{equation}$$\n"
    assert_equal result.text, ResearchMathGuard.normalize(result.text).text

    begin
      require "kramdown"
      require "kramdown-parser-gfm"
    rescue LoadError
      skip "Kramdown is verified in GitHub Actions (bundle exec)"
    end
    html = Kramdown::Document.new(result.text, input: "GFM").to_html
    assert_match(/\\\[\\frac\{d\\ln\(\\mathrm\{TOF\}\)\}.*?=\\frac\{1\}\{\\mathrm\{TOF\}\}.*?\\\]/m, html)
    refute_match(/<p>\s*=\\frac/, html)
  end

  def test_orphan_equation_continuation_fails_loudly
    error = assert_raises(ResearchMathGuard::FormulaError) do
      ResearchMathGuard.normalize("正文\n=\\frac{1}{\\mathrm{TOF}}\n", source: "demo.md")
    end
    assert_includes error.message, "demo.md:2"
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

  def test_boltzmann_constant_assignment_with_latex_subscript
    source = "k_{\\mathrm B}=8.617333262\\times10^{-5}\\ \\mathrm{eV/K}\n"
    result = ResearchMathGuard.normalize(source)
    assert_equal 1, result.wrapped_count
    assert_equal "$" + "$\n" + source + "$" + "$\n", result.text
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
    expected = source.sub("Here is $\\lambda$ and \\(\\theta\\).") { "Here is $$\\lambda$$ and $$\\theta$$." }
    assert_equal expected, ResearchMathGuard.normalize(source).text
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
