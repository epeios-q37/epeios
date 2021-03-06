/*
	Copyright (C) 2015 Claude SIMON (http://q37.info/contact/).

	This file is part of dmnzq.

    dmnzq is free software: you can redistribute it and/or
	modify it under the terms of the GNU Affero General Public License as
	published by the Free Software Foundation, either version 3 of the
	License, or (at your option) any later version.

    dmnzq is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
	Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with dmnzq.  If not, see <http://www.gnu.org/licenses/>
*/

#include "dmnzq.h"

#include "misc.h"

#include "registry.h"

#include "scltool.h"
#include "sclerror.h"

#include "csdlec.h"

#include "err.h"
#include "cio.h"
#include "epsmsc.h"
#include "xpp.h"
#include "fnm.h"
#include "flf.h"
#include "plgn.h"
#include "csdmxs.h"

using cio::CErr;
using cio::COut;
using cio::CIn;

SCLI_DEF( dmnzq, NAME_LC, NAME_MC );

const scli::sInfo &scltool::SCLTOOLInfo( void )
{
	return dmnzq::Info;
}

static void PrintHeader_( void )
{
	COut << NAME_MC " V" VERSION << " (" WEBSITE_URL ")" << txf::nl;
	COut << "Copyright (C) " COPYRIGHT << txf::nl;
	COut << txf::pad << "Build : " __DATE__ " " __TIME__ << " (" << cpe::GetDescription() << ')' << txf::nl;
}

namespace {
	using misc::sModule;

	csdlec::library_embedded_client_core__ *Core_ = NULL;

	void ExitFunction_( void )
	{
	qRH
		str::string Message;
	qRB
		if ( Core_ != NULL ) {
			Message.Init();
			COut << sclmisc::GetBaseTranslation( "TerminatingModule", Message ) << txf::nl << txf::commit;
			delete Core_;
			COut << sclmisc::GetBaseTranslation( "ModuleTerminated", Message ) << txf::nl << txf::commit;
		}

		Core_ = NULL;
	qRR
	qRT
	qRE
	}

	void LoadModule_( const bso::char__ *ModuleFilename )
	{
	qRH
		lcl::locale SharedLocale;
		rgstry::registry SharedRegistry;
		csdlec::library_data__ LibraryData;
		lcl::meaning Meaning, MeaningBuffer;
		str::string Translation;
		err::buffer__ ErrBuffer;
		sclmisc::sRack SCLRack;
	qRB
		SharedLocale.Init();
		SharedRegistry.Init();

		SCLRack.Init( *err::qRRor, *sclerror::SCLERRORError, cio::GetCurrentSet(), scllocale::GetRack() );

		LibraryData.Init( csdleo::cRegular, ModuleFilename, &SCLRack, csdleo::mRemote );

		if ( ( Core_ = new csdlec::library_embedded_client_core__ ) == NULL )
			qRAlc();

		if ( !Core_->Init( ModuleFilename, LibraryData, err::hUserDefined ) ) {
			Meaning.Init();
			Meaning.SetValue( "UnableToLoadModule" );
			Meaning.AddTag( ModuleFilename );
			sclerror::SetMeaning( Meaning );
			qRAbort();
		}
	qRR
		Meaning.Init();
		Meaning.SetValue( "ModuleError" );
		Meaning.AddTag( ModuleFilename );

		if ( ERRType >= err::t_amount ) {
			if ( sclerror::IsErrorPending() ) {
				MeaningBuffer.Init();
				Meaning.AddTag( sclerror::GetMeaning( MeaningBuffer ) );
			} else {
				Translation.Init();
				Meaning.AddTag( sclmisc::GetBaseTranslation( "UnkonwnError", Translation ) );
			}
		} else {
			Meaning.AddTag( err::Message( ErrBuffer ) );
		}

		Translation.Init();
		sclmisc::GetBaseTranslation( Meaning, Translation );

		cio::CErr << Translation << txf::nl << txf::commit;
	qRT
	qRE
	}

	using misc::cHandler;

	void Process_(
		cHandler &Handler,
		sModule &Module,
		misc::sTimeout Timeout )
	{
	qRH
		csdmxs::rProcessing Muxer;
	qRB
		Muxer.Init( Module );
		Handler.Handle( Muxer, Timeout );
	qRR
	qRT
	qRE
	}

	void Process_( misc::sModule &Module )
	{
	qRH
		plgn::rRetriever<cHandler> Retriever;
		str::wString PluginId, PluginArguments;
		misc::sTimeout Timeout = misc::NoTimeout;
	qRB
		PluginId.Init();
		PluginArguments.Init();

		if ( Module.PluginOverride( PluginId, PluginArguments, Timeout ) ) {
			if ( PluginId.Amount() == 0 )
				qRFwk();
		} else
			PluginId.Init();

		// If 'PluginId' is empty, it (and 'PluginArguments') will not be used.

		Retriever.Init();

		sclmisc::Plug( misc::SlotPluginTarget, PluginId, PluginArguments, NULL, Retriever );

		Process_( Retriever.Plugin(), Module, Timeout );
	qRR
	qRT
	qRE
	}

	void ProcessLoop_( misc::sModule &Module )
	{
		while ( 1 )
			Process_( Module );
	}


	void Process_( void )
	{
	qRH
		TOL_CBUFFER___ Buffer;
	qRB
		atexit( ExitFunction_ );

		cio::COut.Commit();

		LoadModule_( sclmisc::MGetValue( registry::Module, Buffer ) );

		ProcessLoop_( Core_->GetCallback() );
	qRR
	qRT
	qRE
	}

	void AboutPlugin_( void )
	{
	qRH
		plgn::rRetriever<cHandler> Retriever;
	qRB
		Retriever.Init();

		sclmisc::Plug( misc::SlotPluginTarget, NULL, Retriever );

		cio::COut << Retriever.Details() << txf::nl << Retriever.Identifier() << txf::commit;
	qRR
	qRT
	qRE
	}
}

#define C( name )\
	else if ( Command == #name )\
		name##_()

int scltool::SCLTOOLMain(
	const str::string_ &Command,
	const scltool::oddities__ &Oddities )
{
	int ExitValue = EXIT_FAILURE;
qRH
qRB
	if ( Command == "Version" )
		PrintHeader_();
	else if ( Command == "License" )
		epsmsc::PrintLicense( NAME_MC );
	C( Process );
	C( AboutPlugin );
	else
		qRGnr();

	ExitValue = EXIT_SUCCESS;
qRR
qRT
qRE
	return ExitValue;
}

#undef C

Q37_GCTOR( dmnzq )
{
}