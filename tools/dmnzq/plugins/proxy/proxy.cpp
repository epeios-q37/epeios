/*
	Copyright (C) 2016 Claude SIMON (http://q37.info/contact/).

	This file is part of 'dmnzq'.

    'dmnzq' is free software: you can redistribute it and/or
	modify it under the terms of the GNU Affero General Public License as
	published by the Free Software Foundation, either version 3 of the
	License, or (at your option) any later version.

    'dmnzq' is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
	Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with 'dmnzq'.  If not, see <http://www.gnu.org/licenses/>
*/

// 'proxy' slot plugin.

#include "misc.h"

#include "registry.h"

#include "prxy.h"

#include "sclplugin.h"
#include "sclmisc.h"

#include "mtk.h"

#define PLUGIN_NAME	"proxy"

namespace {

	using misc::cHandler;
	using misc::sModule;
	using misc::sTimeout;

	struct data__ {
		prxy::rIODriver *IODriver;
		sModule *Module;
		mtx::handler___ Mutex;
		const char *Origin;
		void reset( bso::bool__ P = true )
		{
			if ( P )
				if ( Mutex != mtx::UndefinedHandler )
					mtx::Delete( Mutex );

			IODriver = NULL;
			Module = NULL;
			Origin = NULL;

			Mutex = mtx::UndefinedHandler;
		}
		void Init(
			prxy::rIODriver *IODriver,
			sModule &Module,
			const char *Origin )
		{
			reset();

			Mutex = mtx::Create();

			this->IODriver = IODriver;
			this->Module = &Module;
			this->Origin = Origin;
		}
		E_CDTOR( data__ );
	};

	void Process_( void *UP )
	{
	qRFH
		data__ &Data = *(data__ *)UP;
		prxy::rIODriver *IODriver = Data.IODriver;
		sModule &Module = *Data.Module;
		ntvstr::string___ Origin;
		void *MUP = NULL;
		bso::sBool OwnerShipTaken = false;
	qRFB
		Origin.Init( Data.Origin );

		mtx::Unlock( Data.Mutex );

		MUP = Module.PreProcess( IODriver, Origin );

		while ( Module.Process( IODriver, MUP ) == csdscb::aContinue );
	qRFR
	qRFT
		if( !Module.PostProcess( MUP ) )
			qRGnr();
	
		delete IODriver;
	qRFE( sclmisc::ErrFinal() )
	}

	class sPlugin
	: public cHandler
	{
	private:
		TOL_CBUFFER___ HostService_, Identifier_;
	protected:
		virtual void MISCHandle(
			sModule &Module,
			sTimeout Timeout) override
		{
		qRH
			prxy::rIODriver *IODriver = NULL;
			data__ Data;
			lcl::meaning Meaning;
		qRB
			IODriver = new prxy::rIODriver;

			if ( IODriver == NULL )
				qRAlc();

			Meaning.Init();

			while ( IODriver->Init( HostService_, Identifier_, prxybase::tServer, Timeout == misc::NoTimeout ? sck::NoTimeout : Timeout * 1000, Meaning ) ) {
				Data.Init( IODriver, Module, HostService_ );

				mtx::Lock( Data.Mutex );

				mtk::RawLaunch( Process_, &Data );

				mtx::Lock( Data.Mutex );
				mtx::Unlock( Data.Mutex );

				IODriver = NULL;

				IODriver = new prxy::rIODriver;

				if ( IODriver == NULL )
					qRAlc();
			}

			sclmisc::ReportAndAbort( Meaning );
		qRR
		qRT
			if ( IODriver != NULL )
				delete IODriver;
		qRE
		}
	public:
		void reset( bso::bool__ P = true )
		{
		}
		E_CVDTOR( sPlugin );
		void Init( void )
		{
		}
		bso::sBool SCLPLUGINInitialize( plgn::sAbstract *Abstract )
		{
		qRH
			str::string HostService, Identifier;
		qRB
			if ( Abstract != NULL )
				qRGnr();

			HostService.Init();
			sclmisc::MGetValue( registry::HostService, HostService );

			Identifier.Init();
			sclmisc::MGetValue( registry::Identifier, Identifier );

			HostService.Convert( HostService_ );
			Identifier.Convert( Identifier_ );
		qRR
		qRT
		qRE
			return true;
		}
	};
}

SCLPLUGIN_DEF( sPlugin );

const char *sclmisc::SCLMISCTargetName = PLUGIN_NAME;

void sclplugin::SCLPLUGINPluginIdentifier( str::dString &Identifier )
{
	Identifier.Append( IDENTIFIER );
}

void sclplugin::SCLPLUGINPluginDetails( str::dString &Details )
{
	Details.Append( PLUGIN_NAME " V" VERSION " - Build " __DATE__ " " __TIME__ " (" );
	Details.Append( cpe::GetDescription() );
	Details.Append( ')' );
}

