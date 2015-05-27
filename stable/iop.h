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

//	$Id: iop.h,v 1.12 2013/04/06 15:33:18 csimon Exp $

#ifndef IOP__INC
#define IOP__INC

#define IOP_NAME		"IOP"

#define	IOP_VERSION	"$Revision: 1.12 $"

#define IOP_OWNER		"Claude SIMON (http://zeusw.org/intl/contact.html)"

#if defined( E_DEBUG ) && !defined( IOP_NODBG )
#define IOP_DBG
#endif

/* Begin of automatic documentation generation part. */

//V $Revision: 1.12 $
//C Claude SIMON (http://zeusw.org/intl/contact.html)
//R $Date: 2013/04/06 15:33:18 $

/* End of automatic documentation generation part. */

/******************************************************************************/
				  /* do not modify anything above this limit */
				  /*			  unless specified			 */
				  /*******************************************/

/* Addendum to the automatic documentation generation part. */
//D Input/Output Picker 
/* End addendum to automatic documentation generation part. */

/*$BEGIN$*/

#include "err.h"
#include "flw.h"
#include "cpe.h"

#ifdef IOP_BUFFER_SIZE
#	define IOP__BUFFER_SIZE	IOP_BUFFER_SIZE
#else
#	define IOP__BUFFER_SIZE	1024
#endif

#ifdef E_USE_STANDARD_IO
#	define IOP__USE_STANDARD_IO
#elif defined( CPE_WIN )
#	define IOP__USE_LOWLEVEL_IO
#elif defined( CPE_LINUX )
#	define IOP__USE_LOWLEVEL_IO
#elif defined( CPE_XCODE )
#	define IOP__USE_LOWLEVEL_IO
#elif defined( CPE_CYGWIN )
#	define IOP__USE_LOWLEVEL_IO
#elif defined( CPE_MINGW )
#	define IOP__USE_LOWLEVEL_IO
#else
#	error "Undefined platform ! Define one or use 'E_USE_STANDARD_IO'"
#endif

#ifdef IOP__USE_STANDARD_IO
#	include "cslio.h"
#elif defined( IOP__USE_LOWLEVEL_IO )
#	include "llio.h"
#else
#	error "Undefined I/O enviroment !"
#endif

namespace iop {
#ifdef IOP__USE_LOWLEVEL_IO
	typedef llio::lowlevel_input__		input__;
	typedef llio::lowlevel_output__		output__;
	typedef llio::lowlevel_io__			io__;
	using llio::descriptor__;
	using llio::size__;
#	define IOP_UNDEFINED_DESCRIPTOR	LLIO_UNDEFINED_DESCRIPTOR
#elif defined( IOP__USE_STANDARD_IO )
	typedef cslio::standard_input__		input__;
	typedef cslio::standard_output__		output__;
	typedef cslio::standard_io__			io__;
	using cslio::descriptor__;
	using csio::size__;
#	define IOP_UNDEFINED_DESCRIPTOR	CSLIO_UNDEFINED_DESCRIPTOR
#else
#	error "Undefined I/O enviroment !"
#endif


}

/*$END$*/
				  /********************************************/
				  /* do not modify anything belove this limit */
				  /*			  unless specified		   	  */
/******************************************************************************/

#endif
