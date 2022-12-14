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

#ifndef DWTDCT_INC_
# define DWTDCT_INC_

# define DWTDCT_NAME		"DWTDCT"

# if defined( E_DEBUG ) && !defined( DWTDCT_NODBG )
#  define DWTDCT_DBG
# endif

// Directory WatCher Directory ConTent

# include "bso.h"
# include "err.h"
# include "str.h"
# include "ltf.h"
# include "lstctn.h"

# include "dwtbsc.h"
# include "dwtxcl.h"
# include "dwtght.h"

namespace dwtdct {
	using namespace dwtbsc;

	E_ROW( irow__ );

	typedef bch::E_BUNCHt_( drow__, irow__ ) i2d_;
	E_AUTO( i2d );

	typedef bch::E_BUNCHt_( exclusion__, frow__ ) fexclusions_;
	E_AUTO( fexclusions );

	typedef bch::rHF fexclusions_hf___;
	typedef bch::rFH fexclusions_fh___;


	typedef bch::E_BUNCHt_( fil::size__, frow__ ) sizes_;
	E_AUTO( sizes );

	typedef bch::rHF sizes_hf___;
	typedef bch::rFH sizes_files_hook___;


	typedef bch::E_BUNCHt_( time_t, frow__ ) timestamps_;
	E_AUTO( timestamps );

	typedef bch::rHF timestamps_hf___;
	typedef bch::rFH timestamps_fh___;


	typedef ctn::E_MCONTAINERt_( str::string_, frow__ ) fstrings_;
	E_AUTO( fstrings );

	typedef ctn::rHF fstrings_hf___;
	typedef ctn::rFH fstrings_fh___;


	typedef ctn::E_MCONTAINERt_( str::string_, dwtbsc::grow__ ) gstrings_;
	E_AUTO( gstrings );

	class dir_data_
	{
	public:
		struct s
		{
			time_t Timestamp;
			dwtght::grow__ GhostRow;	// Gestion du renommage de r???pertoire.
			name_::s Name;
			oddity_::s Oddity;
			exclusion__ Exclusion;
		} &S_;
		name_ Name;
		oddity_ Oddity;
		dir_data_( s &S )
		: S_( S ),
		  Name( S.Name ),
		  Oddity( S.Oddity )
		{}
		void reset( bso::bool__ P = true )
		{
			S_.Timestamp = 0;
			S_.GhostRow = qNIL;
			S_.Exclusion = x_Undefined;

			Name.reset( P );
			Oddity.reset( P );
		}
		void plug( qASd *AS )
		{
			Name.plug( AS );
			Oddity.plug( AS );
		}
		dir_data_ &operator =( const dir_data_ &DD )
		{
			S_.Timestamp = DD.S_.Timestamp;
			S_.GhostRow = DD.S_.GhostRow;
			S_.Exclusion = DD.S_.Exclusion;

			Name = DD.Name;
			Oddity = DD.Oddity;

			return *this;
		}
		void Init( void )
		{
			S_.Timestamp = 0;
			S_.GhostRow = qNIL;
			S_.Exclusion = x_Undefined;

			Name.Init();
			Oddity.Init();
		}
		E_RWDISCLOSE_( time_t, Timestamp );
		E_RWDISCLOSE_( dwtght::grow__, GhostRow );
		E_RWDISCLOSE_( exclusion__, Exclusion );
	};

	struct files_data_hf___
	{
	public:
		fstrings_hf___ Names;
		fexclusions_hf___ Exclusions;
		sizes_hf___ Sizes;
		timestamps_hf___ Timestamps;
		void reset( bso::bool__ P = true )
		{
			Names.reset( P );
			Exclusions.reset( P );
			Sizes.reset( P );
			Timestamps.reset( P );
		}
		E_CDTOR( files_data_hf___ );
		void Init(
			const fnm::name___ &Path,
			const fnm::name___ &Basename );
	};

	struct files_data_fh___
	{
	public:
		fstrings_fh___ Names;
		fexclusions_fh___ Exclusions;
		sizes_files_hook___ Sizes;
		timestamps_fh___ Timestamps;
		void reset( bso::bool__ P = true )
		{
			Names.reset( P );
			Exclusions.reset( P );
			Sizes.reset( P );
			Timestamps.reset( P );
		}
		E_CDTOR( files_data_fh___ );
		uys::eState Init(
			files_data_hf___ &Filenames,
			uys::mode__ Mode,
			uys::behavior__ Behavior,
			flsq::id__ ID )
		{
			uys::eState State = Names.Init( Filenames.Names, Mode, Behavior, ID );

			if ( !State.IsError() ) {
				if ( Exclusions.Init( Filenames.Exclusions, Mode, Behavior, ID ) != State )
					State = uys::sInconsistent;
			}

			if ( !State.IsError() ) {
				if ( Sizes.Init( Filenames.Sizes, Mode, Behavior, ID ) != State )
					State = uys::sInconsistent;
			}

			if ( !State.IsError() ) {
				if ( Timestamps.Init( Filenames.Timestamps, Mode, Behavior, ID ) != State )
					State = uys::sInconsistent;
			}

			return State;
		}
	};


	class files_data_
	{
	public:
		struct s
		{
			fstrings_::s Names;
			fexclusions_::s Exclusions;
			sizes_::s Sizes;
			timestamps_::s Timestamps;
		};
		fstrings_ Names;
		fexclusions_ Exclusions;
		sizes_ Sizes;
		timestamps_ Timestamps;
		files_data_( s &S )
		: Names( S.Names ),
		  Exclusions( S.Exclusions ),
		  Sizes( S.Sizes ),
		  Timestamps( S.Timestamps )
		{}
		void reset( bso::bool__ P = true )
		{
			Names.reset( P );
			Exclusions.reset( P );
			Sizes.reset( P );
			Timestamps.reset( P );
		}
		void plug( files_data_fh___ &Hook )
		{
			Names.plug( Hook.Names );
			Exclusions.plug( Hook.Exclusions );
			Sizes.plug( Hook.Sizes );
			Timestamps.plug( Hook.Timestamps );
		}
		void plug( qASd *AS )
		{
			Names.plug( AS );
			Exclusions.plug( AS );
			Sizes.plug( AS );
			Timestamps.plug( AS );
		}
		files_data_ &operator =( const files_data_ &FD )
		{
			Names = FD.Names;
			Exclusions = FD.Exclusions;
			Sizes = FD.Sizes;
			Timestamps = FD.Timestamps;

			return *this;
		}
		void Init( void )
		{
			Names.Init();
			Exclusions.Init();
			Sizes.Init();
			Timestamps.Init();
		}
		E_NAVt( Names., frow__ );
	};

	class goofs_data_
	{
	public:
		struct s
		{
			gstrings_::s
				Names,
				Oddities;
		};
		gstrings_
			Names,
			Oddities;
		goofs_data_( s &S )
		: Names( S.Names ),
		  Oddities( S.Oddities )
		{}
		void reset( bso::bool__ P = true )
		{
			Names.reset( P );
			Oddities.reset( P );
		}
		void plug( qASd *AS )
		{
			Names.plug( AS );
			Oddities.plug( AS );
		}
		goofs_data_ &operator =( const goofs_data_ &GD )
		{
			Names = GD.Names;
			Oddities = GD.Oddities;

			return *this;
		}
		void Init( void )
		{
			Names.Init();
			Oddities.Init();
		}
	};

	class item_
	{
	public:
		struct s
		{
			irow__ Parent;
			str::string_::s Path;
			dir_data_::s Dir;
			files_data_::s Files;
			goofs_data_::s Goofs;
		} &S_;
		str::string_ Path;
		dir_data_ Dir;
		files_data_ Files;
		goofs_data_ Goofs;
		item_( s &S )
		: S_( S ),
		  Path( S.Path ),
		  Dir( S.Dir ),
		  Files( S.Files ),
		  Goofs( S.Goofs )
		{}
		void reset( bso::bool__ P = true )
		{
			S_.Parent = qNIL;

			Path.reset( P );
			Dir.reset( P );
			Files.reset( P );
			Goofs.reset( P );
		}
		void plug( qASd *AS )
		{
			Path.plug( AS );
			Dir.plug( AS );
			Files.plug( AS );
			Goofs.plug( AS );
		}
		item_ &operator =( const item_ &I )
		{
			S_.Parent = I.S_.Parent;

			Path = I.Path;
			Dir = I.Dir;
			Files = I.Files;
			Goofs = I.Goofs;

			return *this;
		}
		void Init( void )
		{
			S_.Parent = qNIL;

			Path.Init();
			Dir.Init();
			Files.Init();
			Goofs.Init();
		}
		E_RWDISCLOSE_( irow__, Parent );
	};

	E_AUTO( item )

	typedef bch::E_BUNCHt_( item_ *, irow__ ) _items_;

	void _Delete( _items_ &Items );

	class items_
	: public _items_
	{
	public:
		struct s
		: public _items_::s
		{};
		void reset( bso::bool__ P = true )
		{
			if ( P )
				_Delete( *this );

			_items_::reset( P );
		}
		items_( s &S )
		: _items_( S )
		{}
		// Other methds are inherited.
	};

	E_AUTO( items );

	typedef stkbch::qBSTACKdl( irow__ ) irows_;
	E_AUTO( irows );

	typedef bch::E_BUNCHt_( dwtbsc::files_ *, irow__ ) files_set_;
	E_AUTO( files_set );

	typedef bch::E_BUNCHt_( dwtbsc::commons_ *, irow__ ) commons_set_;
	E_AUTO( commons_set );

	typedef items_ content_;
	E_AUTO( content );

	using tol::timer__;

	class exploration_observer__
	: public timer__
	{
	protected:
		virtual void DWTDCTReport(
			bso::uint__ Handled,
			bso::uint__ ToHandle,
			tamount__ ThreadAmount ) = 0;
	public:
		void Report(
			bso::uint__ Handled,
			bso::uint__ ToHandle,
			tamount__ ThreadAmount )
		{
			if ( IsEnabled() ) {
				DWTDCTReport( Handled, ToHandle, ThreadAmount );
				Launch();
			}
		}
	};

	void Explore( 
		const str::string_ &Path,
		tamount__ ThreadAmountMax,
		const dwtxcl::excluder_ &Excluder,
		const dwtbsc::limitations__ &Limitations,
		const dwtbsc::ghosts_oddities_ &GO,
		exclusions_handling__ ExclusionsHandling,
		content_ &Content,
		exploration_observer__ &Observer );

	qENUM( GhostsSettingStat ) {
		gssHandled,
		gssTotal,
		gssCreated,
		gssUpdated,
		gssSkipped,
		gssFailed,
		gssIntruder,
		gssExpected,
		gss_amount,
		gss_Undefined
	};

	struct fGhostsSettingStats
	{
	private:
		bso::uint__ Core_[gss_amount];
		void Test_( eGhostsSettingStat Stat ) const
		{
			if ( Stat >= gss_amount )
				qRFwk();
		}
	public:
		void reset( bso::sBool = true )
		{
			memset(Core_, 0, sizeof( Core_ ) );
		}
		qCDTOR( fGhostsSettingStats );
		void Init( void )
		{
			memset(Core_, 0, sizeof( Core_ ) );
		}
		bso::uint__ GetValue( eGhostsSettingStat Stat ) const
		{
			Test_( Stat );

			return Core_[Stat];
		}
		void SetValue(
			eGhostsSettingStat Stat,
			bso::uint__ Value )
		{
			Test_( Stat );

			Core_[Stat] = Value;
		}
		void Inc( eGhostsSettingStat Stat )
		{
			Test_( Stat );
			Core_[Stat]++;
		}
	};

	class fGhostsSettingObserver
	: public timer__
	{
	protected:
		virtual void DWTDCTReport( const fGhostsSettingStats &Stats ) = 0;
	public:
		void Report(const fGhostsSettingStats &Stats )
		{
			if ( IsEnabled() ) {
				DWTDCTReport( Stats );
				Launch();
			}
		}
	};

	typedef bch::E_BUNCHt_( dwtght::grow__, irow__ ) i2g_;
	E_AUTO( i2g );
	
	// ATTENTION : 'Content' doit avoir ???t??? r???cup???r??? avec 'rhKeepGhostLike'.
	void SetGhosts(
		const str::string_ &Root,
		const content_ &Content,
		const dwtbsc::ghosts_oddities_ &GO,
		fGhostsSettingObserver &GhostsSettingObserver,
		i2g_ &I2G );	// Cr???er dans chaque r???pertoire le r???pertoire sp???cial servant ??? d???tecter le renommage des r???pertoires.

	// ATTENTION : 'Content' doit avoir ???t??? r???cup???r??? avec 'rhKeepGhostLike'.
	void DelGhosts(
		const str::string_ &Root,
		const content_ &Content,
		const dwtbsc::ghosts_oddities_ &GO,
		dwtdct::exploration_observer__ &Observer );	// Supprime toute trace des 'ghostt's

	class rBasicGhostsSettingObserver
	: public fGhostsSettingObserver
	{
	protected:
		virtual void DWTDCTReport( const fGhostsSettingStats &Stats ) override;
	private:
		ltf::line_text_oflow___<> _Flow;
		str::string _Message;
	public:
		void reset( bso::bool__ P = true )
		{
			fGhostsSettingObserver::reset( P );
			_Flow.reset( P );
			_Message.reset( P );
		}
		E_CVDTOR( rBasicGhostsSettingObserver );
		void Init(
			const str::string_ &Message,
			txf::text_oflow__ &TFLow,
			tol::delay__ Delay )
		{
			fGhostsSettingObserver::Init( Delay );

			_Flow.Init( TFLow );
			_Message.Init( Message );
		}
	};

	void TestGhosts(
		const str::string_ &Root,
		const content_ &Content,
		const dwtbsc::ghosts_oddities_ &GO,
		const str::string_ &NoGhostMessage,
		const str::string_ &GhostIgnoredMessage,
		txf::text_oflow__ &TFlow );

	class basic_exploration_observer___
	: public exploration_observer__
	{
	protected:
		virtual void DWTDCTReport(
			bso::uint__ Handled,
			bso::uint__ ToHandle,
			tamount__ ThreadAmount );
	private:
		str::string _Message;
		ltf::line_text_oflow___<> _Flow;
	public:
		void reset( bso::bool__ P = true )
		{
			exploration_observer__::reset( P );

			_Message.Init();
			_Flow.reset( P );
		}
		E_CVDTOR( basic_exploration_observer___ );
		void Init(
			tol::delay__ Delay,
			const str::string &Message,
			txf::text_oflow__ &TFlow )
		{
			exploration_observer__::Init( Delay );

			_Message.Init( Message );
			_Flow.Init( TFlow );
		}
	};

	// List of files per ghost.
	typedef ctn::E_MCONTAINERt_( frows_, grow__ ) gfrows_;
	E_AUTO( gfrows );

	typedef ctn::rHF gfrows_hf___;
	typedef ctn::rFH gfrows_fh___;

	struct rGhost2FilesHF
	{
	public:
		gfrows_hf___ GFRows;
		files_data_hf___ Files;
		void reset( bso::bool__ P = true )
		{
			GFRows.reset( P );
			Files.reset( P );
		}
		E_CDTOR( rGhost2FilesHF );
		void Init(
			const fnm::name___ &Path,
			const fnm::name___ &Basename );
	};

	struct rGhost2FilesFH
	{
	public:
		gfrows_fh___ GFRows;
		files_data_fh___ Files;
		void reset( bso::bool__ P = true )
		{
			GFRows.reset( P );
			Files.reset( P );
		}
		E_CDTOR( rGhost2FilesFH );
		uys::eState Init(
			rGhost2FilesHF &Filenames,
			uys::mode__ Mode,
			uys::behavior__ Behavior,
			flsq::id__ ID )
		{
			uys::eState State = GFRows.Init( Filenames.GFRows, Mode, Behavior, ID );

			if ( !State.IsError() ) {
				if ( Files.Init( Filenames.Files, Mode, Behavior, ID ) != State )
					State = uys::sInconsistent;
			}

			return State;
		}
	};


	// Files rattached to each ghost.
	class ghost2files_
	{
	public:
		struct s {
			gfrows_::s GFRows;
			files_data_::s Files;
		};
		gfrows_ GFRows;
		files_data_ Files;
		ghost2files_( s &S )
		: GFRows( S.GFRows ),
		  Files( S.Files )
		{}
		void reset( bso::bool__ P = true )
		{
			GFRows.reset( P );
			Files.reset( P );
		}
		void plug( rGhost2FilesFH &Hook )
		{
			GFRows.plug( Hook.GFRows );
			Files.plug( Hook.Files );
		}
		void plug( qASd *AS )
		{
			GFRows.plug( AS );
			Files.plug( AS );
		}
		ghost2files_ &operator =( const ghost2files_ &G2F )
		{
			GFRows = G2F.GFRows;
			Files = G2F.Files;

			return *this;
		}
		void Init( void )
		{
			GFRows.Init();
			Files.Init();
		}
		void Append(
			grow__ GRow,
			const item_ &Item );
		void Append(
			const content_ &Content,
			const i2g_ &I2G );
	};

	E_AUTO( ghost2files );

	struct ghost2files_rack___
	{
	public:
		ghost2files G2F;
		rGhost2FilesFH Hook;
		void reset( bso::bool__ P = true )
		{
			G2F.reset( P );
			Hook.reset( P );
		}
		E_CDTOR( ghost2files_rack___ );
		void Init( void )
		{
			G2F.reset();
			Hook.reset();

			// 'Init(...)' called by dedicated functions.
		}
	};

	ghost2files_ &GetRWG2F(
		const str::string_ &Root,
		const dwtbsc::ghosts_oddities_ &GO,
		ghost2files_rack___ &Rack );

	const ghost2files_ &GetROG2F(
		const str::string_ &Root,
		const dwtbsc::ghosts_oddities_ &GO,
		ghost2files_rack___ &Rack );

	void Fill(
		const content_ &Content,
		const ghost2files_ &G2F,
		dKernel &Kernel );

}

#endif
