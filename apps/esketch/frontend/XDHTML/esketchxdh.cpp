/*
	Copyright (C) 2016 Claude SIMON (http://zeusw.org/epeios/contact.html).

	This file is part of 'eSketch' software.

    'eSketch' is free software: you can redistribute it and/or modify it
    under the terms of the GNU Affero General Public License as published
    by the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    'eSketch' is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with 'eSketch'.  If not, see <http://www.gnu.org/licenses/>.
*/

#include "sclxdhtml.h"
#include "sclmisc.h"

#include "frdrgstry.h"

#include "core.h"

const char *sclmisc::SCLMISCTargetName = BASE_NAME;

void sclxdhtml::SCLXDHTMLInitialization( xdhcmn::mode__ Mode )
{
qRH
	sclfrntnd::features___ Features;
qRB
	core::Core.Init( Mode );

	if ( Mode == xdhcmn::mMultiUser ) {
		Features.Init();
		sclfrntnd::GuessBackendFeatures( Features );
		core::Kernel().Init( Features );
	}
qRR
qRT
qRE
}

xdhcmn::session_callback__ *sclxdhtml::SCLXDHTMLRetrieveCallback(
	const char *Language,
	xdhcmn::proxy_callback__ *ProxyCallback )
{
	core::fSession *Session = new core::fSession;

	if ( Session == NULL )
		qRGnr();

	Session->Init( core::Kernel(), Language, ProxyCallback );

	switch ( core::Core.Mode() ) {
	case xdhcmn::mMonoUser:
		::prolog::SetLayout( *Session );
		break;
	case xdhcmn::mMultiUser:
//		login::SetLayout( *Session );
		break;
	default:
		qRGnr();
		break;
	}

	return Session;
}

void sclxdhtml::SCLXDHTMLReleaseCallback( xdhcmn::session_callback__ *Callback )
{
	if ( Callback == NULL )
		qRGnr();

	delete Callback;
}

