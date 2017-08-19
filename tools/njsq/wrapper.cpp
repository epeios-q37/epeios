/*
	Copyright (C) 2016 by Claude SIMON (http://zeusw.org/epeios/contact.html).

	This file is part of 'NJSq'.

    'NJSq' is free software: you can redistribute it and/or modify it
    under the terms of the GNU Affero General Public License as published
    by the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    'NJSq' is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with 'NJSq'.  If not, see <http://www.gnu.org/licenses/>.
*/

#include "wrapper.h"

#include "n4allw.h"
#include "n4njs.h"
#include "nodeq.h"
#include "sclerror.h"
#include "v8q.h"

using namespace wrapper;

typedef n4all::cCaller cCaller_;

namespace {
	inline void GetString_(
		int Index,
		const v8::FunctionCallbackInfo<v8::Value> &Info,
		str::dString &Value )
	{
		qRH
			v8q::sString String;
		qRB
			String.Init( Info[Index] );

			String.Get( Value );
		qRR
		qRT
		qRE
	}

	namespace {
		class rRStream
		: public n4njs::cURStream
		{
		private:
			nodeq::sRStream Core_;
		protected:
			virtual bso::sBool NANJSRead( str::dString &Chunk ) override
			{
				return Core_.Read( Chunk );
			}
		public:
			void reset( bso::sBool P = true )
			{
				tol::reset( P, Core_ );
			}
			qCVDTOR( rRStream );
			void Init( v8::Local<v8::Value> Value )
			{
				Core_.Init( Value );
			}
		};
	}

	inline void GetStream_(
		int Index,
		const v8::FunctionCallbackInfo<v8::Value> &Info,
		n4njs::cURStream *&Stream )
	{
	qRH
	qRB
		Stream = new rRStream;

		if ( Stream == NULL )
			qRAlc();

		Stream->Init( Info[Index] );
	qRR
	qRT
	qRE
	}
}

void SetReturnValue_(
	const v8::FunctionCallbackInfo<v8::Value> &Info,
	const str::dString &Value )
{
	Info.GetReturnValue().Set( v8q::sString( Value ).Core() );
}

namespace {
	class sCaller_
	: public cCaller_ {
	private:
		qRMV( const v8::FunctionCallbackInfo<v8::Value>, I_, Info_ );
	protected:
		virtual void N4ALLGetArgument(
			bso::sU8 Index,
			n4all::sEnum Type,
			void *Value ) override
		{
			Index++;	// The first one was the function id.

			if ( Index >= I_().Length() )
				qRGnr();

			switch ( Type ) {
			case n4all::tString:
				GetString_( Index, I_(), *( str::dString * )Value );
				break;
			case n4njs::tStream:
				GetStream_( Index, I_(), ( n4njs::cURStream **)Value );
				break;
			case n4njs::tBuffer:
				GetBuffer_( Index, I_(), ( n4njs::cUBuffer **)Value );
				break;
			case n4njs::tCallback:
				GetCallback_( Index, I_(), ( n4njs::cUCallback **)Value );
				break;
			default:
				qRGnr();
				break;
			}
		}
		virtual void N4ALLSetReturnValue(
			n4all::sEnum Type,
			const void *Value ) override
		{
			switch ( Type ) {
			case n4all::tString:
				SetReturnValue_( I_(), *( const str::dString * )Value );
				break;
			default:
				qRGnr();
				break;
			}
		}
	public:
		void reset( bso::sBool = true )
		{
			Info_ = NULL;
		}
		qCDTOR( sCaller_ );
		void Init( const v8::FunctionCallbackInfo<v8::Value> &Info )
		{
			Info_ = &Info;
		}
	};
}

void wrapper::Launch( const v8::FunctionCallbackInfo<v8::Value>& Info )
{
qRH
	sCaller_ Caller;
qRB
	if ( Info.Length() < 1 )
		qRGnr();

	if ( !Info[0]->IsUint32() )
		qRGnr();

	v8::Local<v8::Uint32> Index = v8::Local<v8::Uint32>::Cast(Info[0] );

	Caller.Init( Info );

	n4allw::GetLauncher().Launch( n4allw::GetFunction( Index->Uint32Value()), Caller );

	if ( sclerror::IsErrorPending() )
		qRAbort();	// To force the handling of a pending error.
qRR
qRT
qRE
}

