#!/usr/bin/ruby

static = "src/herobase/static/"
bootstrap = "src/herobase/static/bootstrap/"

watch( 'src/herobase/static/bootstrap/less/.*\.less' )  { |md|
    system("lessc #{bootstrap}less/bootstrap.less > #{bootstrap}css/bootstrap.css && echo \"bootstrap/less/bootstrap.less > bootstrap/css/bootstrap.css\"")
    system("lessc #{static}less/style.less > #{static}css/style.css && echo \"less/style.less > css/style.css\"")
}
##watch( 'src/herobase/static/bootstrap/less/variables\.less' )  { |md| system("lessc #{static}less/style.less > #{static}css/style.css && echo \"less/style.less > css/style.css\"") }
watch( 'src/herobase/static/less/(.*)\.less' )  { |md| system("lessc #{static}less/style.less > #{static}css/style.css && echo \"less/style.less > css/style.css\"") }
##{ |md| system("lessc #{md[0]} > #{static}css/#{md[1]}.css && echo \"less/#{md[1]}.less > css/#{md[1]}.css\" ") }