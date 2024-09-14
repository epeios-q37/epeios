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


#include "server.h"

#include "registry.h"

#include "csdcmn.h"
#include "csdbns.h"

#include "mtk.h"
#include "lstbch.h"

#include "sclm.h"

using namespace server;

namespace {
	lstbch::qLBUNCHw( sck::rRWDriver *, sRow ) Drivers_;

	sRow New_(sck::sSocket Socket)
	{
		sRow Row = qNIL;
	qRH;
		sck::rRWDriver* Driver = NULL;
	qRB;
		if ( (Driver = new sck::rRWDriver) == NULL )
			qRAlc();

		Driver->Init(Socket, false, fdr::ts_Default);

		Row = Drivers_.Add(Driver);
	qRR;
		if ( Driver != NULL )
			delete Driver;

		Driver = NULL;
	qRT;
	qRE;
		return Row;
	}

	sck::rRWDriver& Get_(sRow Row)
	{
		sck::rRWDriver* Driver = NULL;

		Driver = Drivers_.Get(Row);

		if ( Driver == NULL )
			qRGnr();

		return *Driver;
	}
}

namespace protocol_ {
	qCDEF(char*, Id, "2b45ad37-2dcd-437c-9185-6ffbfcedfbbf");
	qCDEF(csdcmn::sVersion, LastVersion, 0);
}

namespace {
	inline const str::dString& Get_(
		flw::rRFlow& Flow,
		str::dString& String)
	{
		return csdcmn::Get(Flow, String);
	}

	inline void Put_(
		const str::dString& String,
		flw::rWFlow& Flow)
	{
		return csdcmn::Put(String, Flow);
	}
}


namespace {
	csdcmn::sVersion Handshake_(
		fdr::rRWDriver& Driver)
	{
		csdcmn::sVersion ProtocolVersion = csdcmn::UnknownVersion;
	qRH;
		flw::rDressedRWFlow<> Flow;
		str::wString SystemLabel;
		str::wString Notification;
		const char* Command = NULL;
	qRB;
		Flow.Init(Driver);

		switch ( ProtocolVersion = csdcmn::GetProtocolVersion(protocol_::Id, protocol_::LastVersion, Flow) ) {
		case csdcmn::UnknownVersion:
			Put_("\nUnknown server protocol version!\n", Flow);
			Flow.Commit();
			qRGnr();
			break;
		case csdcmn::BadProtocol:
			Put_("\nUnknown server protocol!\n", Flow);
			Flow.Commit();
			qRGnr();
			break;
		default:
			if ( ProtocolVersion > protocol_::LastVersion )
				qRUnx();

			SystemLabel.Init();
			Get_(Flow, SystemLabel);
			Put_("", Flow);

			Notification.Init();
			sclm::OGetValue(registry::definition::Notification, Notification);

			tagsbs::SubstituteLongTag(Notification, "SystemLabel", SystemLabel);

			Put_(Notification, Flow);

			Flow.Commit();
		}
	qRR;
	qRT;
	qRE;
		return ProtocolVersion;
	}

	namespace {
		struct gHandleData {
		public:
			sck::sSocket Socket;
			csdbns::tIP IP;
			gHandleData(void)
			{
				Socket = sck::Undefined;
				*IP = 0;
			}
		};

		void HandleRoutine_(
			gHandleData &Data,
			mtk::gBlocker &Blocker)
		{
		qRH;
			sck::sSocket Socket = sck::Undefined;
			sRow Row = qNIL;
		qRB;
			Socket = Data.Socket;

			Blocker.Release();

			if ( Socket == sck::Undefined )
				qRFwk();

			Row = New_(Socket);

			Handshake_(Get_(Row));
		qRR;
		qRT;
		qRE;
		}
	}

	struct gListenData {
	public:
		csdbns::sService Service;
		gListenData(void) {
			Service = csdbns::Undefined;
		}
	};

	void ListenRoutine_(
		gListenData &ListenData,
		mtk::gBlocker &Blocker)
	{
	qRH;
		csdbns::sService Service = csdbns::Undefined;
		gHandleData HandleData;
		csdbns::rListener Listener;
	qRB;
		Service = ListenData.Service;

		Blocker.Release();

		if ( Service == csdbns::Undefined )
			qRUnx();

		Listener.Init(Service);

		while ( true ) {
			HandleData.Socket = Listener.GetConnection(HandleData.IP);

			mtk::Launch<gHandleData>(HandleRoutine_, HandleData);
		}
	qRR;
	qRT;
	qRE;
	}
}

void server::Initialize(void)
{
	qRH;
	gListenData Data;
	qRB;
	Data.Service = sclm::MGetU16(registry::parameter::server::Service);

	mtk::Launch<gListenData>(ListenRoutine_, Data);
	qRR;
	qRT;
	qRE;
}

sRow server::Get(void)
{
	return Drivers_.First();
}

sck::rRWDriver& server::Get(sRow Row)
{
	return Get_(Row);
}



