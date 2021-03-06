/*
	Copyright (C) 2015 Claude SIMON (http://q37.info/contact/).

	This file is part of dpkq.

    dpkq is free software: you can redistribute it and/or
	modify it under the terms of the GNU Affero General Public License as
	published by the Free Software Foundation, either version 3 of the
	License, or (at your option) any later version.

    dpkq is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
	Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with dpkq.  If not, see <http://www.gnu.org/licenses/>
*/

// DATA Common

#ifndef DATA_C_INC_
# define DATA_C_INC_

# include "dpktbl.h"

# include "str.h"

namespace data_c {
	extern str::wString NamespaceLabel;	// With tailing ':' !

	void Initialize( void );

	typedef dpktbl::tables_ dData;
	qW( Data );
}

#endif
