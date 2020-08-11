/*
MIT License

Copyright (c) 2017 Claude SIMON (https://q37.info/s/rmnmqd49)

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
*/

import info.q37.atlas.*;
import java.util.HashMap;

class Test extends Atlas {
	static private String readAsset_( String path )  {
		return readAsset( path, "Test" );
	}

	@Override
	public void handle(String action, String id ) {
		if ( action.equals( "" ) ) {
			dom.setLayout("",readAsset_( "Main.html") );
			dom.scrollTo(dom.lastChild("Main"));
			dom.toggleClasses( new HashMap<String,String>()
			{{
				put(dom.firstChild("Main"), "test");
				put(dom.previousSibling("Middle"), "test");
				put(dom.nextSibling("Middle"), "test");
			}});
			dom.scrollTo(dom.firstChild("Main"));
		} else {
			System.out.println("No or unknown action !");
			System.exit(1);
		}
	}

	public static void main(String[] args) {
		String dir;

		launch(() -> new Test(), readAsset_("Head.html"), "Test", GUI.DEFAULT, args);
	}
}
