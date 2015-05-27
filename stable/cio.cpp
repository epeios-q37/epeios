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



//	$Id: cio.cpp,v 1.48 2013/04/06 14:50:43 csimon Exp $

#define CIO__COMPILATION

#include "cio.h"

#include "flx.h"

using namespace cio;

static target__ Target_ = t_Undefined;

static flx::void_iflow_driver___ _VInDriver;
static flx::void_oflow_driver___ _VOutDriver;
static flx::void_oflow_driver___ _VErrDriver;

static iof::io_iflow_driver___ _SInDriver;
static iof::io_oflow_driver___ _SOutDriver;
static iof::io_oflow_driver___ _SErrDriver;

static set__
	_Current,
	_Console( _SInDriver, _SOutDriver, _SErrDriver ),
	_Void( _VInDriver, _VOutDriver, _VErrDriver );

cif__ cio::CInF;
cof___ cio::COutF, cio::CErrF;

txf::text_iflow__ cio::CIn;
txf::text_oflow__ cio::COut, cio::CErr;

#if defined( CPE_WIN )
#	include <io.h>
#	include <fcntl.h>
#endif

#ifdef IOP__USE_LOWLEVEL_IO
iop::descriptor__ cio::CInDescriptor = 0, cio::COutDescriptor = 1, cio::CErrDescriptor = 2;
#elif defined( IOP__USE_STANDARD_IO )
iop::descriptor__ cio::cind = stdin, cio::coutd = stdout, cio::cerrd = stderr;
#else
#	error "Unkonw I/O enviroment !"
#endif

const set__ &cio::GetConsoleSet( void )
{
	return _Console;
}

const set__ &cio::GetVoidSet( void )
{
	return _Void;
}

const set__ &cio::GetCurrentSet( void )
{
	return _Current;
}

static void InitializeConsole_( void )
{
#if defined( CPE_WIN )
	if ( _setmode( _fileno( stdin ), _O_BINARY ) == -1 )
		ERRLbr();

	if ( _setmode( _fileno( stdout ), _O_BINARY ) == -1 )
		ERRLbr();

	if ( _setmode( _fileno( stderr ), _O_BINARY ) == -1 )
		ERRLbr();
#endif
	_SInDriver.Init( CInDescriptor, fdr::ts_Default );
	_SOutDriver.Init( COutDescriptor, fdr::ts_Default );
	_SErrDriver.Init( CErrDescriptor, fdr::ts_Default );
}

const set__ &cio::GetSet( target__ Target )
{
	switch ( Target ) {
	case tConsole:
		return GetConsoleSet();
		break;
	case tVoid:
		return GetVoidSet();
		break;
	case tCurrent:
		return GetCurrentSet();
		break;
	default:
		ERRFwk();
		break;
	}

	return GetVoidSet();	// To avoid a warning.
}

target__ cio::GetTarget( const set__ &Set )
{
	if ( &Set == &GetConsoleSet() )
		return tConsole;
	else if ( &Set == &GetVoidSet() )
		return tVoid;
	else
		return tUser;
}

void cio::Initialize( target__ Target )
{
	switch ( Target ) {
	case tConsole:
		CInF.Init( _SInDriver );
		COutF.Init( _SOutDriver );
		CErrF.Init( _SErrDriver );
		break;
	case tVoid:
		CInF.Init( _VInDriver );
		COutF.Init( _VOutDriver );
		CErrF.Init( _VErrDriver );
		break;
	case tUser:
		if ( !CInF.IsInitialized() )
			ERRFwk();

		if ( !COutF.IsInitialized() )
			ERRFwk();

		if ( !CErrF.IsInitialized() )
			ERRFwk();

		break;
	default:
		ERRPrm();
		break;
	}

	_Current.Init( CInF.Driver(), COutF.Driver(), CErrF.Driver() );

	cio::CIn.Init( CInF );
	cio::COut.Init( COutF );
	cio::CErr.Init( CErrF );

	::Target_ = Target;
}

void cio::Initialize( const set__ &Set )
{
	CInF.Init( Set.In() );
	COutF.Init( Set.Out() );
	CErrF.Init( Set.Err() );

	Initialize( tUser );
}

target__ cio::Target( void )
{
	return ::Target_;
}

#ifndef Q37_LIBRARY
Q37_GCTOR( cio )
{
	InitializeConsole_();
}
#endif
