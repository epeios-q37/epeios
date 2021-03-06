/*
	Copyright (C) 2015 Claude SIMON (http://q37.info/contact/).

	This file is part of fwtchrq.

    fwtchrq is free software: you can redistribute it and/or
	modify it under the terms of the GNU Affero General Public License as
	published by the Free Software Foundation, either version 3 of the
	License, or (at your option) any later version.

    fwtchrq is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
	Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with fwtchrq.  If not, see <http://www.gnu.org/licenses/>
*/

#include "misc.h"

#include "registry.h"

#include "cio.h"
#include "flf.h"

using namespace misc;

dwtbsc::exclusions_handling__ misc::GetExclusionsHandling_( const sclrgstry::registry_ &Registry )
{
	dwtbsc::exclusions_handling__ ExclusionsHandling = dwtbsc::ehNone;
qRH
	str::string RawExclusionHandling;
qRB
	RawExclusionHandling.Init();
	
	if ( sclrgstry::OGetValue(Registry, registry::ExclusionsHandling, RawExclusionHandling) ) {
		if ( RawExclusionHandling == "Regular" )
			ExclusionsHandling = dwtbsc::ehRegular;
		else if ( RawExclusionHandling == "Keep" ) 
			ExclusionsHandling = dwtbsc::ehKeep;
		else if ( RawExclusionHandling == "Skip" ) 
			ExclusionsHandling = dwtbsc::ehSkip;
		else if ( RawExclusionHandling == "None" ) 
			ExclusionsHandling = dwtbsc::ehNone;
		else
			sclrgstry::ReportBadOrNoValueForEntryErrorAndAbort( registry::ExclusionsHandling );
	}
qRR
qRT
qRE
	return ExclusionsHandling;
}


void misc::Append(
	const char *Tag,
	const str::string_ &Value,
	str::strings_ &Tags,
	str::strings_ &Values )
{
	if ( Tags.Append( str::string( Tag ) ) != Values.Append( Value ) )
		qRGnr();
}

void misc::Append(
	const char *Tag,
	const rgstry::entry___ &Entry,
	const sclrgstry::registry_ &Registry,
	str::strings_ &Tags,
	str::strings_ &Values )
{
qRH
	str::string Value;
qRB
	Value.Init();
	sclrgstry::MGetValue( Registry, Entry, Value );

	Append( Tag, Value, Tags, Values );
qRR
qRT
qRE
}

void misc::Dump(
	dwtftr::drow__ Root,
	const dwtftr::file_tree_ &Tree,
	const fnm::name___ &Filename )
{
qRH
	sclmisc::text_oflow_rack___ Rack;
	xml::writer Writer;
qRB
	Writer.Init( Rack.Init( Filename ), xml::oIndent, xml::e_Default );

	Writer.PushTag( MISC_NAME_MC );

	Writer.PushTag( "FileTree" );

	Tree.Dump( Root, Writer );

	Writer.PopTag();

	Writer.PopTag();
qRR
	Rack.HandleError();
qRT
qRE
}

void misc::Dump(
	const dwtmov::movings_ &Movings,
	dwtcpr::drow__ SceneRoot,
	const dwtcpr::scene_ &Scene,
	const fnm::name___ &Filename )
{
qRH
	sclmisc::text_oflow_rack___ Rack;
	xml::writer Writer;
qRB
	Writer.Init( Rack.Init( Filename ), xml::oIndent, xml::e_Default );

	Writer.PushTag( MISC_NAME_MC );

	Writer.PushTag( "Dirs" );

	dwtmov::Dump( Movings, Writer );

	Writer.PopTag();

	Writer.PushTag( "Files" );

	dwtcpr::Dump( SceneRoot, Scene, Writer );

	Writer.PopTag();

	Writer.PopTag();
qRR
	Rack.HandleError();
qRT
qRE
}


