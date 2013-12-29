#!/usr/bin/env ruby

def rel_path path
  File.join(File.dirname(__FILE__), path)
end

def file_contents path
  #puts "reading #{path.inspect}"
  return IO.read(rel_path path)
end
messages_lines = file_contents("locale/de/LC_MESSAGES/django.po").lines

current = {}
entries = []
until messages_lines.empty? do
  l = messages_lines.shift
  case l
  when /^#:/
    l.scan(/(?<= )(\S+):(\d+)/) do |file, num|
      puts "got #{file}:#{num}"
      current[:locations] ||= []
      current[:locations] << {file: file, line: num.to_i}
    end
  when /^(#|$)/
    # do nothing, it's a just garbage
  when /^msgid/
    msgid = l[/(?<=msgid ").*(?="$)/]
    throw :msgid_nil if msgid.nil?
    until messages_lines[0] =~ /^msgstr/
      part = messages_lines.shift[/(?<=")(\\.|[^"])*(?="$)/]
      throw :msgid_part_nil if part.nil?
      msgid += part
    end
    current[:msgid] = msgid
  when /^msgstr/
    msgstr = l[/(?<=msgstr ").*(?="$)/]
    throw :msgstr_nil if msgstr.nil?
    until messages_lines[0] =~ /^$/
      part = messages_lines.shift[/(?<=")(\\.|[^\"])*(?="$)/]
      throw :msgstr_part_nil if part.nil?
      msgstr += part
    end
    current[:msgstr] = msgstr

    puts "pushing #{current.inspect}\n\n"
    entries << current
    current = {}
  else
    puts "unknown line #{l.inspect}"
    throw :unknown_line
  end
end

es = entries
entries = []
es.each do |e|
  next unless e[:locations]
  e[:locations].each do |loc|
    new = e
    new[:locations] = [loc]
    entries << new
  end
end

entries = entries.sort_by { |e| 10000000 - e[:locations][0][:line] }
entries = entries.reject {|e| e[:msgstr].empty? }

entries.each do |entry|
  next if entry[:locations].nil?

  msgid_re  = Regexp.new(
    Regexp.escape(entry[:msgid])
      .gsub("\\\\n", "(\\\\\\n|\\n)")
      .gsub(/(\\+\")/, "(\\1|\")")
      .gsub(/\%\\\(([^ \t\r\n\f\)]+)\\\)s/, "({{\\s*\\1\\s*}}|\\0)"))
  #puts "original msgstr: #{entry[:msgstr].inspect}"
  msgstr_re = Regexp.new(Regexp.escape(entry[:msgstr])
      .gsub("\\\\n", "(\\\\\\n|\\n)")
      .gsub(/(\\+\")/, "(\\1|\")")
      .gsub(/\%\\\(([^ \t\r\n\f\)]+)\\\)s/, "({{\\s*\\1\\s*}}|\\0)"))
  #puts "strs: #{msgstr_re.source.inspect}"
  #print "id: #{entry[:msgid]}\nre: #{msgid_re}\nstr: #{entry[:msgstr]}\nre: #{msgstr_re}\n\n"

  entry[:locations].each do |location|
    contents_string = file_contents(location[:file])
    skipped_part = contents_string.lines[0..(location[:line] - 2)].join
    contents = contents_string.lines[(location[:line] - 1)..-1].join
    first_line_length = contents.lines[0].length
    puts "in #{location[:file]}:#{location[:line]} (first line length #{first_line_length}):\nstr_re: #{msgstr_re.to_s}\nid_re: #{msgid_re.to_s}\nmsgstr_re: #{contents[msgstr_re]} (#{contents.index(msgstr_re)})\nmsgid_re: #{contents[msgid_re]} (#{contents.index(msgid_re)})\n\n"

    if contents[msgstr_re] and contents.index(msgstr_re) <= first_line_length
      puts "Skipping #{entry[:msgstr]}\n\n"
    elsif contents[msgid_re]
      if contents.index(msgid_re) > first_line_length
        throw :not_on_first_line
      end
      str_for_replace = entry[:msgstr]
      str_for_replace.gsub!(/\%\(([^ \t\r\n\f\)]+)\)s/, "{{ \\1 }}")
      if location[:file] =~ /\.html$/ and contents.lines[0] =~ /blocktrans/
        #puts "    rewriting newlines in #{location[:file]}:#{location[:line]} for #{contents.lines[0]}"
        str_for_replace.gsub!("\\n", "\n")
      else
        puts "NOT rewriting newlines in #{location[:file]} for #{contents.lines[0]}"
      end
      new_contents = contents.sub(msgid_re, str_for_replace)

      puts "writing:\n=======...\n#{skipped_part[-4..-1]}\n---------\n#{new_contents[0..3]}\n...=======\n"
      IO.write(rel_path(location[:file]), skipped_part + new_contents)
    else
      throw :not_found
    end
  end
end

pofile_lines_old = file_contents("locale/de/LC_MESSAGES/django.po").lines
pofile_lines_new = []
until pofile_lines_old.empty?
  until pofile_lines_old.empty? or pofile_lines_old[0] =~ /^msgid/
    puts "= #{pofile_lines_old[0]}"
    pofile_lines_new << pofile_lines_old.shift
  end
  break if pofile_lines_old.empty?

  msgid_lines = []
  until pofile_lines_old.empty? or pofile_lines_old[0] =~ /^msgstr/
    puts "I #{pofile_lines_old[0]}"
    msgid_lines << pofile_lines_old.shift
  end

  msgstr_lines = []
  until pofile_lines_old.empty? or pofile_lines_old[0] =~ /^$/
    puts "S #{pofile_lines_old[0]}"
    msgstr_lines << pofile_lines_old.shift
  end

  puts "msgid: #{msgid_lines.inspect}\nmsgstr: #{msgstr_lines.inspect}\n"
  if (msgid_lines.one? and msgid_lines[0] =~ /^msgid ""$/) or (msgstr_lines.one? and msgstr_lines[0] =~ /^msgstr ""$/)
    # header block or empty translation, keep the original
    puts "skipping\n"
    pofile_lines_new += msgid_lines
    pofile_lines_new += msgstr_lines
  else
    puts "switching\n"
    pofile_lines_new << msgstr_lines[0].sub(/^msgstr/, "msgid")
    pofile_lines_new += msgstr_lines[1..-1]
    pofile_lines_new << msgid_lines[0].sub(/^msgid/, "msgstr")
    pofile_lines_new += msgid_lines[1..-1]
  end
end
IO.write(rel_path("locale/de/LC_MESSAGES/django.po"), pofile_lines_new.join)
