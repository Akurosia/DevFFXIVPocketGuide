source "https://rubygems.org"

# Use the Ruby version from your environment (Chirpy 6.4.2 requires >= 3.0)
ruby RUBY_VERSION

# Core Jekyll + template engine
gem "jekyll", "~> 4.4", ">= 4.4.1"
gem "liquid", "~> 4.0", ">= 4.0.4"

# Theme (stay on 6.4.x to avoid breaking changes in 7.x)
gem "jekyll-theme-chirpy", "~> 6.4", ">= 6.4.2"

# Windows file watching
gem "wdm", ">= 0.1.0", platforms: [:mingw, :x64_mingw, :mswin]

# Jekyll plugins
group :jekyll_plugins do
  gem "jekyll-last-modified-at", "~> 1.3"
  gem "jekyll-sitemap",          "~> 1.4"
  gem "jekyll-include-cache",    "~> 0.2"

  gem "jekyll-commonmark"
  gem "jekyll-youtube"
  gem "htmlbeautifier"

  gem "jekyll-archives",     "~> 2.2"
  gem "jekyll-paginate",     "~> 1.1"
  gem "jekyll-redirect-from","~> 0.16"
  gem "jekyll-seo-tag",      "~> 2.8"
end

gem "webrick", "~> 1.7"
