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

#ifndef SCLDAEMON__INC
# define SCLDAEMON__INC

# define SCLDAEMON_NAME		"SCLDAEMON"

# if defined( E_DEBUG ) && !defined( SCLDAEMON_NODBG )
#  define SCLDAEMON_DBG
# endif

// SoCLe DAEMON

# include "err.h"
# include "flw.h"

# include "csdscb.h"

# include "sclrgstry.h"

# ifndef SCLDAEMON_DISABLE_ERROR_DETECTION
#  ifdef E_DEBUG
#   define SCLDAEMON__ERROR_DETECTION_ENABLED
#  endif
# endif

namespace scldaemon {
	class daemon___
	{
	protected:
		virtual bso::bool__ SCLDAEMONProcess( flw::ioflow__ &Flow ) = 0;
	public:
		void reset( bso::bool__ P = true )
		{
			// Standardization.
		}
		E_CVDTOR( daemon___ );
		void Init( void )
		{
			// Standardization.
		}
		bso::bool__ Process( flw::ioflow__ &Flow )
		{
			return SCLDAEMONProcess( Flow );
		}
	};

	typedef csdscb::cProcessing cProcessing_; 

	class rCallback
	: public cProcessing_
	{
	protected:
		virtual bso::sBool CSDSCBPluginOverride(
			str::dString &Id,
			str::dString &Arguments,
			csdscb::sTimeout &Timeout ) override
		{
			return SCLDAEMONPluginOverride( Id, Arguments, Timeout );
		}
		virtual void *CSDSCBPreProcess(
			flw::sIOFlow *Flow,
			const ntvstr::char__ *Origin,
			bso::sBool *OwnerShipTaken ) override
		{
			return SCLDAEMONNew( Origin );
		}
		virtual csdscb::action__ CSDSCBProcess(
			flw::ioflow__ *Flow,
			void *UP ) override
		{
			daemon___ &Daemon = *(daemon___ *)UP;

			if ( Daemon.Process( *Flow ) )
				return csdscb::aContinue;
			else
				return csdscb::aStop;
		}
		virtual void CSDSCBPostProcess( void *UP ) override
		{
		qRH
		qRB
			delete (daemon___ *)UP;
		qRR
# ifndef CPE_S_POSIX
#  ifdef SCLDAEMON__ERROR_DETECTION_ENABLED
			strcpy( NULL, "There should no be errors, but, if one occurs, this line should facilitate the debugging." );
#  endif
# endif
			ERRRst();
		qRT
		qRE
		}
	protected:
		virtual bso::sBool SCLDAEMONPluginOverride(
			str::dString &Id,
			str::dString &Arguments,
			csdscb::sTimeout &Timeout )
		{
			return false;
		}
		virtual daemon___ *SCLDAEMONNew( const ntvstr::char__ *Origin ) = 0;
	public:
		void reset( bso::bool__ P = true )
		{
		}
		E_CVDTOR( rCallback );
		void Init( void )
		{
		}
	};

	/* Called once, when the library is loaded. All the 'registry' stuff is already initialized.
	The same returned callback is used to handle each connection (one callback for all connections,
	and NOT a callbackper connection). */
	rCallback *SCLDAEMONGetCallback(
		csdleo::context__ Context,
		csdleo::mode__ Mode );	// To overload !
}

#endif
