/*
	Copyright (C) 2018 Claude SIMON (http://q37.info/contact/).

	This file is part of XDHq.

	XDHq is free software: you can redistribute it and/or
	modify it under the terms of the GNU Affero General Public License as
	published by the Free Software Foundation, either version 3 of the
	License, or (at your option) any later version.

	XDHq is distributed in the hope that it will be useful,
	but WITHOUT ANY WARRANTY; without even the implied warranty of
	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
	Affero General Public License for more details.

	You should have received a copy of the GNU Affero General Public License
	along with XDHq If not, see <http://www.gnu.org/licenses/>.
*/

import info.q37.atlas.*;

class Hello extends Atlas {
	public void handle( DOM dom, String action, String id )
	{
		switch( action) {
		case "Connect":
			dom.setLayout("", new Tree(), "Main.xsl");
			break;
		case "Typing":
			dom.setContent("name", dom.getContent(id));
			break;
		case "Clear":
			if ( dom.confirm( "Are you sure ?" ) ) dom.setContents( new String[][] { { "input", ""}, { "name", ""} } );
			break;
		}
	}
	public static void main(String[] args) throws Exception {
		launch("Connect", "Hello", Atlas.Type.DEFAULT, args );

		for (;;) new Hello();
	}
}