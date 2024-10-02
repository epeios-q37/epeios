/*
  Copyright (C) 2024 Claude SIMON (http://q37.info/contact/).

  This file is part of the 'UCUq' toolkit.

  'UCUq' is free software: you can redistribute it and/or modify it
  under the terms of the GNU Affero General Public License as published
  by the Free Software Foundation, either version 3 of the License, or
  (at your option) any later version.

  'UCUq' is distributed in the hope that it will be useful,
  but WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
  GNU Affero General Public License for more details.

  You should have received a copy of the GNU Affero General Public License
  along with 'UCUq'.  If not, see <http://www.gnu.org/licenses/>.
*/


#include "switcher.h"

#include "common.h"
#include "messages.h"
#include "registry.h"
#include "backend.h"
#include "frontend.h"

#include "csdbns.h"
#include "csdcmn.h"

#include "mtk.h"

using namespace switcher;

namespace {
	namespace protocol_ {
		qCDEF(char *, Id, "c37cc83e-079f-448a-9541-5c63ce00d960");
		qCDEF(csdcmn::sVersion, LastVersion, 0);
	}

	struct rFeatures_ {
	public:
		str::wString SystemLabel;
		csdcmn::sVersion ProtocolVersion;
		void reset(bso::sBool P = true)
		{
			SystemLabel.reset(P);
			ProtocolVersion = csdcmn::UnknownVersion;
		}
		qCDTOR(rFeatures_);
		void Init(void)
		{
			SystemLabel.Init();
			ProtocolVersion = csdcmn::UnknownVersion;
		}
	};

	common::eCaller Handshake_(
		fdr::rRWDriver &Driver,
		rFeatures_ &Features)
	{
		common::eCaller Caller = common::c_Undefined;
	qRH;
		flw::rDressedRWFlow<> Flow;
		str::wString Notification, Translation, RawCaller;
	qRB;
		Flow.Init(Driver);

		switch ( Features.ProtocolVersion = csdcmn::GetProtocolVersion(protocol_::Id, protocol_::LastVersion, Flow) ) {
		case csdcmn::UnknownVersion:
			Translation.Init();
			common::Put(messages::GetTranslation(messages::iUnknownProtocol, Translation), Flow);
			Flow.Commit();
			qRGnr();
			break;
		case csdcmn::BadProtocol:
			Translation.Init();
			common::Put(messages::GetTranslation(messages::iUnknownProtocolVersion, Translation), Flow);
			Flow.Commit();
			qRGnr();
			break;
		default:
			if ( Features.ProtocolVersion > protocol_::LastVersion )
				qRUnx();
			break;
		}

		RawCaller.Init();
		common::Get(Flow, RawCaller);

		common::Get(Flow, Features.SystemLabel);

		if ( (Caller = common::GetCaller(RawCaller)) == common::c_Undefined ) {
			Translation.Init();
			common::Put(messages::GetTranslation(messages::iUnknownCaller, Translation, RawCaller), Flow);
			Flow.Commit();
			qRGnr();
		}

		common::Put("", Flow);

		Notification.Init();
		sclm::OGetValue(registry::definition::Notification, Notification);

		tagsbs::SubstituteLongTag(Notification, "SystemLabel", Features.SystemLabel);

		common::Put(Notification, Flow);

		Flow.Commit();
	qRR;
	qRT;
	qRE;
		return Caller;
	}

	struct gData_
	{
	public:
		sck::sSocket Socket;
		csdbns::tIP IP;
		gData_(void)
		{
			Socket = sck::Undefined;
			*IP = 0;
		}
	};

	namespace {
		const backend::dSelector &GetSelector_(
			fdr::rRWDriver &Driver,
			backend::dSelector &Selector)
		{
		qRH;
			flw::rDressedRWFlow<> Flow;
		qRB;
			Flow.Init(Driver);

			common::Get(Flow, Selector.Token);
			common::Get(Flow, Selector.Id);

			common::Put("", Flow);
			Flow.Commit();
		qRR;
		qRT;
		qRE;
			return Selector;
		}
	}

	void HandleRoutine_(
		gData_ &Data,
		mtk::gBlocker &Blocker)
	{
	qRH;
		sck::sSocket Socket = sck::Undefined;
		sck::rRWDriver *Driver = NULL;
		sdr::tRow Row = qNIL;
		rFeatures_ Features;
		common::eCaller Caller = common::c_Undefined;
		backend::wSelector Selector;
	qRB;
		Socket = Data.Socket;

		Blocker.Release();

		if ( Socket == sck::Undefined )
			qRGnr();

		Driver = qNEW(sck::rRWDriver);

		Driver->Init(Socket, true, fdr::ts_Default);

		Features.Init();

		switch ( Caller = Handshake_(*Driver, Features) ) {
		case common::cBackend:
			Selector.Init();

			if ( backend::New(GetSelector_(*Driver, Selector), Driver) == qNIL )
				qRUnx();
				
			Driver = NULL;	// To avoid deleting when exiting this method.
			break;
		case common::cFrontend:
			frontend::Process(*Driver);
			break;
		default:
			qRUnx();
			break;
		}
	qRR;
		if ( Driver != NULL ) {
			qDELETE(Driver);
		}
	qRT;
	qRE;
	}

}

void switcher::Process(void)
{
qRH;
	csdbns::rListener Listener;
	gData_ Data;
qRB;
	Listener.Init(sclm::MGetU16(registry::parameter::Service));

	while ( true ) {
		Data.Socket = Listener.GetConnection(Data.IP);

		mtk::Launch<gData_>(HandleRoutine_,Data);
	}
qRR;
qRT;
qRE;
}