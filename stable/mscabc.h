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

// MuSiC ABC (notation)

#ifndef MSCABC_INC_
# define MSCABC_INC_

# define MSCABC_NAME		"MSCABC"

# if defined( E_DEBUG ) && !defined( MSCABC_NODBG )
#  define MSCABC_DBG
# endif

# include "mscmld.h"

# include "bso.h"
# include "err.h"
# include "flx.h"

namespace mscabc {
  bso::sS8 Convert(
    const mscmld::dMelody &Melody,
    mscmld::eAccidental Accidental,
    bso::sU8 Width,
    bso::sBool EscapeNL,
    txf::sWFlow &ABC);

  inline bso::sS8 Convert(
    const mscmld::dMelody &Melody,
    mscmld::eAccidental Accidental,
    bso::sU8 Width,
    bso::sBool EscapeNL,
    str::dString &ABC)
  {
    return Convert(Melody, Accidental, Width, EscapeNL, flx::rStringTWFlow(ABC)());
  }
}

#endif
