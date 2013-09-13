#!/usr/bin/env watchr

require 'fileutils'
puts 'reloaded'

WSGI_FILE = File.join(File.dirname(__FILE__), *%w[ .. src youarehero wsgi.py])

Dir.chdir(File.join(File.dirname(__FILE__), ".."))

watch('^src/.*') do |md|
  unless File.identical?(md[0], WSGI_FILE)
    puts "#{md[0]} modified, touching #{WSGI_FILE}"
    FileUtils.touch(WSGI_FILE)
  end
end


