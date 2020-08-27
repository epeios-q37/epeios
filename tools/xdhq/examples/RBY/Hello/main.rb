=begin
MIT License

Copyright (c) 2018 Claude SIMON (https://q37.info/s/rmnmqd49)

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
=end

require 'Atlas'

def readAsset(path)
	return Atlas::readAsset(path, "Hello")
end

def acConnect(userObject, dom)
	dom.inner("", readAsset("Main.html"))
	dom.focus("input")
end

def acSubmit(userObject, dom)
	dom.alert("Hello, " + dom.getContent("input") + "!")
	dom.focus("input")
end

def acClear(userObject, dom)
	if dom.confirm?("Are you sure?")
		dom.setContent("input", "")
	end
	dom.focus("input")
end

callbacks = {
	"" => method(:acConnect),
	"Submit" => method(:acSubmit),
	"Clear" => method(:acClear),
}

Atlas.launch(callbacks, -> () {}, readAsset("Head.html"), "Hello")
