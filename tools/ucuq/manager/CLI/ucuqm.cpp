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
#include "tagsbs.h"

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

		// cio::COut << Response << txf::nl << txf::commit;
	qRR;
	qRT;
	qRE;
	}

	void InitAndConnect_(csdbnc::rRWFlow &Flow)
	{
	qRH;
		str::wString HostService;
		ntvstr::hBuffer Buffer;
	qRB;
		HostService.Init();
		sclm::MGetValue(registry::parameter::HostService, HostService);

		Flow.Init(HostService.Convert(Buffer), sck::NoTimeout, qRPDefault);

		HandShake_(Flow);
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

	bso::sBool HandleAnswer_(
		flw::rRFlow &Flow,
		str::dString *Result = NULL)
	{
		ucumng::eAnswer Answer = ucumng::a_Undefined;
	qRH;
		str::wString Response;
	qRB;
		Response.Init();

		Answer = GetAnswer_(Flow);
		ucucmn::Get(Flow, Response);

		ucucmn::Dismiss(Flow);

		if ( Answer ) {
			cio::CErr << "Error: " << Response << txf::nl << txf::commit;
		} else if ( Response.Amount() ) {
			if ( Result == NULL )
				cio::COut << Response << txf::nl << txf::commit;
			else
				*Result = Response;
		}
	qRR;
	qRT;
	qRE;
		return Answer;
	}

	bso::sBool HandleAnswer_(
		flw::rRFlow &Flow,
		str::dString &Result)
	{
		return HandleAnswer_(Flow, &Result);
	}


	bso::sBool BaseExecuteScript_(
		const char *ScriptName,
		tagsbs::dTaggedValues &Values,
		str::dString *Result)
	{
		bso::sBool OK = false;
	qRH;
		csdbnc::rRWFlow Flow;
		str::wString Token, Id, TaggedScript, Script, Expression;
	qRB;
		tol::Init(Token, Id, TaggedScript, Expression);

		sclm::MGetValue(registry::parameter::Token, Token);

		sclm::MGetValue(registry::parameter::Id, Id);
		registry::GetScript(ScriptName, TaggedScript);
		registry::GetScriptExpression(ScriptName, Expression);

		Script.Init();

		tagsbs::SubstituteLongTags(TaggedScript, Values, Script);

		InitAndConnect_(Flow);

		ucucmn::Put(ucumng::GetLabel(ucumng::rExecute_1), Flow);
		ucucmn::Put(Token, Flow);
		ucucmn::Put(Id, Flow);
		ucucmn::Put(Script, Flow);
		ucucmn::Put(Expression, Flow);
		ucucmn::Commit(Flow);

		OK = HandleAnswer_(Flow, Result);
	qRR;
	qRT;
	qRE;
		return OK;
	}

	bso::sBool ExecuteScript_(
		const char *ScriptName,
		str::dString *Result = NULL)
	{
		bso::sBool OK = false;
	qRH;
		tagsbs::wTaggedValues Values;
	qRB;
		Values.Init();

		BaseExecuteScript_(ScriptName, Values, Result);
	qRR;
	qRT;
	qRE;
		return OK;
	}

	bso::sBool ExecuteScript_(
		const char *ScriptName,
		str::dString &Result)
	{
		return ExecuteScript_(ScriptName, &Result);
	}

	template <typename... others> bso::sBool ExecuteScript_(
		const char *ScriptName,
		str::dString *Result,
		const char *Tag1,
		const others &...Others)
	{
		bso::sBool OK = false;
	qRH;
		tagsbs::wTaggedValues Values;
	qRB;
		Values.Init();

		Values.Append(Tag1, Others...);

		BaseExecuteScript_(ScriptName, Values, Result);
	qRR;
	qRT;
	qRE;
		return OK;
	}

	template <typename... others> bso::sBool ExecuteScript_(
		const char *ScriptName,
		str::dString &Result,
		const char *Tag1,
		const others &...Others)
	{
		ExecuteScript_(ScriptName, &Result, Tag1, Others...);
	}

	template <typename... others> bso::sBool ExecuteScript_(
		const char *ScriptName,
		const char *Tag1,
		const others &...Others)
	{
		return ExecuteScript_(ScriptName, (str::dString *)NULL, Tag1, Others...);
	}

	void Close_( void )
	{
	qRH;
		csdbnc::rRWFlow Flow;
		str::wString Token;
	qRB;
		InitAndConnect_(Flow);

		ucucmn::Put(ucumng::GetLabel(ucumng::rClose_1), Flow);

		Token.Init();
		ucucmn::Put(sclm::MGetValue(registry::parameter::Token, Token), Flow);

		ucucmn::Commit(Flow);
	qRR;
	qRT;
	qRE;
	}


	void FetchConfig_(void)
	{
		ExecuteScript_("FetchConfig");
	}

	void SetProxy_(void)
	{
	qRH;
		str::wString Proxy;
	qRB;
		Proxy.Init();

		sclm::MGetValue(registry::parameter::BackendProxy, Proxy);

		ExecuteScript_("SetProxy", "Proxy", Proxy);
	qRR;
	qRT;
	qRE;
	}

	void SetToken_(void)
	{
	qRH;
		str::wString NewToken;
	qRB;
		NewToken.Init();

		sclm::MGetValue(registry::parameter::NewToken, NewToken);

		ExecuteScript_("SetToken", "NewToken", NewToken);
	qRR;
	qRT;
	qRE;
	}

	void SetVirtualToken_(void)
	{
	qRH;
		str::wString VToken, BToken, BId;
		csdbnc::rRWFlow Flow;
		ucumng::eAnswer Answer = ucumng::a_Undefined;
	qRB;
		tol::Init(VToken, BToken, BId);

		sclm::MGetValue(registry::parameter::VirtualToken, VToken);
		sclm::MGetValue(registry::parameter::BackendToken, BToken);
		sclm::OGetValue(registry::parameter::BackendId, BId);

		InitAndConnect_(Flow);

		ucucmn::Put(ucumng::GetLabel(ucumng::rClose_1), Flow);
		ucucmn::Put(VToken, Flow);
		ucucmn::Put(BToken, Flow);
		ucucmn::Put(BId, Flow);

		ucucmn::Commit(Flow);

		HandleAnswer_(Flow);
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
	C(FetchConfig);
	C(SetProxy);
	C(SetToken);
	else
		qRGnr();

	ExitValue = EXIT_SUCCESS;
qRR;
qRT;
qRE;
	return ExitValue;
}
