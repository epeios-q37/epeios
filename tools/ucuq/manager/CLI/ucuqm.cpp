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
		const str::dString &Script,
		const str::dString &Expression,
		tagsbs::dTaggedValues &Values,
		str::dString *Result)
	{
		bso::sBool OK = false;
	qRH;
		csdbnc::rRWFlow Flow;
		str::wString Token, Id;
	qRB;
		tol::Init(Token, Id);

		sclm::MGetValue(registry::parameter::Token, Token);
		sclm::MGetValue(registry::parameter::Id, Id);

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

	bso::sBool BaseExecuteScript_(
		const char *ScriptName,
		tagsbs::dTaggedValues &Values,
		str::dString *Result)
	{
		bso::sBool OK = false;
	qRH;
		csdbnc::rRWFlow Flow;
		str::wString TaggedScript, Script, Expression;
	qRB;
		tol::Init(TaggedScript, Expression);

		registry::GetScript(ScriptName, TaggedScript);
		registry::GetScriptExpression(ScriptName, Expression);

		Script.Init();

		tagsbs::SubstituteLongTags(TaggedScript, Values, Script);

		OK = BaseExecuteScript_(Script, Expression, Values, Result);
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
		return ExecuteScript_(ScriptName, &Result, Tag1, Others...);
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
		str::wString Token, Id;
	qRB;
		tol::Init(Token, Id);

		sclm::MGetValue(registry::parameter::Token, Token);
		sclm::OGetValue(registry::parameter::Id, Id);
	
		InitAndConnect_(Flow);

		ucucmn::Put(ucumng::GetLabel(ucumng::rClose_1), Flow);
		ucucmn::Put(Token, Flow);
		ucucmn::Put(Id, Flow);

		ucucmn::Commit(Flow);
	qRR;
	qRT;
	qRE;
	}

	void Execute_(void)
	{
	qRH;
		str::wString FileName, Script, Expression;
		tagsbs::wTaggedValues Values;
		sclm::rRDriverRack Rack;
	qRB;
		tol::Init(FileName, Script, Expression, Values);

		sclm::OGetValue(registry::parameter::In, FileName);
		sclm::OGetValue(registry::parameter::Expression, Expression);

		flx::GetString(Rack.Init(FileName), Script);

		BaseExecuteScript_(Script, Expression, Values, NULL);
	qRR;
	qRT;
	qRE;
	}

	void Config_(void)
	{
		ExecuteScript_("Config");
	}

	void SetProxy_(void)
	{
	qRH;
		str::wString Proxy;
	qRB;
		Proxy.Init();

		sclm::MGetValue(registry::parameter::NewProxy, Proxy);

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

	void Create_(void)
	{
	qRH;
		str::wString VToken, Token, DeviceId;
		csdbnc::rRWFlow Flow;
		ucumng::eAnswer Answer = ucumng::a_Undefined;
	qRB;
		tol::Init(VToken, Token, DeviceId);

		sclm::MGetValue(registry::parameter::VToken, VToken);
		sclm::MGetValue(registry::parameter::Token, Token);
		sclm::OGetValue(registry::parameter::Id, DeviceId);

		InitAndConnect_(Flow);

		ucucmn::Put(ucumng::GetLabel(ucumng::rCreate_1), Flow);
		ucucmn::Put(VToken, Flow);
		ucucmn::Put(Token, Flow);
		ucucmn::Put(DeviceId, Flow);

		ucucmn::Commit(Flow);

		HandleAnswer_(Flow);
	qRR;
	qRT;
	qRE;
	}

	void Delete_(void)
	{
	qRH;
		str::wString RToken, VToken;
		csdbnc::rRWFlow Flow;
		ucumng::eAnswer Answer = ucumng::a_Undefined;
	qRB;
		tol::Init(RToken, VToken);

		sclm::MGetValue(registry::parameter::Token, RToken);
		sclm::OGetValue(registry::parameter::VToken, VToken);

		InitAndConnect_(Flow);

		ucucmn::Put(ucumng::GetLabel(ucumng::rDelete_1), Flow);
		ucucmn::Put(RToken, Flow);
		ucucmn::Put(VToken, Flow);

		ucucmn::Commit(Flow);

		HandleAnswer_(Flow);
	qRR;
	qRT;
	qRE;
	}
	
	void Fetch_(void)
	{
	qRH;
		str::wString RToken;
		csdbnc::rRWFlow Flow;
		ucumng::eAnswer Answer = ucumng::a_Undefined;
		str::wStrings RTokenIds, VTokens, VTokenIds;
		sdr::sRow Row = qNIL;
	qRB;
		RToken.Init();

		sclm::MGetValue(registry::parameter::Token, RToken);

		InitAndConnect_(Flow);

		ucucmn::Put(ucumng::GetLabel(ucumng::rFetch_1), Flow);
		ucucmn::Put(RToken, Flow);

		ucucmn::Commit(Flow);

		HandleAnswer_(Flow);

		tol::Init(RTokenIds, VTokens, VTokenIds);
		ucucmn::Get(Flow, RTokenIds);
		ucucmn::Get(Flow, VTokens);
		ucucmn::Get(Flow, VTokenIds);

		ucucmn::Dismiss(Flow);

		if ( VTokens.Amount() != VTokenIds.Amount() )
			qRGnr();

		cio::COut << "{\"Ids\":[";

		Row = RTokenIds.First();

		while ( Row != qNIL ) {
			cio::COut << '"' << RTokenIds(Row) << '"';

			Row = RTokenIds.Next(Row);

			if ( Row != qNIL )
				cio::COut << ",";
		}

		cio::COut << "],";

		cio::COut << "\"VTokens\":[";

		Row = VTokens.First();

		while ( Row != qNIL ) {
			if ( VTokenIds(Row).Amount() )
				cio::COut << "[";

			cio::COut << '"' << VTokens(Row) << '"';

			if ( VTokenIds(Row).Amount() )
				cio::COut << ",\"" << VTokenIds(Row) << "\"]";

			Row = VTokens.Next(Row);

			if ( Row != qNIL )
				cio::COut << ',';
		}

		cio::COut << "]}\n";
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
	C(Close);
	C(Execute);
	C(Config);
	C(SetProxy);
	C(SetToken);
	C(Create);
	C(Delete);
	C(Fetch);
	else
		qRGnr();

	ExitValue = EXIT_SUCCESS;
qRR;
qRT;
qRE;
	return ExitValue;
}
