/*
	Copyright (C) 2022 Claude SIMON (http://q37.info/contact/).

	This file is part of the 'TASq' tool.

    'TASq' is free software: you can redistribute it and/or modify it
    under the terms of the GNU Affero General Public License as published
    by the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    'TASq' is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with 'TASq'.  If not, see <http://www.gnu.org/licenses/>.
*/

// TaSQ STRiNG

#ifndef TSQSTRNG_INC_
# define TSQSTRNG_INC_

# include "lstcrt.h"
# include "str.h"
# include "tol.h"

namespace tsqstrng {
  qROW( Row );

  typedef lstcrt::qLMCRATEd( str::dString, sRow ) dStrings;
  qW( Strings );
}

#endif
