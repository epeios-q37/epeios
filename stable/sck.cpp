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

#define SCK_COMPILATION_

#include "sck.h"

#ifdef CPE_S_POSIX
#	define SCK__IGNORE_SIGPIPE
#endif


#ifdef SCK__IGNORE_SIGPIPE
#	include <signal.h>
#endif

using namespace sck;

#ifdef CPE_S_WIN
bool sck::Ready_ = false;
// 'ssize_t' does not exist in Windows.
// It is used as return type for 'select' and 'recv'
// under POSIX, so we use the type returned by same
// functions under windows.
typedef int ssize_t;
#else
bool sck::Ready_ = true;
#endif

/*
	Under Windows, the 'FD_SETSIZE' is the max amount of socket a 'select'
	can simultaneously monitor.
	Under POSIX, the 'FD_SETSIZE' is the max value (usually 1024) of a file descriptor
	a select can monitor, hence the use of 'poll'.
*/

namespace {
#ifdef CPE_S_WIN
	flw::size__ WindowsRead_(
		socket__ Socket,
		flw::size__ Amount,
		void *Buffer,
		duration__ Timeout,
		const bso::sBool *BreakFlag)
	{
		fd_set fds;
		ssize_t Result;

		FD_ZERO(&fds);
		FD_SET(Socket, &fds);

		if ( Timeout == SCK_INFINITE )
			Result = select((int)( Socket + 1 ), &fds, NULL, NULL, NULL);
		else {
			timeval TV;

			TV.tv_sec = Timeout / 1000;
			TV.tv_usec = (Timeout % 1000 ) * 1000;

			do
				Result = select((int)( Socket + 1 ), &fds, NULL, NULL, &TV);	// Unlike what happens under Linux,, 'select' does not modify 'TV'.
			while ( !Result && !*BreakFlag );
		}

		if ( Result == 1 ) {
			Result = recv(Socket, (cast__)Buffer, (int)Amount, 0);

			if ( Result == SCK_SOCKET_ERROR ) {
				Result = SCK_DISCONNECTED;

				if ( Error() != SCK_ECONNRESET )
					qRLbr();
			} else if ( !Result && Amount )
				Result = SCK_DISCONNECTED;
		} else if ( Result == SCK_SOCKET_ERROR )
			qRLbr();
		else if ( ( Result == 0 ) && ( Timeout == SCK_INFINITE ) )
			qRSys();

		return Result;
	}

	flw::size__ WindowsWrite_(
		socket__ Socket,
		const void *Buffer,
		flw::size__ Amount,
		duration__ Timeout,
		const bso::sBool *BreakFlag)
	{
		fd_set fds;
		int Result;

		FD_ZERO(&fds);
		FD_SET(Socket, &fds);

		if ( Timeout == SCK_INFINITE )
			Result = select((int)( Socket + 1 ), NULL, &fds, NULL, NULL);
		else {
			timeval TV;

			TV.tv_sec = Timeout / 1000;
			TV.tv_usec = ( Timeout % 1000 ) * 1000;

			do {
				Result = select((int)( Socket + 1 ), NULL, &fds, NULL, &TV);	// Unlike what happens under Linux,, 'select' does not modify 'TV'.
			} while ( !Result && !*BreakFlag );
		}

		if ( Result == 1 ) {
			Result = send(Socket, (const cast__)Buffer, (int)Amount, 0);

			if ( Result == SCK_SOCKET_ERROR ) {
				Result = SCK_DISCONNECTED;

				if ( Error() != SCK_ECONNRESET )
					qRLbr();
			} else if ( !Result && Amount )	// I assume that, because the send is call immediatly after the select, this can not be happen.
				qRFwk();
		} else if ( Result == SCK_SOCKET_ERROR )
			qRLbr();
		else if ( ( Result == 0 ) && ( Timeout == SCK_INFINITE ) )
			qRSys();

		return Result;
	}
#else
	bso::sSign poll_(
		socket__ Socket,
		int Flags,
		duration__ Timeout,
		const bso::sBool *BreakFlag)
	{
		bso::sSign Return = 0;

		int Result = 0;
		pollfd fds;

		fds.fd = Socket;
		fds.events = Flags;
		fds.revents = 0;

		if ( Timeout == NoTimeout ) {
			if ( BreakFlag != NULL )
				qRFwk();

			Result = poll(&fds, 1, -1);
		} else {
			if ( BreakFlag == NULL )
				qRFwk();

			do
				Result = poll(&fds, 1, Timeout);
			while ( !Result && !*BreakFlag );
		}

		if ( Result == 1 ) {
			if ( fds.revents & POLLERR )
				qRLbr();
			else if ( fds.revents & POLLHUP )
				Return = -1;
			else if ( fds.revents & ~Flags )
				qRLbr();
			else
				Return = 1;
		} else if ( Result < 0 )
			qRLbr();
		else if ( Result > 1 )
			qRLbr();
		else if ( Timeout == NoTimeout )
			qRLbr();
		else
			Return = 0;

		return Return;
	}

	flw::size__ PosixRead_(
		socket__ Socket,
		flw::size__ Amount,
		void *Buffer,
		duration__ Timeout,
		const bso::sBool *BreakFlag)
	{
		ssize_t Result = 0;

		switch ( poll_(Socket, POLLIN | POLLPRI, Timeout, BreakFlag) ) {
		case -1:
			Result = SCK_DISCONNECTED;
			break;
		case 0:
			Result = 0;
			break;
		case 1:
			Result = recv(Socket, (cast__)Buffer, (int)Amount, 0);

			if ( Result == 0 )
				qRLbr();
			break;
		default:
			qRUnx();
			break;
		}

		return Result;
	}

	flw::size__ PosixWrite_(
		socket__ Socket,
		const void *Buffer,
		flw::size__ Amount,
		duration__ Timeout,
		const bso::sBool *BreakFlag)
	{
		ssize_t Result = 0;

		switch ( poll_(Socket, POLLOUT, Timeout, BreakFlag) ) {
		case -1:
			Result = SCK_DISCONNECTED;
			break;
		case 0:
			Result = 0;
			break;
		case 1:
			Result = send(Socket, (const cast__)Buffer, (int)Amount, 0);

			if ( Result == 0 )
				qRLbr();
			break;
		default:
			qRUnx();
			break;
		}

		return Result;
	}
#endif
}

flw::size__ sck::Read(
	socket__ Socket,
	flw::size__ Amount,
	void *Buffer,
	duration__ Timeout,
	const bso::sBool *BreakFlag)
{
#ifdef CPE_S_WIN
	return WindowsRead_(Socket, Amount, Buffer, Timeout, BreakFlag);
#else
	return PosixRead_(Socket, Amount, Buffer, Timeout, BreakFlag);
#endif
}

flw::size__ sck::Write(
	socket__ Socket,
	const void *Buffer,
	flw::size__ Amount,
	duration__ Timeout,
	const bso::sBool *BreakFlag)
{
#ifdef CPE_S_WIN
	return WindowsWrite_(Socket, Buffer, Amount, Timeout, BreakFlag);
#else
	return PosixWrite_(Socket, Buffer, Amount, Timeout, BreakFlag);
#endif
}

#ifdef SCK__WIN
#	define SHUT_RDWR 2	// Workaround, 'SD_BOTH' being not available because inclusion of 'winsock2.h' fails.
#elif defined( SCK__POSIX )
# define ioctlsocket ioctl
# define closesocket	close
#else
#	error
#endif

bso::sBool sck::Shutdown(
	socket__ Socket,
	qRPN )
{
	if ( shutdown( Socket, SHUT_RDWR ) != 0 ) {
		if ( qRPT )
			qRLbr();

		return false;
	} else
		return true;
}


// Some errors are ignored.
bso::sBool sck::Close(
	socket__ Socket,
	qRPN )	// To set to 'qRPU' when called from destructors !
{
	u_long Mode = 1;	// Non-blocking.
	bso::sBool Error = ioctlsocket( Socket, FIONBIO, &Mode ) != 0;

	Error |= !Shutdown(Socket, qRPU);

	if ( (closesocket( Socket ) != 0) || Error ) {
		if ( qRPT )
			qRLbr();

		return false;
	}

	return true;
}


Q37_GCTOR( sck )
{
#ifdef SCK__IGNORE_SIGPIPE
	signal( SIGPIPE, SIG_IGN );
#endif
}
