/*
	Copyright (C) 2021 Claude SIMON (http://q37.info/contact/).

	This file is part of the 'TASq' tool.

    'TASq' is free software: you can redistribute it and/or modify it
    under the terms of the GNU Affero General Public License as published
    by the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    'TASq' is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with 'TASq'.  If not, see <http://www.gnu.org/licenses/>.
*/


#include "tasq.h"

#include "registry.h"

#include "tsqbndl.h"
#include "tsqxmlc.h"
#include "tsqxmlp.h"
#include "tsqxmlw.h"

#include "sclm.h"
#include "sclt.h"

#include "err.h"
#include "cio.h"
#include "epsmsc.h"
#include "xpp.h"
#include "fnm.h"
#include "flf.h"

using cio::CErr;
using cio::COut;
using cio::CIn;

SCLI_DEF( tasq, NAME_LC, NAME_MC );

const scli::sInfo &sclt::SCLTInfo( void )
{
	return tasq::Info;
}

namespace {
	void PrintHeader_( void )
	{
		COut << NAME_MC " V" VERSION << " (" WEBSITE_URL ")" << txf::nl;
		COut << "Copyright (C) " COPYRIGHT << txf::nl;
		COut << txf::pad << "Build: " __DATE__ " " __TIME__ << " (" << cpe::GetDescription() << ')' << txf::nl;
	}

	namespace _ {
	  void GetFilenames(
      str::dString &DBFileAffix,
      str::dString &XMLFilename)
      {
        sclm::MGetValue(registry::parameter::DBFileAffix, DBFileAffix);
        sclm::MGetValue(registry::parameter::XMLFilename, XMLFilename);
      }
	}

	void Export_( void )
	{
	qRH;
    str::wString DBFileAffix, XMLFilename;
    sclm::rTWFlowRack Rack;
    xml::rWriter Writer;
    tsqbndl::hGuard Guard;
    bso::sBool Initialized = false;
	qRB;
    tol::Init(DBFileAffix, XMLFilename);
    _::GetFilenames(DBFileAffix, XMLFilename);

    if ( tsqbndl::Initialize(DBFileAffix) ) {
      Initialized = true;

      Writer.Init(Rack.Init(XMLFilename), xml::lIndent);

      Writer.PushTag(tsqxmlc::GetLabel(tsqxmlc::tTASq));

      tsqxmlw::WriteCorpus(Writer);
      tsqxmlw::WriteAllTasks(tsqbndl::CGet(Guard), tsqxmlw::ffExport, Writer);

      Writer.PopTag();
    } else {
      cio::COut << "No '" << DBFileAffix << "' to export!";
    }
	qRR;
    Rack.HandleError();
	qRT;
    if ( Initialized )
      tsqbndl::Immortalize();
	qRE;
	}

	void Import_( void )
	{
	qRH;
    str::wString DBFileAffix, XMLFilename;
    sclm::rXRFlowRack Rack;
    xml::rParser Parser;
    tsqbndl::hGuard Guard;
    bso::sBool Initialized = false;
	qRB;
    tol::Init(DBFileAffix, XMLFilename);
    _::GetFilenames(DBFileAffix, XMLFilename);

    if ( !tsqbndl::Initialize(DBFileAffix) ) {
      Initialized = true;

      Parser.Init(Rack.Init(XMLFilename), xml::eh_Default);

      tsqxmlp::Parse(Parser, tsqbndl::Get(Guard));
    } else {
      cio::COut << '\'' << DBFileAffix << "' already exists!" << txf::nl;
    }
	qRR;
    Rack.HandleError();
	qRT;
    if ( Initialized )
      tsqbndl::Immortalize();
	qRE;
	}
}

#define C( name )\
	else if ( Command == #name )\
		name##_()

int sclt::SCLTMain(
	const str::dString &Command,
	const sclt::fOddities &Oddities )
{
	int ExitValue = EXIT_FAILURE;
qRH;
qRB;
	if ( Command == "Version" )
		PrintHeader_();
	else if ( Command == "License" )
		epsmsc::PrintLicense( NAME_MC );
	C( Export );
  C( Import );
	else
		qRGnr();

	ExitValue = EXIT_SUCCESS;
qRR;
qRT;
qRE;
	return ExitValue;
}
