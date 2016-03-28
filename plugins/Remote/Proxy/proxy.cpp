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

// 'proxy' remote plugin.

#include "registry.h"

#include "rpproxy.h"

#include "sclmisc.h"
#include "sclplugin.h"
#include "sclmisc.h"

#include "csdrcd.h"
#include "csdmxc.h"

#include "prxy.h"

#define PLUGIN_NAME	"proxy"

typedef csdmxc::cCallback cCallback_;

class rCallback
: public cCallback_
{
private:
	qCBUFFERr HostService_, Identifier_;
	prxy::rFlow *FlowAsPointer_( void *UP ) const
	{
		if ( UP == NULL )
			qRFwk();

		return (prxy::rFlow *)UP;
	}
	prxy::rFlow &F_( void *UP ) const
	{
		return *FlowAsPointer_( UP );
	}
protected:
	virtual void *CSDMXCNew( void ) override
	{
		prxy::rFlow *Flow = NULL;
	qRH
		lcl::meaning Meaning;
	qRB
		Flow = new prxy::rFlow;

		if ( Flow == NULL )
			qRAlc();

		Meaning.Init();

		if ( !Flow->Init( HostService_, Identifier_, prxybase::tClient, Meaning ) )
			sclmisc::ReportAndAbort( Meaning );
	qRR
	qRT
	qRE
		return Flow;
	}
	virtual csdmxc::fFlow &CSDMXCExtractFlow( void *UP ) override
	{
		return F_( UP );
	}
	virtual void CSDMXCRelease( void *UP ) override
	{
		delete FlowAsPointer_( UP );
	}
	virtual time_t CSDMXCEpochTimeStamp( void *UP ) override
	{
		return F_( UP ).EpochTimeStamp();
	}
public:
	void reset( bso::sBool = true )
	{
	}
	qCVDTOR( rCallback );
	void Init(
		const str::string_ &HostService,
		const str::string_ &Identifier )
	{
		HostService.Convert( HostService_ );
		Identifier.Convert( Identifier_ );
	}
};

typedef csdrcd::driver___ _plugin___;

class plugin___
: public _plugin___
{
private:
	rCallback Callback_;
	csdmxc::rCore Core_;
	csdmxc::rClientIOFlow Flow_;
protected:
	virtual fdr::size__ FDRWrite(
		const fdr::byte__ *Buffer,
		fdr::size__ Amount ) override
	{
		return Flow_.WriteUpTo( Buffer, Amount );
	}
	virtual void FDRCommit( void ) override
	{
		return Flow_.Commit();
	}
	virtual fdr::size__ FDRRead(
		fdr::size__ Maximum,
		fdr::byte__ *Buffer ) override
	{
		return Flow_.ReadUpTo( Maximum, Buffer );
	}
	virtual void FDRDismiss( void ) override
	{
		return Flow_.Dismiss();
	}
public:
	void reset( bso::bool__ P = true )
	{
		_plugin___::reset( P );
		Flow_.reset( P );
		Core_.reset( P );
		Callback_.reset( P );
	}
	E_CVDTOR( plugin___ );
	bso::bool__ Init(
		const char *HostService,
		const char *Identifier )
	{
		_plugin___::Init();

		Callback_.Init( str::string( HostService ), str::string( Identifier ) );

		if ( !Core_.Init( Callback_ ) )
			return false;

		Flow_.Init( Core_ );

		return true;
	}
	bso::sBool SCLPLUGINInitialize( void *UP )
	{
		bso::sBool Success = false;
	qRH
		str::wString HostService, Identifier;
		qCBUFFERr HostServiceBuffer, IdentifierBuffer;
		rpproxy::rData *Data = (rpproxy::rData *)UP;
	qRB
		HostService.Init();
		sclmisc::MGetValue( registry::HostService, HostService );

		Identifier.Init();
		sclmisc::MGetValue( registry::Identifier, Identifier );

		if ( !Init( HostService.Convert( HostServiceBuffer ), Identifier.Convert( IdentifierBuffer ) ) )
			if ( Data == NULL  )
				sclmisc::ReportAndAbort( "UnableToConnectTo", HostService );
			else {
				if ( Data != plgn::NonNullUP ) {
					Data->HostService = HostService;
				}

				qRReturn;
			}
		
		Success = true;
	qRR
	qRT
	qRE
		return Success;
	}
};

SCLPLUGIN_DEF( plugin___ );

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

