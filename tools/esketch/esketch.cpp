/*
	'esketch' by Claude SIMON (simon.claude@zeusw.org)

	This file is part of the Epeios project (http://zeusw.org/epeios/).

    This file is part of 'esketch' tool.

    'esketch' is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    'esketch' is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with 'esketch'.  If not, see <http://www.gnu.org/licenses/>.
*/

#include "esketch.h"

#include "registry.h"

#include "scltool.h"
#include "sclerror.h"

#include "err.h"
#include "cio.h"
#include "epsmsc.h"
#include "xpp.h"
#include "fnm.h"
#include "flf.h"

using cio::CErr;
using cio::COut;
using cio::CIn;

/* Beginning of the part which handles command line arguments. */

static void PrintUsage_( void )
{
	scltool::PrintDefaultCommandDescriptions( NAME_LC );

	scltool::PrintCommandDescription( "TestCommand" );

#if 0	// Exemples.
// Commands.
	scltool::PrintCommandDescription( "ProcessCommand", "[%ThreadAmountMaxOption%=<max-thread>] <path> [<output>]");
	cio::COut << txf::nl;

// Options.
	scltool::PrintOptionsHeader();
	scltool::PrintOptionDescription( "max-thread", "ThreadAmountMaxOption" );

// Arguments.
	scltool::PrintArgumentsHeader();
	scltool::PrintArgumentDescription( "path", "PathArgumentDescription" );
	scltool::PrintArgumentDescription( "output", "OutputArgumentDescription" );
#endif
}

static void PrintHeader_( void )
{
	COut << NAME_MC " V" VERSION << " (" WEBSITE_URL ")" << txf::nl;
	COut << "Copyright " COPYRIGHT << txf::nl;
	COut << txf::pad << "Build : "__DATE__ " " __TIME__ << " (" << cpe::GetDescription() << ')' << txf::nl;
}

/* End of the part which handles command line arguments. */

static void Go_( const str::string_ &Command )
{
ERRProlog
ERRBegin
	if ( Command == "Test" )
		cio::COut << "Test" << txf::nl;
	else
		scltool::ReportAndAbort( "BadCommand" );
ERRErr
ERREnd
ERREpilog
}

const char *scltool::TargetName = NAME_LC;

void scltool::Main(
	int argc,
	const char *argv[] )
{
ERRProlog
	str::string Command;
ERRBegin
	Command.Init();
	scltool::GetCommand( Command );

	if ( Command == "Usage" )
		PrintUsage_();
	else if ( Command == "Version" )
		PrintHeader_();
	else if ( Command == "License" )
		epsmsc::PrintLicense();
	else
		Go_( Command );
ERRErr
ERREnd
ERREpilog
}
