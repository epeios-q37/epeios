/*
	Copyright (C) 2000-2015 Claude SIMON (http://q37.info/contact/).

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

//	$Id: srv.h,v 1.13 2012/11/14 16:06:37 csimon Exp $

#ifndef SRV__INC
#define SRV__INC

#define SRV_NAME		"SRV"

#define	SRV_VERSION	"$Revision: 1.13 $"

#define SRV_OWNER		"Claude SIMON (http://zeusw.org/intl/contact.html)"

#if defined( E_DEBUG ) && !defined( SRV_NODBG )
#define SRV_DBG
#endif

/* Begin of automatic documentation generation part. */

//V $Revision: 1.13 $
//C Claude SIMON (http://zeusw.org/intl/contact.html)
//R $Date: 2012/11/14 16:06:37 $

/* End of automatic documentation generation part. */

/******************************************************************************/
				  /* do not modify anything above this limit */
				  /*			  unless specified			 */
				  /*******************************************/

/* Addendum to the automatic documentation generation part. */
//D SeRVer 
/* End addendum to automatic documentation generation part. */

/*$BEGIN$*/

#error "Obsolete. Use 'CSDBNS' library instead."

#include "err.h"
#include "sck.h"

#define SRV__DEFAULT_TIMEOUT	SCK__DEFAULT_TIMEOUT

namespace srv {
	using namespace sck;

	//t The type of a service.
	typedef bso::ushort__	service__;

	enum action__ {
		aContinue,
		aStop,
		a_amount,
		a_Undefined
	};



	//c User functions with socket.
	class socket_functions__ {
	protected:
		virtual void *SRVPreProcess( sck::socket__ Socket ) = 0;
		virtual action__ SRVProcess(
			sck::socket__ Socket,
			void *UP ) = 0;
		virtual void SRVPostProcess( void *UP ) = 0;
	public:
		void *PreProcess( sck::socket__ Socket )
		{
			return SRVPreProcess( Socket );
		}
		action__ Process(
			sck::socket__ Socket,
			void *UP )
		{
			return SRVProcess( Socket, UP );
		}
		void PostProcess( void *UP )
		{
			SRVPostProcess( UP );
		}
	};

	//c User functions with flow handler.
	class flow_functions__ {
	protected:
		virtual void *SRVPreProcess( flw::ioflow__ &Flow ) = 0;
		virtual action__ SRVProcess(
			flw::ioflow__ &Flow,
			void *UP ) = 0;
		virtual void SRVPostProcess( void *UP ) = 0;
	public:
		void *PreProcess( flw::ioflow__ &Flow )
		{
			return SRVPreProcess( Flow );
		}
		action__ Process(
			flw::ioflow__ &Flow,
			void *UP )
		{
			return SRVProcess( Flow, UP );
		}
		void PostProcess( void *UP )
		{
			SRVPostProcess( UP );
		}
	};

	//c To listen at a port..
	class listener___
	{
	private:
		socket__ Socket_;
		/* Retourne une socket sur une connection. FONCTION BLOQUANTE.
		Lorsque 'IgnorerErreur'  vrai, toute les erreurs sont ignores, ceci pour garantir
		la prsence du processus d'coute. */
		socket__ Interroger_( err::handle ErrHandle );
	public:
		void reset( bool P = true )
		{
			if ( P )
			{
				if ( Socket_ != SCK_INVALID_SOCKET )
					Close( Socket_ );
			}

			Socket_ = SCK_INVALID_SOCKET;
		}
		listener___( void )
		{
			reset( false );
		}
		~listener___( void )
		{
			reset( true );
		}
		/*f Initialzation with 'Service' as port to listen.
		A maximum of 'Amount' are accepted in the waiting queue. */
		bso::bool__ Init(
			service__ Service,
			int Amount,
			err::handle ErrHandle = err::hUsual );
		/*f Initialzation with 'Service' as port to listen.
		A maximum of 'Amount' are accepted in the waiting queue. */
		bso::bool__ Init(
			service__ Service,
			err::handle ErrHandle = err::hUsual,
			int Amount = 5 )
		{
			return Init( Service, Amount, ErrHandle );
		}
		//f Return the first available connection. BLOCKING FUNCTION.
		socket__ GetConnection( err::handle ErrHandle = err::hUsual )
		{
			return Interroger_( ErrHandle );
		}
		//f Initialize 'Socket' with the first connection available. BLOCKING FUNCTION.
		void GetConnection(
			socket__ &Socket,
			err::handle ErrHandle = err::hUsual )
		{
			Socket = Interroger_( ErrHandle );
		}
		//f Handle new connection using 'Functions'. BLOCKING FUNCTION.
		void Process(
			socket_functions__ &Functions,
			err::handle ErrHandle = err::hUsual );
	};

#ifdef CPE__T_MT
	/*c Handling a server, with process duplication for each client. */
	class server___
	: public listener___
	{
	public:
		void reset( bool P = true )
		{
			listener___::reset( P );
		}
		server___( void )
		{
			reset( false );
		}
		~server___( void )
		{
			reset( true );
		}
		/*f Initialzation with 'Service' as port to listen.
		A maximum of 'Amount' are accepted in the waiting queue. */
		bso::bool__ Init(
			service__ Service,
			int Amount,
			err::handle ErrHandle = err::hUsual )
		{
			return listener___::Init( Service, Amount, ErrHandle );
		}
		/*f Initialzation with 'Service' as port to listen.
		A maximum of 'Amount' are accepted in the waiting queue. */
		bso::bool__ Init(
			service__ Service,
			err::handle ErrHandle = err::hUsual,
			int Amount = 5 )
		{
			return listener___::Init( Service, Amount, ErrHandle );
		}
		/*f Handle each new connection using 'Functions'. */
		void Process(
			socket_functions__ &Functions,
			err::handle ErrHandle = err::hUsual );
		/*f Handle each new connection using 'Functions'. */
		void Process(
			flow_functions__ &Functions,
			sck::duration__ TimeOut = SRV__DEFAULT_TIMEOUT,
			err::handle ErrHandle = err::hUsual );
	};

#endif
}
/*$END$*/
				  /********************************************/
				  /* do not modify anything belove this limit */
				  /*			  unless specified		   	  */
/******************************************************************************/

#endif
