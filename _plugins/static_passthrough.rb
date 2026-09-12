# Copies large static translation trees outside Jekyll's normal read/write path.
# The directory is excluded in _config.yml, so Jekyll does not scan thousands
# of JSON files during the READ phase. Existing unchanged destination files are
# preserved on incremental builds.
require "fileutils"

Jekyll::Hooks.register :site, :post_write do |site|
  source_root = File.join(site.source, "assets", "translations")
  next unless Dir.exist?(source_root)

  destination_root = File.join(site.dest, "assets", "translations")
  FileUtils.mkdir_p(destination_root)

  copied = 0
  skipped = 0
  started = Process.clock_gettime(Process::CLOCK_MONOTONIC)

  Dir.glob(File.join(source_root, "**", "*"), File::FNM_DOTMATCH).each do |source|
    next if File.directory?(source)

    relative = source.delete_prefix(source_root + File::SEPARATOR)
    destination = File.join(destination_root, relative)
    source_stat = File.stat(source)

    if File.exist?(destination)
      destination_stat = File.stat(destination)
      if destination_stat.size == source_stat.size && destination_stat.mtime.to_i >= source_stat.mtime.to_i
        skipped += 1
        next
      end
    end

    FileUtils.mkdir_p(File.dirname(destination))
    FileUtils.copy_file(source, destination)
    FileUtils.touch(destination, mtime: source_stat.mtime)
    copied += 1
  end

  elapsed = Process.clock_gettime(Process::CLOCK_MONOTONIC) - started
  Jekyll.logger.info "Static translations:", "#{copied} copied, #{skipped} unchanged (#{format('%.2f', elapsed)}s)"
end
