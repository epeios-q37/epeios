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

#ifndef CSDMNB_INC_
# define CSDMNB_INC_

# define CSDMNB_NAME		"CSDMNB"

# if defined( E_DEBUG ) && !defined( CSDMNB_NODBG )
#  define CSDMNB_DBG
# endif

// Client-Server Devices Muxed Network Base

# include "err.h"
# include "bso.h"
# include "flw.h"
# include "dtfptb.h"

# define CSDMNB_PING	BSO_U8_MAX
# define CSDMNB_CLOSE	( CSDMNB_PING - 1 )
# define CSDMNB_UNDEFINED	( CSDMNB_CLOSE - 1 )
# define CSDMNB_RESERVED	CSDMNB_UNDEFINED

namespace csdmnb {
	typedef bso::u8__ id__;

	inline void PutId(
		id__ Id,
		flw::oflow__ &Flow )
	{
		dtfptb::PutU8( Id, Flow );
	}

	inline id__ GetId( flw::iflow__ &Flow )
	{
		return dtfptb::GetU8( Flow );
	}
}

#endif
