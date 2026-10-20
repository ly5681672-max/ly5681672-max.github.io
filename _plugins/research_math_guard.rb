# frozen_string_literal: true

# Normalizes unambiguously standalone LaTeX in blog posts before Markdown
# rendering. Source .md files remain unchanged; already delimited equations,
# inline math, code fences, and inline code are preserved verbatim.
module ResearchMathGuard
  class FormulaError < StandardError; end

  Result = Struct.new(:text, :wrapped_count, keyword_init: true)
  MATH_ENVIRONMENTS = %w[aligned alignedat gathered cases split matrix pmatrix bmatrix Bmatrix vmatrix Vmatrix array].freeze
  BARE_COMMAND = /\A\\(?:boxed|frac|dfrac|tfrac)\s*\{/
  MATH_VARIABLE = /\A\\(?:theta|Delta|lambda|tau|sum|prod|alpha|beta|gamma|omega|mu|sigma|rho|partial|nabla|dot|mathrm|text)(?=[^A-Za-z]|$)/
  MATH_OPERATOR = /(?:=|\\(?:leq|geq|approx|simeq|propto|equiv|to|rightarrow)\b)/
  ASSIGNMENT = /\A[A-Za-z][A-Za-z0-9_{}^*\\ ]*\s*=\s*.*\\(?:frac|dfrac|tfrac|mathrm|theta|Delta|lambda|partial|times)\b/
  ENV_START = /\A\\begin\{([A-Za-z]+\*?)\}/
  FENCE = /\A {0,3}([`~])\1{2,}/
  HTML_CODE_START = /<(pre|code|script|style)\b/i
  LIQUID_CODE_START = /\{%\s*(highlight|raw|comment)\b/

  module_function

  def normalize(markdown, source: "post")
    lines = markdown.lines
    out = []
    converted = 0
    fence = nil
    math_delim = nil
    html_code = nil
    liquid_code = nil
    index = 0

    while index < lines.length
      line = lines[index]
      stripped = line.strip

      if fence
        fence = nil if stripped.match?(/\A#{Regexp.escape(fence[0])}{#{fence.length},}\s*\z/)
        out << line
        index += 1
        next
      end

      if (match = line.match(FENCE))
        fence = match[0].strip[/\A[`~]+/]
        out << line
        index += 1
        next
      end

      if liquid_code
        liquid_code = nil if line.match?(/\{%\s*end#{Regexp.escape(liquid_code)}\s*%\}/)
        out << line
        index += 1
        next
      end
      if (match = line.match(LIQUID_CODE_START))
        liquid_code = match[1] unless line.match?(/\{%\s*end#{Regexp.escape(match[1])}\s*%\}/)
        out << line
        index += 1
        next
      end

      if html_code
        html_code = nil if line.match?(%r{</#{html_code}\s*>}i)
        out << line
        index += 1
        next
      end
      if (match = line.match(HTML_CODE_START))
        html_code = match[1] unless line.match?(%r{</#{match[1]}\s*>}i)
        out << line
        index += 1
        next
      end

      # Respect explicit block math, including internal align/gather/cases.
      if math_delim
        math_delim = nil if stripped == math_delim
        out << line
        index += 1
        next
      end
      if stripped == '$$' || stripped == '\\['
        math_delim = stripped == '$$' ? '$$' : '\\]'
        out << line
        index += 1
        next
      end

      # Indented Markdown code, inline math and prose are never rewritten.
      if line.match?(/\A(?: {4}|\t)/) || stripped.empty? ||
         stripped.start_with?('\\[', '`') ||
         stripped.include?('`')
        out << line
        index += 1
        next
      end

      if (start = stripped.match(ENV_START)) && MATH_ENVIRONMENTS.include?(start[1])
        env = start[1]
        ending = /\\end\{#{Regexp.escape(env)}\}/
        last = index
        last += 1 until last >= lines.length || lines[last].match?(ending)
        if last >= lines.length
          raise FormulaError, "#{source}:#{index + 1}: unmatched \\begin{#{env}}; no automatic modification"
        end
        block = lines[index..last]
        validate_braces!(block.join, source, index + 1)
        append_display(out, block, lines, last)
        converted += 1
        index = last + 1
        next
      end

      strong = stripped.match?(BARE_COMMAND)
      if strong
        if stripped.match?(/\p{Han}/)
          raise FormulaError, "#{source}:#{index + 1}: ambiguous LaTeX mixed with prose; add explicit math delimiters"
        end
        last = balanced_block_end(lines, index, source)
        block = lines[index..last]
        if block.join.match?(/\p{Han}/)
          raise FormulaError, "#{source}:#{index + 1}: ambiguous LaTeX mixed with prose; add explicit math delimiters"
        end
        validate_braces!(block.join, source, index + 1)
        append_display(out, block, lines, last)
        converted += 1
        index = last + 1
        next
      end

      variable = stripped.match?(MATH_VARIABLE) && stripped.match?(MATH_OPERATOR)
      assignment = stripped.match?(ASSIGNMENT) && !stripped.match?(/\p{Han}/)
      if variable || assignment
        if stripped.match?(/\p{Han}/)
          raise FormulaError, "#{source}:#{index + 1}: ambiguous LaTeX mixed with prose; add explicit math delimiters"
        end
        validate_braces!(stripped, source, index + 1)
        append_display(out, [line], lines, index)
        converted += 1
      else
        normalized_line, inline_count = normalize_inline_math(line)
        out << normalized_line
        converted += inline_count
      end
      index += 1
    end

    raise FormulaError, "#{source}: missing closing math delimiter #{math_delim}" if math_delim

    Result.new(text: out.join, wrapped_count: converted)
  end

  DOLLAR_MATH = /(\$\$.*?\$\$|\$(?:\\.|[^$\n])+\$)/

  # Kramdown's inline-math syntax is $...$. Convert MathJax-style \\(...\\)
  # delimiters before Markdown parsing, then recognize only unambiguous
  # parenthesized LaTeX in prose. Existing dollar math remains untouched.
  def normalize_inline_math(line)
    converted = 0
    parts = line.split(DOLLAR_MATH)
    normalized = parts.each_with_index.map do |part, index|
      next part if index.odd?

      inline = part.gsub(/\\\((.+?)\\\)/) do
        converted += 1
        "$#{Regexp.last_match(1)}$"
      end

      math_parts = inline.split(DOLLAR_MATH)
      math_parts.each_with_index.map do |segment, segment_index|
        if segment_index.odd?
          segment
        else
          normalized_segment, count = normalize_parenthetical_math(segment)
          converted += count
          normalized_segment
        end
      end.join
    end.join

    [normalized, converted]
  end

  def normalize_parenthetical_math(text)
    converted = 0
    normalized = text.gsub(/(?<!\\)(\(([^()\n]{1,160})\)|（([^（）\n]{1,160})）)/) do |candidate|
      match = Regexp.last_match
      content = match[2] || match[3]
      before = text[0...match.begin(0)]

      if !before.rstrip.end_with?("]") && parenthetical_math?(content, before)
        converted += 1
        "$#{candidate}$"
      else
        candidate
      end
    end

    [normalized, converted]
  end

  def parenthetical_math?(content, before)
    return false if content.match?(/\A\s*(?:https?:\/\/|mailto:|www\.)/i) || content.include?("://")

    return true if content.match?(/\\[A-Za-z]+/)
    return true if content.match?(/[A-Za-z][A-Za-z0-9]*[_^](?:\{[A-Za-z0-9\\]|[A-Za-z0-9])/)
    return true if content.match?(/[=<>≤≥≈±×÷]/)

    content.match?(/\A\s*[A-Za-z]\s*\z/) &&
      before.match?(/(?:常数|参数|变量|符号|能量|温度|时间|速率|频率|波长|长度|质量|压力|电荷|电势|化学势|覆盖度|自由能|活化因子)\s*\z/)
  end

  def balanced_block_end(lines, start, source)
    depth = 0

    (start...lines.length).each do |line_index|
      escaped = false
      lines[line_index].each_char do |char|
        if escaped
          escaped = false
          next
        end
        if char == '\\'
          escaped = true
        elsif char == '%'
          break
        elsif char == '{'
          depth += 1
        elsif char == '}'
          depth -= 1
          raise FormulaError, "#{source}:#{start + 1}: unbalanced LaTeX braces; no automatic modification" if depth.negative?
        end
      end
      return line_index if depth.zero?
    end

    raise FormulaError, "#{source}:#{start + 1}: unbalanced LaTeX braces; no automatic modification"
  end

  def validate_braces!(latex, source, line)
    depth = 0
    escaped = false
    latex.each_char do |char|
      if escaped
        escaped = false
        next
      end
      if char == '\\'
        escaped = true
      elsif char == '{'
        depth += 1
      elsif char == '}'
        depth -= 1
        raise FormulaError, "#{source}:#{line}: unbalanced LaTeX braces; no automatic modification" if depth.negative?
      end
    end
    raise FormulaError, "#{source}:#{line}: unbalanced LaTeX braces; no automatic modification" unless depth.zero?
  end

  def append_display(out, block, lines, last)
    out << "\n" if !out.empty? && !out.last.strip.empty?
    out << "$$\n"
    block.each { |line| out << (line.end_with?("\n") ? line : "#{line}\n") }
    out << "$$\n"
    next_line = lines[last + 1]
    out << "\n" if next_line && !next_line.strip.empty?
  end
end

if defined?(Jekyll::Hooks)
  Jekyll::Hooks.register :posts, :pre_render do |post|
    result = ResearchMathGuard.normalize(post.content, source: post.respond_to?(:relative_path) ? post.relative_path : post.path)
    next unless result.wrapped_count.positive?

    post.content = result.text
    Jekyll.logger.info("Math guard:", "normalized #{result.wrapped_count} formula(s) in #{post.relative_path}")
  rescue ResearchMathGuard::FormulaError => e
    raise Jekyll::Errors::FatalException, "Math guard rejected formula: #{e.message}"
  end
end
