/*
	Copyright (C) 2018 Claude SIMON (http://q37.info/contact/).

	This file is part of XDHq.

	XDHq is free software: you can redistribute it and/or
	modify it under the terms of the GNU Affero General Public License as
	published by the Free Software Foundation, either version 3 of the
	License, or (at your option) any later version.

	XDHq is distributed in the hope that it will be useful,
	but WITHOUT ANY WARRANTY; without even the implied warranty of
	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
	Affero General Public License for more details.

	You should have received a copy of the GNU Affero General Public License
	along with XDHq. If not, see <http://www.gnu.org/licenses/>.
*/

#include "xdhqznd.h"

#include "registry.h"
#include "treep.h"
#include "xdhp.h"

#include "iof.h"
#include "xpp.h"
#include "lcl.h"
#include "sclznd.h"

void sclznd::SCLZNDInfo( txf::sWFlow &Flow )
{
	Flow << NAME_MC << " v" << VERSION << txf::nl
		 << txf::pad << "Build : " __DATE__ " " __TIME__ " (" << cpe::GetDescription() << ')';
}

namespace {
	SCLZND_F( ReturnArgument_ )
	{
	qRH
		str::wString Input, Text;
	qRB
		Input.Init();
		Caller.Get( Input );

		Text.Init();
		sclmisc::GetBaseTranslation( "Argument", Text, Input );

		Caller.SetReturnValue( Text );
	qRR
	qRT
	qRE
	}
}

void sclznd::SCLZNDRegister( sclznd::sRegistrar &Registrar )
{
	Registrar.Register( ReturnArgument_ );	// 0.
	Registrar.Register( treep::New, treep::Delete, treep::PushTag, treep::PopTag, treep::PutValue, treep::PutAttribute );	// 1 - 6.
	Registrar.Register( xdhp::Listen, xdhp::New, xdhp::Delete, xdhp::GetAction );	// 7 - 10.
	Registrar.Register( xdhp::Alert, xdhp::Confirm, xdhp::SetLayout, xdhp::GetContents, xdhp::SetContents, xdhp::DressWidgets ); // 11 - 16.
	Registrar.Register( xdhp::AddClasses, xdhp::RemoveClasses, xdhp::ToggleClasses, xdhp::EnableElements, xdhp::DisableElements );	// 17 - 21.
	Registrar.Register( xdhp::GetAttribute, xdhp::SetAttribute, xdhp::GetProperty, xdhp::SetProperty );	// 22 - 25.
}

const char *sclmisc::SCLMISCTargetName = NAME_LC;
const char *sclmisc::SCLMISCProductName = NAME_MC;