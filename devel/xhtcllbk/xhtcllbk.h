﻿/*
	'xhtcllbk.h' by Claude SIMON (http://zeusw.org/).

	'xhtcllbk' is part of the Epeios framework.

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

#ifndef XHTCLLBK__INC
# define XHTCLLBK__INC

# define XHTCLLBK_NAME		"XHTCLLBK"

# if defined( E_DEBUG ) && !defined( XHTCLLBK_NODBG )
#  define XHTCLLBK_DBG
# endif

/******************************************************************************/
				  /* do not modify anything above this limit */
				  /*			  unless specified			 */
				  /*******************************************/

// XHT(ML) CaLLBacK

# include "err.h"
# include "flw.h"
# include "tol.h"
# include "sdr.h"
# include "bch.h"
# include "xtf.h"
# include "strmrg.h"
# include "iof.h"

# define XHTCLLBK_SHARED_DATA_VERSION_NUMBER	"6"

# define XHTCLLBK_SHARED_DATA_VERSION	XHTCLLBK_SHARED_DATA_VERSION_NUMBER "-" CPE_ARCHITECTURE_LABEL

# define XHTCLLBK_RETRIEVE_FUNCTION_NAME		XHTCLLBKRetrieve

namespace xhtcllbk {
	typedef ntvstr::char__ nchar__;
	typedef ntvstr::string___ nstring___;

	class upstream_callback__ {
	protected:
		virtual void XHTCLLBKGetLanguage(
			TOL_CBUFFER___ &Buffer ) = 0;
		virtual void XHTCLLBKExecuteJavascript(
			const nchar__ *Script,
			TOL_CBUFFER___ &Buffer ) = 0;
		virtual void XHTCLLBKOpenDialog(
			const nchar__ *XML,
			const nchar__ *XSL,
			const nchar__ *Title,
			TOL_CBUFFER___ &Buffer ) = 0;
		virtual void XHTCLLBKSetChildren(
			const nchar__ *Id,
			const nchar__ *XML,
			const nchar__ *XSL ) = 0;
		virtual void XHTCLLBKSetCasting(
			const nchar__ *XML,
			const nchar__ *XSL ) = 0;
		virtual void XHTCLLBKSetProperty(
			const nchar__ *Id,
			const nchar__ *Name,
			const nchar__ *Value ) = 0;
		virtual void XHTCLLBKGetProperty(
			const nchar__ *Id,
			const nchar__ *Name,
			TOL_CBUFFER___ &Buffer ) = 0;
		virtual void XHTCLLBKSetAttribute(
			const nchar__ *Id,
			const nchar__ *Name,
			const nchar__ *Value ) = 0;
		virtual void XHTCLLBKGetAttribute(
			const nchar__ *Id,
			const nchar__ *Name,
			TOL_CBUFFER___ &Buffer ) = 0;
		virtual void XHTCLLBKGetResultAttribute(
			const nchar__ *Id,
			TOL_CBUFFER___ &Buffer ) = 0;
		virtual void XHTCLLBKRemoveAttribute(
			const nchar__ *Id,
			const nchar__ *Name ) = 0;
		virtual void XHTCLLBKGetSelectValue(
			const nchar__ *Id,
			TOL_CBUFFER___ &Buffer ) = 0;
	public:
		void reset( bso::bool__ P = true )
		{
			//Standardisation.
		}		
		E_CVDTOR( upstream_callback__ );
		void Init( void )
		{
			//Standardisation.
		}
		const char *GetLanguage( TOL_CBUFFER___ &Buffer )
		{
			XHTCLLBKGetLanguage( Buffer );

			return Buffer;
		}
		const char *ExecuteJavascript(
			const nstring___ &Script,
			TOL_CBUFFER___ &Buffer )
		{
			XHTCLLBKExecuteJavascript( Script.Internal(), Buffer );

			return Buffer;
		}
		const char *OpenDialog(
			const nstring___ &XML,
			const nstring___ &XSL,
			const nstring___ &Title,
			TOL_CBUFFER___ &Buffer )
		{
			XHTCLLBKOpenDialog( XML.Internal(), XSL.Internal(), Title.Internal(), Buffer );

			return Buffer;
		}
		void SetChildren(
			const nstring___ &Id,
			const nstring___ &XML,
			const nstring___ &XSL )
		{
			XHTCLLBKSetChildren( Id.Internal(), XML.Internal(), XSL.Internal() );
		}
		void SetCasting(
			const nstring___ &XML,
			const nstring___ &XSL )
		{
			XHTCLLBKSetCasting( XML.Internal(), XSL.Internal() );
		}
		void ExecuteJavascript( const nstring___ &Script )
		{
		ERRProlog
			TOL_CBUFFER___ Buffer;
		ERRBegin
			ExecuteJavascript( Script, Buffer );
		ERRErr
		ERREnd
		ERREpilog
		}
		const char *GetProperty(
			const nstring___ &Id,
			const nstring___ &Name,
			TOL_CBUFFER___ &Buffer )
		{
			XHTCLLBKGetProperty(Id.Internal(), Name.Internal(), Buffer );

			return Buffer;
		}
		void SetProperty(
			const nstring___ &Id,
			const nstring___ &Name,
			const nstring___ &Value )
		{
			XHTCLLBKSetProperty( Id.Internal(), Name.Internal(), Value.Internal() );
		}
		const char *GetAttribute(
			const nstring___ &Id,
			const nstring___ &Name,
			TOL_CBUFFER___ &Buffer )
		{
			XHTCLLBKGetAttribute( Id.Internal(), Name.Internal(), Buffer );

			return Buffer;
		}
		void SetAttribute(
			const nstring___ &Id,
			const nstring___ &Name,
			const nstring___ &Value )
		{
			XHTCLLBKSetAttribute( Id.Internal(), Name.Internal(), Value.Internal() );
		}
		const char *GetResultAttribute(
			const nstring___ &Id,
			TOL_CBUFFER___ &Buffer )
		{
			XHTCLLBKGetResultAttribute( Id.Internal(), Buffer );

			return Buffer;
		}
		void RemoveAttribute(
			const nstring___ &Id,
			const nstring___ &Name )
		{
			XHTCLLBKRemoveAttribute( Id.Internal(), Name.Internal() );
		}
		const char *GetSelectValue(
			const nstring___ &Id,
			TOL_CBUFFER___ &Buffer )
		{
			XHTCLLBKGetSelectValue( Id.Internal(), Buffer );

			return Buffer;
		}
	};

	class session_callback__
	{
	protected:
		virtual void XHTCLLBKLaunch(
			const char *Id,
			const char *Action ) = 0;
	public:
		void reset( bso::bool__ = true )
		{
			// Standardisation.
		}
		E_CVDTOR( session_callback__ );
		void Init( void )
		{
			// Standardisation.
		}
		void Launch(
			const char *Id,
			const char *Action )
		{
			return XHTCLLBKLaunch( Id, Action );
		}
	};

	class downstream_callback__
	{
	protected:
		virtual void XHTCLLBKOnLoad( const char *Launcher ) = 0;
		virtual void XHTCLLBKBaseLanguage( TOL_CBUFFER___ &Buffer ) = 0;
		virtual session_callback__ *XHTCLLBKNew( upstream_callback__ &Callback ) = 0;
		// Destruction by destructor member.
		virtual void XHTCLLBKOnUnload( void ) = 0;
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
		void OnLoad( const char *Launcher )
		{
			return XHTCLLBKOnLoad( Launcher );
		}
		const char *BaseLanguage( TOL_CBUFFER___ &Buffer )
		{
			XHTCLLBKBaseLanguage( Buffer );

			return Buffer;
		}
		session_callback__ *New( upstream_callback__ &Callback )
		{
			return XHTCLLBKNew( Callback );
		}
		void OnUnload( void )
		{
			return XHTCLLBKOnUnload();
		}
	};

#pragma pack( push, 1)
		// NOTA : Si modifié, modifier 'CSDLEO_SHARED_DATA_VERSION' !
	class shared_data__
	{
	private:
		const char *_Version;	// Toujours en première position.
		bso::uint__ _Control;	// Une valeur relative au contenu de la structure, à des fins de test primaire de compatibilité.
		upstream_callback__ *_Callback;
		const char *_LauncherIdentification;
		fdr::oflow_driver_base___ *_OFlowDriver;
	public:
		void reset( bso::bool__ = true )
		{
			_Version = NULL;
			_Control = 0;
			_Callback = NULL;
		}
		E_CDTOR( shared_data__ );
		void Init(
			upstream_callback__ &Callback,
			const char *LauncherIndetification,
			fdr::oflow_driver_base___ &OFlowDriver )
		{
			_Version = XHTCLLBK_SHARED_DATA_VERSION;
			_Control = ControlComputing();
			_Callback = &Callback;
			_LauncherIdentification = LauncherIndetification;
			_OFlowDriver = &OFlowDriver;
		}
		size_t ControlComputing( void )
		{
			return sizeof( shared_data__ );
		}
		upstream_callback__ &Callback( void ) const
		{
			if ( _Callback == NULL )
				ERRFwk();

			return *_Callback;
		}
		const char *LauncherIdentification( void ) const
		{
			if ( _LauncherIdentification == NULL )
				ERRFwk();

			return _LauncherIdentification;
		}
		fdr::oflow_driver_base___ &OFlowDriver( void ) const
		{
			if ( _OFlowDriver == NULL )
				ERRFwk();

			return *_OFlowDriver;
		}
	};
#pragma pack( pop )

	void Escape(
		const str::string_ &Source,
		str::string_ &Target,
		bso::char__ Delimiter,	// Devrait être '\'', '"' ou 0. Si 0, échappe '\'' et '\"', sinon échappe 'Delimiter'.
		bso::char__ EscapeChar = strmrg::DefaultEscapeToken );
#if 0
	void Unescape(
		const str::string_ &Source,
		str::string_ &Target,
		bso::char__ EscapeChar = DefaultEscapeChar );
#endif
	typedef downstream_callback__ *(retrieve)( const shared_data__ &Data );

	typedef strmrg::table_ params_;
	E_AUTO( params );

	inline bso::bool__ Split(
		const str::string_ &Input,
		params_ &Params )
	{
		return strmrg::Split( Input, Params );
	}

	inline void Merge(
		const params_ &Params,
		str::string_ &Target )
	{
		return strmrg::Merge( Params, Target );
	}


	using strmrg::retriever__;

}

				  /********************************************/
				  /* do not modify anything belove this limit */
				  /*			  unless specified		   	  */
/******************************************************************************/

#endif
