# Fast sitemap generator for the Pocket Guide.
#
# jekyll-sitemap renders a large Liquid template over every document in this
# repository and was taking ~65 seconds by itself. This hook writes the same
# kind of sitemap directly after Jekyll has written the site, avoiding Liquid.

require "cgi"
require "set"
require "time"

Jekyll::Hooks.register :site, :post_write do |site|
  site_url = site.config.fetch("url", "").to_s.sub(%r{/$}, "")
  baseurl = site.config.fetch("baseurl", "").to_s

  documents = site.collections.values.flat_map(&:docs)
  items = site.pages + documents
  seen = Set.new
  rows = []

  items.each do |item|
    next unless item.respond_to?(:url)
    next if item.url.nil? || item.url.empty?
    next if item.data && item.data["sitemap"] == false

    # Keep the sitemap focused on public HTML pages rather than generated
    # assets, feeds, JSON, CSS, or the sitemap itself.
    output_ext = item.respond_to?(:output_ext) ? item.output_ext.to_s : ""
    next unless output_ext.empty? || output_ext == ".html"

    path = item.url.to_s
    next if path == "/sitemap.xml"
    next if seen.include?(path)
    seen.add(path)

    loc = "#{site_url}#{baseurl}#{path}"

    lastmod = nil
    if item.respond_to?(:data) && item.data
      lastmod = item.data["last_modified_at"] || item.data["date"]
    end
    lastmod ||= item.date if item.respond_to?(:date)

    lastmod_xml = ""
    if lastmod
      begin
        parsed = lastmod.respond_to?(:iso8601) ? lastmod : Time.parse(lastmod.to_s)
        lastmod_xml = "\n    <lastmod>#{CGI.escapeHTML(parsed.iso8601)}</lastmod>"
      rescue ArgumentError, TypeError
        # Invalid optional date data should not break a production build.
      end
    end

    rows << "  <url>\n    <loc>#{CGI.escapeHTML(loc)}</loc>#{lastmod_xml}\n  </url>"
  end

  rows.sort!

  xml = <<~XML
    <?xml version="1.0" encoding="UTF-8"?>
    <urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
    #{rows.join("\n")}
    </urlset>
  XML

  File.write(site.in_dest_dir("sitemap.xml"), xml)
  Jekyll.logger.info "Fast Sitemap:", "wrote #{rows.length} URLs"
end
