/*
	Copyright (C) 2021 Claude SIMON (http://q37.info/contact/).

	This file is part of the 'McRq' tool.

    'McRq' is free software: you can redistribute it and/or modify it
    under the terms of the GNU Affero General Public License as published
    by the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    'McRq' is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with 'McRq'.  If not, see <http://www.gnu.org/licenses/>.
*/


#include "mcrq.h"

#include "registry.h"

#include "sclm.h"
#include "sclt.h"

#include "csdbns.h"

#include "err.h"
#include "cio.h"
#include "epsmsc.h"
#include "xpp.h"
#include "fnm.h"
#include "flf.h"

using cio::CErr;
using cio::COut;
using cio::CIn;

SCLI_DEF( mcrq, NAME_LC, NAME_MC );

namespace {
	typedef csdbns::cProcessing cProcessing_;

	class sProcessing
	: public cProcessing_ {
	protected:
		virtual void* CSDSCBPreProcess(
			fdr::rRWDriver* RWDriver,
			const ntvstr::char__* Origin) override
		{
			return NULL;
		}
		virtual csdbns::eAction CSDSCBProcess(
			fdr::rRWDriver* RWDriver,
			void* UP) override
		{
			return csdbns::aContinue;
		}
		virtual bso::sBool CSDSCBPostProcess(void* UP) override
		{
			return false;
		}
	public:
		void reset(bso::sBool = true)
		{}
		qCDTOR(sProcessing);
		void Init(void)
		{}
	};
}

const scli::sInfo &sclt::SCLTInfo( void )
{
	return mcrq::Info;
}

namespace {
	void PrintHeader_( void )
	{
		COut << NAME_MC " V" VERSION << " (" WEBSITE_URL ")" << txf::nl;
		COut << "Copyright (C) " COPYRIGHT << txf::nl;
		COut << txf::pad << "Build: " __DATE__ " " __TIME__ << " (" << cpe::GetDescription() << ')' << txf::nl;
	}

	void Launch_( void )
	{
	qRH;
		csdbns::rServer Server;
		sProcessing Callback;
	qRB;
		Callback.Init();	
		Server.Init(sclm::MGetU16(registry::parameter::Service), Callback);
		Server.Process(NULL);
	qRR;
	qRT;
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
	C( Launch );
	else
		qRGnr();

	ExitValue = EXIT_SUCCESS;
qRR;
qRT;
qRE;
	return ExitValue;
}
