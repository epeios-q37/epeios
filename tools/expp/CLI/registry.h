/*
	Header for the 'registry' module by Claude SIMON (http://zeusw.org/epeios/contact.html).
	Part of th 'xxx_app' tool.
	Copyright (C) 2011 by Claude SIMON (http://zeusw.org/epeios/contact.html).

	This file is part of the Epeios project (http://zeusw.org/epeios/).

    This file is part of 'expp'.

    'expp' is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    'expp' is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with 'expp'.  If not, see <http://www.gnu.org/licenses/>.
*/

#ifndef REGISTRY__INC
# define REGISTRY__INC

# include "sclrgstry.h"

namespace registry {
	using namespace sclrgstry;

	namespace {
		using rgstry::entry___;
	}

	extern entry___ Source;
	extern entry___ Destination;
	extern entry___ Indentation;
	extern entry___ NameSpace;
}

#endif
