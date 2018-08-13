/*
	Copyright (C) 2017 Claude SIMON (http://zeusw.org/epeios/contact.html).

	This file is part of 'XDHq' software.

    'XDHq' is free software: you can redistribute it and/or modify it
    under the terms of the GNU Affero General Public License as published
    by the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    'XDHq' is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with 'XDHq'.  If not, see <http://www.gnu.org/licenses/>.
*/

#ifndef PROXY_INC_
# define PROXY_INC_

# include "prtcl.h"

# include "csdscb.h"
# include "flw.h"
# include "str.h"

namespace proxy {
	using prtcl::StandBy;

	struct rArguments
	{
	public:
		str::wString Command;
		str::wStrings Strings;
		crt::qCRATEwl( str::dStrings ) XStrings;
		void reset( bso::sBool P = true )
		{
			tol::reset( P, Command, Strings, XStrings );
		}
		qCDTOR( rArguments );
		void Init( void )
		{
			tol::Init( Command, Strings, XStrings );
		}
	};

	void Send(
		flw::sWFlow &Flow,
		const rArguments &NewArguments );

	qENUM( Type )
	{
		tVoid,
			tString,
			tStrings,
			t_amount,
			t_Undefined
	};

	class rReturn
	{
	private:
		eType Type_;
		str::wString String_;
		str::wStrings Strings_;
		void Test_( eType Type ) const
		{
			if ( Type_ != Type )
				qRGnr();
		}
	public:
		void reset( bso::sBool P = true )
		{
			tol::reset( P, String_, Strings_ );
			Type_ = t_Undefined;
		}
		qCDTOR( rReturn );
		void Init( void )
		{
			tol::Init( String_, Strings_ );
			Type_ = t_Undefined;
		}
		str::dString &StringToSet( void )
		{
			Test_( t_Undefined );

			Type_ = tString;

			return String_;
		}
		str::dStrings &StringsToSet( void )
		{
			Test_( t_Undefined );

			Type_ = tStrings;

			return Strings_;
		}
		eType GetType( void ) const
		{
			return Type_;
		}
		const str::dString &GetString( void ) const
		{
			Test_( tString );

			return String_;
		}
		const str::dStrings &GetStrings( void ) const
		{
			Test_( tStrings );

			return Strings_;
		}
	};

	void Recv(
		eType ReturnType,
		flw::sRFlow &Flow,
		rReturn &Return );


	typedef tht::rReadWrite rControl_;

	// Data received from proxy.
	class rRecv
	: public rControl_
	{
	private:
	public:
		rReturn Return;
		str::wString	// For the launching of an action.
			Id,
			Action;
		void reset( bso::sBool P = true )
		{
			rControl_::reset( P );
			tol::reset( Return, Id, Action );
		}
		qCDTOR( rRecv );
		void Init( void )
		{
			rControl_::Init();
			tol::Init( Return, Id, Action );
		}
	};

	// Data sent to proxy.
	class rSent
	: public rControl_
	{
	public:
		rArguments Arguments;
		void reset( bso::sBool P = true )
		{
			rControl_::reset( P );
			tol::reset( P, Arguments );
		}
		qCDTOR( rSent );
		void Init( void )
		{
			rControl_::Init();
			tol::Init( Arguments );
		}
	};


	struct rData
	{
	private:
		eType ReturnType_;
	public:
		rRecv Recv;
		rSent Sent;
		str::wString Language;
		bso::sBool Handshaked;
		bso::sBool PendingRequest;
		void reset( bso::sBool P = true )
		{
			tol::reset( P, Recv, Sent, Language, Handshaked, PendingRequest );
			ReturnType_ = t_Undefined;
		}
		qCDTOR( rData );
		void Init( void )
		{
			reset();

			tol::Init( Recv, Sent, Language );
			ReturnType_ = t_Undefined;
			PendingRequest = false;
			Handshaked = false;
		}
		void SetReturnType( eType Type )
		{
			ReturnType_ = Type;
			PendingRequest = true;
		}
		eType GetReturnType( void ) const
		{
			if ( ReturnType_ == t_Undefined )
				qRGnr();

			return ReturnType_;

		}
		bso::sBool _IsTherePendingRequest( void ) const
		{
			return PendingRequest;
		}
	};

	void Handshake_(
		flw::sRFlow &Flow,
		str::dString &Language );

	void GetAction_(
		flw::sRWFlow &Flow,
		str::dString &Id,
		str::dString &Action );

	template <typename data> class rProcessing
	: public csdscb::cProcessing
	{
	private:
		// Action to launch on a new session.
		str::wString NewSessionAction_;
	protected:
		virtual void *CSDSCBPreProcess( const ntvstr::char__ *Origin ) override
		{
			data *Data = NULL;
		qRH;
			flw::sDressedRWFlow<> Flow;
		qRB;
			Data = PRXYNew();

			if ( Data == NULL )
				qRAlc();
		qRR;
			if ( Data != NULL )
				delete Data;
		qRT;
		qRE;
			return Data;
		}
		virtual csdscb::eAction CSDSCBProcess(
			fdr::rRWDriver *IODriver,
			void *UP ) override
		{
		qRH;
			flw::sDressedRWFlow<> Flow;
			data &Data = *(data *)UP;
		qRB;
			if ( UP == NULL )
				qRGnr();

			Flow.Init( *IODriver );

			if ( !Data.Handshaked ) {
				Data.Recv.WriteDismiss();

				Handshake_( Flow, Data.Language );
				Data.Handshaked = true;

				flw::PutString( StandBy, Flow );
				Flow.Commit();
			} else {
				if ( Data._IsTherePendingRequest() ) {
					Data.Recv.WriteBegin();
					Data.Recv.Return.Init();
					proxy::Recv( Data.GetReturnType(), Flow, Data.Recv.Return );
					Data.PendingRequest = false;
					Data.Recv.WriteEnd();
					PRXYOnPending( &Data );
				} else {
					Data.Recv.WriteBegin();
					tol::Init( Data.Recv.Id, Data.Recv.Action );
					GetAction_( Flow, Data.Recv.Id, Data.Recv.Action );
					if ( Data.Recv.Action.Amount() == 0 ) {
						if ( Data.Recv.Id.Amount() == 0 )
							Data.Recv.Action = NewSessionAction_;
						else
							qRGnr();
					}
					Data.Recv.WriteEnd();
					PRXYOnAction( &Data );
				}

				Data.Sent.ReadBegin();

				// 'Data.Request' is set by the 'PRXYOn...' method above.
				if ( Data._IsTherePendingRequest() )
					proxy::Send( Flow, Data.Sent.Arguments );
				else
					flw::PutString( StandBy, Flow );

				Data.Sent.ReadEnd();
			}
		qRR;
		qRT;
		qRE;
			return csdscb::aContinue;
		}
		virtual bso::sBool CSDSCBPostProcess( void *UP ) override
		{
			data *Data = (data *)UP;

			if ( Data == NULL )
				qRGnr();

			delete Data;

			return false;
		}
		virtual data *PRXYNew( void ) = 0;
		virtual void PRXYOnAction( data *Data ) = 0;
		virtual void PRXYOnPending( data *Data ) = 0;
	public:
		void reset( bso::sBool P = true )
		{
			tol::reset( P, NewSessionAction_ );
		}
		qCVDTOR( rProcessing );
		void Init( const str::dString &NewSessionAction )
		{
			NewSessionAction_.Init( NewSessionAction );
		}
	};

	template <typename data> class rSharing
	{
	private:
		rControl_ Control_;
		data *Data_;
	public:
		void reset( bso::sBool P = true )
		{
			tol::reset( P, Control_, Data_ );
		}
		qCDTOR( rSharing );
		void Init( void )
		{
			Control_.Init();
			Data_ = NULL;
		}
		void Write( data *Data )
		{
			Control_.WriteBegin();

			if ( Data_ != NULL )
				qRGnr();

			if ( Data == NULL )
				qRGnr();

			Data_ = Data;

			Control_.WriteEnd();

		}
		data *Read( void )
		{
			Control_.ReadBegin();

			data *Data = Data_;

			if ( Data_ == NULL )
				qRFwk();

			Data_ = NULL;

			Control_.ReadEnd();

			return Data;
		}
	};
}

#endif