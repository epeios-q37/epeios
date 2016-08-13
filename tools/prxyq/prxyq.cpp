/*
	Copyright (C) 2016 by Claude SIMON (http://zeusw.org/epeios/contact.html).

	This file is part of 'prxyq'.

    'prxyq' is free software: you can redistribute it and/or modify it
    under the terms of the GNU Affero General Public License as published
    by the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    'prxyq' is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with 'prxyq'.  If not, see <http://www.gnu.org/licenses/>.
*/

#include "registry.h"
#include "watchdog.h"

#include "prxybase.h"

#include "scltool.h"
#include "sclerror.h"

#include "err.h"
#include "cio.h"
#include "epsmsc.h"
#include "xpp.h"
#include "fnm.h"
#include "flf.h"
#include "csdcmn.h"
#include "csdbnc.h"
#include "csdbns.h"
#include "lstbch.h"
#include "ctn.h"

using cio::CErr;
using cio::COut;
using cio::CIn;

# define NAME_MC			"prxyq"
# define NAME_LC			"prxyq"
# define NAME_UC			"PRXYQ"
# define WEBSITE_URL		"http://q37.info/"
# define AUTHOR_NAME		"Claude SIMON"
# define AUTHOR_CONTACT		"http://q37.info/contact/"
# define OWNER_NAME			"Claude SIMON"
# define OWNER_CONTACT		"http://q37.info/contact/"
# define COPYRIGHT			COPYRIGHT_YEARS " " OWNER_NAME " (" OWNER_CONTACT ")"	

namespace {
	bso::sBool FreezeFlag_ = false;	// For watchdog testing putpose.

	void PrintHeader_( void )
	{
		COut << NAME_MC " V" VERSION << " (" WEBSITE_URL ")" << txf::nl;
		COut << "Copyright (C) " COPYRIGHT << txf::nl;
		COut << txf::pad << "Build : " __DATE__ " " __TIME__ << " (" << cpe::GetDescription() << ')' << txf::nl;
	}

	typedef fdr::ioflow_driver___<> _flow_driver___;

	typedef flw::standalone_ioflow__<> _flow__;

	class flow___
	: public _flow_driver___,
	  public _flow__
	{
	private:
		Q37_MRMDF( flw::iflow__, IF_, IFlow_ );
		Q37_MRMDF( flw::oflow__, OF_, OFlow_ );
	protected:
		virtual fdr::size__ FDRWrite(
			const fdr::byte__ *Buffer,
			fdr::size__ Maximum) override
		{
			return OF_().WriteUpTo( Buffer, Maximum );
		}
		virtual void FDRCommit( void ) override
		{
			OF_().Commit();
		}
		virtual fdr::size__ FDRRead(
			fdr::size__ Maximum,
			fdr::byte__ *Buffer ) override
		{
			return IF_().ReadUpTo( Maximum, Buffer );
		}
		virtual void FDRDismiss( void ) override
		{
			IF_().Dismiss();
		}
public:
		void reset( bso::bool__ P = true )
		{
			_flow__::reset( P );
			_flow_driver___::reset( P );
			IFlow_ = NULL;
			OFlow_ = NULL;
		}
		E_CVDTOR( flow___ );
		void Init( void )
		{
			reset();

			_flow_driver___::Init( fdr::ts_Default );
			_flow__::Init( *this );

			// Other initializaiton will be made by other methods.
		}
		void SetIn( flw::iflow__ &Flow )
		{
			if ( IFlow_ != NULL )
				qRGnr();

			IFlow_ = &Flow;
		}
		void SetOut( flw::oflow__ &Flow )
		{
			if ( OFlow_ != NULL )
				qRGnr();

			OFlow_ = &Flow;
		}
		bso::sBool IsSet( void ) const
		{
			if ( IFlow_ != NULL ) {
				if ( OFlow_ != NULL )
					return true;
				else
					qRGnr();
			} else if ( OFlow_ == NULL )
				return false;
			else
				qRGnr();



		}
	};

	class rProxy
	{
	private:
		flow___ C2S_, S2C_;
		mtx::handler___
			PairingMutex_,	// To wait for the pairing.
			CommitMutex_;	// To ensure that the pairing data is transmitted.
		void Process_( flw::ioflow__ &Flow )
		{
		qRFH
			fdr::byte__ Buffer[1024];
			fdr::size__ Size = 0,  Written = 0;
//			err::buffer__ ERRBuffer;
		qRFB
			while ( ( Size = Flow.ReadUpTo( sizeof( Buffer ), Buffer ) ) != 0) {
				Written = 0;
				while ( Size > Written )
					Written += Flow.WriteUpTo( Buffer + Written, Size - Written );
				Flow.Commit();
			}
		qRFR
			if ( ERRType == err::tLibrary ) {
				// cio::COut << ">>>" << txf::pad << err::Message( ERRBuffer ) << txf::nl << txf::commit;	// sck.cpp:78 'WSAECONNABORTED'.
				ERRRst();
			}
		qRFT
		qRFE( sclmisc::ErrFinal() )
		}
		void Process_( prxybase::eType Type )
		{
			switch ( Type ) {
			case prxybase::tClient:
				Process_( C2S_ );
				break;
			case prxybase::tServer:
				Process_( S2C_ );
				break;
			default:
				qRGnr();
				break;
			}
		}
		bso::sBool WaitForOther_(void)	// If the returning value is 'true', then the thread is the one which deletes the proxy.
		{
			if ( mtx::TryToLock( PairingMutex_ ) ) {
				mtx::Lock( PairingMutex_ );
				mtx::Unlock( PairingMutex_ );
				return true;
			} else {
				mtx::Unlock( PairingMutex_ );
				return false;
			}
		}
		void Plug_(
			flw::ioflow__ &Flow,
			prxybase::eType Type )
		{
			switch ( Type ) {
			case prxybase::tClient:
				C2S_.SetIn( Flow );
				S2C_.SetOut( Flow );
				break;
			case prxybase::tServer:
				S2C_.SetIn( Flow );
				C2S_.SetOut( Flow );
				break;
			default:
				qRGnr();
				break;
			}
		}
	public:
		void reset( bso::bool__ P = true )
		{
			C2S_.reset( false );
			S2C_.reset( false );

			if ( P ) {
				if ( PairingMutex_ != mtx::UndefinedHandler )
					mtx::Delete( PairingMutex_ );

				if ( CommitMutex_ != mtx::UndefinedHandler )
					mtx::Delete( CommitMutex_ );
			}

			PairingMutex_ = mtx::UndefinedHandler;
			CommitMutex_ = mtx::UndefinedHandler;
		}
		E_CDTOR( rProxy );
		bso::sBool Init(
			flw::ioflow__ &Flow,
			prxybase::eType Type )
		{
			reset();

			C2S_.Init();
			S2C_.Init();

			Plug_( Flow, Type );

			PairingMutex_ = mtx::Create();
			CommitMutex_ = mtx::Create();

			mtx::Lock( CommitMutex_ );

			mtx::Lock( PairingMutex_ );
			mtx::Lock( PairingMutex_ );	// Unlocked by 'Plug(...)'.
			mtx::Unlock( PairingMutex_ );

			prxybase::PutAnswer( prxybase::aOK, Flow );

			Flow.Commit();

			mtx::Unlock( CommitMutex_ );

			Process_( Type );

			return WaitForOther_();
		}
		bso::sBool Plug(
			flw::ioflow__ &Flow,
			prxybase::eType Type )
		{
			Plug_( Flow, Type );

			mtx::Unlock( PairingMutex_ );

			prxybase::PutAnswer( prxybase::aOK, Flow );

			Flow.Commit();

			mtx::Lock( CommitMutex_ );
			mtx::Unlock( CommitMutex_ );

			Process_( Type );

			return WaitForOther_();
		}
	};

	using csdbns::cProcessing;

	class dPending
	{
	public:
		struct s {
			rProxy *Proxy;
			str::dString::s Id;
		} &S_;
		str::dString Id;
		dPending( s &S )
		: S_( S ),
		  Id( S.Id )
		{}
		void reset( bso::sBool P = true )
		{
			S_.Proxy = NULL;
			Id.reset( P );
		}
		void plug( str::cHook &Hook )
		{
			Id.plug(Hook );
		}
		void plug( qASd *AS )
		{
			Id.plug( AS );
		}
		const dPending &operator =( const dPending &P )
		{
			S_.Proxy = P.S_.Proxy;

			Id = P.Id;

			return *this;
		}
		void Init(
			rProxy *Proxy,
			const str::dString &Id )
		{
			S_.Proxy = Proxy;

			this->Id.Init( Id );
		}
		rProxy *Proxy( void ) const
		{
			if ( S_.Proxy == NULL )
				qRGnr();

			return S_.Proxy;
		}
	};

	qW( Pending );

	typedef ctn::qMCONTAINERdl( dPending ) dPendings;
	qW( Pendings );

	wPendings PendingClients_, PendingServers_;

	tht::rLocker Locker_;

	void DeletePendings_( dPendings &Pendings)
	{
		sdr::sRow Row = Pendings.First();

		while ( Row != qNIL ) {
			delete Pendings( Row ).Proxy();

			Pendings.Flush();

			Row = Pendings.Next( Row );
		}

		Pendings.reset();
	}

	rProxy *SearchPendingAndRemoveIfExists_(
		const str::string_ &Id,
		dPendings &Pendings )
	{
		rProxy *Proxy = NULL;
	qRH
		sdr::row__ Row = qNIL;
	qRB
		Row = Pendings.First();

		while ( ( Row != qNIL ) && ( Pendings( Row ).Id != Id ) )
			Row = Pendings.Next( Row );

		if ( Row != qNIL ) {
			Proxy = Pendings(Row).Proxy();
			Pendings.Flush();
			Pendings.Remove( Row );
		}

	qRR
	qRT
	qRE
		return Proxy;
	}

	dPendings &GetPendings_( prxybase::eType Type )
	{
		switch ( Type ) {
		case prxybase::tClient:
			return PendingClients_;
			break;
		case prxybase::tServer:
			return PendingServers_;
			break;
		default:
			qRGnr();
			break;
		}

		return *(dPendings *)NULL;	//To avoid a warning.
	}

	namespace {
		void Dismiss_(
			dPendings &Pendings,
			const str::dString &ID )
		{
			sdr::sRow Row = Pendings.Last();
			sdr::sRow Previous = qNIL;

			while ( Row != qNIL ) {
				if ( Pendings( Row ).Id == ID ) {
					Previous = Pendings.Previous( Row );

					delete Pendings( Row ).Proxy();

					Pendings.Remove( Row );

					Row = Previous;
				} else
					Row = Pendings.Previous( Row );
			}
		}
	}

	// Close cponnections frome all server of ID 'ID'.
	void DismissServers_( const str::dString &ID )
	{
		Dismiss_( PendingServers_, ID );
	}

	namespace plug_ {
		namespace {
			void Create_(
				const str::string_ &Id,
				flw::ioflow__ &Flow,
				prxybase::eType Type )
			{
			qRH
				rProxy *Proxy = NULL;
				wPending Pending;
			qRB
				Proxy = new rProxy;

				if ( Proxy == NULL )
					qRAlc();

				Pending.Init( Proxy, Id );

				GetPendings_( Type ).Append( Pending );

				Locker_.Unlock();	// Locked by caller.

				if ( Proxy->Init( Flow, Type ) )	// Blocking until deconnection.
					delete Proxy;
			qRR
			qRT
			qRE
			}

			void Plug_(
				rProxy *Proxy,
				flw::ioflow__ &Flow,
				prxybase::eType Type )
			{
				Locker_.Unlock();	// Locked by caller.

				if ( Proxy->Plug( Flow, Type ) )	// Blocking until deconnection.
					delete Proxy;
			}
		}

		void A (flw::ioflow__ &Flow )
		{
		qRH
			prxybase::eType Type = prxybase::t_Undefined;
			str::string Id;
			rProxy *Proxy = NULL;
		qRB
			Type = prxybase::GetType( Flow );

			Id.Init();
			prxybase::GetId( Flow, Id );

			Locker_.Lock();

			switch ( Type ) {
			case prxybase::tClient:
				Proxy = SearchPendingAndRemoveIfExists_( Id, GetPendings_( prxybase::tServer ) );
				break;
			case prxybase::tServer:
				Proxy = SearchPendingAndRemoveIfExists_( Id, GetPendings_( prxybase::tClient ) );
				break;
			default:
				qRGnr();
				break;
			}

			if ( Proxy == NULL ) 
				Create_( Id, Flow, Type );
			else
				Plug_( Proxy, Flow, Type );
		qRR
		qRT
		qRE
		}
	}

	void Plug_(
		csdcmn::sVersion Version,
		flw::sIOFlow &Flow )
	{
		switch ( Version ) {
		default:
			return plug_::A( Flow );
			break;
#pragma warning( suppress: 4065 )	//  switch statement contains 'default' but no 'case' labels.
		}
	}

	namespace dismiss_ {
		void A( flw::sIOFlow &Flow )
		{
		qRH
			str::wString ID;
		qRB
			ID.Init();

			prxybase::GetId( Flow, ID );

			Locker_.Lock();

			DismissServers_( ID );

			prxybase::PutAnswer( prxybase::aOK, Flow );

			Flow.Commit();
		qRR
		qRT
		qRE
		}
	}

	void Dismiss_(
		csdcmn::sVersion Version,
		flw::sIOFlow &Flow )
	{
		switch ( Version ) {
		default:
			return dismiss_::A( Flow );
			break;
#pragma warning( suppress: 4065 )	//  switch statement contains 'default' but no 'case' labels.
		}
	}


	namespace ping_ {
		void A( flw::ioflow__ &Flow )
		{
			prxybase::PutAnswer( prxybase::aOK, Flow );

			Flow.Commit();
		}
	}

	void Ping_(
		csdcmn::sVersion Version,
		flw::sIOFlow &Flow )
	{
		switch ( Version ) {
		default:
			return ping_::A( Flow );
			break;
#pragma warning( suppress: 4065 )	//  switch statement contains 'default' but no 'case' labels.
		}
	}

	namespace freeze_{
		void A(
			flw::ioflow__ &Flow,
			bso::sBool FromLocalhost )
		{
			if ( FromLocalhost ) {
				FreezeFlag_ = true;
				prxybase::PutAnswer( prxybase::aOK, Flow );
			} else
				prxybase::PutAnswer( prxybase::aForbidden, Flow );


			Flow.Commit();
		}
	}

	void Freeze_(
		csdcmn::sVersion Version,
		flw::sIOFlow &Flow,
		bso::sBool FromLocalhost )
	{
		switch ( Version ) {
		default:
			return freeze_::A( Flow, FromLocalhost );
			break;
#pragma warning( suppress: 4065 )	//  switch statement contains 'default' but no 'case' labels.
		}
	}

	namespace crash_ {
		void A(
			flw::ioflow__ &Flow,
			bso::sBool FromLocalhost )
		{
			if ( FromLocalhost ) {
				tol::Crash();
			} else
				prxybase::PutAnswer( prxybase::aForbidden, Flow );

			Flow.Commit();
		}
	}

	void Crash_(
		csdcmn::sVersion Version,
		flw::sIOFlow &Flow,
		bso::sBool FromLocalhost )
	{
		switch ( Version ) {
		default:
			return crash_::A( Flow, FromLocalhost );
			break;
#pragma warning( suppress: 4065 )	//  switch statement contains 'default' but no 'case' labels.
		}
	}

	namespace dismiss_ {

	}


	class callback__
	: public cProcessing
	{
	private:
		bso::sBool FromLocalhost_;
	protected:
		void *CSDSCBPreProcess( const ntvstr::char__ *Origin ) override
		{
		qRH
			qCBUFFERr Buffer;
		qRB
			FromLocalhost_ = strncmp( ntvstr::string___( Origin ).UTF8( Buffer ), "127.", 4 ) == 0;
		qRR
		qRT
		qRE
			return NULL;
		}
		csdscb::action__ CSDSCBProcess(
			flw::ioflow__ &Flow,
			void *UP ) override
		{
		qRH
			prxybase::eType Type = prxybase::t_Undefined;
			str::string Id;
			rProxy *Proxy = NULL;
			csdcmn::sVersion Version = csdcmn::UndefinedVersion;
		qRB
			if ( ( Version = csdcmn::GetProtocolVersion( prxybase::ProtocolId, Flow ) ) != prxybase::ProtocolVersion )
				qRGnr();

			switch ( prxybase::GetRequest( Flow ) ) {
			case prxybase::rPlug:
				Plug_( Version, Flow );
				break;
			case prxybase::rDismiss:
				Dismiss_( Version, Flow );
				break;
			case prxybase::rPing:
				Ping_( Version, Flow );
				break;
			case prxybase::rFreeze:
				Freeze_( Version, Flow, FromLocalhost_ );
				break;
			case prxybase::rCrash:
				Crash_( Version, Flow, FromLocalhost_ );
				break;
			default:
				qRGnr();
				break;
			}
		qRR
			Locker_.UnlockIfLocked();
		qRT
		qRE
			return csdscb::aStop;
		}
		virtual void CSDSCBPostProcess( void *UP ) override
		{}
	public:
		void reset( bso::bool__ P = true )
		{
			FromLocalhost_ = false;
		}
		E_CVDTOR( callback__ );
		void Init( void )
		{
			FromLocalhost_ = false;
		}
	};
}

namespace {

	void Process_( void )
	{
	qRH
		csdbns::server___ Server;
		callback__ Callback;
	qRB
		Callback.Init();
		Server.Init(sclmisc::MGetU16( registry::parameter::Service ), Callback );
		Server.Process( &FreezeFlag_ );
	qRR
	qRT
	qRE
	}

	void Ping_( void )
	{
		watchdog::Ping();
	}

	void Freeze_( void )
	{
		watchdog::Freeze();
	}

	void Crash_( void )
	{
		watchdog::Crash();
	}
}

#define C( name )\
	else if ( Command == #name )\
		name##_()
		

int scltool::SCLTOOLMain(
	const str::string_ &Command,
	const scltool::oddities__ &Oddities )
{
	int ExitValue = EXIT_FAILURE;
qRH
qRB
	if ( Command == "Version" )
		PrintHeader_();
	else if ( Command == "License" )
		epsmsc::PrintLicense( NAME_MC );
	C( Process );
	C( Ping );
	C( Freeze );
	C( Crash );
	else
		qRGnr();

	ExitValue = EXIT_SUCCESS;
qRR
qRT
qRE
	return ExitValue;
}

const char *sclmisc::SCLMISCTargetName = NAME_LC;

Q37_GCTOR( prxyq )
{
	PendingClients_.Init();
	PendingServers_.Init();

	Locker_.Init();
}

Q37_GDTOR( prxyq )
{
	DeletePendings_( PendingClients_ );
	DeletePendings_( PendingServers_ );
}

