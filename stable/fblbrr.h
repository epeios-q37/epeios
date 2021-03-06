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

//D Frontend/Backend Layout Backend Remote Request

#ifndef FBLBRR_INC_
# define FBLBRR_INC_

# define FBLBRR_NAME		"FBLBRR"

# if defined( E_DEBUG ) && !defined( FBLBRR_NODBG )
#  define FBLBRR_DBG
# endif

# include "err.h"
# include "flw.h"
# include "flx.h"
# include "fblbrq.h"


namespace fblbrr {
	using namespace fblbrq;

	struct parameter__
	{
		void *Content;
		cast__ Cast;
		void reset( bso::bool__ = true )
		{
			Content = NULL;
			Cast = c_Undefined;
		}
		parameter__( cast__ Cast = c_Undefined )
		{
			reset( false );

			this->Cast = Cast;
		}
		~parameter__( void )
		{
			reset();
		}
		void Init(
			void *Content,
			cast__ Cast )
		{
			reset();

			this->Content = Content;
			this->Cast = Cast;
		}
	};

	typedef bch::E_BUNCH_( parameter__ ) parameters_;
	E_AUTO( parameters );


	class remote_callbacks___
	: public callbacks__
	{
	private:
		parameters _Parameters;
		flx::size_embedded_iflow___ _IFlow;
		void *_Get(
			sdr::row__ Row,
			cast__ Cast )
		{
			parameter__ Parameter = _Parameters( Row );

			if ( Parameter.Cast != Cast )
				qRFwk();

			return Parameter.Content;
		}
	protected:
		virtual void FBLBRQPopIn(
			sdr::row__ CRow,
			flw::iflow__ &Flow,
			cast__ Cast );
		virtual void FBLBRQPopInEnd(
			sdr::row__ CRow,
			flw::iflow__ &Flow );
		virtual void FBLBRQPopOut(
			sdr::row__ CRow,
			flw::iflow__ &Flow,
			cast__ Cast );
		virtual void FBLBRQPush(
			bso::bool__ FirstCall,
			const casts_ &Casts,
			flw::oflow__ &Flow );
		virtual const void *FBLBRQGet(
			sdr::row__ Row,
			cast__ Cast )
		{
			return _Get( Row, Cast );
		}
		virtual void *FBLBRQPut(
			sdr::row__ Row,
			cast__ Cast )
		{
			return _Get( Row, Cast );
		}
		flw::iflow__ &FBLBRQGetFlow( sdr::row__ Row )
		{
			return *(flw::iflow__ *)_Get( Row, cFlow );
		}
		void FBLBRQPutFlow(
			sdr::row__ Row,
			flw::iflow__ &Flow )
		{
			parameter__ Parameter;

			Parameter.Init( &Flow, cFlow );

			if ( _Parameters.Append( Parameter) != Row )
				qRFwk();
		}
	public:
		void reset( bso::bool__ P = true )
		{
			callbacks__::reset( P );
			_Parameters.reset( P );
			_IFlow.reset( P );
		}
		remote_callbacks___( void ) 
		{
			reset( false );
		}
		virtual ~remote_callbacks___( void ) 
		{
			reset();
		}
		void Init( void )
		{
			reset();

			_Parameters.Init();
			callbacks__::Init();
			// '_IFlow(Driver)' initialis seulement lorsque utilis.
		}
	};
}

#endif
