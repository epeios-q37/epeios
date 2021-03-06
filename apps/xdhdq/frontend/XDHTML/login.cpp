/*
	Copyright (C) 2016 Claude SIMON (http://zeusw.org/epeios/contact.html).

	This file is part of 'XDHDq' software.

    'XDHDq' is free software: you can redistribute it and/or modify it
    under the terms of the GNU Affero General Public License as published
    by the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    'XDHDq' is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with 'XDHDq'.  If not, see <http://www.gnu.org/licenses/>.
*/

#include "login.h"

#include "core.h"
#include "main.h"
#include "prolog.h"
#include "registry.h"

#include "xdhdws.h"

#include "sclfrntnd.h"

namespace {
	qCDEF( char *, XSLAffix_, "Login" );

	namespace layout_ {
		void Get(
			core::rSession &Session,
			xml::dWriter &Writer )
		{
			sclxdhtml::login::GetLayout( Session, Writer );
		}
	}
}

void login::SetLayout( core::rSession &Session )
{
	Session.SetDocumentLayout( XSLAffix_, layout_::Get );
}

void login::Display( core::rSession &Session )
{
	SetLayout( Session );

	Session.SwitchTo( base::pLogin );
}

#define AC( name ) BASE_AC( login, name )

AC( SwitchBackendType )
{
}

AC( DisplayEmbeddedBackendFilename )
{
	sclxdhtml::login::DisplaySelectedEmbeddedBackendFilename( Session, Id );
}

 AC( Connect )
{
qRH
	fblfrd::incompatibility_informations IncompatibilityInformations;
	sclfrntnd::rFeatures Features;
qRB
	if ( core::Core.Mode() == xdhcmn::mMonoUser ) {
		Features.Init();
		sclxdhtml::login::GetBackendFeatures( Session, Features );
		core::Kernel().Init( Features, plgn::EmptyAbstracts );
	}

	IncompatibilityInformations.Init();
	if ( !Session.Connect( fblfrd::compatibility_informations__( XDDINF_LC_AFFIX, XDHDQ_API_VERSION ), IncompatibilityInformations ) )
		qRGnr();

	main::Display( Session );
qRR
	Session.Disconnect();
qRE
qRT
}

AC( Dismiss )
{
	prolog::Display( Session );
}

