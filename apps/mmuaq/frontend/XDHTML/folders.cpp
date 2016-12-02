/*
	Copyright (C) 2016 Claude SIMON (http://zeusw.org/epeios/contact.html).

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

#include "folders.h"

#include "core.h"
#include "registry.h"
#include "sclfrntnd.h"

namespace {

	qCDEF( char *, XSLAffix_, "Folders" );

	void GetContext_(
		core::rSession &Session,
		str::string_ &XML )
	{
	qRH
		base::rContextRack Rack;
	qRB
		Rack.Init( XSLAffix_, XML, Session );

		if ( Session.User.FolderDragInProgress() )
			Rack().PutAttribute( "FolderDragging", "InProgress" );

		if ( Session.User.MailDragInProgress() )
			Rack().PutAttribute( "MailDragging", "InProgress" );

		Rack().PutAttribute( "CurrentFolder", **Session.User.Folder().Current, **frdinstc::UndefinedFolder );
	qRR
	qRT
	qRE
	}

	static void GetContent_(
		const sclrgstry::registry_ &Registry,
		core::rSession &Session,
		str::string_ &XML )
	{
	qRH
		base::rContentRack Rack;
	qRB
		Rack.Init( XSLAffix_, XML, Session );
	
		Session.User.DumpFolders( Rack );
	qRR
	qRT
	qRE
	}
}

void folders::SetLayout(
	const char *Id,
	core::rSession &Session )
{
qRH
	str::string XML, XSL;
qRB
	XML.Init(); 
	GetContent_( Session.Registry(), Session, XML );

	XSL.Init();
	sclxdhtml::LoadXSLAndTranslateTags( rgstry::tentry___( registry::definition::XSLLayoutFile, XSLAffix_ ), Session.Registry(), XSL );

	Session.FillElement( Id, XML, XSL );

	SetCasting( Id, Session );

//	Session.SwitchTo( core::folders );
qRR
qRT
qRE
}

void folders::SetCasting(
	const char *Id,
	core::rSession &Session )
{
qRH
	str::string XML, XSL;
qRB
	XML.Init();
	GetContext_( Session,  XML );

	XSL.Init();
	sclxdhtml::LoadXSLAndTranslateTags(rgstry::tentry___( registry::definition::XSLCastingFile, XSLAffix_ ), Session.Registry() , XSL );

	Session.FillElementCastings( Id, XML, XSL );
qRR
qRT
qRE
}

#define AC( name ) BASE_AC( folders, name )

AC( SelectFolder )
{
	frdinstc::sFolder Folder = frdinstc::UndefinedFolder;
	Session.GetNumericalContent( Id, **Folder );

	Session.User.SelectFolder( Folder );

	main::SetMailsLayout( Session );
	main::SetFoldersCasting( Session );
}

AC( DragFolder )
{
	frdinstc::sFolder Folder = frdinstc::UndefinedFolder;

	Session.GetNumericalContent( Id, **Folder );

	Session.User.DragFolder( Folder );

	main::SetFoldersCasting( Session);
}

AC( EndFolderDragging )
{
	Session.User.EndFolderDragging();

	main::SetFoldersCasting( Session);
}

AC( DropToFolder )
{
	frdinstc::sFolder Folder = frdinstc::UndefinedFolder;

	Session.GetNumericalContent( Id, **Folder );

	if ( Session.User.DropToFolder( Folder ) )
		main::SetFoldersLayout( Session );
	else
		main::SetMailsLayout( Session );
}
