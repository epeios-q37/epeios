/*
	'ntvstr.h' by Claude SIMON (http://zeusw.org/).

	'ntvstr' is part of the Epeios framework.

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

#ifndef NTVSTR__INC
# define NTVSTR__INC

# define NTVSTR_NAME		"NTVSTR"

# if defined( E_DEBUG ) && !defined( NTVSTR_NODBG )
#  define NTVSTR_DBG
# endif

/******************************************************************************/
				  /* do not modify anything above this limit */
				  /*			  unless specified			 */
				  /*******************************************/

// NaTiVe STRing

# include "err.h"
# include "flw.h"

# include "cpe.h"
# include "tol.h"
# include "strng.h"

# if defined( CPE_POSIX )
#  define NTVSTR__MBS	// 'Multi-Byte Strings'
# elif defined( CPE_WIN )
#  define NTVSTR__WCS	// 'Wide-Char Strings'
# else
#  error "Unknown target !"
# endif

// Pour viter d'avoir  inclure 'str.h'
namespace str {
	class string_;
}


namespace ntvstr {
# ifdef NTVSTR__MBS
	typedef char char__;
	E_CDEF( unsigned int, UTF8, 0 );
	E_CDEF( unsigned int, System, 0 );
# elif defined( NTVSTR__WCS )
	typedef wchar_t char__;
	E_CDEF( unsigned int, UTF8, CP_UTF8 );
	E_CDEF( unsigned int, System, CP_ACP );
# else
#  error
# endif

	typedef tol::E_BUFFER___( char__ ) core___;

	typedef tol::E_BUFFER___( bso::char__ ) buffer___;

	// Retourne la taille d'une chane de caractres natifs, en tenant compte de son encodage (ne correspond pas ncessairement au nombre de 'char__').
	inline bso::size__ Size( const char__ * Str )
	{
# ifdef NTVSTR__WCS
		return wcslen( Str );
# elif defined( NTVSTR__MBS )
		bso::size__ Size = mbstowcs( NULL, Str, 0);

		if ( Size == BSO_SIZE_MAX )
			ERRFwk();

		return Size;
# else
#  error
# endif
	}

	// Retourne la taille d'une chane de caratres natifs, en 'char__'.
	inline bso::size__ Amount( const char__ * Str )
	{
# ifdef NTVSTR__WCS
		return wcslen( Str );
# elif defined( NTVSTR__MBS )
		return strlen( Str );
# else
#  error
# endif
	}

	// 'Native string' ; 'string' utilisant en interne l'encodage natif. LEs 'str::string_' passs en paramtres sont encods en 'UTF-8'.
	class string___
	{
	private:
		core___ _Core;
		const bso::char__ *_Convert(
			unsigned int CodePage,
			TOL_CBUFFER___ &Buffer ) const;
		const str::string_ &_Convert(
			unsigned int CodePage,
			str::string_ &Buffer ) const;
	public:
		void reset( bso::bool__ P = true )
		{
			_Core.reset( P );
		}
		E_CDTOR( string___ );
# ifndef NTVSTR__MBS
		string___( const char *String )
		{
			reset( false );

			Init( String );
		}
# endif
		string___( const char__ *String )
		{
			reset( false );
			Init( String );
		}
		string___( const str::string_ &String )
		{
			reset( false );
			Init( String );
		}
# ifdef CPE_WIN
#  if defined( CPE_X86 ) || defined( CPE_MSVC )
		string___( int String )	// Pour traiter le cas ou c'est 'NULL' (assimil  un int) qui est pass en paramtre.
#  elif defined( CPE_X64 )
		string___( long long int String )	// Pour traiter le cas ou c'est 'NULL' (assimil  un long long int) qui est pass en paramtre.
#  else
#   error
#  endif
		{
			reset( false );

			if ( String != 0 )
				ERRFwk();

			Init( (char__ *)NULL );
		}
# endif
		string___ &operator =( const string___ &S )
		{
			Init( S.Internal() );

			return *this;
		}
		void Init( void )
		{
			_Core.reset();
		}
		void Init( const bso::char__ *String );
# ifndef NTVSTR__MBS
		void Init( const char__ *String );
# endif
		void Init( const str::string_ &String );
		void Init( const string___ &String )
		{
			Init();

			operator =( String );
		}
		void Forget( void )
		{
			_Core.Forget();
		}
		const bso::char__ *UTF8( TOL_CBUFFER___ &Buffer ) const
		{
			return _Convert( ntvstr::UTF8, Buffer );
		}
		const str::string_ &UTF8( str::string_ &Buffer ) const
		{
			return _Convert( ntvstr::UTF8, Buffer );
		}
		const bso::char__ *SystemEncoding( TOL_CBUFFER___ &Buffer ) const
		{
			return _Convert( ntvstr::System, Buffer );
		}
		const str::string_ &SystemEncoding( str::string_ &Buffer ) const
		{
			return _Convert( ntvstr::System, Buffer );
		}
		const core___ &Internal( void ) const
		{
			return _Core;
		}
		core___ &ExposedInternal( void )
		{
			return _Core;
		}
		// Retourne la taille, en tenant compte de l'encodage (ne correspond pas ncessairement au nombre de 'char__').
		bso::size__ Size( void ) const
		{
			if ( _Core == NULL )
				return 0;
			else
				return ntvstr::Size( _Core );
		}
		// Retourne la taille d'une chane de caratres natifs, en 'char__'.
		bso::size__ Amount( void ) const
		{
			if ( _Core == NULL )
				return 0;
			else
				return ntvstr::Amount( _Core );
		}
		bso::bool__ IsEmpty( void ) const
		{
			return Amount() == 0;
		}
		operator const char__*() const
		{
			return _Core;
		}
	};

	template <typename s, typename b> inline const bso::char__ *ToSystemEncoding(
		const s &String,
		b &Buffer )
	{
		return string___( String ).SystemEncoding( Buffer );
	}

	template <typename s, typename b> inline const bso::char__ *ToUTF8(
		const s &String,
		b &Buffer )
	{
		return string___( String ).UTF8( Buffer );
	}
}

				  /********************************************/
				  /* do not modify anything belove this limit */
				  /*			  unless specified		   	  */
/******************************************************************************/

#endif
