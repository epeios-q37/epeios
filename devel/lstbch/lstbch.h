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

// LiST BunCH 

#ifndef LSTBCH__INC
# define LSTBCH__INC

# define LSTBCH_NAME		"LSTBCH"

# define	LSTBCH_VERSION	"$Revision: 1.46 $"

# define LSTBCH_OWNER		"Claude SIMON (http://zeusw.org/intl/contact.html)"

# if defined( E_DEBUG ) && !defined( LSTBCH_NODBG )
#  define LSTBCH_DBG
# endif

# include "err.h"
# include "flw.h"
# include "bch.h"
# include "lst.h"

/*************************/
/****** New version ******/
/*************************/

# define qLBUNCHv( type, row ) E_LBUNCHt_( type, row )
# define qLBUNCHi( type, row ) E_LBUNCHt( type, row )

# define qLBUNCHvl( type ) qLBUNCHv( type, sdr::fRow )
# define qLBUNCHil( type ) qLBUNCHi( type, sdr::fRow )

/*************************/
/****** Old version ******/
/*************************/

namespace lstbch {

	using lst::list_;
	using bch::bunch_;

	class fCore
	{
	protected:
		virtual bch::fCore &LSTBCHGetBunch( void ) = 0;
		virtual lst::fCore &LSTBCHGetList( void ) = 0;
	public:
		qCALLBACK_DEF( Core );
		bch::fCore &GetBunch( void )
		{
			return LSTBCHGetBunch();
		}
		lst::fCore &GetList( void )
		{
			return LSTBCHGetList();
		}
	};


	//c Bunch associated to a list.
	template <typename type, typename row, typename row_t> class list_bunch_
	: public fCore,
	  public list_<row, row_t>,
	  public bunch_<type, row>
	{
	protected:
		virtual bch::fCore &LSTBCHGetBunch( void ) override
		{
			return *this;
		}
		virtual lst::fCore &LSTBCHGetList( void ) override
		{
			return *this;
		}
		virtual void LSTAllocate(
			sdr::size__ Size,
			aem::mode__ Mode ) override
		{
			bunch_<type, row>::Allocate( Size, Mode );
		}
	public:
		struct s
		: public list_<row, row_t>::s,
		  public bunch_<type, row>::s
		{};
		list_bunch_( s &S )
		: list_<row, row_t>( S ),
		  bunch_<type, row>( S )
		{}
		void reset( bso::bool__ P = true )
		{
			fCore::reset( P );
			list_<row, row_t>::reset( P );
			bunch_<type, row>::reset( P );
		}
		void plug( qAS_ &AS )
		{
			list_<row, row_t>::plug( AS );
			bunch_<type, row>::plug( AS );
		}
		list_bunch_ &operator =( const list_bunch_ &LB )
		{
			list_<row, row_t>::operator =( LB );
			bunch_<type, row>::operator =( LB );

			return *this;
		}
		//f Initialization.
		void Init( void )
		{
			fCore::Init();
			list_<row, row_t>::Init();
			bunch_<type, row>::Init();
		}
		void Allocate(
			sdr::size__ Size,
			aem::mode__ Mode = aem::m_Default )
		{
			list_<row, row_t>::Allocate( Size, Mode );
		}
		E_NAVt( list_<E_COVER2(row,row_t)>::, row )
		row Add(
			const type &Object,
			row Row = qNIL )
		{
			Row = list_<row, row_t>::New( Row );

			bunch_<type, row>::Store( Object, Row );

			return Row;
		}
		row Add(
			const type *Object,
			row Row = qNIL )
		{
			Row = list_<row, row_t>::New( Row );

			bunch_<type, row>::Store( Object, Row );

			return Row;
		}
		//f Delete entry 'Row'.
		void Remove( row Row )
		{
			list_<row, row_t>::Delete( Row );
		}
		row Search( type Object ) const
		{
			row Row = bunch_<type, row>::Search( Object );

			if ( Row != qNIL )
				if ( !list_<row, row_t>::Exists( Row ) )
					Row = qNIL;

			return Row;
		}
		//f Create new entry and return its row.
		row New( void )
		{
			return list_<row, row_t>::New();
		}
		//f Create new entry with row 'Row'.
		row New( row Row )
		{
			return list_<row, row_t>::New( Row );
		}
		// To avoid the use of herited 'Append' methods.
		void Append( void ) const
		{
			qRFbd();
		}
		bunch_<type, row> &Bunch( void )
		{
			return *this;
		}
		const bunch_<type, row> &Bunch( void ) const
		{
			return *this;
		}
		list_<row, row_t> &List( void )
		{
			return *this;
		}
		const list_<row, row_t> &List( void ) const
		{
			return *this;
		}
	};

	E_AUTO3( list_bunch )

#ifndef FLS__COMPILATION

	class fHook
	{
	protected:
		virtual bch::fHook &LSTBCHGetBunchHook( void ) = 0;
		virtual lst::fHook &LSTBCHGetListHook( void ) = 0;
	public:
		qCALLBACK_DEF( Hook );
		bch::fHook &GetBunchHook( void )
		{
			return LSTBCHGetBunchHook();
		}
		lst::fHook &GetListHook( void )
		{
			return LSTBCHGetListHook();
		}
	};

	inline bso::fBool Plug(
		fCore &Core,
		fHook &Hook )
	{
		bso::fBool Exists = bch::Plug( Core.GetBunch(), Hook.GetBunchHook() );

		return lst::Plug( Core.GetList(), Hook.GetListHook(), Core.GetBunch().GetAmount() );
	}

	class rRH
	: public fHook
	{
	private:
		bch::rRH Bunch_;
		lst::rRH List_;
	public:
		void reset( bso::bool__ P = true )
		{
			fHook::reset( P );

			Bunch_.reset( P );
			List_.reset( P );
		}
		qCDTOR( rRH );
		void Init( void )
		{
			Bunch_.Init();
			List_.Init();

			fHook::Init();
		}
	};


	struct rHF
	{
	public:
		bch::rHF Bunch;
		lst::rHF List;
		void reset( bso::bool__ P = true )
		{
			Bunch.reset( P );
			List.reset( P );
		}
		E_CDTOR( rHF );
		void Init(
			const fnm::name___ &Path,
			const fnm::name___ &Basename );
	};

	class rFH
	: public fHook
	{
	private:
		bch::rFH Bunch_;
		lst::rFH List_;
	public:
		void reset( bso::bool__ P = true )
		{
			fHook::reset( P );

			Bunch_.reset( P );
			List_.reset( P );
		}
		qCDTOR( rFH );
		uys::eState Init(
			const rHF &Filenames,
			fCore &Core,
			uys::mode__ Mode,
			uys::behavior__ Behavior,
			flsq::id__ ID )
		{
			uys::eState State = Bunch_.Init( Filenames.Bunch, Core.GetBunch(), Mode, Behavior, ID );

			if ( !State.IsError() ) {
				if ( List_.Init( Filenames.List, Core.GetList(), Mode, Behavior, ID ) != State )
					State = uys::sInconsistent;
			}

			fHook::Init();

			return State;
		}
	};
# endif

# define E_LBUNCHtx_( type, row, row_t )		list_bunch_<type, row, row_t>
# define E_LBUNCHtx( type, row, row_t )		list_bunch<type, row, row_t>

# define E_LBUNCHt_( type, row )	E_LBUNCHtx_( type, row, sdr::row_t__)
# define E_LBUNCHt( type, row )	E_LBUNCHtx( type, row, sdr::row_t__)

# define  E_LBUNCH_( type )		E_LBUNCHt_( type, sdr::row__ )
# define  E_LBUNCH( type )		E_LBUNCHt( type, sdr::row__ )
}

#endif
