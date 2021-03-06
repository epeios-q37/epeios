/*
	Copyright (C) 2016-2017 Claude SIMON (http://zeusw.org/epeios/contact.html).

	This file is part of 'MMUAq' software.

    'MMUAq' is free software: you can redistribute it and/or modify it
    under the terms of the GNU Affero General Public License as published
    by the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    'MMUAq' is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with 'MMUAq'.  If not, see <http://www.gnu.org/licenses/>.
*/

#include "wrpexample.h"
#include "registry.h"
#include "dir.h"
#include "fnm.h"

#include "muainf.h"

#include "common.h"

#include "sclmisc.h"

using namespace wrpexample;
using namespace muaxmp;

#define M( message )	E_CDEF( char *, message, #message )

namespace message_ {
	M( TestMessage );
/*
	M(  );
*/
}

#undef M


using common::rStuff;

const char *wrpexample::dMyObject::PREFIX = WRPEXAMPLE_MYOBJECT_PREFIX;
const char *wrpexample::dMyObject::NAME = WRPEXAMPLE_MYOBJECT_NAME;

#define ARGS (\
	dMyObject_ &MyObject,\
	fblbkd::backend___ &Backend,\
	fblbkd::rRequest &Request )

typedef void (* f_manager ) ARGS;

void wrpexample::dMyObject::HANDLE(
	fblbkd::backend___ &Backend,
	fblbkd::rModule &Module,
	fblbkd::command__ Command,
	fblbkd::rRequest &Request )
{
	((f_manager)Module.Functions( Command ))( *this, Backend, Request );
}

#define DEC( name )	static void exported##name ARGS

DEC( Test )
{
qRH
qRB
	REPORT( TestMessage );
qRR
qRT
qRE
}

DEC( ToUC )
{
qRH
	str::string String;
qRB
	String.Init(Request.StringIn() );

	str::ToUpper( String );

	Request.StringOut() = String;
qRR
qRT
qRE
}

#define D( name )	#name, (void *)exported##name

void wrpexample::dMyObject::NOTIFY(	fblbkd::rModule &Module	)
{
	Module.Add( D( ToUC ),
			fblbkd::cString,
		fblbkd::cEnd,
			fblbkd::cString,
		fblbkd::cEnd );

	Module.Add( D( Test ),
		fblbkd::cEnd,
		fblbkd::cEnd );
}

