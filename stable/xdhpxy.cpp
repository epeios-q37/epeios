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

#define XDHPXY_COMPILATION_

#include "xdhpxy.h"

using namespace xdhpxy;

extern "C" typedef xdhcbk::retrieve retrieve;

bso::bool__ xdhpxy::proxy___::Init(
	const str::string_ &ModuleFileName,
	const char *Identification )
{
	bso::bool__ Success = false;
qRH
	xdhcbk::shared_data__ Data;
	fnm::name___ Location;
	TOL_CBUFFER___ Buffer;
qRB
	Location.Init();
	Data.Init( XDHPXYGetUpstreamCallback(), Identification, fnm::GetLocation( ModuleFileName, Location ).UTF8( Buffer ) );

	_Library.Init( ModuleFileName );

	retrieve *Retrieve = dlbrry::GetFunction<retrieve *>( E_STRING( XDHCBK_RETRIEVE_FUNCTION_NAME ), _Library );

	if ( Retrieve == NULL )
		qRReturn;

    _Callback = Retrieve();

	if ( _Callback == NULL )
		qRFwk();

	_Callback->Initialize( Data );

	Success = true;
qRR
qRT
qRE
	return Success;
}
