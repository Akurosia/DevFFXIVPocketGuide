source "https://rubygems.org"
ruby RUBY_VERSION

# Hello! This is where you manage which Jekyll version is used to run.
# When you want to use a different version, change it below, save the
# file and run `bundle install`. Run Jekyll with `bundle exec`, like so:
#
#     bundle exec jekyll serve
#
# This will help ensure the proper Jekyll version is running.
# Happy Jekylling!
gem 'liquid', '>= 4.0.4'
gem "jekyll", github: "jekyll/jekyll"
#gem "liquid-c"
# This is the default theme for new Jekyll sites. You may change this to anything you like.
#gem "minima", "~> 2.0"
gem 'jekyll-theme-chirpy', '~> 6.4', '>= 6.4.2'
# If you want to use GitHub Pages, remove the "gem "jekyll"" above and
# uncomment the line below. To upgrade, run `bundle update github-pages`.
# gem 'github-pages', group: :jekyll_plugins

gem 'wdm', '>= 0.1.0' if Gem.win_platform?

# If you have any plugins, put them here!
group :jekyll_plugins do
   gem "jekyll-last-modified-at"
   gem "jekyll-sitemap"
   gem "jekyll-include-cache"
   gem "jekyll-commonmark"
   gem "jekyll-youtube"
   gem 'htmlbeautifier'
   #gem "jekyll-admin"
end
gem "webrick", "~> 1.7"
