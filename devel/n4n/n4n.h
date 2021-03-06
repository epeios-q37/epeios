/*
	Copyright (C) 1999 Claude SIMON (http://q37.info/contact/).

	This file is part of the Epeios framework.

	The Epeios framework is free software: you can redistribute it and/or
	modify it under the terms of the GNU Affero General Public License as
	published by the Free Software Foundation, either version 3 of the
	License, or (at your option) any later version.

	The Epeios framework is distributed in the hope that it will be useful,
	but WITHOUT ANY WARRANTY; without even the implied warranty of
	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
	Affero General Public License for more details.

	You should have received a copy of the GNU Affero General Public License
	along with the Epeios framework.  If not, see <http://www.gnu.org/licenses/>
*/

// Native 4 Node.js
// Extension to the 'N4A' library for 'Node.js'.
// Common part between wrapper and component ('scln4n').

#ifndef N4N_INC_
# define N4N_INC_

# define N4N_NAME		"N4N"

# if defined( E_DEBUG ) && !defined( N4N_NODBG )
#  define N4N_DBG
# endif

# include "err.h"
# include "n4a.h"

namespace n4n {
	class sFunction {

	};

	class cStream {
	protected:
		virtual void N4NOnReadable( sFunction &Callback ) = 0;
	public:
		qCALLBACK( Stream );
		void OnReadable( sFunction &Callback )
		{
			return N4NOnReadable( Callback );
		}
	};

}

#endif
