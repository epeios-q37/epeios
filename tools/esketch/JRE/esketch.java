/*
	Copyright (C) 2007-2017 Claude SIMON (http://q37.info/contact/).

	This file is part of esketch.

	esketch is free software: you can redistribute it and/or
	modify it under the terms of the GNU Affero General Public License as
	published by the Free Software Foundation, either version 3 of the
	License, or (at your option) any later version.

	esketch is distributed in the hope that it will be useful,
	but WITHOUT ANY WARRANTY; without even the implied warranty of
	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
	Affero General Public License for more details.

	You should have received a copy of the GNU Affero General Public License
	along with esketch. If not, see <http://www.gnu.org/licenses/>.
*/

class eSketch {
	native public static String info();
	native private static void register();
	native private static Object wrapper(
		int index,
		Object... objects);
		
	public Object core;
	
	static
	{
		System.loadLibrary("esketchjre");
		register();
	}
	
	public eSketch( Object core )
	{
		this.core = core;
	}
	
	public String getText()
	{
		return (java.lang.String)wrapper( 0 );
	}
	
	public void finalize()
	{
	}
}

class eSketchDemo {
	private static void displayCompilationTime() throws Exception
	{
		System.out.println( new java.util.Date(new java.io.File(eSketchDemo.class.getClassLoader().getResource(eSketchDemo.class.getCanonicalName().replace('.', '/') + ".class").toURI()).lastModified()) );
	}
	
	public static void main ( String[] args ) throws Exception
	{
		System.out.println( eSketch.info() );
		System.out.println();
		// displayCompilationTime();

		eSketch Sketch = new eSketch( null );

		System.out.println( Sketch.getText() );
	}

}

