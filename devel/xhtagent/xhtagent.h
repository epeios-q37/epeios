/*
	'xhtagent.h' by Claude SIMON (http://zeusw.org/).

	'xhtagent' is part of the Epeios framework.

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

#ifndef XHTAGENT__INC
# define XHTAGENT__INC

# define XHTAGENT_NAME		"XHTAGENT"

# if defined( E_DEBUG ) && !defined( XHTAGENT_NODBG )
#  define XHTAGENT_DBG
# endif

/******************************************************************************/
/* do not modify anything above this limit */
/*			  unless specified			 */
/*******************************************/

// XHT(ML) AGENT

# include "xhtcllbk.h"

# include "err.h"
# include "flw.h"

namespace xhtagent {

	typedef ntvstr::string___ nstring___;

	class agent_core___ {
	private:
		xhtcllbk::upstream_callback__ *_Callback;
		xhtcllbk::upstream_callback__ &_C( void ) const
		{
			if ( _Callback == NULL )
				ERRFwk();

			return *_Callback;
		}
		xhtcllbk::event_manager _Manager;
	public:
		void reset( bso::bool__ P = true )
		{
			_Callback = NULL;
			_Manager.reset( P );
		}
		E_CDTOR( agent_core___ );
		void Init( xhtcllbk::upstream_callback__ &Callback )
		{
			_Callback = &Callback;
			_Manager.Init();
		}
		const xhtcllbk::event_manager_ &EventManager( void ) const
		{
			return _Manager;
		}
		void ClearEventManager( void )
		{
			_Manager.Init();
		}
		void AddEventHandler(
			const char *EventName,
			xhtcllbk::event_handler__ &Handler )
		{
			if ( !_Manager.Add( EventName, Handler ) )
				ERRFwk();
		}
		void ExecuteJavascript( const nstring___ &Script )
		{
			return _C().ExecuteJavascript( Script );
		}
		const char *GetAttribute(
			const nstring___ &Id,
			const nstring___ &Name,
			TOL_CBUFFER___ &Buffer )
		{
			return _C().GetAttribute( Id, Name, Buffer );
		}
		void SetAttribute(
			const nstring___ &Id,
			const nstring___ &Name,
			const nstring___ &Value )
		{
			_C().SetAttribute( Id, Name, Value );
		}
		void RemoveAttribute(
			const nstring___ &Id,
			const nstring___ &Name )
		{
			_C().RemoveAttribute( Id, Name );
		}
		void SetString(
			const nstring___ &Id,
			const nstring___ &Name,
			const str::string_ &Value );
		const char *GetString(
			const nstring___ &Id,
			const nstring___ &Name,
			TOL_CBUFFER___ &Buffer )
		{
			return _C().GetProperty( Id, Name, Buffer );
		}
		void SetValue(
			const nstring___ &Id,
			const str::string_ &Value )
		{
			SetString(Id, "value", Value );
		}
		const char * GetValue(
			const nstring___ &Id,
			TOL_CBUFFER___ &Buffer )
		{
			return GetString(Id, "value", Buffer );
		}
		const char *GetSelectValue(
			const nstring___ &Id,
			TOL_CBUFFER___ &Buffer )
		{
			return _C().GetSelectValue( Id, Buffer );
		}
		const str::string_ &GetSelectValue(
			const char *Id,
			str::string_ &Buffer );
		void SetChildren(
			const nstring___ &Id,
			const nstring___ &XML,
			const nstring___ &XSL )
		{
			_C().SetChildren( Id, XML, XSL );
		}
		void SetPaddings(
			const nstring___ &XML,
			const nstring___ &XSL )
		{
			_C().SetPaddings( XML, XSL );
		}
		void Show(
			const nstring___ &Id,
			bso::bool__ Value = true )
		{
			if ( Value  )
				RemoveAttribute( Id, "hidden" );
			else
				SetAttribute( Id, "hidden", "hidden" );
		}
		void Hide(
			const nstring___ &Id,
			bso::bool__ Value = true )
		{
			Show( Id, !Value );
		}
		void Alert( const str::string_ &Message );
		void Alert( const char *Message )
		{
			Alert( str::string( Message ) );
		}
	};

	template <typename eh> class agent___
	: public agent_core___
	{
	public:
		eh Handlers;
	};
}

				  /********************************************/
				  /* do not modify anything belove this limit */
				  /*			  unless specified		   	  */
/******************************************************************************/

#endif
