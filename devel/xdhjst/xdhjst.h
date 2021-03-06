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

#ifndef XDHJST_INC_
# define XDHJST_INC_

# define XDHJST_NAME		"XDHJST"

# if defined( E_DEBUG ) && !defined( XDHJST_NODBG )
#  define XDHJST_DBG
# endif

// X(SL)/DH(TML) JavaScript-related Tools

# include "err.h"

# include "xdhcbk.h"

# include "ntvstr.h"
# include "ctn.h"
# include "str.h"

namespace xdhjst {
	typedef ntvstr::char__ nchar__;
	typedef ntvstr::string___ nstring___;

	E_ENUM( script_name ) {
		snAttributeGetter,
		snAttributeRemover,
		snAttributeSetter,
		snElementFiller,
		snDocumentFiller,
		snCastingFiller,
		snContentGetter,
		snContentSetter,
		snDialogAlert,
		snDialogConfirm,
		snFocuser,
		snLog,
		snPropertyGetter,
		snPropertySetter,
		snWidgetContentRetriever,
		snWidgetFocuser,
		sn_amount,
		sn_Undefined,
	};

	const str::string_ &GetTaggedScript(
		script_name__ ScriptName,
		str::string_ &Buffer );

	void GetScript(
		script_name__ ScriptName,
		str::string_ &Script,
		va_list List );

	const str::string_ &GetScript(
		script_name__ ScriptName,
		str::string_ *Script,	// Was '&Script', but should not work due 'va_start(...)' restrictions concerning references (but it worked under MSVC).
		... );

	namespace scripter {	// Functions generating a script.
		inline void DialogAlert(
			const nstring___ &XML,
			const nstring___ &XSL,
			const nstring___ &Title,
			const nstring___ &CloseText,
			str::string_ &Script )
		{
			GetScript( snDialogAlert, &Script, XML.Internal()(), XSL.Internal()(), Title.Internal()(), CloseText.Internal()() );
		}

		inline void RemoveAttribute(
			const nstring___ &Id,
			const nstring___ &Name,
			str::string_ &Script )
		{
			GetScript( snAttributeRemover, &Script, Id.Internal()(), Name.Internal()() );
		}

		inline void GetAttribute(
			const nstring___ &Id,
			const nstring___ &Name,
			str::string_ &Script )
		{
			GetScript( snAttributeGetter, &Script, Id.Internal()(), Name.Internal()() );
		}

		inline void SetAttribute(
			const nstring___ &Id,
			const nstring___ &Name,
			const nstring___ &Value,
			str::string_ &Script )
		{
			GetScript( snAttributeSetter, &Script, Id.Internal()(), Name.Internal()(), Value.Internal()() );
		}

		inline void SetContent(
			const nstring___ &Id,
			const nstring___ &Value,
			str::string_ &Script )
		{
			GetScript( snContentSetter, &Script, Id.Internal()(), Value.Internal()() );
		}

		inline void GetProperty(
			const nstring___ &Id,
			const nstring___ &Name,
			str::string_ &Script )
		{
			GetScript( snPropertyGetter, &Script, Id.Internal()(), Name.Internal()() );
		}
	}

	/*
	namespace scripter {
		void HandleEventsDigest(
			const str::string_ &FrameId,
			const xdhcbk::args_ &Digest,
			str::string_ &Script );

		void HandleEventsDigests(
			const str::string_ &FrameId,
			const xdhcbk::args_ &Digests,
			str::string_ &Script );

		void HandleWidgetsDigest(
			const str::string_ &FrameId,
			const xdhcbk::args_ &Digest,
			str::string_ &Script );

		void HandleWidgetsDigests(
			const str::string_ &FrameId,
			const xdhcbk::args_ &Digests,
			str::string_ &Script );

		void HandleEventsWidgetsDigests(
			const str::string_ &FrameId,
			const xdhcbk::args_ &Digests,
			str::string_ &Script );

		void HandleEventsWidgetsDigests(
			const str::string_ &FrameId,
			const str::string_ &Digests,
			str::string_ &Script );

		void HandleCastsDigest(
			const str::string_ &FrameId,
			const xdhcbk::args_ &Digest,
			str::string_ &Script );

		void HandleCastsDigests(
			const str::string_ &FrameId,
			const xdhcbk::args_ &Digests,
			str::string_ &Script );
	}
	*/
}

#endif
