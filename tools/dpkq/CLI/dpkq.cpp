/*
	Copyright (C) 2010-2015 Claude SIMON (http://q37.info/contact/).

	This file is part of dpkq.

    dpkq is free software: you can redistribute it and/or
	modify it under the terms of the GNU Affero General Public License as
	published by the Free Software Foundation, either version 3 of the
	License, or (at your option) any later version.

    dpkq is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
	Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with dpkq.  If not, see <http://www.gnu.org/licenses/>
*/

#include "dpkq.h"

#include "context.h"
#include "data.h"
#include "registry.h"

#include "sclt.h"
#include "scle.h"
#include "sclm.h"

#include "err.h"
#include "cio.h"
#include "epsmsc.h"
#include "fnm.h"
#include "flf.h"

using cio::CErr;
using cio::COut;
using cio::CIn;

SCLI_DEF( dpkq, NAME_LC, NAME_MC );

static void PrintHeader_( void )
{
	COut << NAME_MC " V" VERSION << " (" WEBSITE_URL ")" << txf::nl;
	COut << "Copyright (C) " COPYRIGHT << txf::nl;
	COut << txf::pad << "Build : " __DATE__ " " __TIME__ << " (" << cpe::GetDescription() << ')' << txf::nl;
}


using data::sId;

using data::dData;
using data::wData;

void LaunchViewer_(
	sId RecordId,
	sId TableId,
	const dpktbl::table_ &Table,
	const dpkctx::context_ &Context,
	const str::string_ &RecordLabel,
	const str::string_ &TableLabel,
	const str::string &DataFilename,
	const str::string &OutputFilename,
	const str::string_ &XSLFilename )
{
qRH
	str::string Viewer;
	TOL_CBUFFER___ SBuffer;
	bso::integer_buffer__ IBuffer;
	tagsbs::tvalues TaggedValues;
qRB
	Viewer.Init();
	sclm::OGetValue( registry::Viewer, Viewer );

	if ( ( Viewer.Amount() != 0 ) && ( OutputFilename.Amount() != 0 ) ) {
		TaggedValues.Init();
		TaggedValues.Append("RI", bso::Convert( RecordId, IBuffer ) );
		TaggedValues.Append("RL", RecordLabel );
		TaggedValues.Append("TI", bso::Convert( TableId, IBuffer ) );
		TaggedValues.Append("TL", TableLabel);
		TaggedValues.Append("TA", bso::Convert(Table.Records.Amount(), IBuffer));
		TaggedValues.Append("TS", bso::Convert(Table.Skipped(), IBuffer));
		TaggedValues.Append("SA", bso::Convert(Context.Pool.S_.Session, IBuffer));
		TaggedValues.Append("CA", bso::Convert(Context.Pool.S_.Cycle, IBuffer));
		TaggedValues.Append("SS", bso::Convert(data_d::GetSkippedAmount(Context.Pool.S_.Session, Context.Pool, Table.Records), IBuffer));
		TaggedValues.Append("CS", bso::Convert(data_d::GetSkippedAmount(Context.Pool.S_.Cycle, Context.Pool, Table.Records), IBuffer));
		TaggedValues.Append("Data", DataFilename );
		TaggedValues.Append("XSL", XSLFilename );
		TaggedValues.Append("Output",OutputFilename );
		tagsbs::SubstituteLongTags( Viewer, TaggedValues, '$' );
		tol::System( Viewer.Convert( SBuffer ) );
	}
qRR
qRT
qRE
}

void Process_( void )
{
qRH
	str::wString Namespace;
	str::string DataFilename;
	wData Data;
	dpkctx::context Context;
	str::string OutputFilename;
	str::string XSLFilename;
	bso::uint__ SessionMaxDuration = 0;
	str::string Label, TableLabel;
	sId Id = 0;
qRB
	data::Initialize();

	Id = sclm::OGetUInt( registry::Id, data::All );

	switch ( Id ) {
	case data::Undefined:
		Id = 0;
		break;
	case 0:
		Id = data::All;
		break;
	default:
		break;
	}

	DataFilename.Init();
	if ( !sclm::BGetValue(registry::Data, DataFilename, err::h_Default) )
		sclm::ReportAndAbort( "DataFileNotSpecifiedError" );

	OutputFilename.Init();
	if ( !sclm::BGetValue(registry::Output, OutputFilename, err::h_Default) )
		sclm::ReportAndAbort( "OutputFileNotSpecifiedError" );

	XSLFilename.Init();
	sclm::OGetValue( registry::XSL, XSLFilename );

	Context.Init();
	context::Retrieve( Context);

	Data.Init();
	data::Retrieve( DataFilename, Data );

	SessionMaxDuration = sclm::OGetUInt( registry::SessionMaxDuration, 0 );

	Label.Init();
	TableLabel.Init();
	Id = data::Display( Id, Data, XSLFilename, SessionMaxDuration, Label, TableLabel, Context, OutputFilename );

	context::Dump( Context );

	LaunchViewer_( Id, *Data.Last() + 1, Data( Data.Last() ), Context, Label, TableLabel, DataFilename, OutputFilename, XSLFilename );
qRR
qRT
qRE
}

#define C( name )\
	else if ( Command == #name )\
		name##_()

int sclt::SCLTMain(
	const str::string_ &Command,
	const sclt::oddities__ &Oddities )
{
	int ExitValue = EXIT_FAILURE;
qRH
qRB
	if ( Command == "Version" )
		PrintHeader_();
	else if ( Command == "License" )
		epsmsc::PrintLicense( NAME_MC );
		C( Process );
	else
		qRGnr();

	ExitValue = EXIT_SUCCESS;
qRR
qRT
qRE
	return ExitValue;
}

const scli::sInfo &sclt::SCLTInfo( void )
{
	return dpkq::Info;
}
