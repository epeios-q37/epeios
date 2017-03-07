/*
	Copyright (C) 1999-2017 Claude SIMON (http://q37.info/contact/).

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

#define SCLN__COMPILATION

#include "scln.h"

#include "nodeq.h"
#include "uvq.h"

#include "sclmisc.h"

#include "bch.h"
#include "cio.h"
#include "cpe.h"

#include <node_version.h>

using namespace scln;

// Not activated yet !
namespace error_ {
	typedef uvq::cASync cASync_;

	class sCallback_
	: public cASync_
	{
	protected:
		virtual void UVQWork( void ) override;
		virtual uvq::eBehavior UVQAfter( void ) override;
	};

	namespace {
		tht::rLocker Lock_;
		tht::rBlocker Blocker_;
		str::wString Message_;
		sCallback_ Callback_;

		bso::sBool GetMessage_( str::dString &Message )
		{
			bso::sBool Exists = false;
		qRH
			tht::rLockerHandler Locker;
		qRB
			Locker.Init( Lock_ );

			Exists =  Message_.Amount() != 0;

			if ( Exists ) {
				Message.Append( Message_ );
				Message_.Init();
			}
		qRR
		qRT
		qRE
			return Exists;
		}
	}

	void sCallback_::UVQWork( void )
	{
		if ( uvq::AmountPending() > 1 )
			Blocker_.Wait();
	}

	uvq::eBehavior sCallback_::UVQAfter( void )
	{
		uvq::eBehavior Behavior = uvq::bExitOnly;
	qRH
		str::wString Message;
	qRB
		Message.Init();

		if ( GetMessage_(Message) ) {
			Behavior = uvq::bRelaunch;
			v8q::GetIsolate()->ThrowException( v8::Exception::Error( v8q::ToString( Message ) ) );
		}
	qRR
	qRT
	qRE
		return Behavior;
	}

	void Initialize( void )
	{
		Blocker_.Init( true );
		Lock_.Init();
		Message_.Init();
	}

	void SetMessage( const str::dString &Message )
	{
	qRH
		tht::rLockerHandler Locker;
	qRB
		if ( Message.Amount() == 0 )
			qRFwk();

		Locker.Init( Lock_ );

		if ( Message_.Amount() == 0 ) {
			Message_.Append( Message );
			Blocker_.Unblock();
		}
	qRR
	qRT
	qRE
	}

	void Launch( void )
	{
		uvq::Launch( Callback_ );
	}
}

void scln::ErrFinal( v8::Isolate *Isolate )
{
qRH
	str::wString Message;
	err::buffer__ Buffer;
qRB
	Isolate = v8q::GetIsolate( Isolate );

	Message.Init();

	if ( ERRType != err::t_Abort ) {
		ERRRst();	// To avoid relaunching of current error by objects of the 'FLW' library.

		Message.Append( err::Message( Buffer ) );
	} else if ( sclerror::IsErrorPending() )
		sclmisc::GetSCLBasePendingErrorTranslation( Message );

	if ( Isolate != NULL )
		Isolate->ThrowException( v8::Exception::Error( v8q::ToString( Message ) ) ); 
	else
		error_::SetMessage( Message );
qRR
	ERRRst();
qRT
qRE
}


namespace {
	bch::qBUNCHwl( sFunction_ ) Functions_;
}

void scln::sRegistrar::Register( sFunction_ Function )
{
	Functions_.Append( Function );
}

void scln::sRegistrar::Register(
	const char *Name,
	v8::FunctionCallback Function )
{
	NODE_SET_METHOD( E_(), Name, Function );
}


namespace {
	void Launch_( const v8::FunctionCallbackInfo<v8::Value>& Info )
	{
	qRFH
		v8q::sArguments Arguments;
	qRFB
		if ( Info.Length() < 1 )
			qRGnr();

		if ( !Info[0]->IsUint32() )
			qRGnr();

		v8::Local<v8::Uint32> Index = v8::Local<v8::Uint32>::Cast(Info[0] );

		if ( !Functions_.Exists( Index->Uint32Value() ) )
			qRGnr();

		Arguments.Init( Info );

		Functions_( Index->Uint32Value())( Arguments );

		if ( sclerror::IsErrorPending() )
			qRAbort();	// To force the handling of a pending error.
	qRFR
	qRFT
	qRFE( ErrFinal( Info.GetIsolate() ) )
	}
}

namespace {
	namespace {
		void GetExtendedInfo_( str::dString &Info )
		{
		qRH
			flx::rStringOFlow BaseFlow;
			txf::sOFlow Flow;
		qRB
			BaseFlow.Init( Info );
			Flow.Init( BaseFlow );

			Flow << sclmisc::SCLMISCProductName << " v" << SCLNProductVersion << " - Node v" NODE_VERSION_STRING " ABI v" NODE_STRINGIFY( NODE_MODULE_VERSION )  << txf::nl
			     << txf::pad << "Build : " __DATE__ " " __TIME__ " (" <<  cpe::GetDescription() << ')';
		qRR
		qRT
		qRE
		}
		void GetInfo_( str::dString &Info )
		{
		qRH
			flx::rStringOFlow BaseFlow;
			txf::sOFlow Flow;
		qRB
			BaseFlow.Init( Info );
			Flow.Init( BaseFlow );

			Flow << sclmisc::SCLMISCProductName << " v" << SCLNProductVersion << " - Build : " __DATE__ " " __TIME__;
		qRR
		qRT
		qRE
		}
	}

	void GetExtendedInfo_(const v8::FunctionCallbackInfo<v8::Value>& Args)
	{
	qRH
		str::wString Info;
	qRB
		Info.Init();

		GetExtendedInfo_( Info );

		Args.GetReturnValue().Set( v8q::sString( Info ).Core() );
	qRR
	qRT
	qRE
	}

	void GetInfo_(const v8::FunctionCallbackInfo<v8::Value>& Args)
	{
	qRH
		str::wString Info;
	qRB
		Info.Init();

		GetInfo_( Info );

		Args.GetReturnValue().Set( v8q::sString( Info ).Core() );
	qRR
	qRT
	qRE
	}
}

namespace {
	err::err___ Error_;
	sclerror::rError SCLError_;
	scllocale::rRack Locale_;
	sclmisc::sRack Rack_;
}

namespace {
	namespace {
		void GetParentModuleFilename_(
			v8::Local<v8::Value> Module,
			str::dString &Filename )
		{
		qRH
			char *Buffer = NULL;
			v8q::sString String;
		qRB
			String.Init( v8q::sObject( v8q::sObject(Module).Get( "parent" ) ).Get( "filename" ) );
			Buffer = (char *)malloc(String.Size() + 1 );

			if ( Buffer == NULL )
				qRAlc();

			String.Get( Buffer );

			Filename.Append( Buffer, String.Size() );
		qRR
		qRT
			if ( Buffer != NULL  )
				free( Buffer );
		qRE
		}
	}

	void GetParentModuleLocation_(
		v8::Local<v8::Value> Module,
		str::dString &Location )
	{
	qRH
		str::wString Filename;
		fnm::rName Path;
	qRB
		Filename.Init();

		GetParentModuleFilename_( Module, Filename );

		Path.Init();
		fnm::GetLocation( Filename, Path );

		Path.UTF8( Location );
	qRR
	qRT
	qRE
	}
}

void scln::Register_(
	v8::Local<v8::Object> Exports,
	v8::Local<v8::Value> Module,
	void* priv )
{
qRFH
	str::wString Location;
qRFB
	sRegistrar Registrar;

	NODE_SET_METHOD( Exports, "extendedInfo", GetExtendedInfo_ );
	NODE_SET_METHOD( Exports, "info", GetInfo_ );
	NODE_SET_METHOD( Exports, "_wrapper", Launch_ );

	cio::Initialize( cio::GetConsoleSet() );
	Rack_.Init( Error_, SCLError_, cio::GetSet( cio::t_Default ), Locale_ );

	Location.Init();
	GetParentModuleLocation_( Module, Location );

	sclmisc::Initialize( Rack_, Location, qRPU );

	Registrar.Init( Exports );

	Functions_.Init();
	scln::SCLNRegister( Registrar );
	/*
	error_::Initialize();

	error_::Launch();
	*/
qRFR
qRFT
qRFE( ErrFinal() )
}

qGCTOR( scln )
{
	Error_.Init();
	SCLError_.Init();
	Locale_.Init();

//  Segmentaiton fault when launched here, so launched in 'Register_()'.
//	error_::Initialize();

// Sudenly stops to work ('Segmentation fault', so was deplaced in the 'Register_' function.
//	Functions_.Init();
}