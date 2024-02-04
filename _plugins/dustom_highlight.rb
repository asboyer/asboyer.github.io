# frozen_string_literal: true

require 'jekyll'
require 'liquid'
require 'rouge' # Ensure Rouge is required for highlighting

module Jekyll
  module Tags
    class HighlightBlock < Liquid::Block
      include Liquid::StandardFilters

      SYNTAX = %r!^([a-zA-Z0-9.+#_-]+)((\s+\w+(=(\w+|"([0-9]+\s)*[0-9]+"))?)*)$!.freeze
      OPTIONS_REGEX = %r!(?:\w="[^"]*"|\w=\w|\w)+!.freeze

      def initialize(tag_name, markup, tokens)
        super
        if markup.strip =~ SYNTAX
          @lang = Regexp.last_match(1).downcase
          @highlight_options = parse_options(Regexp.last_match(2))
        else
          raise SyntaxError, "Syntax Error in tag 'highlight' while parsing the following markup: #{markup}"
        end
      end

      def render(context)
        prefix = context["highlighter_prefix"] || ""
        suffix = context["highlighter_suffix"] || ""
        code = super.to_s.gsub(%r!\A(\n|\r)+|(\n|\r)+\z!, "")

        output = case context.registers[:site].highlighter
                 when "pygments"
                   render_pygments(code, context)
                 when "rouge"
                   render_rouge(code)
                 else
                   render_codehighlighter(code)
                 end

        rendered_output = add_code_tag(output)
        prefix + rendered_output + suffix
      end

      private

    def parse_options(input)
      options = {}
      return options if input.empty?

      input.scan(OPTIONS_REGEX) do |opt|
        key, value = opt.split("=")
        if value&.include?('"')
          value = value.delete('"').split.map(&:to_i) # Convert to an array of integers
        end
        options[key.to_sym] = value || true
      end

      options[:linenos] = "inline" if options[:linenos] == true
      options[:start_line] = Integer(options[:start_line]) unless options[:start_line].nil?
      options[:mark_lines] = options[:mark_lines] ? options[:mark_lines].map(&:to_i) : []
      options
    end


      def render_pygments(code, context)
        # Pygments highlighting logic (if applicable)
        Jekyll.logger.warn "Pygments is not supported. Falling back to Rouge."
        render_rouge(code)
      end

    def render_rouge(code)
      require 'rouge'
      formatter = Rouge::Formatters::HTML.new(line_numbers: @highlight_options[:linenos], wrap: false)
      if @highlight_options[:mark_lines]
        formatter = Rouge::Formatters::HTMLLineHighlighter.new(formatter, highlight_lines: @highlight_options[:mark_lines])
      end
      lexer = Rouge::Lexer.find_fancy(@lang, code) || Rouge::Lexers::PlainText.new
      formatter.format(lexer.lex(code))
    end


      def render_codehighlighter(code)
        h(code).strip
      end

    def add_code_tag(code)
      code_attributes = %[
        class="language-#{@lang.to_s.tr("+", "-")}"
        data-lang="#{@lang}"
      ].strip # Ensure we properly format the string without attempting to join

      # Use string interpolation to assemble the final HTML snippet
      "<figure class=\"highlight\"><pre><code #{code_attributes}>#{code.chomp}</code></pre></figure>"
    end

    end
  end
end

Liquid::Template.register_tag("dustom_highlight", Jekyll::Tags::HighlightBlock)
