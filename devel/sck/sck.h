/*
	Copyright (C) 1999 Claude SIMON (http://q37.info/contact/).

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

#ifndef SCK_INC_
#define SCK_INC_

#define SCK_NAME		"SCK"

#if defined( E_DEBUG ) && !defined( SCK_NODBG )
#define SCK_DBG
#endif

//D SoCKet

#include "err.h"
#include "cpe.h"
#include "fdr.h"
#include "flw.h"
#include "tol.h"

#if defined( CPE_S_POSIX )
#	define SCK__POSIX
#elif defined( CPE_S_WIN )
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
#	define SCK_EAGAIN				WSAEWOULDBLOCK	// No'WSAEAGAIN', but this entry allows some simplification.
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
# include <poll.h>
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

//d Value to give to the 'Timeout' parameter to indicate waiting forever.
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
#define SCK__DEFAULT_AMOUNT	FLW_AMOUNT_MAX

/**************/
/**** OLD *****/
/**************/

namespace sck {
	using flw::byte__;
#ifdef SCK__WIN
	typedef SOCKET socket__;
	typedef char *cast__;
#elif defined( SCK__POSIX )
	typedef int	socket__;
	typedef void *cast__;
#else
#	error
#endif
	typedef cast__ sCast_;

	typedef int error__;

	typedef bso::u16__	duration__;

	qCDEF(duration__, NoTimeout, SCK_INFINITE);

	/* NOTA: Les deux dclarations ci-dessous ont t mise en place pour simplifier
	l'usage des sockets sous Windows. En effet, ce dernier, et lui seul, ne ralise
	pas automatiquement l'initialisation de la couche rseau. Cette bibliothque,
	cependant, propose une fonction permettant d'assurer un comportement identique
	sur un maximum de sytme. Cette fonction n'est pas utilise par cette bibliothque,
	mais une utilisation pertinente de cette fonction, notamment par les bibliothques
	grant respectivement les fonctionnalits de serveur et de client, permettront
	 l'utilisateur de faire abstraction de la contrainte impose par Windows. */

	 // Vrai si l'initialisation de la couche rseau a t faite, faux sinon.
	extern bool Ready_;
}

/**************/
/**** NEW *****/
/**************/

namespace sck {
	typedef duration__ sTimeout;
	typedef socket__ sSocket;

	qCDEF(sSocket, Undefined, SCK_INVALID_SOCKET);
}

/**************/
/**** OLD *****/
/**************/

namespace sck {

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
				qRLbr();
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
		socket__ Desc = socket( PF_INET, SOCK_STREAM, 0 );

		if ( ( Desc == SCK_INVALID_SOCKET ) && ( ErrorHandling == err::hThrowException ) )
			qRSys();

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

	/*f The socket 'Socket' becomes blocking or not, depend on the value of 'Value'.
	Not currently available under Be OS. */
	inline void Blocking(
		socket__ Socket,
		bso::bool__ Value)
	{
		unsigned long *V;

		if ( Value )
			V = (unsigned long *)"\x0\x0\x0\x0";
		else
			V = (unsigned long *)"1111";

#	ifdef SCK__WIN
		ioctlsocket(Socket, FIONBIO, V);
#	elif defined( SCK__POSIX )
		ioctl(Socket, FIONBIO, V);
#	else
#		error
#	endif
	}

	/*f Put in 'Buffer' up to 'Amount' bytes for the 'Socket' socket. Return
	the amount effectively red. If 0 is returned, it means that the 'Timeout'
	expired. If the connection no longer exists, then 'SCK_DISCONNECTED' is
	returned. */
	flw::size__ Read(
		socket__ Socket,
		flw::size__ Amount,
		void *Buffer,
		duration__ Timeout,	// En secondes.
		const bso::sBool *BreakFlag);

	/*f Write up to 'Amount' bytes from 'Buffer' to the socket 'Socket'. Return
	the amount effectively written. If 0 is returned, it means 'Timeout' expired.
	If connection no longer exists, then 'SCK_DISCONNECTED' is returned. */
	flw::size__ Write(
		socket__ Socket,
		const void *Buffer,
		flw::size__ Amount,
		duration__ Timeout,	// En secondes.
		const bso::sBool *BreakFlag);

	/* To initiate a connection closing, which socket is handled from another thread.
	The socket will be than closed gracefully. See 'Close(…)' */
	bso::sBool Shutdown(
		socket__ Socket,
		qRPN);

	// Close the socket 'Socket'.
	/* If 'Socket' is in a 'select' in another thread (waiting that data is available to be red),
	it would be indefinitely blocked in this 'select', and the socket will be never closed.
	To avoid this, use 'Shutdown(…)'.
	*/
	bso::sBool Close(
		socket__ Socket,
		qRPN);	// To set to 'qRPU' when called from destructors !

	typedef fdr::ioflow_driver___<> _ioflow_driver___;

	//c Socket as input/output flow driver.
	class socket_ioflow_driver___
		: public _ioflow_driver___
	{
	private:
		socket__ Socket_;
		duration__ Timeout_;	// En secondes.
		bso::bool__ IsAlive_;	// Still at true after reading or writing returning 0 when break occurs.
		bso::sBool Owner_;
		time_t EpochTimeStamp_;	// Horodatage de la dernire activit (lecture ou criture);
		const bso::sBool *BreakFlag_;
		void _Touch(void)
		{
			EpochTimeStamp_ = tol::EpochTime(false);
		}
	protected:
		virtual fdr::size__ FDRRead(
			fdr::size__ Maximum,
			fdr::byte__ *Buffer) override
		{
			fdr::sSize Red = 0;

			if ( !IsAlive_ )
				qRFwk();

			if ( ( Red = sck::Read(Socket_, ( Maximum ), Buffer, Timeout_, BreakFlag_) ) == (fdr::sSize)SCK_DISCONNECTED ) {
				Red = 0;
				IsAlive_ = false;
			} else
				_Touch();

			return Red;
		}
		virtual bso::sBool FDRDismiss(
			bso::sBool Unlock,
			qRPN ) override
		{
			return true;
		}
		virtual fdr::sTID FDRRTake( fdr::sTID Owner ) override
		{
			return fdr::UndefinedTID;
		}
		virtual fdr::size__ FDRWrite(
			const fdr::byte__ *Buffer,
			fdr::size__ Maximum ) override
		{
			fdr::sSize Written = 0;

			if ( !IsAlive_ )
				qRFwk();

			if ( ( Written = sck::Write(Socket_, Buffer, Maximum, Timeout_, BreakFlag_) ) == (fdr::sSize)SCK_DISCONNECTED ) {
				Socket_ = SCK_INVALID_SOCKET;
				IsAlive_ = false;
				Written = 0;
			} else
				_Touch();

			return Written;
		}
		virtual bso::sBool FDRCommit(
			bso::sBool Unlock,
			qRPN ) override
		{
			return true;
		}
		virtual fdr::sTID FDRWTake( fdr::sTID Owner ) override
		{
			return fdr::UndefinedTID;
		}
	public:
		void reset( bool P = true )
		{
			_ioflow_driver___::reset( P );

			if ( P ) {
				if ( Socket_ != Undefined ) {
					if ( Owner_ )
						Close( Socket_, qRPU );
				}
			}

			Socket_ = Undefined;
			Timeout_ = NoTimeout;
			IsAlive_ = false;
			EpochTimeStamp_ = 0;
			Owner_ = false;
			BreakFlag_ = NULL;
		}
		socket_ioflow_driver___( void )
		{
			reset( false );
		}
		virtual ~socket_ioflow_driver___( void )
		{
			reset();
		}
		//f Initialization with socket 'Socket' and 'Timeout' as timeout.
		void Init(
			socket__ Socket,
			bso::sBool TakeOwnership,
			fdr::thread_safety__ ThreadSafety)	// En secondes.
		{
			reset();

			_ioflow_driver___::Init( ThreadSafety );

			Socket_ = Socket;
			Owner_ = TakeOwnership;
			IsAlive_ = true;
			_Touch();	// On suppose qu'il n'y a pas une trop longue attente entre la cration de la socket et l'appel  cette mthode ...
		}
		void RearmAfterBreak(fdr::thread_safety__ ThreadSafety)	// To rearm the drive after a break on timeout.
		{
			if ( !IsAlive_ )
				qRFwk();

			_ioflow_driver___::Init(ThreadSafety);
		}
		void SetBreakFlag(
			sTimeout Timeout,	// In ms
			const bso::sBool *Flag)
		{
			if ( ( Timeout != NoTimeout ) && ( Flag == NULL ) )
				qRFwk();

			Timeout_ = Timeout;
			BreakFlag_ = Flag;
		}
		void EraseBreakFlag(void)
		{
			SetBreakFlag(NoTimeout, NULL);
		}
		qRODISCLOSEs(socket__, Socket);
		qRODISCLOSEs(time_t, EpochTimeStamp);
		qRODISCLOSEs(bso::sBool, IsAlive);
	};

	//c Socket as input/output flow driver.
	class socket_ioflow___
	: public flw::ioflow__
	{
	private:
		socket_ioflow_driver___ Driver_;
		flw::byte__ Cache_[2 * SCK_SOCKET_FLOW_BUFFER_SIZE];
	public:
		void reset( bool P = true )
		{
			ioflow__::reset( P );
			Driver_.reset( P );
		}
		socket_ioflow___( void )
		{
			reset( false );
		}
		virtual ~socket_ioflow___( void )
		{
			reset();
		}
		//f Initialization with socket 'Socket' and 'Timeout' as timeout.
		void Init(
			socket__ Socket,
			bso::sBool TakeOwnership) // En secondes.
		{
			reset();

			Driver_.Init(Socket, TakeOwnership, fdr::ts_Default);
			ioflow__::Init(Driver_, Cache_, sizeof( Cache_ ));
		}
		void SetBreakFlag(
			sTimeout Timeout,	// In ms
			const bso::sBool *Flag)
		{
			Driver_.SetBreakFlag(Timeout, Flag);
		}
		void EraseBreakFlag(void)
		{
			Driver_.EraseBreakFlag();
		}
		socket__ Socket( void ) const
		{
			return Driver_.Socket();
		}
		time_t EpochTimeStamp( void ) const
		{
			return Driver_.EpochTimeStamp();
		}
		bso::sBool IsALive(void) const
		{
			return Driver_.IsAlive();
		}
	};
}

/**************/
/**** NEW *****/
/**************/

namespace sck {
	typedef socket_ioflow_driver___ rRWDriver;
	typedef socket_ioflow___ rRWFlow;
}
#endif
