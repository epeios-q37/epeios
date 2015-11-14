/*
	Copyright (C) 2015 Claude SIMON (http://q37.info/contact/).

	This file is part of fwtchrq.

    fwtchrq is free software: you can redistribute it and/or
	modify it under the terms of the GNU Affero General Public License as
	published by the Free Software Foundation, either version 3 of the
	License, or (at your option) any later version.

    fwtchrq is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
	Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with fwtchrq.  If not, see <http://www.gnu.org/licenses/>
*/

// File WaTcher FileTRee

#ifndef FWTFTR__INC
# define FWTFTR__INC

# ifdef XXX_DBG
#	define FWTFTR__DBG
# endif

# include "fwtbsc.h"

# include "fwtdct.h"
# include "fwtmov.h"
# include "fwtbsc.h"

# include "dir.h"
# include "fil.h"
# include "dtr.h"
# include "xml.h"
# include "ltf.h"

namespace fwtftr {

	using namespace fwtbsc;

	// Version du contenu du flux XML.
	enum version__ {
		v0_1,
		v_amount,
		v_Current = v_amount - 1,
		v_Undefined
	};

	const char *GetLabel( version__ Version );

	version__ GetVersion( const str::string_ &Pattern );

	typedef dtr::E_DTREEt_( fwtbsc::drow__ ) dtree_;
	E_AUTO( dtree );

	class file_tree_
	: public kernel_,
	  public dtree_
	{
	public:
		struct s
		: public kernel_::s,
		  public dtree_::s
		{};
		file_tree_( s &S )
		: kernel_( S ),
		  dtree_( S )
		{}
		void reset( bso::bool__ P = true )
		{
			kernel_::reset( P );
			dtree_::reset( P );
		}
		void plug( qAS_  &AS )
		{
			kernel_::plug( AS );
			dtree_::plug( AS );
		}
		file_tree_ &operator =( const file_tree_ &FT )
		{
			kernel_::operator =( FT );
			dtree_::operator =( FT );

			return *this;
		}
		void Init( void )
		{
			kernel_::Init();
			dtree_::Init();
		}
		const str::string_ &GetPath(
			drow__ Row,
			str::string_ &Path ) const;
		 void Dump( 
			 drow__ Row,
			 xml::writer_ &Writer,
			 version__ Version = v_Current ) const;
	};

	E_AUTO( file_tree );

	class file_tree_files_hook___;

	class file_tree_hook_filenames___
	{
	private:
		dtr::hook_filenames___ Tree_;
		fwtbsc::kernel_hook_filenames___ Kernel_;
	public:
		void reset( bso::bool__ P = true )
		{
			Tree_.reset( P );
			Kernel_.reset( P );
		}
		E_CDTOR( file_tree_hook_filenames___ );
		void Init(
			const fnm::name___ &Path,
			const fnm::name___ &Basename );

		friend file_tree_files_hook___;
	};

	class file_tree_files_hook___
	{
	private:
		dtr::files_hook___ Tree_;
		fwtbsc::kernel_files_hook___ Kernel_;
	public:
		void reset( bso::bool__ P = true )
		{
			Tree_.reset( P );
			Kernel_.reset( P );
		}
		E_CDTOR( file_tree_files_hook___ );
		void Init(
			file_tree_hook_filenames___ &Filenames,
			uys::mode__ Mode,
			uys::behavior__ Behavior,
			flsq::id__ ID )
		{
			Tree_.Init( Filenames.Tree_, Mode, Behavior, ID );
			Kernel_.Init( Filenames.Kernel_, Mode, Behavior, ID );
		}
		friend uys::state__ Plug(
			file_tree_ &Tree,
			file_tree_files_hook___ &Hook );
	};

	inline uys::state__ Plug(
		file_tree_ &Tree,
		file_tree_files_hook___ &Hook )
	{
		uys::state__ State = dtr::Plug( Tree, Hook.Tree_ );

		if ( State.IsError() )
			Hook.reset();
		else if ( fwtbsc::Plug( Tree, Hook.Kernel_ ) != State ) {
			State = uys::sInconsistent;
			Hook.reset();
		}

		return State;
	}

	struct file_tree_rack___ {
		file_tree_files_hook___ Hook;
		file_tree Tree;
		void reset( bso::bool__ P = true )
		{
			Hook.reset( P );
			Tree.reset( P );
		}
		E_CDTOR( file_tree_rack___ );
		void Init( void )
		{
			Hook.reset();
			Tree.reset();

			// L'initialisation proprement dite sera r�alis�e par des fonctions d�di�es.
		}
	};

	class processing_observer__
	: public fwtbsc::observer__
	{
	protected:
		virtual void FWTFTRReport(
			bso::uint__ Handled,
			bso::uint__ Total ) = 0;
	public:
		void Report(
			bso::uint__ Handled,
			bso::uint__ Total )
		{
			return FWTFTRReport( Handled, Total );
		}
	};
	
	drow__ Process(
		const fwtdct::content_ &Content,
		file_tree_ &Tree,
		processing_observer__ &Observer );

	class load_observer__
	: public fwtbsc::observer__
	{
	protected:
		virtual void FWTFTRReport(
			bso::uint__ Handled,
			bso::uint__ Total ) = 0;
	public:
		void Report(
			bso::uint__ Handled,
			bso::uint__ Total )
		{
			FWTFTRReport( Handled, Total );
		}
	};

	drow__ Load(
		xml::parser___ &Parser,
		version__ Version,
		file_tree_ &Tree,
		load_observer__ &Observer );

	typedef fwtbsc::observer___ _observer___;

	class basic_processing_observer___
	: public processing_observer__,
	  public _observer___
	  
	{
	protected:
		virtual void FWTFTRReport(
			bso::uint__ Handled,
			bso::uint__ ToHandle )
		{
			_observer___::Report_( Handled, ToHandle );
		}
	public:
		void reset( bso::bool__ P = true )
		{
			processing_observer__::reset( P );
			_observer___::reset( P );
		}
		E_CVDTOR( basic_processing_observer___ );
		void Init(
			const str::string_ &Message,
			txf::text_oflow__ &Flow,
			tol::delay__ Delay )
		{
			processing_observer__::Init( Delay );
			_observer___::Init( Message, Flow );
		}
	};

	class basic_load_observer___
	: public load_observer__,
	  public _observer___
	{
	protected:
		virtual void FWTFTRReport(
			bso::uint__ Handled,
			bso::uint__ ToHandle )
		{
			_observer___::Report_( Handled, ToHandle );
		}
	public:
		void reset( bso::bool__ P = true )
		{
			load_observer__::reset( P );
			_observer___::reset( P );
		}
		E_CVDTOR( basic_load_observer___ );
		void Init(
			const str::string_ &Message,
			txf::text_oflow__ &Flow,
			tol::delay__ Delay )
		{
			load_observer__::Init( Delay );
			_observer___::Init( Message, Flow );
		}
	};

	void Sort(
		drow__ Root,
		file_tree_ &Tree,
		fwtbsc::sort_type__ SortType );
}


#endif
