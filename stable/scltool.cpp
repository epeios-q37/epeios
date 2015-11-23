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

#define SCLTOOL__COMPILATION

#include "scltool.h"

#include "cio.h"
#include "tagsbs.h"

#include "sclrgstry.h"
#include "scllocale.h"
#include "sclmisc.h"
#include "sclerror.h"
#include "sclargmnt.h"

using namespace scltool;

using cio::COut;
using scllocale::GetLocale;

static err::err___ qRRor_;
static sclerror::error___ SCLError_;

bso::bool__ scltool::IgnoreUnknownArguments = false;

static rgstry::entry___ &Parameters_ = sclrgstry::Parameters;

static rgstry::entry___ RegistriesToDump_( "RegistriesToDump", Parameters_ );


static inline bso::bool__ ReportSCLPendingError_( void )
{
	bso::bool__ Exists = false;
qRH
	str::string Translation;
qRB
	Translation.Init();
	
	Exists = sclmisc::GetSCLBasePendingErrorTranslation( Translation );

	cio::CErr << Translation << txf::nl;
qRR
qRT
qRE
	return Exists;
}

namespace {
	void FillRegistry_(
		int argc,
		ntvstr::char__ *argv[],
		bso::bool__ IgnoreUnknownArguments )
	{
	qRH
		str::strings Arguments;
		int i = 0;
		TOL_CBUFFER___ SBuffer;
	qRB
		Arguments.Init();

		while ( i < argc )
			Arguments.Append( str::string( ntvstr::string___( argv[i++] ).UTF8( SBuffer ) ) );

		sclargmnt::FillRegistry( Arguments, sclargmnt::faIsCommand, IgnoreUnknownArguments ? sclargmnt::uaIgnore : sclargmnt::uaReport );
	qRR
	qRT
	qRE
	}
}

namespace {
	void DumpRegistries_( txf::text_oflow__ &Flow )
	{
	qRH
		rgstry::row__ Row = qNIL;
		rgstry::level__ Level = qNIL;
	qRB
		Flow << txf::tab << "----- Configuration registry -----" << txf::nl;
		sclmisc::GetRegistry().Dump( sclmisc::GetRegistryConfigurationLevel(), qNIL, true, xml::oIndent, xml::e_Default, Flow );
		Flow << txf::tab << "----- Project registry -----" << txf::nl;
		sclmisc::GetRegistry().Dump( sclmisc::GetRegistryProjectLevel(), qNIL, true, xml::oIndent, xml::e_Default, Flow );
		Flow << txf::tab << "----- Setup registry -----" << txf::nl;
		sclmisc::GetRegistry().Dump( sclmisc::GetRegistrySetupLevel(), qNIL, true, xml::oIndent, xml::e_Default, Flow );
		Flow << txf::tab << "----- Arguments registry -----" << txf::nl;
		sclmisc::GetRegistry().Dump( sclmisc::GetRegistryArgumentsLevel(), qNIL, true, xml::oIndent, xml::e_Default, Flow );

		Flow << txf::nl << txf::commit;
	qRR
	qRT
	qRE
	}

	void DumpRegistriesIfRequired_( void )
	{
	qRH
		str::string DumpRegistries;
	qRB
		DumpRegistries.Init();

		if ( sclmisc::BGetValue( RegistriesToDump_, DumpRegistries ) )
			DumpRegistries_( cio::COut );
	qRR
	qRT
	qRE
	}
}

static int main_(
	const oddities__ &Oddities,
	const cio::set__ &CIO )
{
	int ExitValue = EXIT_SUCCESS;
qRH
	str::string Command;
	bso::bool__ RegistriesDumped = false;
qRB
	sclmisc::Initialize( &qRRor_, &SCLError_, CIO, (const char *)NULL );

	FillRegistry_( Oddities.argc, Oddities.argv, IgnoreUnknownArguments );

	sclmisc::LoadProject();

	sclmisc::FillSetupRegistry();

	sclmisc::RefreshBaseLanguage();

	DumpRegistriesIfRequired_();
	RegistriesDumped = true;

	Command.Init();

	if ( sclargmnt::GetCommand( Command ) == "Usage" )
		sclargmnt::PrintUsage( cio::COut );
	else
		ExitValue = SCLTOOLMain( Command, Oddities );
qRR
	if ( !RegistriesDumped )
		DumpRegistriesIfRequired_();

	if ( ERRType >= err::t_amount ) {
		switch ( ERRType ) {
		case err::t_Abort:
			if ( ReportSCLPendingError_() )
				ExitValue = EXIT_FAILURE;
			ERRRst();
			break;
		case err::t_Free:
			ERRRst();
			qRFwk();
			break;
		case err::t_None:
			ERRRst();
			qRFwk();
			break;
		case err::t_Return:
			ERRRst();
			qRFwk();
			break;
		default:
			ERRRst();
			qRFwk();
			break;
		}
	}
qRT
qRE
	return ExitValue;
}

static void ErrFinal_( void )
{

	if ( ERRType != err::t_Abort ) {
		err::buffer__ Buffer;

		const char *Message = err::Message( Buffer );

		ERRRst();	// To avoid relaunching of current error by objects of the 'FLW' library.

		qRH
		qRB
			if ( cio::IsInitialized() ) {
				if ( cio::Target() == cio::tConsole ) {
					cio::COut << txf::commit;
					cio::CErr << txf::nl << txf::tab;
				}

				cio::CErr << "{ " << Message << " }";

				if ( cio::Target() == cio::tConsole )
					cio::CErr << txf::nl;

				cio::CErr << txf::commit;
			} else
				qRFwk();
		qRR
		qRT
		qRE
	} else
		ERRRst();
}

#ifdef CPE_S_WIN

# undef system	// Defined in 'tol.h', referenced in below header file.

# include <iostream>

static void SetStdOutToNewConsole_( void )
{
	int hCrt;
	FILE *hf;

	AllocConsole();
	hCrt = _open_osfhandle(
		(intptr_t)GetStdHandle( STD_OUTPUT_HANDLE ),
		_O_TEXT
		);
	hf = _fdopen( hCrt, "w" );
	*stdout = *hf;
	setvbuf( stdout, NULL, _IONBF, 0 );
}

// MSVC will use either 'wmain' or 'wWinMain' (and ignore the other) depending of the value of 'SubSystem'.

int wmain(
	int argc,
	wchar_t *argv[] )
{
	int ExitValue = EXIT_SUCCESS;
qRFH
	oddities__ Oddities;
qRFB
	Oddities.argc = argc;
	Oddities.argv = argv;

	ExitValue = main_( Oddities, cio::GetSet( cio::t_Default ) );
qRFR
qRFT	
	cio::COut.Commit();
	cio::CErr.Commit();
	cio::CIn.Dismiss();
qRFE( ErrFinal_() )
	return ExitValue;
}

int WINAPI wWinMain(
		HINSTANCE hInstance,
		HINSTANCE hPrevInstance,
		PWSTR pCmdLine,
		int nCmdShow )
{
	int ExitValue = EXIT_SUCCESS;
qRFH
	str::string SOut, SErr;
	flx::bunch_oflow_driver___<str::string_, bso::char__> FOut, FErr;
	flx::void_iflow_driver___ FIn;
	cio::set__ CIO;
	oddities__ Oddities;
qRFB
	Oddities.argv = CommandLineToArgvW( GetCommandLineW(), &Oddities.argc );

	Oddities.hInstance = hInstance;
	Oddities.hPrevInstance = hPrevInstance;
	Oddities.nCmdShow = nCmdShow;
	Oddities.pCmdLine = pCmdLine;

	SOut.Init();
	FOut.Init( SOut, fdr::ts_Default );

	SErr.Init();
	FErr.Init( SErr, fdr::ts_Default );

	FIn.Init( fdr::ts_Default, flx::a_Default );

	CIO.Init( FIn, FOut, FErr );

	ExitValue = main_( Oddities, CIO );
qRFR
qRFT
	if ( Oddities.argv != NULL )
		LocalFree( Oddities.argv );

	cio::COut.reset();
	cio::CErr.reset();
	cio::CIn.reset();

	FOut.reset();
	FErr.reset();
	FIn.reset();

# if 0	/// Fait planter 'CEF'.
	if ( SOut.Amount() )
		MessageBoxW( NULL, ntvstr::string___( SOut ).Internal(), ntvstr::string___( sclmisc::SCLMISCTargetName ).Internal(), MB_OK );

	if ( SErr.Amount() )
		MessageBoxW( NULL, ntvstr::string___( SErr ).Internal(), ntvstr::string___( sclmisc::SCLMISCTargetName ).Internal(), MB_OK | MB_TASKMODAL );
# else
	if ( SOut.Amount() || SErr.Amount() )
	{
		SetStdOutToNewConsole_();

		if ( SOut.Amount() )
			std::wcout << (wchar_t *)ntvstr::string___( SOut ).Internal() << std::endl;

		if ( SErr.Amount() )
			std::wcout << (wchar_t *)ntvstr::string___( SErr ).Internal() << std::endl;
	}
# endif
qRFE( ErrFinal_() )
	return ExitValue;
}

#else
int main(
	int argc,
	char *argv[] )
{
	int ExitValue = EXIT_SUCCESS;
qRFH
	oddities__ Oddities;
qRFB
	Oddities.argv = argv;
	Oddities.argc = argc;

	ExitValue = main_( Oddities, cio::GetSet( cio::t_Default ) );
qRFR
qRFT	
	cio::COut.Commit();
	cio::CErr.Commit();
	cio::CIn.Dismiss();
qRFE( ErrFinal_() )
	return ExitValue;
}
#endif

static inline void signal_( int s )
{
	exit( EXIT_SUCCESS );
}

static inline void ExitOnSignal_( void )
{
#ifdef CPE_S_POSIX
	signal( SIGHUP, signal_ );
#elif defined( CPE_S_WIN )
	signal( SIGBREAK, signal_ );
#else
#	error "Undefined target !"
#endif
	signal( SIGTERM, signal_ );
	signal( SIGABRT, signal_ );
	signal( SIGINT, signal_ );	// Documentations about this signal not very clear, but this handles Ctrl-C.
}

Q37_GCTOR( scltool )
{
	ExitOnSignal_();
	qRRor_.Init();
	SCLError_.Init();
}
