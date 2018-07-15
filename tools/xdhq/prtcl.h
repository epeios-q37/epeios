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

// PRoToCoL
// Unlike other modules in the same directory, this one is shared between client and server.
// Other modules are only for the server part of the software.

#ifndef PRTCL_INC_
# define PRTCL_INC_

# include "csdcmn.h"
# include "flw.h"
# include "tol.h"


namespace prtcl {
	static qCDEF( char *, ProtocolId, "712a58bf-2c9a-47b2-ba5e-d359a99966de" );
	qCDEF( bso::sU8, ProtocolVersion, 0 );

	qENUM( Request ) {
		rLaunch_1,	// Event was launched.
		rReady_1,	// Potential pending data are available, and client is available for new action.
		r_amount,
		r_Undefined
	};

	const char *GetLabel( eRequest Request );

	eRequest GetRequest( const str::dString &Pattern );

	eRequest GetRequest( flw::iflow__ &Flow );

	void PutRequest(
		eRequest Request,
		flw::oflow__ &Flow );

	qENUM( Command )
	{
		cStandBy_1,
		cError_1,
		cExecute_1,
		cAlert_1,
		cConfirm_1,
		cSetLayout_1,
		cGetContents_1,
		cSetContents_1,
		cDressWidgets_1,
		cAddClasses_1,
		cRemoveClasses_1,
		cToggleClasses_1,
		cEnableElements_1,
		cDisableElements_1,
		cSetAttribute_1,
		cGetAttribute_1,
		cRemoveAttribute_1,
		cSetProperty_1,
		cGetProperty_1,
		cFocus_1,
		cNew,	// Will replace all above commands, except the 2 first ones.
		c_amount,
		c_Undefined
	};

	const char *GetLabel( eCommand Command );

	eCommand GetCommand( const str::dString &Pattern );

	eCommand GetCommand( flw::iflow__ &Flow );

	void SendCommand(
		eCommand Command,
		flw::oflow__ &Flow );

	using csdcmn::Put;
	using csdcmn::Get;
}

#endif