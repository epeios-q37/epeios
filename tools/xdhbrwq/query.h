/*
	Header for the 'query' module by Claude SIMON (http://zeusw.org/epeios/contact.html).
	Part of the 'xdhbrwq' tool.
	Copyright (C) 2015 by Claude SIMON (http://zeusw.org/epeios/contact.html).

	This file is part of the Epeios project (http://zeusw.org/epeios/).

    This file is part of 'xdhbrwq'.

    'xdhbrwq' is free software: you can redistribute it and/or modify it
    under the terms of the GNU Affero General Public License as published
    by the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    'xdhbrwq' is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with 'xdhbrwq'.  If not, see <http://www.gnu.org/licenses/>.
*/

#ifndef QUERY_INC_
# define QUERY_INC_

# include "tol.h"
# include "str.h"
# include "xml.h"

namespace query {

	typedef str::string_ item_;
	typedef str::string item;

	E_ROW( irow__ );	// Item row.

	typedef ctn::E_MCONTAINERt_( item_, irow__ ) items_;
	E_AUTO( items );

	struct pair__ {
		public:
		irow__
			Field,
			Value;
		void reset( bso::bool__ = true )
		{
			Field = Value = qNIL;
		}
		E_CDTOR( pair__ );
		void Init( void )
		{
			Field = Value = qNIL;
		}
	};

	E_ROW( prow__ );	//	'Pair row'. 

	typedef bch::E_BUNCHt_( pair__, prow__ ) _pairs_;
	E_AUTO( _pairs );

	class pairs_
	{
	public:
		struct s {
			items_::s Items;
			_pairs_::s Pairs;
		};
		items_ Items;
		_pairs_ Pairs;
		pairs_( s &S )
		: Items( S.Items ),
		  Pairs( S.Pairs )
		{}
		void reset( bso::bool__ P = true )
		{
			Items.reset( P );
			Pairs.reset( P );
		}
		void plug( qASd *AS  )
		{
			Items.plug( AS );
			Pairs.plug( AS );
		}
		pairs_ &operator =( const pairs_ &P )
		{
			Items = P.Items;
			Pairs = P.Pairs;

			return *this;
		}
		void Init( void )
		{
			Items.Init();
			Pairs.Init();
		}
		prow__ Add(
			const item_ &Field,
			const item_ &Value );
		void FillWith( flw::iflow__ &Flow );
		prow__ Find( const item_ &Field ) const;
		bso::bool__ GetValue(
			const item_ &Field,
			item_ &Value ) const;
		void Dump( xml::writer_ &Writer ) const;


	};

	E_AUTO( pairs );
}
	

#endif
