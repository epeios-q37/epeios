/*
	Copyright (C) 1999-2016 Claude SIMON (http://q37.info/contact/).

	This file is part of the Epeios framework.

	The Epeios framework is free software: you can redistribute it and/or
	modify it under the terms of the GNU Affero General Public License as
	published by the Free Software Foundation, either version 3 of the
	License, or (at your option) any later version.

	The Epeios framework is distributed in the hope that it will be useful,
	but WITHOUT ANY WARRANTY; without even the implied warranty of
	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
	Affero General Public License for more details.

	You should have received a copy of the GNU Affero General Public License
	along with the Epeios framework.  If not, see <http://www.gnu.org/licenses/>
*/

#ifndef CSDSNS__INC
# define CSDSNS__INC

# define CSDSNS_NAME		"CSDSNS"

# if defined( E_DEBUG ) && !defined( CSDSNS_NODBG )
#  define CSDSNS_DBG
# endif

// Client-Server Standard Network Server

# include "err.h"
# include "flw.h"
# include "csdbns.h"
# include "csdsnb.h"
# include "lstbch.h"
# include "mtx.h"

namespace csdsns {

	using namespace csdsnb;
	using namespace csdscb;

	using csdbns::port__;

	enum log__ {
		lNew,
		lStore,
		lTestAndGet,
		lDelete,
		l_amount,
		l_Undefined
	};

	const char *GetLogLabel( log__ Log );

	typedef void *_user_pointer__;

	class log_functions__ {
	protected:
		virtual void CSDSNSLog(
			log__ Log,
			id__ Id,
			void *UP,
			sdr::size__ Amount )
		{}
	public:
		void reset( bso::bool__  = true )
		{
			// Standardisation.
		}
		log_functions__( void )
		{
			reset( false );
		}
		~log_functions__( void )
		{
			reset();
		}
		void Init( void )
		{
			// Standardisation.
		}
		void Log(
			log__ Log,
			id__ Id,
			_user_pointer__ UP,
			sdr::size__ Amount )
		{
			CSDSNSLog( Log, Id, UP, Amount );
		}
	};

	typedef lstbch::E_LBUNCH_( _user_pointer__ ) user_pointers_;

	class core_
	{
	private:
		bso::bool__ _Exists( id__ Id ) const
		{
			return UPs.Exists( Id );
		}
		void _Log(
			log__ Log,
			id__ Id,
			void *UP ) const
		{
			if ( S_.Log.Functions != NULL ) {
qRH
qRB
				mtx::Lock( S_.Log.Mutex );
				S_.Log.Functions->Log( Log, Id, UP, UPs.Amount() );
qRR
qRT
				mtx::Unlock( S_.Log.Mutex );
qRE
			}
		}
	public:
		struct s
		{
			user_pointers_::s UPs;
			mtx::handler___ Mutex;
			struct log__ {
				log_functions__ *Functions;
				mtx::handler___ Mutex;
			} Log;
		} &S_;
		user_pointers_ UPs;
		core_ ( s &S )
		: S_( S ),
		  UPs( S.UPs )
		{}
		void reset( bso::bool__ P = true )
		{
			if ( P ) {
				if ( S_.Mutex != mtx::UndefinedHandler )
					mtx::Delete( S_.Mutex );
			}

			UPs.reset( P );
			S_.Mutex = mtx::UndefinedHandler;
			S_.Log.Mutex = mtx::UndefinedHandler;
			S_.Log.Functions = NULL;

		}
		void plug( qAS_ &AS )
		{
			UPs.plug( AS );
		}
		core_ &operator =( const core_ &C )
		{
			qRFwk();

			return *this;
		}
		void Init( log_functions__ &LogFunctions )
		{
			reset();

			UPs.Init();
			S_.Mutex = mtx::Create();
			S_.Log.Mutex = mtx::Create();
			S_.Log.Functions = &LogFunctions;
		}
		id__ New( void )
		{
			mtx::Lock( S_.Mutex );

			sdr::row__ Row = UPs.New();

			if ( *Row >= BSO_U16_MAX )
				qRLmt();

			mtx::Unlock( S_.Mutex );

			_Log( lNew, (id__)*Row, NULL );

			return (id__)*Row;
		}
		void Store(
			_user_pointer__ UP,
			id__ Id )
		{
#ifdef CSDSNS_DBG
			if ( Id == CSDSNB_UNDEFINED )
				qRFwk();
#endif
			mtx::Lock( S_.Mutex );
			UPs.Store( UP, Id );
			mtx::Unlock( S_.Mutex );

			_Log( lStore, Id, UP );
		}
		bso::bool__ Exists( id__ Id ) const
		{
			bso::bool__ Result;

			mtx::Lock( S_.Mutex );

			Result =  _Exists( Id );

			mtx::Unlock( S_.Mutex );

			return Result;
		}
		bso::bool__ TestAndGet(
			id__ Id,
			void *&UP ) const
		{
			bso::bool__ Result = false;

			mtx::Lock( S_.Mutex );

			Result = _Exists( Id );

			if ( Result )
				UP = UPs( Id );

			mtx::Unlock( S_.Mutex );

			_Log( lTestAndGet, Id, UP );

			return Result;
		}
		bso::bool__ Delete( id__ Id )
		{
			bso::bool__ Result = false;

			mtx::Lock( S_.Mutex );

			Result = _Exists( Id );

			if ( Result )
				UPs.Delete( Id );

			mtx::Unlock( S_.Mutex );

			_Log( lDelete, Id, NULL );

			return Result;
		}

	};

	E_AUTO( core)

	class _callback___
	: public callback__
	{
	private:
		core _Core;
		callback__ *_Callback;
		ntvstr::string___ _Origin;
		void _Clean( void );	// Appelle le 'PostProcess' pour tous les objets utilisateurs.
	protected:
		virtual void *CSDSCBPreProcess( const ntvstr::char__ *Origin ) override
		{
			_Origin.Init( Origin );

			return NULL;
		}
		virtual action__ CSDSCBProcess(
			flw::ioflow__ &Flow,
			void *UP )
		{
#ifdef CSDSNS_DBG
			if ( UP != NULL )
				qRFwk();
#endif
			id__ Id = CSDSNB_UNDEFINED;
			action__ Action = aContinue;

			UP = NULL;

			Id = GetId( Flow );

			if ( Id == CSDSNB_UNDEFINED ) {
				Id = _Core.New();
				PutId( Id, Flow );
				UP = _Callback->PreProcess( _Origin );
				_Core.Store( UP, Id );
				Action = _Callback->Process( Flow, UP );
			} else if ( Id == CSDSNB_PING ) {
				Flow.Put( (flw::byte__)0 );
				Flow.Commit();
			} else if ( !_Core.TestAndGet( Id, UP ) ) {
				Flow.Put( (flw::byte__)-1 );
				Flow.Commit();
				Action = aStop;
			} else {
				Flow.Put( 0 );
				Action = _Callback->Process( Flow, UP );
			}

			switch ( Action ) {
			case aContinue:
				break;
			case aStop:
				_Callback->PostProcess( UP );
				if ( Id < CSDSNB_RESERVED )
					_Core.Delete( Id );
				break;
			default:
				qRFwk();
				break;
			}

			return Action;
		}
		virtual void CSDSCBPostProcess( void *UP )
		{
			if ( UP != NULL )
				qRFwk();
		}
	public:
		void reset( bso::bool__ P = true )
		{
			if ( P )
				_Clean();

			_Core.reset( P );
			_Callback = NULL;
			_Origin.reset( P );
			callback__::reset( P );
		}
		_callback___( void)
		{
			reset( false );
		}
		~_callback___( void)
		{
			reset();
		}
		void Init(
			callback__ &Callback,
			log_functions__ &LogFunctions )
		{
			reset();

			_Core.Init( LogFunctions );
			_Callback = &Callback;
			_Origin.Init();
			callback__::Init();
		}
	};

	// Pour l'utilisation en tant que service Windows, voir csdbns::server__'. 
	class server___
	{
	private:
		csdbns::server___ _Server;
		_callback___ _Callback;
	public:
		void Init(
			port__ Port,
			callback__ &Callback,
			log_functions__ &LogFunctions = *(log_functions__ *)NULL )
		{
			_Callback.Init( Callback, LogFunctions );

			_Server.Init( Port, _Callback );
		}
		bso::bool__ LaunchService( const char *ServiceName )
		{
			return _Server.LaunchService( ServiceName );
		}
		void Process( sck::duration__ TimeOut = SCK_INFINITE )
		{
			_Server.Process( TimeOut );
		}
	};


}

#endif
