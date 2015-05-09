/*
	'xdhcbk.h' by Claude SIMON (http://zeusw.org/).

	'xdhcbk' is part of the Epeios framework.

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

#ifndef XDHCBK__INC
# define XDHCBK__INC

# define XDHCBK_NAME		"XDHCBK"

# if defined( E_DEBUG ) && !defined( XDHCBK_NODBG )
#  define XDHCBK_DBG
# endif

// X(SL)/DH(TML) CallBacKs

# include "err.h"
# include "flw.h"
# include "ntvstr.h"
# include "sclerror.h"
# include "strmrg.h"

# define XDHCBK_SHARED_DATA_VERSION_NUMBER	"10"

# define XDHCBK_SHARED_DATA_VERSION			XDHCBK_SHARED_DATA_VERSION_NUMBER "-" CPE_ARCHITECTURE_LABEL

# define XDHCBK_RETRIEVE_FUNCTION_NAME		XDHCBKRetrieve

namespace xdhcbk {
	E_CDEF( char *, CloseActionLabel, "Q37Close" );

	typedef ntvstr::char__ nchar__;
	typedef ntvstr::string___ nstring___;

	class session_callback__
	{
	protected:
		virtual bso::bool__ XDHCBKLaunch(
			const char *Id,
			const char *Action ) = 0;	// Return 'true' if the event propagation had to be stopped.
	public:
		void reset( bso::bool__ = true )
		{
			// Standadization.
		}
		E_CVDTOR( session_callback__ );
		void Init( void )
		{
			// Standardization.
		}
		bso::bool__ Launch(
			const char *Id,
			const char *Action )
		{
			return XDHCBKLaunch( Id, Action );
		}
	};

	enum function__ {		// Parameters :
		fLog,				// Message,
		fAlert,				// XML, XSL, Title.
		fConfirm,			// XML, XSL, Title.
		fSetChildren,		// Id, XML, XSL.
		fSetCasting,		// Id, XML, XSL.
		fSetProperty,		// Id, Name, Value.
		fGetProperty,		// Id, Name.
		fSetAttribute,		// Id, Name, Value.
		fGetAttribute,		// Id, Name.
		fRemoveAttribute,	// Id, Name.
		fGetResult,			// Id.
		fSetContent,		// Id, Value.
		fGetContent,		// Id.
		fFocus,				// Id.
		f_amount,
		f_Undefined
	};

	const char *GetLabel( function__ Function );

	class proxy_callback__
	{
	protected:
		virtual void XDHCBKProcess(
			function__ Function,
			TOL_CBUFFER___ *Result,
			...	) = 0;
	public:
		void reset( bso::bool__ = true )
		{
			// Standardization.
		}
		E_CVDTOR( proxy_callback__ );
		void Init( void )
		{
			// Standardization.
		}
		void Process(
			function__ Function,
			TOL_CBUFFER___ *Result,
			...	)
		{
			va_list List;
			va_start( List, Result );

			return XDHCBKProcess( Function, Result, List );
		}
	};


	class upstream_callback__ {
	protected:
		virtual proxy_callback__ *XDHCBKNew( void ) = 0;
	public:
		void reset( bso::bool__ P = true )
		{
			// Standardisation.
		}		
		E_CVDTOR( upstream_callback__ );
		void Init( void )
		{
			// Standardisation.
		}
		proxy_callback__ *New( void )
		{
			return XDHCBKNew();
		}
	};

#pragma pack( push, 1)
	// NOTA : is modified, increment 'CSDLEO_SHARED_DATA_VERSION' !
	class shared_data__
	{
	private:
		const char *_Version;	// Toujours en premire position.
		bso::uint__ _Control;	// Une valeur relative au contenu de la structure,  des fins de test primaire de compatibilit.
		err::err___ *_ERRError;
		sclerror::error___ *_SCLError;
		const cio::set__ *_CIO;
		upstream_callback__ *_Callback;
		const char *_LauncherIdentification;
		const char *_Localization;
	public:
		void reset( bso::bool__ = true )
		{
			_Version = NULL;
			_Control = 0;
			_ERRError = NULL;
			_SCLError = NULL;
			_CIO = NULL;
			_Callback = NULL;
			_LauncherIdentification = NULL;
			_Localization = NULL;
		}
		E_CDTOR( shared_data__ );
		void Init(
			upstream_callback__ &Callback,
			const char *LauncherIdentification,
			const char *Localization )
		{
			_Version = XDHCBK_SHARED_DATA_VERSION;
			_Control = ControlComputing();
			_ERRError = err::ERRError;
			_SCLError = sclerror::SCLERRORError;
			_CIO = &cio::GetCurrentSet();
			_Callback = &Callback;
			_LauncherIdentification = LauncherIdentification;
			_Localization = Localization;
		}
		size_t ControlComputing( void )
		{
			return sizeof( shared_data__ );
		}
		Q37_PMDF( err::err___, ERRError, _ERRError );
		Q37_PMDF( sclerror::error___, SCLError, _SCLError );
		Q37_PMDF( upstream_callback__, Callback, _Callback );
		Q37_PMDF( const char, LauncherIdentification, _LauncherIdentification );
		Q37_PMDF( const char, Localization, _Localization );
		Q37_RMDF( const cio::set__, CIO, _CIO );
	};
#pragma pack( pop )

	class downstream_callback__
	{
	protected:
		virtual void XDHCBKInitialize( const shared_data__ &Data ) = 0;
		virtual void XDHCBKBaseLanguage( TOL_CBUFFER___ &Buffer ) = 0;
		virtual session_callback__ *XDHCBKNew( void ) = 0;
	public:
		void reset( bso::bool__ = true )
		{
			// Standardisation.
		}
		E_CVDTOR( downstream_callback__ );
		void Init( void )
		{
			// Standardisation.
		}
		void Initialize( const shared_data__ &Data )
		{
			return XDHCBKInitialize( Data );
		}
		const char *BaseLanguage( TOL_CBUFFER___ &Buffer )
		{
			XDHCBKBaseLanguage( Buffer );

			return Buffer;
		}
		session_callback__ *Newn( void )
		{
			return XDHCBKNew();
		}
	};

	typedef downstream_callback__ *(retrieve)( void );

	void Escape(
		const str::string_ &Source,
		str::string_ &Target,
		bso::char__ Delimiter,	// Devrait tre '\'', '"' ou 0. Si 0, chappe '\'' et '\"', sinon chappe 'Delimiter'.
		bso::char__ EscapeChar = strmrg::DefaultEscapeToken );
#if 0
	void Unescape(
		const str::string_ &Source,
		str::string_ &Target,
		bso::char__ EscapeChar = DefaultEscapeChar );
#endif

	typedef strmrg::table_ args_;
	E_AUTO( args );

	using strmrg::Split;
	using strmrg::Merge;

	using strmrg::retriever__;


}

#endif
