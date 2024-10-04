/*
	Copyright (C) 2021 Claude SIMON (http://q37.info/contact/).

	This file is part of the 'ucuqm' tool.

    'ucuqm' is free software: you can redistribute it and/or modify it
    under the terms of the GNU Affero General Public License as published
    by the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    'ucuqm' is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with 'ucuqm'.  If not, see <http://www.gnu.org/licenses/>.
*/


#include "ucuqm.h"

#include "ucucmn.h"
#include "ucumng.h"

#include "registry.h"

#include "sclm.h"
#include "sclt.h"

#include "err.h"
#include "cio.h"
#include "epsmsc.h"
#include "xpp.h"
#include "fnm.h"
#include "flf.h"
#include "csdbnc.h"

using cio::CErr;
using cio::COut;
using cio::CIn;

SCLI_DEF( ucuqm, NAME_LC, NAME_MC );

const scli::sInfo &sclt::SCLTInfo( void )
{
	return ucuqm::Info;
}

namespace {
	void PrintHeader_( void )
	{
		COut << NAME_MC " V" VERSION << " (" WEBSITE_URL ")" << txf::nl;
		COut << "Copyright (C) " COPYRIGHT << txf::nl;
		COut << txf::pad << "Build: " __DATE__ " " __TIME__ << " (" << cpe::GetDescription() << ')' << txf::nl;
	}

	void HandShake_(flw::rRWFlow &Flow)
	{
	qRH;
		str::wString Response;
		bso::buffer__ Buffer;
	qRB;
		ucucmn::Put(ucucmn::protocol::Id, Flow);
		ucucmn::Put(bso::Convert(ucucmn::protocol::LastVersion, Buffer), Flow);
		ucucmn::Put("Manager", Flow);
		ucucmn::Put("CLI", Flow);

		ucucmn::Commit(Flow);

		Response.Init();
		ucucmn::Get(Flow, Response);

		if ( Response.Amount() )
			sclm::ReportAndAbort(Response);

		Response.Init();
		ucucmn::Get(Flow, Response);

		cio::COut << Response << txf::nl << txf::commit;
	qRR;
	qRT;
	qRE;
	}

	void InitAndConnect(csdbnc::rRWFlow &Flow)
	{
	qRH;
		str::wString HostService;
		ntvstr::hBuffer Buffer;
	qRB;
		HostService.Init();
		sclm::MGetValue(registry::parameter::HostService, HostService);

		Flow.Init(HostService.Convert(Buffer), sck::NoTimeout, qRPDefault);
	qRR;
	qRT;
	qRE;
	}

	ucumng::eAnswer GetAnswer_(flw::rRFlow &Flow)
	{
		bso::sU8 Answer = ucumng::a_Undefined;

		ucucmn::Get(Flow, Answer);

		if ( Answer > ucumng::a_amount )
			qRGnr();

		return (ucumng::eAnswer)Answer;
	}

	void Close_( void )
	{
	qRH;
		csdbnc::rRWFlow Flow;
		str::wString Token;
	qRB;
		InitAndConnect(Flow);
		HandShake_(Flow);

		ucucmn::Put(ucumng::GetLabel(ucumng::rClose_1), Flow);

		Token.Init();
		ucucmn::Put(sclm::MGetValue(registry::parameter::Token, Token), Flow);

		ucucmn::Commit(Flow);
	qRR;
	qRT;
	qRE;
	}


	void FetchConfig_( void )
	{
	qRH;
		csdbnc::rRWFlow Flow;
		str::wString Token, DeviceId, Script, Expression, Response;
		ucumng::eAnswer Answer = ucumng::a_Undefined;
	qRB;
		InitAndConnect(Flow);
		HandShake_(Flow);

		ucucmn::Put(ucumng::GetLabel(ucumng::rExecute_1), Flow);

		tol::Init(Token, DeviceId, Script, Expression);

		sclm::MGetValue(registry::parameter::Token, Token);
		sclm::MGetValue(registry::parameter::DeviceId, DeviceId);
		registry::GetScript("FetchConfig", Script);
		registry::GetScriptExpression("FetchConfig", Expression);

		ucucmn::Put(Token, Flow);
		ucucmn::Put(DeviceId, Flow);
		ucucmn::Put(Script, Flow);
		ucucmn::Put(Expression, Flow);
		ucucmn::Commit(Flow);

		ucucmn::Commit(Flow);

		Response.Init();

		Answer = GetAnswer_(Flow);
		ucucmn::Get(Flow, Response);
			
		ucucmn::Dismiss(Flow);

		if ( Answer ) {
			cio::CErr << "Error:" << Response << txf::nl << txf::commit;
		}
		else {
			cio::COut << Response << txf::nl << txf::commit;
		}
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
	C( Close );
	C( FetchConfig);
	else
		qRGnr();

	ExitValue = EXIT_SUCCESS;
qRR;
qRT;
qRE;
	return ExitValue;
}
