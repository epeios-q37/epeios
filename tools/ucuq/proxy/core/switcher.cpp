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
#include "device.h"
#include "remote.h"
#include "manager.h"

#include "csdbns.h"

#include "mtk.h"

using namespace switcher;

namespace {
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

		switch ( Features.ProtocolVersion = csdcmn::GetProtocolVersion(ucucmn::protocol::Id, ucucmn::protocol::LastVersion, Flow) ) {
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
			if ( Features.ProtocolVersion > ucucmn::protocol::LastVersion )
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
		Flow.Dismiss();
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
		void Get_(
			fdr::rRWDriver &Driver,
			str::dString &RToken,
			str::dString &Id)
		{
		qRH;
			flw::rDressedRWFlow<> Flow;
		qRB;
			Flow.Init(Driver);

			common::Get(Flow, RToken);
			common::Get(Flow, Id);

			common::Put("", Flow);
			Flow.Commit();
		qRR;
		qRT;
		qRE;
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
		str::wString RToken, Id;
	qRB;
		Socket = Data.Socket;

		Blocker.Release();

		if ( Socket == sck::Undefined )
			qRGnr();

		Driver = qNEW(sck::rRWDriver);

		Driver->Init(Socket, true, fdr::ts_Default);

		Features.Init();

		switch ( Handshake_(*Driver, Features) ) {
		case common::cDevice:
			tol::Init(RToken, Id);

			Get_(*Driver, RToken, Id);

			device::New(RToken, Id, Driver);
				
			Driver = NULL;	// To avoid deleting when exiting this method.
			break;
		case common::cRemote:
			remote::Process(*Driver);
			break;
		case common::cManager:
			manager::Process(*Driver);
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