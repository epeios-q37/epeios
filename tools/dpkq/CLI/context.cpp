#include "context.h"
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

#include "context.h"

#include "registry.h"

#include "dpkq.h"

#include "sclm.h"

using namespace context;

namespace {
	static void Retrieve_(
		xml::parser___ &Parser,
		const char *AwaitedTarget,
		dpkctx::context_ &Context )
	{
	qRH
		bso::bool__ Continue = true;
		str::string Target;
	qRB

		Target.Init();

		while ( Continue ) {
			switch ( Parser.Parse( xml::tfObvious | xml::tfStartTagClosed ) ) {
			case xml::tStartTag:
				if ( Parser.TagName() != "Context" )
					qRGnr();

				break;
			case xml::tAttribute:
				if ( Parser.AttributeName() == "Target" ) {
					if ( Target.Amount() != 0 )
						qRGnr();

					Target = Parser.Value();
				} else if ( Parser.AttributeName() != "TimeStamp" )
					qRGnr();
				break;
			case xml::tStartTagClosed:
				if ( Target != AwaitedTarget )
					qRGnr();

				dpkctx::Retrieve( Parser, Context );
				break;
			case xml::t_Processed:
				Continue = false;
				break;
			default:
				qRGnr();
				break;
			}
		}
	qRR
	qRT
	qRE
	}
}

namespace {
	void Retrieve_(
		const str::string_ &FileName,
		dpkctx::context_ &Context )
	{
	qRH
		xml::parser___ Parser;
		flf::file_iflow___ FFlow;
		xtf::extended_text_iflow__ XFlow;
	qRB
		if ( fil::Exists( FileName ) ) {
      if ( FFlow.Init( FileName ) != tol::rSuccess )
				sclm::ReportFileOpeningErrorAndAbort( FileName );

      XFlow.Init( FFlow, utf::f_Default );

      Parser.Init( XFlow, xml::eh_Default );

      Retrieve_( Parser, NAME_LC, Context );
		} else {
			//		COut << "Unable to find context file '" << FileName << "'! It will be created at exit." << txf::nl;
		}
	qRR
	qRT
	qRE
	}
}

void context::Retrieve( dpkctx::context_ &Context )
{
qRH
	str::wString Filename;
qRB
	Filename.Init();

	if ( !sclm::BGetValue(registry::Context, Filename, err::h_Default) )
		sclm::ReportAndAbort( "ContextFileNotSpecifiedError" );

	Retrieve_( Filename, Context );
qRR
qRT
qRE
}

namespace {
	namespace {
		void DumpContext_(
			const dpkctx::context_ &Context,
			xml::rWriter &Writer )
		{
			tol::buffer__ Buffer;

			Writer.PushTag( "Context" );
			Writer.PutAttribute( "Target", NAME_LC );
			Writer.PutAttribute( "TimeStamp", tol::DateAndTime( Buffer ) );

			Dump( Context, Writer );

			Writer.PopTag();
		}
	}

	void DumpWithoutBackup_(
		const dpkctx::context_ &Context,
		const str::string_ &FileName )
	{
	qRH
		flf::file_oflow___ FFlow;
		txf::text_oflow__ TFlow;
		xml::rWriter Writer;
	qRB
		if ( FFlow.Init( FileName ) != tol::rSuccess )
			sclm::ReportFileOpeningErrorAndAbort( FileName );

		TFlow.Init( FFlow );

		Writer.Init( TFlow, xml::oIndent, xml::eUTF_8 );

		DumpContext_( Context, Writer );
	qRR
	qRT
	qRE
	}
}

namespace {
	void Dump_(
		const dpkctx::context_ &Context,
		const str::string_ &FileName )
	{
	qRH
		bso::bool__ Backuped = false;
	qRB
		sclm::CreateBackupFile( FileName );

		Backuped = true;

		DumpWithoutBackup_( Context, FileName );
	qRR
		if ( Backuped )
			sclm::RecoverBackupFile( FileName );
	qRT
	qRE
	}
}

void context::Dump( const dpkctx::context_ &Context )
{
qRH
	str::wString Filename;
qRB
	Filename.Init();

	if ( !sclm::BGetValue(registry::Context, Filename, err::h_Default) )
		sclm::ReportAndAbort( "ContextFileNotSpecifiedError" );

	Dump_( Context, Filename );
qRR
qRT
qRE
}


