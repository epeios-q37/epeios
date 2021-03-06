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

//	$Id: mmm0.h,v 1.8 2012/11/14 16:06:31 csimon Exp $

#ifndef MMM0_INC_
#define MMM0_INC_

#define MMM0_NAME		"MMM0"

#define	MMM0_VERSION	"$Revision: 1.8 $"

#define MMM0_OWNER		"Claude SIMON (http://zeusw.org/intl/contact.html)"


#if defined( E_DEBUG ) && !defined( MMM0_NODBG )
#define MMM0_DBG
#endif

/* Begin of automatic documentation generation part. */

//V $Revision: 1.8 $
//C Claude SIMON (http://zeusw.org/intl/contact.html)
//R $Date: 2012/11/14 16:06:31 $

/* End of automatic documentation generation part. */

/* Addendum to the automatic documentation generation part. */
//D MultiMeMory base 
/* End addendum to automatic documentation generation part. */

/*$BEGIN$*/

#error Do not use. Use 'MMM' instead.

// Ce module contient les dfinitions communes pour tous les 'mmmX' (X > 0), d'o son namesapce 'mmm'.

#include "err.h"
#include "flw.h"
#include "mdr.h"

#ifdef MMM_USE_V1
#	define MMM__USE_V1
#elif defined( MMM_USE_V2 )
#	define MMM__USE_V2
#else
#	define MMM__USE_V2
#endif

#ifdef MMM__USE_V1
#	define MMM_UNDEFINED_DESCRIPTOR	0
#elif defined( MMM__USE_V2 )
#	define MMM_UNDEFINED_DESCRIPTOR NONE
#else
#	error "No 'MMM' version dfined !".
#endif

namespace mmm {
	class multimemory_;	// Prdclaration.

	//t Type d'un descripteur de sous-mmoire dans le multimmoire.
	typedef mdr::row_t__	descriptor__;

	//c The standard memory driver for the multimemory.
	class multimemory_driver__
	: public mdr::E_MEMORY_DRIVER__
	{
	private:
		descriptor__ &_Descriptor;
		// memoire  laquelle il a t affect
		class multimemory_ *Multimemoire_;
		bso::ubyte__ &_Addendum;
		void Liberer_();
	protected:
		// fonction dporte
		// lit  partir de 'Position' et place dans 'Tampon' 'Nombre' octets;
		virtual void MDRRecall(
			mdr::row_t__ Position,
			mdr::size__ Amount,
			mdr::datum__ *Buffer );
		// fonction dporte
		// crit 'Nombre' octets  la position 'Position'
		virtual void MDRStore(
			const mdr::datum__ *Buffer,
			mdr::size__ Amount,
			mdr::row_t__ Position );
		// fonction dporte
		// alloue 'Capacite' octets
		virtual void MDRAllocate( mdr::size__ Size );
		virtual void MDRFlush( void );
	public:
		multimemory_driver__(
			descriptor__ &Descriptor,
			bso::ubyte__ &Addendum,
			mdr::size__ &Extent )
		: _Descriptor( Descriptor ),
		  _Addendum( Addendum ),
		  E_MEMORY_DRIVER__( Extent )
		{}
		void reset( bool P = true )
		{
			if ( P )
				Liberer_();
			else
				Multimemoire_ = NULL;

			_Descriptor = MMM_UNDEFINED_DESCRIPTOR;
			
			E_MEMORY_DRIVER__::reset( P );
		}
		//f Initialization with the 'Multimemory' multimemory.
		void Init( multimemory_ &Multimemory )
		{
			Liberer_();

			Multimemoire_ = &Multimemory;
			_Descriptor = MMM_UNDEFINED_DESCRIPTOR;

			E_MEMORY_DRIVER__::Init();
		}
		//f Return the current descriptor.
		descriptor__ Descriptor( void ) const
		{
			return _Descriptor;
		}
		//f Return the used multimemory.
		multimemory_ *Multimemory( void ) const
		{
			return Multimemoire_;
		}
	};

	class standalone_multimemory_driver__
	: public multimemory_driver__
	{
	private:
		mdr::size__ _Extent;
		descriptor__ _Descriptor;
		bso::ubyte__ _Addendum;
	public:
		standalone_multimemory_driver__( void )
		: multimemory_driver__( _Descriptor, _Addendum, _Extent )
		{}
	};

	#define E_MULTIMEMORY_DRIVER__	standalone_multimemory_driver__

}

/*$END$*/
#endif
