require 'htmlbeautifier'

Jekyll::Hooks.register :site, :post_write do |site|
  # Only run the beautifier for production builds.
  next unless ENV['JEKYLL_ENV'] == 'production'

  puts "Running HTML Beautifier in production mode..."

  beautified = 0
  skipped = 0

  Dir.glob(File.join(site.dest, '**/*.html')).each do |file|
    puts "           Beautifying #{file}"

    begin
      content = File.read(file, encoding: 'UTF-8')
      formatted = HtmlBeautifier.beautify(content)

      # Only write when HtmlBeautifier actually changed something.
      if formatted != content
        File.write(file, formatted, mode: 'w', encoding: 'UTF-8')
      end

      beautified += 1
    rescue StandardError => error
      skipped += 1

      warn "           WARNING: HTML Beautifier skipped #{file}"
      warn "                    #{error.class}: #{error.message}"

      # HtmlBeautifier normally reports errors like:
      #   "Unmatched sequence on line 327"
      # Print a small generated-HTML excerpt so CI shows what triggered it.
      line_number = error.message[/line\s+(\d+)/i, 1]&.to_i

      if line_number && line_number > 0
        begin
          lines = File.readlines(file, encoding: 'UTF-8')
          first = [line_number - 3, 1].max
          last = [line_number + 3, lines.length].min

          warn "                    Generated HTML context:"
          (first..last).each do |number|
            marker = number == line_number ? '>>' : '  '
            warn format(
              "                    %s %5d | %s",
              marker,
              number,
              lines[number - 1].to_s.rstrip
            )
          end
        rescue StandardError => context_error
          warn "                    Could not print context: #{context_error.message}"
        end
      end

      # IMPORTANT:
      # Beautification is cosmetic. Keep the original generated HTML and
      # continue processing the rest of the site instead of failing CI.
      next
    end
  end

  puts "HTML Beautifier finished: #{beautified} file(s) beautified, #{skipped} skipped."
end
