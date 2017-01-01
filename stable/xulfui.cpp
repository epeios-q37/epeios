/*
	Copyright (C) 1999-2017 Claude SIMON (http://q37.info/contact/).

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

#define XULFUI__COMPILATION

#include "xulfui.h"


#include "xulftk.h"

#include "lstbch.h"
#include "lstctn.h"

using namespace xulfui;

bso::bool__ xulfui::steering_callback__::GECKOORegister(
	nsIDOMWindow *Window,
	const str::string_ &Id )
{
	bso::bool__ Success = false;
qRH
	err::buffer__ Buffer;
qRB
	Success = XULFUIRegister( Window, Id );
qRR
	if ( ERRType != err::t_Abort )
		nsxpcm::Alert( err::Message( Buffer ) );
	else
		Success = true;
	ERRRst();
qRT
qRE
	return Success;
}

void xulfui::steering_callback__::GECKOOPreRegistration( void )
{
qRH
	err::buffer__ Buffer;
qRB
	XULFUIPreRegistration();
qRR
	if ( ERRType != err::t_Abort )
		_Trunk->UI().Alert( err::Message( Buffer ) );

	ERRRst();
qRT
qRE
}

void xulfui::steering_callback__::GECKOOPostRegistration( void )
{
qRH
	err::buffer__ Buffer;
qRB
	XULFUIPostRegistration();
qRR
	if ( ERRType != err::t_Abort )
		_Trunk->UI().Alert( err::Message( Buffer ) );

	ERRRst();
qRT
qRE
}
