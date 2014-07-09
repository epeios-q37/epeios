/*
	Header for the 'sck' library by Claude SIMON (http://zeusw.org/intl/contact.html)
	Copyright (C) 2000-2004 Claude SIMON (http://zeusw.org/intl/contact.html).

	This file is part of the Epeios (http://zeusw.org/epeios/) project.

	This library is free software; you can redistribute it and/or
	modify it under the terms of the GNU General Public License
	as published by the Free Software Foundation; either version 3
	of the License, or (at your option) any later version.
 
	This program is distributed in the hope that it will be useful,
	but WITHOUT ANY WARRANTY; without even the implied warranty of
	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
	GNU General Public License for more details.

	You should have received a copy of the GNU General Public License
	along with this program; if not, go to http://www.fsf.org/
	or write to the:
  
         	         Free Software Foundation, Inc.,
           59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
*/

//	$Id: sck.h,v 1.55 2013/05/17 15:03:50 csimon Exp $

#ifndef SCK__INC
#define SCK__INC

#define SCK_NAME		"SCK"

#define	SCK_VERSION	"$Revision: 1.55 $"

#define SCK_OWNER		"Claude SIMON (http://zeusw.org/intl/contact.html)"

#include "ttr.h"

extern class ttr_tutor &SCKTutor;

#if defined( E_DEBUG ) && !defined( SCK_NODBG )
#define SCK_DBG
#endif

/* Begin of automatic documentation generation part. */

//V $Revision: 1.55 $
//C Claude SIMON (http://zeusw.org/intl/contact.html)
//R $Date: 2013/05/17 15:03:50 $

/* End of automatic documentation generation part. */

/******************************************************************************/
				  /* do not modify anything above this limit */
				  /*			  unless specified			 */
				  /*******************************************/

/* Addendum to the automatic documentation generation part. */
//D SoCKet 
/* End addendum to automatic documentation generation part. */

/*$BEGIN$*/

#include "err.h"
#include "cpe.h"
#include "fdr.h"
#include "flw.h"
#include "tol.h"

#if defined( CPE_POSIX )
#	define SCK__POSIX
#elif defined( CPE_WIN )
#	define SCK__WIN
#else
#	error "Uknown target !"
#endif

#ifdef SCK__WIN
#	include <winsock.h>
#	define SCK_INVALID_SOCKET		INVALID_SOCKET
#	define SCK_SOCKET_ERROR			SOCKET_ERROR
#	define SCK_ECONNRESET			WSAECONNRESET
#	define SCK_EWOULDBLOCK			WSAEWOULDBLOCK
#	define SCK_EAGAIN				WSAEWOULDBLOCK	// Pas de 'WSAEAGAIN', mais mettre �a simplifie certaines lignes.
#	define SCK_EINTR				WSAEINTR
#	define SCK_ENOTSOCK				WSAENOTSOCK
#elif defined( SCK__POSIX )
#  include <arpa/inet.h>
#	include <sys/time.h>
#	include <sys/types.h>
#	include <sys/socket.h>
#	include <unistd.h>
#	include <netinet/in.h>
#	include <sys/ioctl.h>
#	include <errno.h>
#	define SCK_INVALID_SOCKET		-1
#	define SCK_SOCKET_ERROR			-1
#	define SCK_ECONNRESET			ECONNRESET
#	define SCK_EWOULDBLOCK			EWOULDBLOCK
#	define SCK_EAGAIN				EAGAIN
#	define SCK_EINTR				EINTR
#	define SCK_ENOTSOCK				ENOTSOCK
#else
#	error
#endif

//d Value to give to the 'TimeOut' parameter to indicate waiting forever.
#define SCK_INFINITE	BSO_U16_MAX

//d Returned value to indicate that the connection no longer exists.
#define SCK_DISCONNECTED	-1

#ifndef SCK_SOCKET_FLOW_BUFFER_SIZE
//d The size of the buffers used by the flows.
#	define SCK_SOCKET_FLOW_BUFFER_SIZE	500
#endif

#ifdef SCK_DEFAULT_TIMEOUT
#	define SCK__DEFAULT_TIMEOUT	SCK_DEFAULT_TIMEOUT
#else
#	define SCK__DEFAULT_TIMEOUT	SCK_INFINITE
#endif

//d Max data amount of concurrent write and read.
#define SCK__DEFAULT_AMOUNT	( 100 * 1024 * 1024 )

namespace sck {
	using flw::datum__;
#ifdef SCK__WIN
	typedef SOCKET socket__;
	typedef char *	cast__;
#elif defined( SCK__POSIX )
	typedef int	socket__;
	typedef void * cast__;
#else
#	error
#endif

	typedef int error__;

	typedef bso::u16__	duration__;

	/* NOTA: Les deux d�clarations ci-dessous ont �t� mise en place pour simplifier
	l'usage des sockets sous Windows. En effet, ce dernier, et lui seul, ne r�alise
	pas automatiquement l'initialisation de la couche r�seau. Cette biblioth�que,
	cependant, propose une fonction permettant d'assurer un comportement identique
	sur un maximum de syt�me. Cette fonction n'est pas utilis�e par cette biblioth�que,
	mais une utilisation pertinente de cette fonction, notamment par les biblioth�ques
	g�rant respectivement les fonctionnalit�s de serveur et de client, permettront
	� l'utilisateur de faire abstraction de la contrainte impos�e par Windows. */

	// Vrai si l'initialisation de la couche r�seau a �t� faite, faux sinon.
	extern bool Ready_;

	//f Initialize TCP/IP layer.
	inline void Initialize( void )
	{
		if ( !Ready_ )
		{
#ifdef SCK__WIN
			WORD wVersionRequested;
			WSADATA wsaData;

			wVersionRequested = MAKEWORD( 1, 1);

			if ( WSAStartup( wVersionRequested, &wsaData ) )
				ERRLbr();
#elif defined( SCK__POSIX )
			Ready_ = true;
#else
#	error
#endif

		}
	}

	//f Create a socket. Only used in some particular multitasking program.
	inline socket__ CreateSocket( err::handling__ ErrorHandling = err::h_Default )
	{
	#ifdef CPE_BEOS
		socket__ Desc = socket( AF_INET, SOCK_STREAM, 0 );
	#else
		socket__ Desc = socket( PF_INET, SOCK_STREAM, 0 );
	#endif
		if ( ( Desc == SCK_INVALID_SOCKET ) && ( ErrorHandling == err::hThrowException ) )
			ERRSys();

		return Desc;
	}

	//f 'Error' becomes the error value returned by 'SCKError()'.
	inline void Error( error__ Error )
	{
#ifdef SCK__WIN
		WSASetLastError( Error );
#elif defined( SCK__POSIX )
		errno = Error;
#else
#	error
#endif
	}

	//f Return the last error.
	inline error__ Error( void )
	{
#ifdef SCK__WIN
		return WSAGetLastError();
#elif defined( SCK__POSIX )
		return errno;
#else
#	error
#endif
	}

	inline const char *ErrorDescription( error__ Error )
	{
#ifdef SCK__WIN
		return ("Not implemented" );
#elif defined( SCK__POSIX )
		return strerror( Error );
#else
#	error
#endif
	}


#ifndef CPE_BEOS
	/*f The socket 'Socket' becomes blocking or not, depend on the value of 'Value'.
	Not currently available under Be OS. */
	inline void Blocking(
		socket__ Socket,
		bso::bool__ Value )
	{
		unsigned long *V;

		if ( Value )
			V = (unsigned long *)"\x0\x0\x0\x0";
		else
			V = (unsigned long *)"1111";

#	ifdef SCK__WIN
		ioctlsocket( Socket, FIONBIO, V );
#	elif defined( SCK__POSIX )
		ioctl( Socket, FIONBIO, V );
#	else
#		error
#	endif
	}
#endif

	/*f Put in 'Buffer' up to 'Amount' bytes for the 'Socket' socket. Return
	the amount effectively red. If 0 is returned, it means that the 'Timeout'
	expired. If the connection no longer exists, then 'SCK_DISCONNECTED' is
	returned. */
	flw::size__ Read(
		socket__ Socket,
		flw::size__ Amount,
		void *Buffer,
		duration__ TimeOut = SCK_INFINITE );	// En secondes.

	/*f Write up to 'Amount' bytes from 'Buffer' to the socket 'Socket'. Return
	the amount effectively written. If 0 is returned, it means 'TimeOut' expired.
	If connection no longer exists, then 'SCK_DISCONNECTED' is returned. */
	flw::size__ Write(
		socket__ Socket,
		const void *Buffer,
		flw::size__ Amount,
		duration__ TimeOut = SCK_INFINITE );	// En secondes.

	//f Close the socket 'Socket'.
	inline void Close( socket__ Socket )
	{
#ifdef SCK__WIN
	//	shutdown( Socket, 2 );
		if ( closesocket( Socket ) == SCK_SOCKET_ERROR )
			ERRLbr();
#elif defined( SCK__POSIX )
	//	shutdown( Socket, 2 );
		if ( close( Socket ) == SCK_SOCKET_ERROR )
			ERRLbr();
#else
#	error
#endif
	}

	typedef fdr::ioflow_driver___<> _ioflow_driver___;

	//c Socket as input/output flow driver.
	class socket_ioflow_driver___
	: public _ioflow_driver___
	{
	private:
		socket__ _Socket;
		duration__ _TimeOut;	// En secondes.
		bso::bool__ _Error;
		time_t _EpochTimeStamp;	// Horodatage de la derni�re activit� (lecture ou �criture);
		void _Touch( void )
		{
			_EpochTimeStamp = tol::EpochTime( false );
		}
	protected:
		virtual fdr::size__ FDRRead(
			fdr::size__ Maximum,
			fdr::datum__ *Buffer )
		{
			if ( ( Maximum = sck::Read( _Socket, ( Maximum ), Buffer, _TimeOut ) ) == SCK_DISCONNECTED )
				Maximum = 0;
			else
				_Touch();

			return Maximum;
		}
		virtual fdr::size__ FDRWrite(
			const fdr::datum__ *Buffer,
			fdr::size__ Maximum )
		{
			if ( _Error )
				ERRFwk();

			if ( ( Maximum = sck::Write( _Socket, Buffer, Maximum, _TimeOut ) ) == SCK_DISCONNECTED ) {
				_Socket = SCK_INVALID_SOCKET;
				_Error = true;
				Maximum = 0;
				ERRLbr();
			} else
				_Touch();

			return Maximum;
		}
		virtual void FDRDismiss( void )
		{}
		virtual void FDRCommit( void )
		{}
	public:
		void reset( bool P = true )
		{
			if ( P ) {
				if ( _Socket != SCK_INVALID_SOCKET ) {
					_ioflow_driver___::Commit();
					Close( _Socket );
				}
			}

			_ioflow_driver___::reset( P );
								
			_Socket = SCK_INVALID_SOCKET;
			_TimeOut = SCK_INFINITE;
			_Error = false;
			_EpochTimeStamp = 0;
		}
		socket_ioflow_driver___( void )
		{
			reset( false );
		}
		virtual ~socket_ioflow_driver___( void )
		{
			reset();
		}
		//f Initialization with socket 'Socket' and 'TimeOut' as timeout.
		void Init(
			socket__ Socket,
			fdr::thread_safety__ ThreadSafety,
			duration__ TimeOut = SCK__DEFAULT_TIMEOUT )	// En secondes.
		{
			reset();
		
			_ioflow_driver___::Init( ThreadSafety );

			_Socket = Socket;
			_TimeOut = TimeOut;
			_Touch();	// On suppose qu'il n'y a pas une trop longue attente entre la cr�ation de la socket et l'appel � cette m�thode ...
		}
		E_RODISCLOSE__( socket__, Socket )
		E_RODISCLOSE__( time_t, EpochTimeStamp )
	};

	//c Socket as input/output flow driver.
	class socket_ioflow___
	: public flw::ioflow__
	{
	private:
		socket_ioflow_driver___ _Driver;
		flw::datum__ _Cache[2 * SCK_SOCKET_FLOW_BUFFER_SIZE];
	public:
		void reset( bool P = true )
		{
			ioflow__::reset( P );
			_Driver.reset( P );
		}
		socket_ioflow___( void )
		{
			reset( false );
		}
		virtual ~socket_ioflow___( void )
		{
			reset();
		}
		//f Initialization with socket 'Socket' and 'TimeOut' as timeout.
		void Init(
			socket__ Socket,
			flw::size__ AmountMax = SCK__DEFAULT_AMOUNT,
			duration__ TimeOut = SCK__DEFAULT_TIMEOUT ) // En secondes.
		{
			reset();

			_Driver.Init( Socket, fdr::tsEnabled, TimeOut );
			ioflow__::Init( _Driver, _Cache, sizeof( _Cache ), AmountMax );
		}
		socket__ Socket( void ) const
		{
			return _Driver.Socket();
		}
		time_t EpochTimeStamp( void )
		{
			return _Driver.EpochTimeStamp();
		}
	};

}

/*$END$*/
				  /********************************************/
				  /* do not modify anything belove this limit */
				  /*			  unless specified		   	  */
/******************************************************************************/

#endif
