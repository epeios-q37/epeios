/*
	Copyright (C) 2016 Claude SIMON (http://zeusw.org/epeios/contact.html).

	This file is part of 'eSketch' software.

    'eSketch' is free software: you can redistribute it and/or modify it
    under the terms of the GNU Affero General Public License as published
    by the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    'eSketch' is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with 'eSketch'.  If not, see <http://www.gnu.org/licenses/>.
*/

// FRontenD INSTanCes

#ifndef FRDINSTC__INC
# define FRDINSTC__INC

# include "frdfrntnd.h"

namespace frdinstc {

	using namespace frdfrntnd;

	class _user___
	{
	private:
		qRVM( frdfrntnd::rFrontend, F_,  Frontend_ );
		esketch::rStatics S_( void )
		{
			return F_().Statics;
		}
		esketch::rSKTMyObject Object_;
	public:
		void reset( bso::bool__ P = true )
		{	
			Frontend_ = NULL;

			Object_.reset( P );
		}
		E_CVDTOR( _user___ );
		void Init( frdfrntnd::rFrontend &Frontend )
		{
			Frontend_ = &Frontend;

			Object_.Init( Frontend.MyObject );
		}
		str::string_ &ToUpper( str::string_ &String )
		{
			str::string Result;

			Result.Init();

			Object_.ToUC( String, Result );

			String = Result;

			return String;
		}
		void TestMessage( void )
		{
			S_().SKTTest();
		}
	};

	class user___
	{
	private:
		_user___ Core_;
		bso::bool__ _TestButtonIsVisible;
	public:
		void reset( bso::bool__ P = true )
		{	
			Core_.reset( P );
			_TestButtonIsVisible = false;
		}
		E_CVDTOR( user___ );
		void Init( frdfrntnd::rFrontend &Frontend )
		{
			if ( Frontend.IsConnected() )
				Core_.Init( Frontend );

			_TestButtonIsVisible = false;
		}
		str::string_ &ToUpper( str::string_ &String )
		{
			return Core_.ToUpper( String );
		}
		void TestMessage( void )
		{
			Core_.TestMessage();
		}
		E_RWDISCLOSE__( bso::bool__, TestButtonIsVisible );
	};
}

#endif
