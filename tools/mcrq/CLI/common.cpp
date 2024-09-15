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


#include "common.h"

#include "locale.h"
#include "registry.h"

#include "sclm.h"

#include "mtk.h"

using namespace common;

sdr::tRow common::rHandler::New(sck::sSocket Socket)
{
	sdr::sRow Row = qNIL;
qRH;
	rItem_ *Item = NULL;
qRB;
	Item = qNEW(rItem_);

	Item->Init(qNEW(sck::rRWDriver));

	Item->Driver->Init(Socket, false, fdr::ts_Default);

	Row = Items_.Add(Item);
qRR;
	if ( Item != NULL ) {
		Item->reset();

		qDELETE(Item);
	}
qRT;
qRE;
	return *Row;
}

void common::rHandler::Delete(sdr::sRow Row)
{
	rItem_ *Item = Items_.Get(Row);

	if ( Item == NULL )
		qRGnr();

	sck::rRWDriver *Driver = Item->Driver;

	qDELETE(Driver);
	qDELETE(Item);

	Items_.Delete(Row);
}

sck::rRWDriver& common::rHandler::Get(sdr::tRow Row)
{
	rItem_ *Item = Items_.Get(Row);

	if ( Item == NULL )
		qRGnr();

	if ( Item->Driver == NULL )
		qRGnr();

	return *Item->Driver;
}

namespace {
	const str::dString &GetTranslation_(
		eTarget Target,
		str::dString &Translation)
	{
		locale::eMessage Message = locale::m_Undefined;

		switch ( Target ) {
		case tClient:
			Message = locale::mClient;
			break;
		case tServer:
			Message = locale::mServer;
			break;
		default:
			qRGnr();
			break;
		}

		return locale::GetTranslation(Message, Translation);
	}
}

namespace {
	struct gProtocol_
	{
		const char* Id;
		csdcmn::sVersion LastVersion;
		eTarget Target;
		gProtocol_(void)
		{
			Id = NULL;
			LastVersion = csdcmn::UnknownVersion;
			Target = t_Undefined;
		}
	};
}

namespace {
	csdcmn::sVersion Handshake_(
		fdr::rRWDriver &Driver,
		const gProtocol_ &Protocol)
	{
		csdcmn::sVersion Version = csdcmn::UnknownVersion;
	qRH;
		flw::rDressedRWFlow<> Flow;
		str::wString SystemLabel;
		str::wString Notification;
		str::wString MessageTranslation, TargetTranslation;
	qRB;
		Flow.Init(Driver);

		switch ( Version = csdcmn::GetProtocolVersion(Protocol.Id, Protocol.LastVersion, Flow) ) {
		case csdcmn::UnknownVersion:
			tol::Init(MessageTranslation, TargetTranslation);
			common::Put(locale::GetTranslation(locale::mUnknownProtocol, MessageTranslation, GetTranslation_(Protocol.Target, TargetTranslation)), Flow);
			Flow.Commit();
			qRGnr();
			break;
		case csdcmn::BadProtocol:
			tol::Init(MessageTranslation, TargetTranslation);
			common::Put(locale::GetTranslation(locale::mUnknownProtocolVersion, MessageTranslation, GetTranslation_(Protocol.Target, TargetTranslation)), Flow);
			Flow.Commit();
			qRGnr();
			break;
		default:
			if ( Version > Protocol.LastVersion )
				qRUnx();

			SystemLabel.Init();
			common::Get(Flow, SystemLabel);
			common::Put("", Flow);

			Notification.Init();
			sclm::OGetValue(registry::definition::Notification, Notification);

			tagsbs::SubstituteLongTag(Notification, "SystemLabel", SystemLabel);

			common::Put(Notification, Flow);

			Flow.Commit();
		}
	qRR;
	qRT;
	qRE;
		return Version;
	}

	namespace {
		eAction Process_(
			cProcessing& Processing,
			sck::rRWDriver& Driver)
		{
			eAction Action = a_Undefined;
		qRH;
			flw::rDressedRWFlow<> Flow;
		qRB;
			Flow.Init(Driver);

			while ( !Flow.EndOfFlow() && ((Action = Processing.Process(Flow)) == common::aContinue) );
		qRR;
		qRT;
		qRE;
			return Action;
		}
	}
}



namespace {
	struct gHandleData_
	: public gProtocol_
	{
	public:
		sck::sSocket Socket;
		csdbns::tIP IP;
		cProcessing* Processing;
		rHandler* Handler;
		gHandleData_(void)
			: gProtocol_()
		{
			Socket = sck::Undefined;
			*IP = 0;
			Processing = NULL;
			Handler = NULL;
		}
		void Set(const gProtocol_ &Protocol)
		{
			memcpy(this, &Protocol, sizeof(gProtocol_));
		}
	};

	void HandleRoutine_(
		gHandleData_ &Data,
		mtk::gBlocker &Blocker)
	{
	qRH;
		rHandler& Handler = *Data.Handler;
		sck::sSocket Socket = sck::Undefined;
		cProcessing* Processing = NULL;
		gProtocol_ Protocol;
		sdr::tRow Row = qNIL;
	qRB;
		Socket = Data.Socket;
		Processing = Data.Processing;
		Protocol = Data;

		Blocker.Release();

		if ( Socket == sck::Undefined )
			qRFwk();

		Row = Handler.New(Socket);

		Handshake_(Handler.Get(Row), Protocol);

		if ( Processing == NULL )
			qRGnr();

		if ( Process_(*Processing, Handler.Get(Row)) == aStopAndDelete )
			Handler.Delete(Row);
	qRR;
	qRT;
	qRE;
	}

	namespace {
		struct gListenData_
		: public gProtocol_
		{
		public:
			rHandler* Handler;
			csdbns::sService Service;
			cProcessing* Processing;
			gListenData_(void)
				: gProtocol_()
			{
				Handler = NULL;
				Service = csdbns::Undefined;
				Processing = NULL;
			}
		};
	}

	void ListenRoutine_(
		gListenData_& ListenData,
		mtk::gBlocker& Blocker)
	{
	qRH;
		csdbns::sService Service = csdbns::Undefined;
		cProcessing* Processing = NULL;
		gHandleData_ HandleData;
		csdbns::rListener Listener;
	qRB;
		HandleData.Processing = ListenData.Processing;
		HandleData.Handler = ListenData.Handler;
		Service = ListenData.Service;
		HandleData.Set(ListenData);

		Blocker.Release();

		if ( Service == csdbns::Undefined )
			qRUnx();

		Listener.Init(Service);

		while ( true ) {
			HandleData.Socket = Listener.GetConnection(HandleData.IP);

			mtk::Launch<gHandleData_>(HandleRoutine_, HandleData);
		}
	qRR;
	qRT;
	qRE;
	}
}

void common::rHandler::Process(
	csdbns::sService Service,
	const char *ProtocolId,
	csdcmn::sVersion ProtocolLastVersion,
	eTarget ProtocolTarget,
	cProcessing &Processing)
{
qRH;
	gListenData_ Data;
qRB;
	Data.Handler = this;
	Data.Service = Service;
	Data.Processing = &Processing;
	Data.Id = ProtocolId;
	Data.LastVersion = ProtocolLastVersion;
	Data.Target = ProtocolTarget;

	mtk::Launch<gListenData_>(ListenRoutine_, Data);
qRR;
qRT;
qRE;
}

sdr::tRow common::rHandler::Get(void) const
{
	sdr::sRow Row = Items_.First();
	sdr::sRow RowLast = qNIL;
	tol::sTimeStamp TimeStamp = 0;
	rItem_ *Item = NULL;

	while ( Row != qNIL ) {
		Item = Items_.Get(Row);

		if ( Item == NULL )
			qRGnr();

		if ( Item->TimeStamp > TimeStamp ) {
			TimeStamp = Item->TimeStamp;
			RowLast = Row;
		}

		Row = Items_.Next(Row);
	}

	return *RowLast;
}
