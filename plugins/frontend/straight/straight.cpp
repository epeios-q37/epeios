/*
	Copyright (C) 2016 Claude SIMON (http://q37.info/contact/).

	This file is part of 'remote' software.

    'remote' is free software: you can redistribute it and/or modify it
    under the terms of the GNU Affero General Public License as published
    by the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    'remote' is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with 'remote'.  If not, see <http://www.gnu.org/licenses/>.
*/

// 'straight' remote plugin.

#include "registry.h"

#include "rpstraight.h"

#include "sclmisc.h"
#include "sclplugin.h"
#include "sclmisc.h"

#include "fblovl.h"

#include "csdrcd.h"

#include "csdmnc.h"

#define PLUGIN_NAME	"straight"

typedef fblovl::cDriver cPlugin_;

namespace {
	csdmxc::rLogCallback LogCallback_;
}

class rPlugin
: public cPlugin_
{
private:
	csdmnc::rCore Core_;
	bso::sBool Connected_;
	void HandleLostConnection_( void )
	{
		Connected_ = false;
		ERRRst();
	}
protected:
	virtual fdr::ioflow_driver_base___ *CSDRCCNew( void ) override
	{
		csdmxc::_driver___ *Driver = new csdmxc::_driver___;

		if ( Driver == NULL )
			qRAlc();

		Driver->Init( Core_, fdr::ts_Default );

		return Driver;
	}
	virtual void CSDRCCDelete( fdr::ioflow_driver_base___ *Driver ) override
	{
		delete Driver;
	}
	virtual fblovl::eMode FBLOVLMode( void ) override
	{
		return fblovl::mSerialized;
	}
public:
	void reset( bso::bool__ P = true )
	{
		Core_.reset( P );
		Connected_ = false;
	}
	qCVDTOR( rPlugin );
	bso::bool__ Init(
		const char *HostService,
		bso::uint__ PingDelay,
		sck::duration__ Timeout )
	{
//		LogCallback_.Init( "h:/temp/MXCLog.txt" );

		if ( !Core_.Init( HostService, PingDelay, Timeout ) )
			return false;

		Connected_ = true;

		return true;
	}
	bso::sBool SCLPLUGINInitialize( plgncore::sAbstract *BaseAbstract )
	{
		bso::sBool Success = false;
	qRH
		str::string HostService;
		bso::uint__ PingDelay = 0;
		sck::duration__ Timeout = sck::NoTimeout;
		TOL_CBUFFER___ Buffer;
		rpstraight::rAbstract *Abstract = (rpstraight::rAbstract *)BaseAbstract;
	qRB
		plgn::Test( BaseAbstract, rpstraight::Identifier );

		HostService.Init();

		sclmisc::MGetValue( registry::parameter::HostService, HostService );
		PingDelay = sclmisc::OGetUInt( registry::parameter::PingDelay, 0 );
		Timeout = sclmisc::OGetU16( registry::parameter::Timeout, sck::NoTimeout );

		if ( !Init( HostService.Convert(Buffer), PingDelay, Timeout ) )
			switch ( plgn::ErrorReporting( Abstract ) ) {
			case plgn::rhInternally:
				sclmisc::ReportAndAbort( "UnableToConnectTo", HostService );
				break;
			case plgn::rhDetailed:
				Abstract->HostService = HostService;
			case plgn::rhBasic:
				qRReturn;
				break;
			default:
				qRGnr();
				break;
			}
		
		Success = true;
	qRR
	qRT
	qRE
		return Success;
	}
};

SCLPLUGIN_DEF( rPlugin );

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

qGCTOR(straight)
{
	if ( strcmp( rpstraight::Identifier, IDENTIFIER ) )
		qRChk();
}
