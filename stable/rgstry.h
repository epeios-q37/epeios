/*
	'rgstry.h' by Claude SIMON (http://zeusw.org/).

	'rgstry' is part of the Epeios framework.

    The Epeios framework is free software: you can redistribute it and/or
	modify it under the terms of the GNU General Public License as published
	by the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    The Epeios framework is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with The Epeios framework.  If not, see <http://www.gnu.org/licenses/>.
*/

#ifndef RGSTRY__INC
#define RGSTRY__INC

#define RGSTRY_NAME		"RGSTRY"

#if defined( E_DEBUG ) && !defined( RGSTRY_NODBG )
#define RGSTRY_DBG
#endif

/******************************************************************************/
				  /* do not modify anything above this limit */
				  /*			  unless specified			 */
				  /*******************************************/

// ReGiSTRY

# include "err.h"
# include "flw.h"
# include "str.h"
# include "lstbch.h"
# include "lstctn.h"
# include "xtf.h"
# include "cpe.h"
# include "xpp.h"
# include "stk.h"
# include "fnm.h"
# include "tagsbs.h"


# define RGSTRY__TAG_MARKER_S	"$"
# define RGSTRY__TAG_MARKER_C	'$'

# define RGSTRY_TAGGING_ATTRIBUTE( attribute ) "[" attribute "=\"" RGSTRY__TAG_MARKER_S "\"]"

# define RGSTRY_TAGGED_ENTRY( tag, attribute )	tag RGSTRY_TAGGING_ATTRIBUTE( attribute )


// Pr�d�claration.
namespace lcl {
	class meaning_;
}

namespace rgstry {

	typedef str::string		_term;
	typedef str::string_	_term_;

	typedef _term_			name_;
	typedef _term			name;

	typedef _term_			value_;
	typedef _term			value;

	class path_item_ {
	public:
		struct s {
			name_::s TagName, AttributeName;
			value_::s AttributeValue;
		};
		name_ TagName, AttributeName;
		value_ AttributeValue;
		path_item_( s &S )
		: TagName( S.TagName ),
		  AttributeName( S.AttributeName ),
		  AttributeValue( S.AttributeValue )
		{}
		void reset( bso::bool__ P = true )
		{
			TagName.reset( P );
			AttributeName.reset( P );
			AttributeValue.reset( P);
		}
		void plug( ags::E_ASTORAGE_ &AS )
		{
			TagName.plug( AS );
			AttributeName.plug( AS );
			AttributeValue.plug( AS );
		}
		path_item_ &operator =( const path_item_ &PI )
		{
			TagName = PI.TagName;
			AttributeName = PI.AttributeName;
			AttributeValue = PI.AttributeValue;

			return *this;
		}
		void Init( void )
		{
			TagName.Init();
			AttributeName.Init();
			AttributeValue.Init();
		}
	};

	E_AUTO( path_item );

	typedef ctn::E_CONTAINER_( path_item_ ) _path_items_;

	class path_
	: public _path_items_
	{
	public:
		struct s
		: _path_items_::s
		{};
		path_( s &S )
		: _path_items_( S )
		{}
		void reset( bso::bool__ P = true )
		{
			_path_items_::reset( P );
		}
		void plug( ags::E_ASTORAGE_ &AS )
		{
			_path_items_::plug( AS );
		}
		_path_items_ &operator =( const _path_items_ &PI )
		{
			_path_items_::operator =( PI );

			return *this;
		}
		void Init( void )
		{
			_path_items_::Init();
		}
	};


	E_AUTO( path )

	sdr::row__ BuildPath(
		const str::string_ &PathString,
		path_ &Path );

	typedef ctn::E_MCONTAINER_( value_ )	values_;
	E_AUTO( values )

	E_ROW( row__ );
	typedef bch::E_BUNCH_( row__ ) rows_;
	E_AUTO( rows );

	typedef values_	tags_;
	E_AUTO( tags );

	class entry___
	{
	private:
		void _GetParentPath(
			bso::bool__ NoTailingSlash,
			str::string_ &Path ) const
		{
			if ( _Parent != NULL ) {
				_Parent->GetPath( Path );

				if ( Path.Amount() != 0 ) {
					if ( Path( Path.Last() ) == '/' ) {
						if ( NoTailingSlash )
							Path.Remove( Path.Last() );
					} else if ( !NoTailingSlash )
						Path.Append( '/' );
				}
			}
		}
		const bso::bool__ _IsPostInitialized( void ) const
		{
			return ( ( _Path.Amount() != 0 )
				     || ( _RawPath == NULL )
					 || ( *_RawPath == 0 ) );
		}
		void _PostInitialize( void ) const;
		const str::string_ &_GetPath(
			const tags_ &Tags,
			str::string_ &Path ) const;
	private:
		const entry___ *_Parent;
		const char *_RawPath;
		mutable str::string _Path;
	protected:
		virtual tagsbs::short_tags_callback__ &RGSTRYGetTagSubstitutionCallback( void ) const
		{
			return *(tagsbs::short_tags_callback__ *)NULL;
		}
	public:
		void reset( bso::bool__ P = true )
		{
			_Parent = NULL;
			_RawPath = NULL;
			_Path.reset( P );
		}
		entry___(
			const char *Path = NULL,	// Non dupliqu� !
			const entry___ &Parent = *(const entry___ *)NULL )
		{
			reset( false );
			Init( Path, Parent );
		}
		virtual ~entry___( void )
		{
			reset();
		}
		void Init(
			const char *Path = NULL,	// Non dupliqu� !
			const entry___ &Parent = *(const entry___ *)NULL )
		{
			_Parent = &Parent;
			_RawPath = Path;

			_Path.Init();
		}
		const str::string_ &GetPath(
			const tags_ &Tags,
			str::string_ &Path ) const
		{
			if ( !_IsPostInitialized() )
				_PostInitialize();

			return _GetPath( Tags, Path );
		}
		const str::string_ &GetPath( str::string_ &Path ) const
		{
			return GetPath( tags(), Path );
		}
	};

	struct tentry__ {
	private:
		const entry___ *_Entry;
		const tags_ *_Tags;
	protected:
		tentry__( void )
		{
			reset( false );
		}
	public:
		void reset( bso::bool__ = true )
		{
			_Entry = NULL;
			_Tags = NULL;
		}
		tentry__(
			const entry___ &Entry,
			const tags_ &Tags = *(const tags_ *)NULL )
		{
			reset( false );

			Init( Entry, Tags );
		}
		~tentry__( void )
		{
			reset();
		}
		void Init( void )
		{
			_Entry = NULL;
			_Tags = NULL;
		}
		void Init(
			const entry___ &Entry,
			const tags_ &Tags = *(const tags_ *)NULL )
		{
			_Entry = &Entry;
			_Tags = &Tags;
		}
		const str::string_ &GetPath( str::string_ &Path ) const
		{
			if ( _Tags != NULL )
				return _Entry->GetPath( *_Tags, Path );
			else
				return _Entry->GetPath( Path );
		}
	};

	class tentry___
	: public tentry__
	{
	private:
		tags _Tags;
	public:
		void reset( bso::bool__ P = true )
		{
			tentry__::reset( P );

			_Tags.reset( P );
		}
		tentry___( void )
		{
			reset( false );
		}
		tentry___(
			const entry___ &Entry,
			const str::string_ &Tag )
		{
			reset( false );

			Init( Entry, Tag );
		}
		tentry___(
			const entry___ &Entry,
			const char *Tag )
		{
			reset( false );

			Init( Entry, Tag );
		}
		~tentry___( void )
		{
			reset();
		}
		void Init( void )
		{
			_Tags.Init();

			tentry__::Init();
		}
		void Init(
			const entry___ &Entry,
			const str::string_ &Tag )
		{
			_Tags.Init();
			_Tags.Append( Tag );

			tentry__::Init( Entry, _Tags );
		}
		void Init(
			const entry___ &Entry,
			const char *Tag )
		{
			Init( Entry, str::string( Tag ) );
		}
	};

	// Nature du noeud.
	enum nature__ 
	{
		nTag,
		nAttribute,
		n_amount,
		n_Undefined
	};

	class node_ {
	public:
		struct s {
			nature__ Nature;
			row__ ParentRow;
			name_::s Name;
			value_::s Value;
			rows_::s Children;
		} &S_;
		name_ Name;
		value_ Value;
		rows_ Children;
		node_( s &S )
		: S_( S ),
		  Name( S.Name ),
		  Value( S.Value ),
		  Children( S.Children )
		{}
		void reset( bso::bool__ P = true )
		{
			S_.Nature = n_Undefined;
			S_.ParentRow = E_NIL;

			Name.reset( P );
			Value.reset( P );
			Children.reset( P );
		}
		void plug( ags::E_ASTORAGE_ &AS )
		{
			Name.plug( AS );
			Value.plug( AS );
			Children.plug( AS );
		}
		node_ &operator =( const node_ &N )
		{
			S_.Nature = N.S_.Nature;
			S_.ParentRow = N.S_.ParentRow;

			Name = N.Name;
			Value = N.Value;
			Children = N.Children;

			return *this;
		}
		void Init( void )
		{
			reset();

			Name.Init();
			Value.Init();
			Children.Init();
		}
		void Init(
			nature__ Nature,
			const name_ &Name,
			const value_ &Value,
			row__ ParentRow = E_NIL )
		{
			Init();

			S_.ParentRow = ParentRow;
			S_.Nature = Nature;

			this->Name = Name;
			this->Value = Value;

			Children.Init();
		}
		void Init(
			nature__ Nature,
			const name_ &Name,
			row__ ParentRow = E_NIL )
		{
			Init( Nature, Name, value(), ParentRow );
		}
		E_RWDISCLOSE_( row__, ParentRow )
		E_RODISCLOSE_( nature__, Nature );
	};

	typedef lstctn::E_LXCONTAINERt_( node_, row__ ) nodes_;
	E_AUTO( nodes )

	typedef ctn::E_CITEMt( node_, row__ )	buffer;

	typedef sdr::row__ cursor__;

	class registry_ {
	private:
		const node_ &_GetNode(
			row__ Row,
			buffer &Buffer ) const
		{
			Buffer.Init( Nodes );

			return Buffer( Row );
		}
		nature__ _GetNature( row__ Row ) const
		{
			buffer Buffer;

			return _GetNode( Row, Buffer ).Nature();
		}
		const name_ &_GetName(
			row__ Row,
			buffer &Buffer ) const
		{
			return _GetNode( Row, Buffer ).Name;
		}
		const value_ &_GetValue(
			row__ Row,
			buffer &Buffer ) const
		{
			return _GetNode( Row, Buffer ).Value;
		}
		row__ _Search(
			const name_ &Name,
			const rows_ &Rows,
			cursor__ &Cursor ) const;
		row__ _Search(
			const name_ &Name,
			row__ Row,
			cursor__ &Cursor ) const
		{
			buffer Buffer;

			return _Search( Name, _GetNode( Row, Buffer ).Children, Cursor );
		}
		row__ _Search(
			nature__ Nature,
			const name_ &Name,
			const rows_ &Rows,
			cursor__ &Cursor ) const;
		row__ _Search(
			nature__ Nature,
			const name_ &Name,
			row__ Row,
			cursor__ &Cursor ) const
		{
			buffer Buffer;

			return _Search( Nature, Name, _GetNode( Row, Buffer ).Children, Cursor );
		}
		row__ _SearchTag(
			const name_ &Name,
			row__ Row,
			cursor__ &Cursor ) const
		{
			return _Search( nTag, Name, Row, Cursor );
		}
		row__ _SearchTag(
			const name_ &Name,
			row__ Row ) const
		{
			cursor__ Cursor = E_NIL;

			return _Search( nTag, Name, Row, Cursor );
		}
		row__ _SearchAttribute(
			const name_ &Name,
			row__ Row,
			cursor__ &Cursor ) const
		{
			return _Search( nAttribute, Name, Row, Cursor );
		}
		row__ _SearchAttribute(
			const name_ &Name,
			row__ Row ) const
		{
			cursor__ Cursor = E_NIL;

			return _Search( nAttribute, Name, Row, Cursor );
		}
		bso::bool__ _AttributeExists(
			const name_ &Name,
			row__ Row ) const
		{
			return _SearchAttribute( Name, Row ) != E_NIL;
		}
		row__ _SearchAttribute(
			const name_ &Name,
			const value_ &Value,
			row__ Row ) const
		{
			Row = _SearchAttribute( Name, Row );

			if ( Row != E_NIL ) {
				buffer Buffer;

				if ( _GetValue( Row, Buffer ) != Value )
					Row = E_NIL;
			}

			return Row;
		}
		bso::bool__ _AttributeExists(
			const name_ &Name,
			const value_ &Value,
			row__ Row ) const
		{
			return _SearchAttribute( Name, Value, Row ) != E_NIL;
		}
		row__ _Search(
			const name_ &TagName,
			const name_ &AttributeName,
			const value_ &AttributeValue,
			row__ Row,
			cursor__ &Cursor ) const;
		row__ _Search(
			const path_item_ &Item,
			row__ Row,
			cursor__ &Cursor ) const
		{
			return _Search( Item.TagName, Item.AttributeName, Item.AttributeValue, Row, Cursor );
		}
		row__ _Search(
			const path_item_ &Item,
			row__ Row ) const
		{
			cursor__ Cursor = E_NIL;

			return _Search( Item, Row, Cursor );
		}
		row__ _Search(
			const path_ &Path,
			sdr::row__ PathRow,
			row__ Row,
			rows_ &ResultRows ) const;
		row__ _Search(
			const path_ &Path,
			row__ Row ) const;
		row__ _Search(
			const str::string_ &PathString,
			row__ Row,
			sdr::row__ *PathErrorRow = NULL ) const;
		row__ _CreateWithoutFlush(
			nature__ Nature,
			const name_ &Name,
			const value_ &Value,
			row__ Row = E_NIL )
		{
			row__ NewRow = Nodes.New();

			Nodes( NewRow ).Init( Nature, Name, Value, Row );

			return NewRow;
		}
		row__ _CreateWithFlush(
			nature__ Nature,
			const name_ &Name,
			const value_ &Value,
			row__ Row = E_NIL )
		{
			Row = _CreateWithoutFlush( Nature, Name, Value, Row );

			Nodes.Flush();

			return Row;
		}
		row__ _CreateTag(
			const name_ &Name,
			row__ Row = E_NIL )
		{
			return _CreateWithFlush( nTag, Name, value(), Row );
		}
		row__ _Add( 
			nature__ Nature,
			const name_ &Name,
			const value_ &Value,
			row__ Row )
		{
			row__ NewRow = _CreateWithoutFlush( Nature, Name, Value, Row );

			Nodes( Row ).Children.Append( NewRow );

			Nodes.Flush();

			return NewRow;
		}
		row__ _AddTag(
			const name_ &Name,
			row__ Row )
		{
			return _Add( nTag, Name, value(), Row );
		}
		row__ _AddAttribute(
			const name_ &Name,
			const value_ &Value,
			row__ Row )
		{
			return _Add( nAttribute, Name, Value, Row );
		}
		row__ _Create(
			const path_item_ &Item,
			row__ Row )
		{
			if ( Item.TagName.Amount() != 0 ) {
				Row = _AddTag( Item.TagName, Row );

				if ( Item.AttributeName.Amount() != 0 )
					_AddAttribute( Item.AttributeName, Item.AttributeValue, Row );
				else
					if ( Item.AttributeValue.Amount() != 0 )
						ERRFwk();

			} else if ( Item.AttributeName.Amount() != 0 )
				Row = _AddAttribute( Item.AttributeName, Item.AttributeValue, Row );
			else
				ERRFwk();

			return Row;
		}
		void _Delete( row__ Row );
		void _Delete( const rows_ &Rows );
		void _DumpAttributes(
			row__ Row,
			xml::writer_ &Writer ) const;
		void _DumpNode(
			row__ Row,
			xml::writer_ &Writer,
			buffer &Buffer ) const
		{
			Writer.PushTag( Buffer( Row ).Name );	// 'PopTag' correspondant fait par m�thode appelante.
			_DumpAttributes( Row, Writer );

			const value_ &Value = Buffer( Row ).Value;

			if ( Value.Amount() != 0 )
				Writer.PutValue( Value );

		}
		sdr::size__ _Dump(
			row__ Root,
			bso::bool__ RootToo,
			xml::writer_ &Writer,
			buffer &Buffer ) const;	// Retourne le nombre d'enfants.
	public:
		struct s {
			nodes_::s Nodes;
		};
		nodes_ Nodes;
		registry_( s &S )
		: Nodes( S.Nodes )
		{}
		void reset( bso::bool__ P = true )
		{
			Nodes.reset( P );
		}
		void plug( ags::E_ASTORAGE_ &AS )
		{
			Nodes.plug( AS );
		}
		registry_ &operator =( const registry_ &R )
		{
			Nodes = R.Nodes;

			return *this;
		}
		void Init( void )
		{
			Nodes.Init();
		}
		void Add(
			row__ Row,
			row__ ParentRow )
		{
			Nodes( ParentRow ).Children.Append( Row );

#ifdef RGSTRY_DBG
			if ( Nodes( Row ).ParentRow() != E_NIL )
				ERRFwk();
#endif
			Nodes( Row ).ParentRow() = ParentRow;

			Nodes.Flush();
		}
		row__ AddTag(
			const name_ &Name,
			row__ Row )
		{
			return _AddTag( Name, Row );
		}
		row__ AddAttribute(
			const name_ &Name,
			const value_ &Value,
			row__ Row )
		{
			return _AddAttribute( Name, Value, Row );
		}
		void SetValue(
			const value_ &Value,
			row__ Row,
			bso::bool__ Append )
		{
			if ( Append )
				Nodes( Row ).Value.Append( Value );
			else
				Nodes( Row ).Value.Init( Value );

			Nodes.Flush();
		}
		row__ Search(
			const path_ &Path,
			row__ Row ) const
		{
			return _Search( Path, Row );
		}
		row__ Search(
			const str::string_ &PathString,
			row__ Row,
			sdr::row__ *PathErrorRow = NULL ) const
		{
			return _Search( PathString, Row, PathErrorRow );
		}
		row__ Create(
			const path_ &Path,
			row__ Row );
		row__ Create(
			const str::string_ &PathString,
			row__ Row,
			sdr::row__ *PathErrorRow = NULL );
		nature__ GetNature( row__ Row ) const
		{
			return _GetNature( Row );
		}
		const value_ &GetValue(
			const path_ &Path,
			row__ Row,
			bso::bool__ *Missing,
			buffer &Buffer ) const;	// Nota : ne met 'Missing' � 'true' que lorque 'Path' n'existe pas. Si 'Missing' est � 'true', aucune action n'est r�alis�e.
		bso::bool__ GetValue(
			const path_ &Path,
			row__ Row,
			value_ &Value ) const
		{
			buffer Buffer;
			bso::bool__ Missing = false;

			Value.Append( GetValue( Path, Row, &Missing, Buffer ) );

			return !Missing;
		}
		const value_ &GetValue(
			const str::string_ &PathString,
			row__ Row,
			bso::bool__ *Missing,
			buffer &Buffer,
			sdr::row__ *PathErrorRow = NULL ) const;	// Nota : ne met 'Missing' � 'true' que lorque 'Path' n'existe pas. Si 'Missing' est � 'true', aucune action n'est r�alis�e.
		bso::bool__ GetValue(
			const str::string_ &PathString,
			row__ Row,
			value_ &Value ) const
		{
			buffer Buffer;
			bso::bool__ Missing = false;

			Value.Append( GetValue( PathString, Row, &Missing, Buffer ) );

			return !Missing;
		}
		const value_ &GetValue(
			const str::string_ &PathString,
			row__ Row,
			buffer &Buffer ) const
		{
			bso::bool__ Missing = false;

			const value_ &Value = GetValue( PathString, Row, &Missing, Buffer );

			if ( Missing )
				ERRFwk();

			return Value;
		}
		const value_ &GetValue(
			const tentry__ &Entry,
			row__ Row,
			bso::bool__ *Missing,
			buffer &Buffer,
			sdr::row__ *PathErrorRow = NULL ) const;	// Nota : ne met 'Missing' � 'true' que lorque 'Path' n'existe pas. Si 'Missing' est � 'true', aucune action n'est r�alis�e.
		bso::bool__ GetValue(
			const tentry__ &Entry,
			row__ Row,
			value_ &Value ) const
		{
			buffer Buffer;
			bso::bool__ Missing = false;

			Value.Append( GetValue( Entry, Row, &Missing, Buffer ) );

			return !Missing;
		}
#if 0
		const value_ &GetValue(
			const entry___ &Entry,
			const tags_ &Tags,
			row__ Row,
			bso::bool__ *Missing,
			buffer &Buffer,
			sdr::row__ *PathErrorRow = NULL ) const;	// Nota : ne met 'Missing' � 'true' que lorque 'Path' n'existe pas. Si 'Missing' est � 'true', aucune action n'est r�alis�e.
#endif
		const value_ &GetValue(
			const tentry__ &Entry,
			row__ Row,
			bso::bool__ *Missing,
			str::string_ &Value,
			sdr::row__ *PathErrorRow = NULL ) const	// Nota : ne met 'Missing' � 'true' que lorque 'Path' n'existe pas. Si 'Missing' est � 'true', aucune action n'est r�alis�e.
		{
			buffer Buffer;

			Value.Append( GetValue( Entry, Row, Missing, Buffer, PathErrorRow ) );

			return Value;
		}
		bso::bool__ GetValues(
			const path_ &Path,
			row__ Row,
			values_ &Values ) const;
		bso::bool__ GetValues(
			const str::string_ &PathString,
			row__ Row,
			values_ &Values,
			sdr::row__ *PathErrorRow = NULL ) const;
		bso::bool__ GetValues(
			const tentry__ &Entry,
			row__ Row,
			values_ &Values,
			sdr::row__ *PathErrorRow = NULL ) const;
#if 0
		bso::bool__ GetValues(
			const entry___ &Entry,
			const tags_ &Tags,
			row__ Row,
			values_ &Values,
			sdr::row__ *PathErrorRow = NULL ) const;
#endif
		row__ SetValue(
			const path_ &Path,
			const value_ &Value,
			row__ Row )
		{
			Row = Create( Path, Row );

			SetValue( Value, Row, false );

			return Row;
		}
		row__ SetValue(
			const str::string_ &PathString,
			const value_ &Value,
			row__ Row,
			sdr::row__ *PathErrorRow = NULL );
		row__ GetParentRow( row__ Row ) const
		{
			buffer Buffer;

			return _GetNode( Row, Buffer ).ParentRow();
		}
		const name_ &GetName(
			row__ Row,
			buffer &Buffer ) const
		{
			return _GetName( Row, Buffer );
		}
		const value_ &GetValue(
			row__ Row,
			buffer &Buffer ) const
		{
			return _GetValue( Row, Buffer );
		}
		const str::string_ &GetCompleteName(
			row__ Row,
			str::string_ &Name,
			const char *Separator = ":" ) const;
		row__ SearchTag(
			const name_ &Name,
			row__ Row ) const
		{
			return _SearchTag( Name, Row );
		}
		row__ SearchAttribute( 
			const name_ &Name,
			row__ Row ) const
		{
			return _SearchAttribute( Name, Row );
		}
		bso::bool__ AttributeExists(
			const name_ &Name,
			row__ Row ) const
		{
			return _AttributeExists( Name, Row );
		}
		const value_ &GetAttributeValue(
			const name_ &Name,
			row__ Row,
			buffer &Buffer ) const
		{
			row__ ResultRow = _SearchAttribute( Name, Row );

#ifdef RGSTRY_DBG
			if ( Row == E_NIL )
				ERRFwk();
#endif
			return _GetValue( ResultRow, Buffer );
		}
		void Delete( row__ Row )
		{
			_Delete( Row );
		}
		bso::bool__ Delete(
			const path_ &Path,
			row__ Row )
		{
			row__ ResultRow = _Search( Path, Row );

			if ( ResultRow != E_NIL ) {
				_Delete( ResultRow );
				return true;
			} else
				return false;
		}
		bso::bool__ Delete(
			const str::string_ &PathString,
			row__ Row,
			sdr::row__ *PathErrorRow = NULL );
		row__ CreateRegistry( const name_ &Name )
		{
			return _CreateTag( Name );
		}
		bso::bool__ Exists(
			const path_ &Path,
			row__ Row ) const
		{
			return _Search( Path, Row ) != E_NIL;
		}
		bso::bool__ Exists(
			const str::string_ &PathString,
			row__ Row,
			sdr::row__ *PathErrorRow = NULL ) const;
		sdr::size__ Dump(
			row__ Root,
			bso::bool__ RootToo,
			xml::writer_ &Writer ) const;	// Retourne le nombre d'enfants.
		sdr::size__ Dump(
			row__ Root,
			bso::bool__ RootToo,
			xml::outfit__ Outfit,
			xml::encoding__ Encoding,
			txf::text_oflow__ &Flow ) const;	// Retourne le nombre d'enfants.
	};

	E_AUTO( registry )

# if 0
	struct error_details_
	{
	public:
		struct s {
			xml::coord__ Coord;
			sdr::row__ PathErrorRow;
			xpp::status__ XPPStatus;
			str::string_::s FileName;
		} &S_;
		str::string_ FileName;
		error_details_( s &S )
		: S_( S ),
		  FileName( S.FileName )
		{}
		void reset( bso::bool__ P = true )
		{
			S_.Coord.reset( P );
			S_.PathErrorRow = E_NIL;
			S_.XPPStatus = xpp::s_Undefined;

			S_.Coord.reset( P );
			FileName.reset( P );
		}
		void plug( sdr::E_MEMORY_DRIVER__ &MD )
		{
			FileName.plug( MD );
		}
		void plug( mmm::E_MULTIMEMORY_ &MM )
		{
			FileName.plug( MM );
		}
		error_details_ &operator =( const error_details_ &ED )
		{
			S_.Coord = ED.S_.Coord;
			S_.PathErrorRow = ED.S_.PathErrorRow;
			S_.XPPStatus = ED.S_.XPPStatus;

			FileName = ED.FileName;

			return *this;
		}
		void Init( void )
		{
			reset();

			S_.Coord.Init();
			FileName.Init();
		}
		E_RODISCLOSE_( xml::coord__, Coord );
		E_RODISCLOSE_( sdr::row__, PathErrorRow );
		E_RODISCLOSE_( xpp::status__, XPPStatus );
	};

	E_AUTO( error_details );
#endif

	row__ Parse(
		xtf::extended_text_iflow__ &XFlow,
		const xpp::criterions___ &Criterions,
		registry_ &Registry,
		row__ &Root,	// Peut �tre = 'E_NIL', auquel cas une nouvelle 'registry' est cr�ee dont la racine est stock�e dans ce param�tre.
		xpp::context___ &Context );

	inline row__ Parse(
		xtf::extended_text_iflow__ &XFlow,
		const xpp::criterions___ &Criterions,
		registry_ &Registry,
		row__ &Root	) // Peut �tre = 'E_NIL', auquel cas une nouvelle 'registry' est cr�ee dont la racine est stock�e dans ce param�tre.
	{
		row__ Row = E_NIL;
	ERRProlog
		xpp::context___ Context;
	ERRBegin
		Context.Init();

		Row = Parse( XFlow, Criterions, Registry, Root, Context );
	ERRErr
	ERREnd
	ERREpilog
		return Row;
	}

	enum status__ {
		sOK,
		sUnableToOpenFile,
		sParseError,	// Pas d'entr�e dans le fichier de traduction : ce sont les traductions du 'parser__' qui sont utilis�s.
		sUnableToFindRootPath,
		sRootPathError,
		s_amount,
		s_Undefined
	};

	const char *GetLabel( status__ Status );

	typedef xpp::context___ _context___;

	struct context___
	: public _context___
	{
		status__ Status;
		sdr::row__ PathErrorRow;
		void reset( bso::bool__ P = true )
		{
			_context___::reset( P );

			Status = s_Undefined;
			PathErrorRow = E_NIL;
		}
		context___( void )
		{
			reset( false );

			Init();
		}
		~context___( void )
		{
			reset();
		}
		void Init( void )
		{
			_context___::Init();

			Status = s_Undefined;
			PathErrorRow = E_NIL;
		}
	};


	void GetMeaning(
		const context___ &Context,
		lcl::meaning_ &Meaning );

	status__ FillRegistry(
		xtf::extended_text_iflow__ &XFlow,
		const xpp::criterions___ &Criterions,
		const char *RootPath,
		rgstry::registry_ &Registry,
		rgstry::row__ &RegistryRoot,
		context___ &Context );

	inline status__ FillRegistry(
		xtf::extended_text_iflow__ &XFlow,
		const xpp::criterions___ &Criterions,
		const char *RootPath,
		rgstry::registry_ &Registry,
		rgstry::row__ &RegistryRoot )
	{
		status__ Status = s_Undefined;
	ERRProlog
		context___ Context;
	ERRBegin
		Context.Init();

		Status = FillRegistry( XFlow, Criterions, RootPath, Registry, RegistryRoot, Context );
	ERRErr
	ERREnd
	ERREpilog
		return Status;
	}

	status__ FillRegistry(
		const fnm::name___ &FileName,
		const xpp::criterions___ &Criterions,
		const char *RootPath,
		rgstry::registry_ &Registry,
		rgstry::row__ &RegistryRoot,
		context___ &Context );

	inline status__ FillRegistry(
		const fnm::name___ &FileName,
		const xpp::criterions___ &Criterions,
		const char *RootPath,
		rgstry::registry_ &Registry,
		rgstry::row__ &RegistryRoot )
	{
		status__ Status = s_Undefined;
	ERRProlog
		context___ Context;
	ERRBegin
		Context.Init();

		Status = FillRegistry( FileName, Criterions, RootPath, Registry, RegistryRoot, Context );
	ERRErr
	ERREnd
	ERREpilog
		return Status;
	}

# if 1	// D�pr�ci�, destin� � dispara�tre. Utiliser 'multi_level_registry_'.
	class overloaded_registry___
	{
	public:
		struct global {
			const registry_ *Registry;
			row__ Root;
		} Global;
		struct local {
			registry_ *Registry;
			row__ Root;
		} Local;
		void reset( bso::bool__ P = true )
		{
			Global.Registry = NULL;
			Global.Root = E_NIL;

			Local.Registry = NULL;
			Local.Root = E_NIL;
		}
		overloaded_registry___( void )
		{
			reset( false );
		}
		~overloaded_registry___( void )
		{
			reset();
		}
		row__ Init(
			const registry_ &Global,
			row__ Root,
			registry_ &Local,	// 'Global' et 'Local' peuvent �tre identiques.
			row__ LocalRoot )	// Si �gal � E_NIL et 'Local' != 'NULL', est cr�e et retourn�.
		{
			buffer Buffer;

			this->Global.Registry = &Global;
			this->Global.Root = Root;

			this->Local.Registry = &Local;

			if ( ( &Local != NULL ) && ( LocalRoot == E_NIL ) )
				LocalRoot = Local.CreateRegistry( this->Global.Registry->GetName( Root, Buffer ) );

			return this->Local.Root = LocalRoot;

		}
		void Init(
			const registry_ &Global,
			row__ Root )
		{
			Init( Global, Root, *(registry_ *)NULL, E_NIL );
		}
		row__ SetLocal(
			registry_ &Registry,	// Si == 'NULL', on prend le 'Global'.
			row__ Root )	// Si == 'E_NIL' est cr�e et retourn�.
		{
			if ( ( &Global.Registry == NULL ) || ( Global.Root == E_NIL ) )
				ERRFwk();

			if ( &Registry == NULL )
				ERRFwk();

			Local.Registry = &Registry;

			if ( Root == E_NIL ) {
				buffer Buffer;

				Root = Registry.CreateRegistry( this->Global.Registry->GetName( Global.Root, Buffer ) );
			}

			return Local.Root = Root;
		}
		const value_ &GetValue(
			const str::string_ &PathString,
			bso::bool__ *Missing,
			buffer &Buffer,
			sdr::row__ *PathErrorRow = NULL  ) const;	// Nota : ne met 'Missing' � 'true' que lorque 'Path' n'existe pas. Si 'Missing' est � 'true', aucune action n'est r�alis�e.
		bso::bool__ GetValue(
			const str::string_ &PathString,
			value_ &Value ) const
		{
			buffer Buffer;
			bso::bool__ Missing = false;

			Value.Append( GetValue( PathString, &Missing, Buffer ) );

			return !Missing;
		}
		bso::bool__ GetValues(
			const str::string_ &PathString,
			values_ &Values,
			sdr::row__ *PathErrorRow = NULL ) const;
		void SetValue(
			const str::string_ &PathString,
			const value_ &Value,
			sdr::row__ *PathErrorRow = NULL )
		{
			Local.Registry->SetValue( PathString, Value, Local.Root, PathErrorRow );
		}
		void Delete( row__ Row )
		{
			Local.Registry->Delete( Row );
		}
		bso::bool__ Exists(
			const str::string_ &Path,
			sdr::row__ *PathErrorRow = NULL ) const;
		void Search(
			const path_ &Path,
			row__ &GlobalRow,
			row__ &LocalRow ) const
		{
			GlobalRow = Global.Registry->Search( Path, Global.Root );
			LocalRow = Local.Registry->Search( Path, Local.Root );
		}
		void Search(
			const str::string_ &Path,
			row__ &GlobalRow,
			row__ &LocalRow,
			sdr::row__ *PathErrorRow = NULL ) const;
 	};

	class overloaded_unique_registry___	// La base de registre de base et locale sont la m�me.
	: public overloaded_registry___
	{
	private:
		row__ _LocalRoot;
	public:
		void reset( bso::bool__ P = true )
		{
			if ( P ) {
				if ( _LocalRoot != E_NIL )
					overloaded_registry___::Delete( _LocalRoot );
			}

			overloaded_registry___::reset( P );
			_LocalRoot = E_NIL;
		}
		overloaded_unique_registry___( void )
		{
			reset( false );
		}
		virtual ~overloaded_unique_registry___( void )
		{
			reset();
		}
		row__ Init(
			registry_ &Global,
			row__ Root )	// Si == 'E_NIL', est cr�e et retourn�.
		{
			reset();

			if ( Root == E_NIL )
				Root = Global.CreateRegistry( name() );

			_LocalRoot = overloaded_registry___::Init( Global, Root, *(registry_ *)NULL, E_NIL );

			return Root;
		}
		row__ Init(
			registry_ &Global,
			row__ Root,
			row__ LocalRoot ) // Si �gal � E_NIL, est cr�e et retourn�.
		{
			reset();

			if ( LocalRoot == E_NIL )
				LocalRoot = _LocalRoot = overloaded_registry___::Init( Global, Root, Global, LocalRoot );
			else
				overloaded_registry___::Init( Global, Root, Global, LocalRoot );

			return LocalRoot;
		}
		row__ SetLocal(
			registry_ &Registry,
			row__ Root )	// Si 'Root' == 'E_NIL'
		{
			if ( Root == E_NIL )
				Root = _LocalRoot = overloaded_registry___::SetLocal( Registry, Root );
			else
				overloaded_registry___::SetLocal( Registry, Root );

			return Root;
		}
	};
# endif
	E_ROW( level__ );
#	define RGSTRY_UNDEFINED_LEVEL	E_NIL
	E_CDEF( level__, UndefinedLevel, E_NIL );

	struct _entry__ {
		row__ Root;
		const registry_ *Registry;
		void reset( bso::bool__ = true )
		{
			Root = E_NIL;
			Registry = NULL;
		}
		void Init(
			row__ Root = E_NIL,
			const registry_ &Registry = *(const registry_ *)NULL )
		{
			this->Root = Root;
			this->Registry = &Registry;
		}
		_entry__(
			row__ Root = E_NIL,
			const registry_ &Registry = *(const registry_ *)NULL )
		{
			Init( Root, Registry );
		}
	};

	typedef stk::E_BSTACKt_( _entry__, level__ ) _entries_;
	typedef stk::E_BSTACKt_( time_t, level__ ) _timestamps_;

	// Registre multi-niveau
	class multi_level_registry_
	{
	private:
		void _Touch( level__ Level )
		{
			TimeStamps.Store( time( NULL ), Level );
		}
		level__ _RawCreateLevel( void )
		{
			level__ Level = TimeStamps.Push( 0 );

			if ( Entries.Push( _entry__() ) != Level )
				ERRFwk();

			_Touch( Level );

			return Level;
		}
		level__ _RawPushLevel( const _entry__ &Entry )
		{
			level__ Level = RGSTRY_UNDEFINED_LEVEL;

			Entries.Store( Entry, Level = _RawCreateLevel() );

			return Level;
		}
		const _entry__ _GetEntry( level__ Level ) const
		{
			return Entries( Level );
		}
		const registry_ &_GetRegistry( level__ Level ) const
		{
			_entry__ Entry = _GetEntry( Level );

			if ( Entry.Registry == NULL )
				return EmbeddedRegistry;
			else
				return *Entry.Registry;
		}
		registry_ &_GetRegistry( level__ Level )
		{
			_entry__ Entry = _GetEntry( Level );

			if ( Entry.Registry != NULL )
				ERRFwk();

			return EmbeddedRegistry;
		}
		row__ _GetRoot( level__ Level ) const
		{
			return _GetEntry( Level ).Root;
		}
	public:
		struct s {
			registry_::s EmbeddedRegistry;
			_entries_::s Entries;
			_timestamps_::s TimeStamps;
		};
		registry_ EmbeddedRegistry;
		_entries_ Entries;
		_timestamps_ TimeStamps;
		multi_level_registry_( s &S )
		: EmbeddedRegistry( S.EmbeddedRegistry ),
		  Entries( S.Entries ),
		  TimeStamps( S.TimeStamps )
		{}
		void reset( bso::bool__ P = true )
		{
			EmbeddedRegistry.reset( P );
			Entries.reset( P );
			TimeStamps.reset( P );
		}
		void plug( ags::E_ASTORAGE_ &AS )
		{
			EmbeddedRegistry.plug( AS );
			Entries.plug( AS );
			TimeStamps.plug( AS );
		}
		multi_level_registry_ &operator =( const multi_level_registry_ &MLR )
		{
			EmbeddedRegistry = MLR.EmbeddedRegistry;
			Entries = MLR.Entries;
			TimeStamps = MLR.TimeStamps;

			return *this;
		}
		void Init( void )
		{
			EmbeddedRegistry.Init();
			Entries.Init();
			TimeStamps.Init();
		}
		E_NAVt( Entries., level__ );
		const registry_ &GetRegistry( level__ Level ) const
		{
			return _GetRegistry( Level );
		}
		registry_ &GetRegistry( level__ Level )
		{
			return _GetRegistry( Level );
		}
		row__ GetRoot( level__ Level ) const
		{
			return _GetRoot( Level );
		}
		void SetRoot(
			level__ Level,
			row__ Root )
		{
			_entry__ Entry = Entries( Level );

			Entry.Root = Root;

			Entries.Store( Entry, Level );
		}
		level__ PushImportedLevel(
			const registry_ &Registry,
			row__ Root )
		{
			return _RawPushLevel( _entry__( Root, Registry ) );
		}
		level__ PushEmbeddedLevel( const name_ &Name = name() )
		{
			return _RawPushLevel( _entry__( EmbeddedRegistry.CreateRegistry( Name ) ) );
		}
		void Push( const multi_level_registry_ &Registry )
		{
			level__ Level = Registry.First();

			while ( Level != RGSTRY_UNDEFINED_LEVEL ) {
				PushImportedLevel( Registry.GetRegistry( Level ), Registry.GetRoot( Level ) );

				Level = Registry.Next( Level );
			}
		}
		void Erase( level__ Level );
		level__ Pop( void )
		{
			level__ Level = Entries.Last();

			if ( Entries.Top().Registry == NULL )
				EmbeddedRegistry.Delete( Entries.Top().Root );

			Entries.Pop();
			TimeStamps.Pop();

			return Level;
		}
		level__ TopLevel( void ) const
		{
			return Entries.Last();
		}
		void Create(
			level__ Level,
			const str::string_ &Path )
		{
			_GetRegistry( Level ).Create( Path, _GetRoot( Level ) );
		}
		const value_ &GetValue(
			level__ Level,
			const path_ &Path,
			bso::bool__ *Missing,
			buffer &Buffer ) const	// Nota : ne met 'Missing' � 'true' que lorque 'Path' n'existe pas. Si 'Missing' est � 'true', aucune action n'est r�alis�e.
		{
			return _GetRegistry( Level ).GetValue( Path, _GetRoot( Level ), Missing, Buffer );
		}
		const value_ &GetValue(
			level__ Level,
			const str::string_ &PathString,
			bso::bool__ *Missing,
			buffer &Buffer,
			sdr::row__ *PathErrorRow = NULL  ) const	// Nota : ne met 'Missing' � 'true' que lorque 'Path' n'existe pas. Si 'Missing' est � 'true', aucune action n'est r�alis�e.
		{
			return _GetRegistry( Level ).GetValue( PathString, _GetRoot( Level ), Missing, Buffer, PathErrorRow );
		}
		const value_ &GetValue(
			const str::string_ &PathString,
			bso::bool__ *Missing,
			buffer &Buffer,
			sdr::row__ *PathErrorRow = NULL  ) const;	// Nota : ne met 'Missing' � 'true' que lorque 'Path' n'existe pas. Si 'Missing' est � 'true', aucune action n'est r�alis�e.
		bso::bool__ GetValue(
			level__ Level,
			const path_ &Path,
			value_ &Value ) const
		{
			return _GetRegistry( Level ).GetValue( Path, _GetRoot( Level ), Value );
		}
		bso::bool__ GetValue(
			level__ Level,
			const str::string_ &PathString,
			value_ &Value,
			sdr::row__ *PathErrorRow = NULL ) const
		{
			buffer Buffer;
			bso::bool__ Missing = false;

			Value.Append( GetValue( Level, PathString, &Missing, Buffer, PathErrorRow ) );

			return !Missing;
		}
		bso::bool__ GetValue(
			const str::string_ &PathString,
			value_ &Value,
			sdr::row__ *PathErrorRow = NULL ) const;
		bso::bool__ GetValue(
			const char *PathString,
			value_ &Value,
			sdr::row__ *PathErrorRow = NULL ) const
		{
			return GetValue( str::string( PathString ), Value, PathErrorRow );
		}
		bso::bool__ GetValue(
			const tentry__ &Entry,
			str::string_ &Value,
			sdr::row__ *PathErrorRow = NULL ) const;
		bso::bool__ GetValue(
			level__ Level,
			const tentry__ &Entry,
			str::string_ &Value,
			sdr::row__ *PathErrorRow = NULL ) const;
#if 0
		bso::bool__ GetValue(
			const entry___ &Entry,
			const tags_ &Tags,
			str::string_ &Value,
			sdr::row__ *PathErrorRow = NULL ) const;
		bso::bool__ GetValue(
			const entry___ &Entry,
			str::string_ &Value,
			sdr::row__ *PathErrorRow = NULL ) const;
#endif
		bso::bool__ GetValues(
			level__ Level,
			const path_ &Path,
			values_ &Values ) const
		{
			return _GetRegistry( Level ).GetValues( Path, _GetRoot( Level ), Values );
		}
		bso::bool__ GetValues(
			level__ Level,
			const str::string_ &PathString,
			values_ &Values,
			sdr::row__ *PathErrorRow = NULL ) const
		{
			return _GetRegistry( Level ).GetValues( PathString, _GetRoot( Level ), Values, PathErrorRow );
		}
		bso::bool__ GetValues(
			const str::string_ &PathString,
			values_ &Values,
			sdr::row__ *PathErrorRow = NULL ) const;
		bso::bool__ GetValues(
			const char *PathString,
			values_ &Values,
			sdr::row__ *PathErrorRow = NULL ) const
		{
			return GetValues( str::string( PathString ), Values, PathErrorRow );
		}
		bso::bool__ GetValues(
			const tentry__ &Entry,
			values_ &Values,
			sdr::row__ *PathErrorRow = NULL ) const;
		void SetValue(
			level__ Level,
			const str::string_ &PathString,
			const value_ &Value,
			sdr::row__ *PathErrorRow = NULL )
		{
			_GetRegistry( Level ).SetValue( PathString, Value, _GetRoot( Level ), PathErrorRow );

			_Touch( Level );
		}
		bso::bool__ SetValue(
			const str::string_ &PathString,
			const value_ &Value,
			sdr::row__ *PathErrorRow = NULL );	// Retourne 'false' si 'PathString' a d�j� la valeur 'Value', 'true' sinon.
		bso::bool__ SetValue(
			const tentry__ &Entry,
			const value_ &Value,
			sdr::row__ *PathErrorRow = NULL );	// Retourne 'false' si 'PathString' a d�j� la valeur 'Value', 'true' sinon.
#if 0
		bso::bool__ SetValue(
			const entry___ &Entry,
			const tags_ &Tags,
			const value_ &Value,
			sdr::row__ *PathErrorRow = NULL );	// Retourne 'false' si 'PathString' a d�j� la valeur 'Value', 'true' sinon.
		bso::bool__ SetValue(
			const entry___ &Entry,
			const value_ &Value,
			sdr::row__ *PathErrorRow = NULL );	// Retourne 'false' si 'PathString' a d�j� la valeur 'Value', 'true' sinon.
#endif
		bso::bool__ Delete(
			const path_ &Path,
			level__ Level )
		{
			if ( _GetRegistry( Level ).Delete( Path, _GetRoot( Level ) ) ) {
				_Touch( Level );
				return true;
			} else
				return false;
		}
		bso::bool__ Delete( 
			const str::string_ &PathString,
			level__ Level,
			sdr::row__ *PathErrorRow = NULL )	// Retourne 'false' si 'PathString' a d�j� la valeur 'Value', 'true' sinon.
		{
			if ( _GetRegistry( Level ).Delete( PathString, _GetRoot( Level ), PathErrorRow ) ) {
				_Touch( Level );
				return true;
			} else
				return false;
		}
		bso::bool__ Delete( 
			const char *PathString,
			level__ Level,
			sdr::row__ *PathErrorRow = NULL )	// Retourne 'false' si 'PathString' a d�j� la valeur 'Value', 'true' sinon.
		{
			return Delete( str::string( PathString ), Level, PathErrorRow );
		}
		bso::bool__ Delete(
			const str::string_ &PathString,
			sdr::row__ *PathErrorRow = NULL );	// Retourne 'false' si 'PathString' a d�j� la valeur 'Value', 'true' sinon.
		bso::bool__ Delete(
			const char *PathString,
			sdr::row__ *PathErrorRow = NULL )	// Retourne 'false' si 'PathString' a d�j� la valeur 'Value', 'true' sinon.
		{
			return Delete( str::string( PathString ), PathErrorRow );
		}
		bso::bool__ MoveTo(
			const str::string_ &Path,
			level__ Level );
		bso::bool__ MoveTo(
			const char *Path,
			level__ Level )
		{
			return MoveTo( str::string( Path ), Level );
		}
		row__ Search(
			level__ Level,
			const path_ &Path ) const
		{
			return _GetRegistry( Level ).Search( Path, _GetRoot( Level ) );
		}
		row__ Search(
			level__ Level,
			const str::string_ &PathString,
			sdr::row__ *PathErrorRow = NULL ) const
		{
			return _GetRegistry( Level ).Search( PathString, _GetRoot( Level ), PathErrorRow );
		}
		row__ Search(
			const str::string_ &PathString,
			level__ &Level,	// Valeur retourn�e != 'E_NIL', contient le 'level' de la registry contenant l'entr�e.
			sdr::row__ *PathErrorRow = NULL ) const;
		row__ Search(
			const tentry__ &Entry,
			level__ &Level,	// Valeur retourn�e != 'E_NIL', contient le 'level' de la registry contenant l'entr�e.
			sdr::row__ *PathErrorRow = NULL ) const;
		bso::bool__ Exists(
			level__ Level,
			const path_ &Path ) const
		{
			return Search( Level, Path ) != E_NIL;
		}
		bso::bool__ Exists(
			level__ Level,
			const str::string_ &PathString,
			sdr::row__ *PathErrorRow = NULL ) const
		{
			return Search( Level, PathString, PathErrorRow ) != E_NIL;
		}
		bso::bool__ Exists(
			const str::string_ &PathString,
			sdr::row__ *PathErrorRow = NULL ) const
		{
			level__ Dummy = E_NIL;
			return Search( PathString, Dummy, PathErrorRow ) != E_NIL;
		}
		bso::bool__ Exists(
			const tentry__ &Entry,
			sdr::row__ *PathErrorRow = NULL ) const
		{
			level__ Dummy = E_NIL;
			return Search( Entry, Dummy, PathErrorRow ) != E_NIL;
		}
		status__ Fill(
			level__ Level,
			xtf::extended_text_iflow__ &XFlow,
			const xpp::criterions___ &Criterions,
			const char *RootPath,
			context___ &Context )
		{
			status__ Status = s_Undefined;
			row__ Root = _GetRoot( Level );
			
			Status = FillRegistry( XFlow, Criterions, RootPath, _GetRegistry( Level ), Root, Context ); 

			Entries.Store( _entry__( Root ), Level );

			_Touch( Level );

			return Status;
		}
		status__ Fill(
			level__ Level,
			xtf::extended_text_iflow__ &XFlow,
			const xpp::criterions___ &Criterions,
			const char *RootPath )
		{
			status__ Status = s_Undefined;
			row__ Root = _GetRoot( Level );
			
			Status = FillRegistry( XFlow, Criterions, RootPath, _GetRegistry( Level ), Root ); 

			Entries.Store( _entry__( Root ), Level );

			_Touch( Level );

			return Status;
		}
		status__ Fill(
			level__ Level,
			const fnm::name___ &FileName,
			const xpp::criterions___ &Criterions,
			const char *RootPath,
			context___ &Context )
		{
			status__ Status = s_Undefined;
			row__ Root = _GetRoot( Level );
			
			Status = FillRegistry( FileName, Criterions, RootPath, _GetRegistry( Level ), Root, Context ); 

			Entries.Store( _entry__( Root ), Level );

			_Touch( Level );

			return Status;
		}
		status__ Fill(
			level__ Level,
			const fnm::name___ &FileName,
			const xpp::criterions___ &Criterions,
			const char *RootPath )
		{
			status__ Status = s_Undefined;
			row__ Root = _GetRoot( Level );
			
			Status = FillRegistry( FileName, Criterions, RootPath, _GetRegistry( Level ), Root ); 

			Entries.Store( _entry__( Root ), Level );

			_Touch( Level );

			return Status;
		}
		sdr::size__ Dump(
			level__ Level,
			row__ Node,	// Si == 'E_NIL', on part de la racine.
			bso::bool__ NodeToo,
			xml::writer_ &Writer ) const
		{
			return _GetRegistry( Level ).Dump( Node == E_NIL ? _GetRoot( Level ) : Node, NodeToo, Writer );
		}
		sdr::size__ Dump(
			level__ Level,
			row__ Node,	// Si == 'E_NIL', on part de la racine.
			bso::bool__ NodeToo,
			xml::outfit__ Outfit,
			xml::encoding__ Encoding,
			txf::text_oflow__ &TFlow ) const
		{
			return _GetRegistry( Level ).Dump( Node == E_NIL ? _GetRoot( Level ) : Node, NodeToo, Outfit, Encoding, TFlow );
		}
		time_t TimeStamp( level__ Level ) const
		{
			return TimeStamps( Level );
		}
	};

	E_AUTO( multi_level_registry )

	inline str::uint__ _GetUnsigned(
		const str::string_ &RawValue,
		str::uint__ Default,
		bso::bool__ *Error,
		str::uint__ Min,
		str::uint__ Max )
	{
		str::uint__ Value = Default;
		sdr::row__ LocalError = E_NIL;

		Value = str::_UIntConversion( RawValue, 0, &LocalError, str::bAuto, Max );

		if ( ( LocalError != E_NIL ) || ( Value < Min ) ) {

			Value = Default;

			if ( Error != NULL )
				*Error = true;
			else
				ERRDta();
		}

		return Value;
	}

	template <typename registry, typename path> inline str::uint__ _GetUnsigned(
		const registry &Registry,
		const path &Path,
		str::uint__ Default,
		bso::bool__ *Error,
		str::uint__ Min,
		str::uint__ Max )
	{
		str::uint__ Value = Default;
	ERRProlog
		str::string RawValue;
		sdr::row__ PathError = E_NIL;
		bso::bool__ ConversionError = false;
	ERRBegin
		RawValue.Init();

		if ( Registry.GetValue( Path, RawValue, &PathError ) )
			Value = _GetUnsigned( RawValue, Default, &ConversionError, Min, Max );

		if ( ( PathError != E_NIL ) || ConversionError ) {

			Value = Default;

			if ( Error != NULL )
				*Error = true;
			else
				ERRDta();
		}
	ERRErr
	ERREnd
	ERREpilog
		return Value;
	}

	template <typename registry, typename path> inline str::sint__ _GetSigned(
		const registry &Registry,
		const path &Path,
		str::sint__ Default,
		bso::bool__ *Error,
		str::sint__ Min,
		str::sint__ Max )
	{
		str::sint__ Value = Default;
	ERRProlog
		str::string RawValue;
		sdr::row__ GenericError = E_NIL;
	ERRBegin
		RawValue.Init();

		if ( Registry.GetValue( Path, RawValue, &GenericError ) )
			Value = str::_SIntConversion( RawValue, 0, &GenericError, str::bAuto, Min, Max );

		if ( ( GenericError != E_NIL ) ) {

			Value = Default;

			if ( Error != NULL )
				*Error = true;
			else
				ERRDta();
		}

	ERRErr
	ERREnd
	ERREpilog
		return Value;
	}


#ifdef _M
#	define RGSRTY__M_BACKUP	_M
#endif

#define _M( name, type, min, max )\
	template <typename registry, typename path> inline type Get##name(\
		const registry &Registry,\
		const path &Path,\
		type Default,\
		bso::bool__ *Error = NULL,\
		type Min = min,\
		type Max = max )\
	{\
		return (type)_GetUnsigned( Registry, Path, Default, Error, Min, Max );\
	}

	_M( UInt, bso::uint__, BSO_UINT_MIN, BSO_UINT_MAX )
#ifdef BSO__64BITS_ENABLED
	_M( U64, bso::u64__, BSO_U64_MIN, BSO_U64_MAX )
#endif
	_M( U32, bso::u32__, BSO_U32_MIN, BSO_U32_MAX )
	_M( U16, bso::u16__, BSO_U16_MIN, BSO_U16_MAX )
	_M( U8, bso::u8__, BSO_U8_MIN, BSO_U8_MAX )

# undef _M

# ifdef RGSRTY__M_BACKUP
#  define _M RGSRTY__M_BACKUP
# endif


#ifdef _M
#	define RGSRTY__M_BACKUP	_M
#endif

#define _M( name, type, min, max )\
	template <typename registry, typename path> inline type Get##name(\
		const registry &Registry,\
		const path &Path,\
		type Default,\
		bso::bool__ *Error = NULL,\
		type Min = min,\
		type Max = max )\
	{\
		return (type)_GetSigned( Registry, Path, Default, Error, Min, Max );\
	}

	_M( Int, bso::sint__, BSO_SINT_MIN, BSO_SINT_MAX )
#ifdef BSO__64BITS_ENABLED
	_M( S64, bso::s64__, BSO_S64_MIN, BSO_S64_MAX )
#endif
	_M( S32, bso::s32__, BSO_S32_MIN, BSO_S32_MAX )
	_M( S16, bso::s16__, BSO_S16_MIN, BSO_S16_MAX )
	_M( SB, bso::s8__, BSO_S8_MIN, BSO_S8_MAX )


# undef _M

# ifdef RGSRTY__M_BACKUP
# define _M RGSRTY__M_BACKUP
# endif

}

				  /********************************************/
				  /* do not modify anything belove this limit */
				  /*			  unless specified		   	  */
/******************************************************************************/

#endif
