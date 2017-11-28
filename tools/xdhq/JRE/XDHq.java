/*
	Copyright (C) 2007-2017 Claude SIMON (http://q37.info/contact/).

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
	along with XDHq. If not, see <http://www.gnu.org/licenses/>.
*/

class JREqDecl {
 protected static String affix = "xdhq";
}

class XDHqData {
	public String
		id,
		action;
};

// Begin of generic part.
class JREq extends JREqDecl {
	native public static String wrapperInfo();
	native public static String componentInfo();
	native private static void init( String location);
	native private static void register( String arguments );
	native protected static Object wrapper(
		int index,
		Object... objects);

	static
	{
		String location = "";
		String osName = System.getProperty("os.name").toLowerCase();

		System.loadLibrary( "jreq" );

		if ( osName.contains( "windows" ) )
			location = "h:/bin";
		else if ( osName.contains( "mac" ) ) {
			location = "/Users/bin";
  } else {
	location = "/home/csimon/bin";
  }

  if ( System.getenv( "EPEIOS_SRC" ) == null ) {
   location = ".";
  }

 	init( location );
  register( "./" + JREqDecl.affix + "jre");
 }
}
// End of generic part.

class XDHq extends JREq {
	public static String returnArgument( String Text )
	{
		return (String)JREq.wrapper( 0, Text  );
	}
	public static void initialize(
		String XML,
		String XSL )
	{
		JREq.wrapper( 1, XML, XSL );
	}
	public static void destructor()
	{
		JREq.wrapper( 2 );
	}
	public static void getAction( XDHqData data )
	{
		JREq.wrapper( 3, data );
	}
	public static void setLayout(
		String XML,
		String XSL )
	{
		JREq.wrapper( 4, XML, XSL );
	}
	public static void setCasting(
		String XML,
		String XSL )
	{
		JREq.wrapper( 5, XML, XSL );
	}
}

class XDHqTest {
	private static void displayBytecodeBuildTimestamp() throws Exception
	{
		System.out.println( "Bytecode build : " + new java.util.Date(new java.io.File(XDHqTest.class.getClassLoader().getResource(XDHqTest.class.getCanonicalName().replace('.', '/') + ".class").toURI()).lastModified()) );
	}
	
	public static void main ( String[] args ) throws Exception
	{
		XDHqData data = new XDHqData();
 		System.out.println( XDHq.wrapperInfo() );
 		System.out.println( XDHq.componentInfo() );
 		displayBytecodeBuildTimestamp();
 		System.out.println( XDHq.returnArgument( "Text from JAVA file" ) );
		XDHq.initialize( "<Root><Layout/></Root>", "../XSL/MainLayout.xsl");
		for(;;) {
			XDHq.getAction( data );
			System.out.println( data.action + " : " + data.id );

			switch ( data.action ) {
			case "ShowTestButton":
				XDHq.setCasting( "<Root><Casting><Test Enabled=\"true\"/></Casting></Root>", "../XSL/MainCasting.xsl" );
				break;
			case "HideTestButton":
				XDHq.setCasting( "<Root><Casting><Test Enabled=\"false\"/></Casting></Root>", "../XSL/MainCasting.xsl" );
				break;
			}
		}

//		XDHq.destructor();
	}
}

