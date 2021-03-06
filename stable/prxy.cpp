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

#define PRXY_COMPILATION_

#include "prxy.h"

using namespace prxy;

#define C( name )	case s##name : return PRXY_NAME "_"  #name; break
 
const char *prxy::GetLabel( eState State )
{
	switch ( State ) {
	C( UnableToConnect );
	C( LostProxyConnexion );
	default:
		qRFwk();
		break;
	}
 
	return NULL;	// To avoid a warning.
}

lcl::meaning_ &prxy::GetMeaning(
	eState State,
	const char *HostService,
	lcl::meaning_ &Meaning )
{
	Meaning.SetValue( GetLabel( State ) );

	Meaning.AddTag( HostService );

	return Meaning;
}

eState prxy::RequestDismiss(
	const char *HostService,
	const char *Identifier,
	qRPN )
{
	eState State = s_Undefined;
qRH
	rProxy_ Proxy;
qRB
	State = Proxy.Init( HostService, Identifier, prxybase::tServer, prxybase::rDismiss_1, sck::NoTimeout, qRP );

	if ( State != sOK )
		return State;

	if ( Proxy.EndOfFlow() ) {
		if ( qRPT )
			qRFwk();

		return sLostProxyConnexion;
	} else {
		if ( prxybase::GetAnswer( Proxy ) != prxybase::aOK )
			qRGnr();

		Proxy.Dismiss();

		return sOK;
	}
qRR
qRT
qRE
	return State;
}

