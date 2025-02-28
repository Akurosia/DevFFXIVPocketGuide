require 'htmlbeautifier'

Jekyll::Hooks.register :site, :post_write do |site|
  # Plugin nur ausführen, wenn JEKYLL_ENV auf "production" gesetzt ist
  if ENV['JEKYLL_ENV'] == 'production'
    puts "Running HTML Beautifier in production mode..."
    Dir.glob(File.join(site.dest, '**/*.html')).each do |file|
      puts "Linting #{file}"
      content = File.read(file)
      formatted = HtmlBeautifier.beautify(content)
      File.write(file, formatted)
    end
  else
    puts "Skipping HTML Beautifier in development mode..."
  end
end
