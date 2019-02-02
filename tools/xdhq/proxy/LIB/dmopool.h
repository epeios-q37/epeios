/*
	Copyright (C) 2017 Claude SIMON (http://zeusw.org/epeios/contact.html).

	This file is part of 'XDHq' software.

    'XDHq' is free software: you can redistribute it and/or modify it
    under the terms of the GNU Affero General Public License as published
    by the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    'XDHq' is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with 'XDHq'.  If not, see <http://www.gnu.org/licenses/>.
*/

/*
	This is the new launcher which will replace the existing one.
	Both will exist together until switching from old to new one is achieved.
*/

// DeMO POOL
// Handles the pool of connexion needed by the DEMO mode.

#ifndef DMOPOOL_INC_
# define DMOPOOL_INC_

# include "sck.h"

namespace dmopool {
	void Initialize();

	typedef bso::sU8 sId;

	qCDEF(sId, Max, bso::U8Max);

	qCDEF( sId, Undefined,Max );

	// eXetended socket.
	struct sXSocket
	{
	public:
		sId Id;
		sck::sSocket Socket;
		void reset( bso::sBool P = true )
		{
			Id = Undefined;
			Socket = sck::Undefined;
		}
		qCVDTOR( sXSocket );
		void Init(
			sId Id = Undefined,
			sck::sSocket Socket = sck::Undefined )
		{
			this->Id = Id;
			this->Socket = Socket;
		}
	};

	sXSocket GetConnection(
		const str::dString &Token,
		str::dString &IP );
}

#endif