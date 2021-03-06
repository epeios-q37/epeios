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

#define XDHUJT_COMPILATION_

#include "xdhujt.h"

#include "xdhujr.h"

#include "sclmisc.h"

#include "stsfsm.h"

using namespace xdhujt;

#define C( name, entry )\
	case sn##name:\
		sclmisc::MGetValue( xdhujr::script::entry, Buffer );\
		break

const str::string_ &xdhujt::GetTaggedScript(
	script_name__ Script,
	str::string_ &Buffer )
{
	switch ( Script ) {
	C( Log, Log );
	C( DialogAlert, dialog::Alert );
	C( DialogConfirm, dialog::Confirm );
	C( ElementFiller, ElementFiller );
	C( DocumentFiller, DocumentFiller );
	C( CastingsFiller, CastingsFiller );
	C( PropertySetter, property::Setter );
	C( PropertyGetter, property::Getter );
	C( AttributeSetter, attribute::Setter );
	C( AttributeGetter, attribute::Getter );
	C( AttributeRemover, attribute::Remover );
	C( WidgetContentRetriever, widget::ContentRetriever );
	C( ContentSetter, content::Setter );
	C( ContentGetter, content::Getter );
	C( WidgetFocuser, widget::Focuser );
	C( Focuser, Focuser );
	C( EventHandlersSetter, EventHandlersSetter );
	C( CastsSetter, CastsSetter );
	C( WidgetsInstantiator, WidgetsInstantiator );
	default:
		qRFwk();
		break;
	}

	return Buffer;
}

namespace {
	void AppendTag_(
		const char *Name,
		const nstring___ &Value,
		str::strings_ &Names,
		str::strings_ &Values )
	{
	qRH
		str::string NameForRawValue;
		str::string EscapedValue;
		TOL_CBUFFER___ Buffer;
	qRB
		Names.Append( str::string( Name ) );
		EscapedValue.Init();
		xdhcmn::Escape( str::string( Value.UTF8( Buffer ) ), EscapedValue, '"' );
		Values.Append( EscapedValue );

		NameForRawValue.Init( Name );
		NameForRawValue.Append( '_' );

		Names.Append( NameForRawValue );
		Values.Append( str::string( Value.UTF8( Buffer ) ) );
	qRR
	qRT
	qRE
	}

	void SubstituteTags_(
		str::string_ &Script,	// Script with tags. When returning, tags are substitued.
		va_list ValueList,
		... )	// The list of the tag name, as 'const char *', with 'NULL' as end marker.
	{
	qRH
		str::strings Names, Values;
		va_list NameList;
		const bso::char__ *Name = NULL;
	qRB
		Names.Init();
		Values.Init();

		va_start( NameList, ValueList );

		Name = va_arg( NameList, const bso::char__ * );

		while ( Name != NULL ) {
			AppendTag_( Name, va_arg( ValueList, const nchar__ * ), Names, Values );

			Name = va_arg( NameList, const bso::char__ * );
		}

		tagsbs::SubstituteLongTags( Script, Names, Values );
	qRR
	qRT
		va_end( NameList );
	qRE
	}
}

#define D( name )\
	E_CDEF( char *, name##_, #name )

D( Message );
D( Id );
D( Name );
D( Value );
D( Method );
D( XML );
D( XSL );
D( Title );
D( CloseText );
D( Cast );
D( Ids );
D( Events );
D( Casts );
D( Types );
D( ParametersSets );

#define S( name, ... )\
	case sn##name:\
	SubstituteTags_( TaggedScript, List, __VA_ARGS__ );\
	break\

void xdhujt::GetScript(
	script_name__ ScriptName,
	str::string_ &Script,
	va_list List )
{
qRH
	str::string TaggedScript;
qRB
	TaggedScript.Init();
	GetTaggedScript( ScriptName, TaggedScript );

	switch ( ScriptName ) {
	S( Log, Message_, NULL );
	S( DialogAlert, XML_, XSL_, Title_, CloseText_, NULL );
	S( DialogConfirm, XML_, XSL_, Title_, CloseText_, NULL );
	S( AttributeSetter, Id_, Name_, Value_, NULL  );
	S( AttributeGetter, Id_, Name_, NULL  );
	S( AttributeRemover, Id_, Name_, NULL  );
	S( PropertySetter, Id_, Name_, Value_, NULL );
	S( PropertyGetter, Id_, Name_, NULL );
	S( ElementFiller, Id_, XML_, XSL_, NULL );
	S( DocumentFiller, XML_, XSL_, NULL );
	S( CastingsFiller, Id_, XML_, XSL_, NULL );
	S( ContentSetter, Id_, Value_, NULL );
	S( ContentGetter, Id_, NULL );
	S( WidgetContentRetriever, Id_, Method_, NULL );
	S( WidgetFocuser, Id_, Method_, NULL );
	S( Focuser, Id_, NULL );
	S( EventHandlersSetter, Ids_, Events_, NULL );
	S( CastsSetter, Ids_, Casts_, NULL );
	S( WidgetsInstantiator, Ids_, Types_, ParametersSets_, NULL );
	default:
		qRFwk();
		break;
	}

	Script.Append( TaggedScript );
qRR
qRT
qRE
}

const str::string_ &xdhujt::GetScript(
	script_name__ ScriptName,
	str::string_ *Buffer,
	... )
{
qRH
	va_list List;
qRB
	va_start( List, Buffer );
	
	GetScript( ScriptName, *Buffer, List );
qRR
qRT
	va_end( List );
qRE
	return *Buffer;
}

namespace {
	void SetXML_(
		const nstring___ &Message,
		str::string_ &XML )
	{
	qRH
		flx::E_STRING_TOFLOW___ STOFlow;
		xml::writer Writer;
		str::string Buffer;
	qRB
		STOFlow.Init( XML );
		Writer.Init( STOFlow, xml::oCompact, xml::e_Default );

		Buffer.Init();
		Writer.PutValue( Message.UTF8( Buffer ), "Content" );
	qRR
	qRT
	qRE
	}

	inline void SetXSL_( str::string_ &XSL )
	{
		XSL.Append("<?xml version=\"1.0\" encoding=\"utf-8\"?>\
			<xsl:stylesheet version=\"1.0\"\
			                xmlns:xsl=\"http://www.w3.org/1999/XSL/Transform\">\
				<xsl:output method=\"text\"\
					        encoding=\"utf-8\"/>\
				<xsl:template match=\"/\">\
					<xsl:value-of select=\"Content\"/>\
				</xsl:template>\
			</xsl:stylesheet>\
		");
	}
}

void xdhujt::scripter::Report(
	const nstring___ &Message,
	str::string_ &Script )
{
qRH
	str::string XML, XSL, CloseText;
qRB
	XML.Init();
	SetXML_( Message, XML );

	XSL.Init();
	SetXSL_( XSL );

	CloseText.Init();
	sclmisc::GetBaseTranslation( "CloseText", CloseText );

	Script.Init();
	scripter::DialogAlert( XML, XSL, nstring___(), CloseText, Script );
qRR
qRT
qRE
}
