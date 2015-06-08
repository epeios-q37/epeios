/*
	Copyright (C) 2000-2015 Claude SIMON (http://q37.info/contact/).

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

#define XMLTOL__COMPILATION

#include "xmltol.h"

#include "stf.h"

using namespace xmltol;

void xmltol::Convert(
	const xml_document_ &XMLDCM,
	xml_database_ &XMLDBS )
{
qRH
	dtr::browser__<value_row__> Browser;
	ctn::E_CMITEMt( tagged_value_, value_row__ ) TaggedValue;
	ctn::E_CMITEMt( tag_, tag_row__ ) Tag;
	tag_row__ TagRow;
	xml_database_filler__ XMLDF;
	bso::bool__ MakePop = false;
	bso::bool__ WasPush = false;
qRB
	Browser.Init( XMLDCM.GetRoot() );

	XMLDBS.Init();

	XMLDBS.tagged_values_::Init( XMLDCM.Tags.GetRoot() );

	XMLDBS.Tags = XMLDCM.Tags;

	TaggedValue.Init( XMLDCM );

	XMLDF.Init( XMLDBS );
	
	Tag.Init( XMLDCM.Tags );

	while( Browser.Position() != NONE ) {
		switch( Browser.Status() ) {
		case dtr::bFirst:
			XMLDF.PushTag( XMLDCM.Tags.GetRoot() );
			MakePop = true;
			break;
		case dtr::bLast:
		case dtr::bParent:
			if ( MakePop ) {
				XMLDF.PopTag();
			}
			MakePop = true;
			break;
		case dtr::bChild:
			if ( WasPush ) {
				MakePop = true;
				WasPush = false;
			} else {
				MakePop = false;
				WasPush = false;
			}
		case dtr::bBrother:
			TagRow = TaggedValue( Browser.Position() ).TagRow();
			
			if ( ( TagRow != NONE ) && Tag( TagRow ).IsAttribute() ) {
				XMLDF.PutAttribute( TagRow, TaggedValue( Browser.Position() ).Value );
			} else {
				XMLDF.PutValue( TaggedValue( Browser.Position() ).Value );
				if ( TagRow != NONE ) {
					XMLDF.PushTag( TagRow );
					WasPush = true;
				}
			}
			break;
		default:
			ERRc();
		}

		XMLDCM.Browse( Browser );
	}
qRR
qRT
qRE
}

void xmltol::Replace(
	tags_ &Tags,
	const xml_database_ &NewTags )
{
qRH
	ctn::E_CMITEMt( tagged_value_, value_row__ ) TaggedValue;
	dtr::browser__< value_row__ > Browser;
	tag_map TagMap;
qRB
	TagMap.Init();

	Merge( NewTags.Tags, Tags, TagMap );

	Browser.Init( NewTags.GetRoot() );
	
	TaggedValue.Init( NewTags );
	
	while( Browser.Position() != NONE ) {
		switch( Browser.Status() ) {
		case dtr::bFirst:
		case dtr::bChild:
		case dtr::bBrother:
		if ( TaggedValue( Browser.Position() ).Value.Amount() != 0 )
			Tags( TagMap( TaggedValue( Browser.Position() ).TagRow() ) ).Name = TaggedValue( Browser.Position() ).Value;
			break;
		case dtr::bLast:
		case dtr::bParent:
			break;
		default:
			ERRc();
		}
		
		NewTags.Browse( Browser );
	}
	
	Tags.Sync();
	
qRR
qRT
qRE
}

