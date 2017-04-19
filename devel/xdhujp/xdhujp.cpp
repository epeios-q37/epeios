/*
	Copyright (C) 1999-2017 Claude SIMON (http://q37.info/contact/).

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

#define XDHUJP__COMPILATION

#include "xdhujp.h"

#include "xdhujr.h"
#include "xdhutl.h"

#include "sclrgstry.h"
#include "sclmisc.h"

using namespace xdhujp;

using xdhutl::nstring___;
using xdhutl::nchar__;
using xdhujs::script_name__;

static const char *Execute_(
	callback__  &Callback,
	script_name__ ScriptName,
	TOL_CBUFFER___ *Buffer,
	va_list List )
{
	const char *Result = NULL;
qRH
	str::string Script;
qRB
	Script.Init();
	GetScript( ScriptName, Script, List );

	Result = Callback.Execute( Script, Buffer );
qRR
qRT
qRE
	return Result;
}

const char *xdhujp::Execute(
	callback__  &Callback,
	script_name__ ScriptName,
	TOL_CBUFFER___ *Buffer,
	... )
{
	const char *Result = NULL;
qRH
	va_list List;
qRB
	va_start( List, Buffer );

	Result = Execute_( Callback, ScriptName, Buffer, List );
qRR
qRT
	va_end( List );
qRE
	return Result;
}

static void AlertConfirm_(
	callback__ &Callback,
	script_name__ ScriptName,
	TOL_CBUFFER___ *Result,
	va_list List )
{
	// NOTA : we use variables, because if we put 'va_arg()' directly as parameter to below function, it's not sure that they are called in the correct order.
	const nchar__ *XML = va_arg( List, const nchar__ * );
	const nchar__ *XSL = va_arg( List, const nchar__ * );
	const nchar__ *Title = va_arg( List, const nchar__ * );
	const nchar__ *CloseText = va_arg( List, const nchar__ * );

	Execute( Callback, ScriptName, Result, XML, XSL, Title, CloseText );
}

static void Append_(
	const str::string_ &Item,
	str::string_ &Tag )
{
	Tag.Append('"');
	Tag.Append( Item );
	Tag.Append('"');
}

static void HandleEvents_(
	const str::strings_ &Ids,
	const xdhutl::event_abstracts_ &Abstracts,
	str::string_ &IdsTag,
	str::string_ &EventsTag )
{
	sdr::row__ Row = qNIL;

	if ( Ids.Amount() != Abstracts.Amount() )
		qRFwk();

	Row = Ids.First();

	IdsTag.Append( "[ " );
	EventsTag.Append( "[ ");

	while ( Row != qNIL ) {
		Append_( Ids( Row ), IdsTag );
		Append_( Abstracts( Row ).Event, EventsTag );

		Row = Ids.Next( Row );

		if ( Row != qNIL ) {
			IdsTag.Append( ", " );
			EventsTag.Append( ", " );
		}
	}

	IdsTag.Append( " ]" );
	EventsTag.Append( " ]");
}

static void HandleEvents_(
	callback__ &Callback,
	const xdhcmn::digest_ &Descriptions )
{
qRH
	str::strings Ids;
	xdhutl::event_abstracts Abstracts;
	str::string IdsTag, EventsTag;
qRB
	Ids.Init();
	Abstracts.Init();
	xdhutl::FillEventAbstracts( Descriptions, Ids, Abstracts );

	if ( Ids.Amount() != 0 ) {
		IdsTag.Init();
		EventsTag.Init();
		HandleEvents_( Ids, Abstracts, IdsTag, EventsTag );

		Execute( Callback, xdhujs::snEventHandlersSetter, NULL,nstring___( IdsTag ).Internal()(), nstring___( EventsTag ).Internal()() );
	}
qRR
qRT
qRE
}

static void HandleWidgets_(
	const str::strings_ &Ids,
	const str::strings_ &Types,
	const str::strings_ &ParametersSets,
	str::string_ &IdsTag,
	str::string_ &TypesTag,
	str::string_ &ParametersSetsTag )
{
	sdr::row__ Row = qNIL;

	if ( Ids.Amount() != Types.Amount() )
		qRFwk();

	if ( Ids.Amount() != ParametersSets.Amount() )
		qRFwk();

	Row = Ids.First();

	IdsTag.Append( "[ " );
	TypesTag.Append( "[ ");
	ParametersSetsTag.Append( "[ ");

	while ( Row != qNIL ) {
		Append_( Ids( Row ), IdsTag );
		Append_( Types( Row ), TypesTag );
		Append_( ParametersSets( Row ), ParametersSetsTag );

		Row = Ids.Next( Row );

		if ( Row != qNIL ) {
			IdsTag.Append( ", " );
			TypesTag.Append( ", " );
			ParametersSetsTag.Append( ", " );
		}
	}

	IdsTag.Append( " ]" );
	TypesTag.Append( " ]");
	ParametersSetsTag.Append( " ]");
}

static void HandleWidgets_(
	callback__ &Callback,
	const xdhcmn::digest_ &Descriptions )
{
qRH
	str::strings Ids, Types, ParametersSets;
	str::string IdsTag, TypesTag, ParametersSetsTag;
qRB
	Ids.Init();
	Types.Init();
	ParametersSets.Init();
	xdhutl::ExtractWidgetsTypesAndParametersSets( Descriptions, Ids, Types, ParametersSets );

	if ( Ids.Amount() != 0 ) {
		IdsTag.Init();
		TypesTag.Init();
		ParametersSetsTag.Init();
		HandleWidgets_( Ids, Types, ParametersSets, IdsTag, TypesTag, ParametersSetsTag );

		Execute( Callback, xdhujs::snWidgetsInstantiator, NULL, nstring___( IdsTag ).Internal()(), nstring___( TypesTag ).Internal()(), nstring___( ParametersSetsTag ).Internal()() );
	}
qRR
qRT
qRE
}

static void FillDocumentOrElement_(
	callback__ &Callback,
	const nchar__ *Id,	// If 'Id' != NULL, it's the id of the element to apply to, otherwise it applies to the document.
	const nchar__ *XML,
	const nchar__ *XSL )
{
qRH
	TOL_CBUFFER___ Result;
	str::string RawDigests;
	xdhcmn::digest Digests, Events, Widgets;
	xdhcmn::retriever__ Retriever;
qRB
	if ( Id == NULL )
		RawDigests.Init( Execute( Callback, xdhujs::snDocumentFiller, &Result, XML, XSL ) );
	else
		RawDigests.Init( Execute( Callback, xdhujs::snElementFiller, &Result, Id, XML, XSL ) );

	Digests.Init();
	xdhcmn::Split( RawDigests, Digests );

	Retriever.Init( Digests );

	Events.Init();
	Retriever.GetTable( Events );

	Widgets.Init();
	Retriever.GetTable( Widgets );

	HandleEvents_( Callback, Events );

	HandleWidgets_( Callback, Widgets );
qRR
qRT
qRE
}

static void FillDocument_(
	callback__ &Callback,
	va_list List )
{
	// NOTA : we use variables, because if we put 'va_arg()' directly as parameter to below function, it's not sure that they are called in the correct order.
	const nchar__ *XML = va_arg( List, const nchar__ * );
	const nchar__ *XSL = va_arg( List, const nchar__ * );

	FillDocumentOrElement_( Callback, NULL, XML, XSL );
}

static void FillElement_(
	callback__ &Callback,
	va_list List )
{
	// NOTA : we use variables, because if we put 'va_arg()' directly as parameter to below function, it's not sure that they are called in the correct order.
	const nchar__ *Id = va_arg( List, const nchar__ * );
	const nchar__ *XML = va_arg( List, const nchar__ * );
	const nchar__ *XSL = va_arg( List, const nchar__ * );

	FillDocumentOrElement_( Callback, Id, XML, XSL );
}

static void HandleCastings_(
	const str::strings_ &Ids,
	const str::strings_ &Castings,
	str::string_ &IdsTag,
	str::string_ &CastingsTag )
{
	sdr::row__ Row = qNIL;

	if ( Ids.Amount() != Castings.Amount() )
		qRFwk();

	Row = Ids.First();

	IdsTag.Append( "[ " );
	CastingsTag.Append( "[ ");

	while ( Row != qNIL ) {
		IdsTag.Append('"');
		IdsTag.Append(Ids( Row) );
		IdsTag.Append('"');

		CastingsTag.Append('"');
		CastingsTag.Append( Castings( Row ) );
		CastingsTag.Append('"');

		Row = Ids.Next( Row );

		if ( Row != qNIL ) {
			IdsTag.Append( ", " );
			CastingsTag.Append( ", " );
		}
	}

	IdsTag.Append( " ]" );
	CastingsTag.Append( " ]");
}

static void HandleCastings_(
	callback__ &Callback,
	const xdhcmn::digest_ &Descriptions )
{
qRH
	str::strings Ids, Castings;
	str::string IdsTag, CastingsTag;
qRB
	Ids.Init();
	Castings.Init();
	xdhutl::FillCastings( Descriptions, Ids, Castings );

	if ( Ids.Amount() ) {
		IdsTag.Init();
		CastingsTag.Init();
		HandleCastings_( Ids, Castings, IdsTag, CastingsTag );

		Execute( Callback, xdhujs::snCastsSetter, NULL, nstring___( IdsTag ).Internal()(), nstring___( CastingsTag ).Internal()() );
	}
qRR
qRT
qRE
}

static void FillCastings_(
	callback__ &Callback,
	const nchar__ *Id,
	const nchar__ *XML,
	const nchar__ *XSL )
{
qRH
	TOL_CBUFFER___ Result;
	str::string RawDigests;
	xdhcmn::digest Castings;
qRB
	RawDigests.Init( Execute( Callback, xdhujs::snCastingsFiller, &Result, Id, XML, XSL ) );

	Castings.Init();
	xdhcmn::Split( RawDigests, Castings );

	HandleCastings_( Callback, Castings );
qRR
qRT
qRE
}

static void FillCastings_(
	callback__ &Callback,
	va_list List )
{
	// NOTA : we use variables, because if we put 'va_arg()' directly as parameter to below function, it's not sure that they are called in the correct order.
	const nchar__ *Id = va_arg( List, const nchar__ * );
	const nchar__ *XML = va_arg( List, const nchar__ * );
	const nchar__ *XSL = va_arg( List, const nchar__ * );

	FillCastings_( Callback, Id, XML, XSL );
}


static void FillData_(
	callback__ &Callback,
	const nchar__ *Id )
{
qRH
	TOL_CBUFFER___ Result;
	str::string RawDigests;
qRB
	RawDigests.Init( Execute(Callback, xdhujs::snDataFiller, &Result, Id ));

	cio::COut << ">>>>>>>>>>>>>>>>> " << RawDigests << " <<<<<<<<<<<<<<<<<<<<<" << txf::nl << txf::commit;

	// TODO.
qRR
qRT
qRE
}

static void FillData_(
	callback__ &Callback,
	va_list List)
{
	const nchar__ *Id = va_arg(List, const nchar__ *);

	FillData_( Callback, Id );
}

static void GetContent_(
	callback__ &Callback,
	const nchar__ *Id,
	TOL_CBUFFER___ *Result )
{
qRH
	str::string Args, Method;
	nstring___ WidgetAttributeName;;
	TOL_CBUFFER___ Buffer;
qRB
	WidgetAttributeName.Init( Callback.GetWidgetAttributeName( Buffer ) );
	Args.Init( Execute( Callback, xdhujs::snAttributeGetter, &Buffer, Id, WidgetAttributeName.Internal()()) );

	Method.Init();

	if ( Args.Amount() != 0 )	// 'true' if the element 'Id' is a widget.
		xdhutl::ExtractWidgetContentRetrievingMethod( Args, Method );

	if ( Method.Amount() == 0 )
		Execute( Callback, xdhujs::snContentGetter, Result, Id );
	else
		Execute( Callback, xdhujs::snWidgetContentRetriever, Result, Id, nstring___( Method ).Internal()() );
qRR
qRT
qRE
}

static void GetContent_(
	callback__ &Callback,
	TOL_CBUFFER___ *Content,
	va_list List )
{
	GetContent_( Callback, va_arg( List, const nchar__ * ), Content );
}

static void Focus_(
	callback__ &Callback,
	const nchar__ *Id )
{
qRH
	str::string Args, Method;
	nstring___ WidgetAttributeName;
	TOL_CBUFFER___ Buffer;
qRB
	WidgetAttributeName.Init( Callback.GetWidgetAttributeName( Buffer ) );
	Args.Init( Execute( Callback, xdhujs::snAttributeGetter, &Buffer, Id, WidgetAttributeName.Internal()()) );

	Method.Init();

	if ( Args.Amount() != 0 )
		xdhutl::ExtractWidgetFocusingMethod( Args, Method );

	if ( Method.Amount() == 0 )
		Execute( Callback, xdhujs::snFocuser, NULL, Id );
	else
		Execute( Callback, xdhujs::snWidgetFocuser, NULL, Id, nstring___( Method ).Internal()() );
qRR
qRT
qRE
}

static void Select_(
	callback__ &Callback,
	const nchar__ *Id )
{
qRH
	str::string Args, Method;
	nstring___ WidgetAttributeName;
	TOL_CBUFFER___ Buffer;
qRB
	WidgetAttributeName.Init( Callback.GetWidgetAttributeName( Buffer ) );
	Args.Init( Execute( Callback, xdhujs::snAttributeGetter, &Buffer, Id, WidgetAttributeName.Internal()()) );

	Method.Init();

	if ( Args.Amount() != 0 )
		xdhutl::ExtractWidgetSelectionMethod( Args, Method );

	if ( Method.Amount() == 0 )
		Execute( Callback, xdhujs::snSelector, NULL, Id );
	else
		Execute( Callback, xdhujs::snWidgetSelector, NULL, Id, nstring___( Method ).Internal()() );
qRR
qRT
qRE
}

static void Focus_(
	callback__ &Callback,
	va_list List )
{
	Focus_( Callback, va_arg( List, const nchar__ * ) );
}

static void Select_(
	callback__ &Callback,
	va_list List )
{
	Select_( Callback, va_arg( List, const nchar__ * ) );
}

static void GetResult_(
	callback__ &Callback,
	const nchar__ *Id,
	TOL_CBUFFER___ *Result )
{
qRH
	str::string ResultAttributeName;
	TOL_CBUFFER___ Buffer;
qRB
	ResultAttributeName.Init( Callback.GetResultAttributeName( Buffer ) );
	Execute( Callback, xdhujs::snAttributeGetter, Result, Id, nstring___( ResultAttributeName ).Internal()() );
qRR
qRT
qRE
}

static void GetResult_(
	callback__ &Callback,
	TOL_CBUFFER___ *Result,
	va_list List )
{
	GetResult_( Callback, va_arg( List, const nchar__ * ), Result );
}

static script_name__ Convert_( xdhcmn::function__ Function )
{
	switch ( Function ) {
	case xdhcmn::fLog:
		return xdhujs::snLog;
		break;
	case xdhcmn::fAlert:
		return xdhujs::snDialogAlert;
		break;
	case xdhcmn::fConfirm:
		return xdhujs::snDialogConfirm;
		break;
	case xdhcmn::fSetProperty:
		return xdhujs::snPropertySetter;
		break;
	case xdhcmn::fGetProperty:
		return xdhujs::snPropertyGetter;
		break;
	case xdhcmn::fSetAttribute:
		return xdhujs::snAttributeSetter;
		break;
	case xdhcmn::fGetAttribute:
		return xdhujs::snAttributeGetter;
		break;
	case xdhcmn::fRemoveAttribute:
		return xdhujs::snAttributeRemover;
		break;
	case xdhcmn::fSetContent:
		return xdhujs::snContentSetter;
		break;
	case xdhcmn::fGetContent:
		qRFwk();
		break;
	case xdhcmn::fGetResult:
		qRFwk();
		break;
	case xdhcmn::fFocus:
		qRFwk();
		break;
	case xdhcmn::fSelect:
		qRFwk();
		break;
	case xdhcmn::fFillDocument:
		qRFwk();
		break;
	case xdhcmn::fFillElement:
		qRFwk();
		break;
	case xdhcmn::fFillCastings:
		qRFwk();
		break;
	case xdhcmn::fFillData:
		qRFwk();
		break;
	default:
		qRFwk();
		break;
	}

	return xdhujs::sn_Undefined;	// To avoid a warning.
}

void xdhujp::proxy_callback__::XDHCMNProcess(
	xdhcmn::function__ Function,
	TOL_CBUFFER___ *Result,
	va_list List )
{
	switch ( Function ) {
	case xdhcmn::fSetProperty:
	case xdhcmn::fGetProperty:
	case xdhcmn::fSetAttribute:
	case xdhcmn::fGetAttribute:
	case xdhcmn::fRemoveAttribute:
	case xdhcmn::fSetContent:
	case xdhcmn::fLog:
		Execute_( C_(), Convert_( Function ), Result, List );
		break;
	case xdhcmn::fAlert:
	case xdhcmn::fConfirm:
		AlertConfirm_( C_(), Convert_( Function ), Result, List );
		break;
	case xdhcmn::fGetResult:
		GetResult_( C_(), Result, List );
		break;
	case xdhcmn::fGetContent:
		GetContent_( C_(), Result, List );
		break;
	case xdhcmn::fFocus:
		Focus_( C_(), List);
		break;
	case xdhcmn::fSelect:
		Select_( C_(), List);
		break;
	case xdhcmn::fFillDocument:
		FillDocument_( C_(), List );
		break;
	case xdhcmn::fFillElement:
		FillElement_( C_(), List );
		break;
	case xdhcmn::fFillCastings:
		FillCastings_( C_(), List);
		break;
	case xdhcmn::fFillData:
		FillData_( C_(), List);
		break;
	default:
		qRFwk();
		break;
	}
}

