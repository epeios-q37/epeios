/*
	Header for the 'fblfrp' library by Claude SIMON (csimon at zeusw dot org)
	Copyright (C) 2004 Claude SIMON.

	This file is part of the Epeios (http://zeusw.org/epeios/) project.

	This library is free software; you can redistribute it and/or
	modify it under the terms of the GNU General Public License
	as published by the Free Software Foundation; either version 2
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

//	$Id: xxx.h,v 1.9 2012/11/14 16:06:23 csimon Exp $

#ifndef FBLFRP__INC
#define FBLFRP__INC

#define FBLFRP_NAME		"FBLFRP"

#define	FBLFRP_VERSION	"$Revision: 1.9 $"

#define FBLFRP_OWNER		"Claude SIMON"

#include "ttr.h"

extern class ttr_tutor &FBLFRPTutor;

#if defined( E_DEBUG ) && !defined( FBLFRP_NODBG )
#define FBLFRP_DBG
#endif

/* Begin of automatic documentation generation part. */

//V $Revision: 1.9 $
//C Claude SIMON (csimon at zeusw dot org)
//R $Date: 2012/11/14 16:06:23 $

/* End of automatic documentation generation part. */

/******************************************************************************/
				  /* do not modify anything above this limit */
				  /*			  unless specified			 */
				  /*******************************************/

/* Addendum to the automatic documentation generation part. */
//D Frontend/Backend Layout Frontend Remote Parameters 
/* End addendum to automatic documentation generation part. */

/*$BEGIN$*/

# include "fblfph.h"

# include "err.h"
# include "flw.h"
# include "tol.h"
# include "flx.h"

# define FBLFRP__OUT_PARAMETERS_AMOUNT_MAX		20	// Le nombre maximum de param�tres en sortie.

namespace fblfrp {

	struct datum__ {
		fblcst::cast__ Cast;
		void *Pointer;
		datum__( 
			fblcst::cast__ Cast = fblcst::c_Undefined,
			void *Pointer = NULL )
		{
			this->Cast = Cast;
			this->Pointer= Pointer;
		}
	};

	typedef fblfph::callbacks__ _callbacks__;

	class remote_callbacks___
	: public _callbacks__
	{
	private:
		bch::E_BUNCH__( datum__, FBLFRP__OUT_PARAMETERS_AMOUNT_MAX ) _Data;
		flx::size_embedded_iflow___ _IFlow;
	protected:
		virtual void FBLFPHPreProcess( void )
		{
			_Data.Init();
		}
		virtual void FBLFPHIn(
			fblcst::cast__ Cast,
			const void *Pointer,
			flw::ioflow__ &Channel );
		virtual void FBLFPHOut(
			flw::ioflow__ &Channel,
			fblcst::cast__ Cast,
			void *Pointer );
		virtual void FBLFPHFlowIn(
			bso::bool__ FirstCall,
			flw::iflow__ &Flow,
			flw::ioflow__ &Channel );
		virtual void FBLFPHFlowOut(
			flw::ioflow__ &Channel,
			flw::iflow__ *&Flow );
		virtual void FBLFPHPostProcess( flw::ioflow__ &Flow );
	public:
		void reset( bso::bool__ P = true )
		{
			_Data.reset( P );
			_callbacks__::reset( P );
			_IFlow.reset( P );
		}
		E_CVDTOR( remote_callbacks___ );
		void Init( void )
		{
			_Data.Init();
			_callbacks__::Init();
			// '_IFlow' initialis� seulement lorsque utilis�.
		}
	};
}

/*$END$*/
				  /********************************************/
				  /* do not modify anything belove this limit */
				  /*			  unless specified		   	  */
/******************************************************************************/

#endif
