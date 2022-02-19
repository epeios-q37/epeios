/*
	Copyright (C) 2007-2017 Claude SIMON (http://q37.info/contact/).

	This file is part of XPPq.

	XPPq is free software: you can redistribute it and/or
	modify it under the terms of the GNU Affero General Public License as
	published by the Free Software Foundation, either version 3 of the
	License, or (at your option) any later version.

	XPPq is distributed in the hope that it will be useful,
	but WITHOUT ANY WARRANTY; without even the implied warranty of
	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
	Affero General Public License for more details.

	You should have received a copy of the GNU Affero General Public License
	along with XPPq. If not, see <http://www.gnu.org/licenses/>.
*/

# include "xppqnjs.h"

#include "parser.h"
#include "registry.h"
#include "stream.h"

#include "sclm.h"
#include "scln4a.h"

void sclnjs::SCLNJSInfo( txf::sWFlow &Flow )
{
	Flow << NAME_MC << " v" << VERSION << txf::nl
		 << txf::pad << "Build : " __DATE__ " " __TIME__ " (" << cpe::GetDescription() << ')';
}

namespace {
	void ReturnArgument_( sclnjs::sCaller &Caller )
	{
	qRH
		str::wString Input, Text;
	qRB
		Input.Init();
		Caller.GetArgument( Input );

		Text.Init();
		sclm::GetBaseTranslation( "Argument", Text, Input );

		Caller.SetReturnValue( Text );
	qRR
	qRT
	qRE
	}
}

namespace console_ {
	SCLNJS_F( OnData )
	{
	qRH
		sclnjs::rObject This;
		sclnjs::rBuffer Chunk;
	qRB
		tol::Init( This, Chunk );
		Caller.GetArgument( This, Chunk );

		cio::COut << Chunk;
	qRR
	qRT
	qRE
	}

	SCLNJS_F( OnEnd )
	{
	qRH
		sclnjs::rObject This;
	qRB
		tol::Init( This );
		Caller.GetArgument( This );

		cio::COut << txf::nl;
	qRR
	qRT
	qRE
	}
}

namespace stream_ {
	namespace {
		qCDEF(char *, TargetId_, "_q37Target");
		qCDEF(char *, TargetReadBlockerId_, "_q37TargetReadBlocker");
		qCDEF(char *, TargetWriteBlockerId_, "_q37TargetWriteBlocker");
		qCDEF(char *, TargetChunkId_, "_q37TargetChunk");

		typedef str::wString rChunk_;

		inline sclnjs::rObject &GetTarget_(sclnjs::rObject &Source)
		{
		  return Source.Get<sclnjs::rObject>(TargetId_);
		}

		namespace {
      inline tht::rBlocker &GetBlocker_(
        const char *Id,
        sclnjs::rObject &Target)
      {
        return Target.Get<tht::rBlocker>(Id);
      }
		}

		inline tht::rBlocker &GetReadBlocker_(sclnjs::rObject &Target)
		{
		  return GetBlocker_(TargetReadBlockerId_, Target);
		}

		inline tht::rBlocker &GetWriteBlocker_(sclnjs::rObject &Target)
		{
		  return GetBlocker_(TargetWriteBlockerId_, Target);
		}

		inline rChunk_ &GetChunk_(sclnjs::rObject &Target)
		{
		  return Target.Get<rChunk_>(TargetChunkId_);
		}
	}

	SCLNJS_F( OnData )
	{
	qRH
		sclnjs::rObject This;  // Source.
		sclnjs::rBuffer Chunk;
	qRB
		tol::Init( This, Chunk );
		Caller.GetArgument( This, Chunk );

		sclnjs::rObject &Target = GetTarget_(This);

    CPq;
		GetWriteBlocker_(Target).Wait();
    CPq;
		Chunk.ToString(GetChunk_(Target));
    CPq;
		GetReadBlocker_(Target).Unblock();
    CPq;
	qRR
	qRT
	qRE
	}

	SCLNJS_F( OnEnd )
	{
	qRH
		sclnjs::rObject This;  // Source.
	qRB
    CPq;
		tol::Init( This );
		Caller.GetArgument( This );
    CPq;
		sclnjs::rObject &Target = GetTarget_(This);
    CPq;
		GetWriteBlocker_(Target).Wait();
    CPq;
		GetChunk_(Target).Init();
    CPq;
		GetReadBlocker_(Target).Unblock();
    CPq;
	qRR
	qRT
	qRE
	}

	SCLNJS_F( Read )
	{
	qRH
		sclnjs::rObject This;  // Target
	qRB
		tol::Init( This );
		Caller.GetArgument( This );

    CPq;
		GetReadBlocker_(This).Wait();
    CPq;

    rChunk_ &Chunk = GetChunk_(This);

//    cio::COut << ">>>" << Chunk << "<<<" << txf::commit;

    CPq;
    if ( Chunk.Amount() )
      Caller.SetReturnValue(Chunk);
    else
      Caller.SetReturnValueAsNull();

    CPq;
    Chunk.Init();
    CPq;
    GetWriteBlocker_(This).Unblock();
    CPq;
	qRR
	qRT
	qRE
	}

	SCLNJS_F( Set )
	{
	qRH
		sclnjs::rObject Source, *This = NULL;
		tht::rBlocker
      *ReadBlocker = NULL,
      *WriteBlocker = NULL;
    rChunk_ *Chunk = NULL;
	qRB
		This = qNEW(sclnjs::rObject);
    ReadBlocker = qNEW(tht::rBlocker);
    WriteBlocker = qNEW(tht::rBlocker);
    Chunk = qNEW(rChunk_);

		tol::Init(Source, *This, *ReadBlocker, *Chunk);

		WriteBlocker->Init(tht::bpDontLock);

		Caller.GetArgument( Source, *This );

		Source.Set(TargetId_, This);
		This->Set(TargetReadBlockerId_, ReadBlocker);
		This->Set(TargetWriteBlockerId_, WriteBlocker);
		This->Set(TargetChunkId_, Chunk);
	qRR
    qDELETE(This);
    qDELETE(ReadBlocker);
    qDELETE(WriteBlocker);
    qDELETE(Chunk);
	qRT
	qRE
	}
}

namespace dummy_ {
	SCLNJS_F( Read )
	{
	qRH
		static bool First = true;
		str::wString Chunk;
	qRB
		if ( First ) {
      First = false;
		  CPq;
		  Chunk.Init("Coucou");
      Caller.SetReturnValue(Chunk);
		  CPq;
		} else {
		  CPq;
		  Caller.SetReturnValueAsNull();
      CPq;
		}
	qRR
	qRT
	qRE
	}

	SCLNJS_F( Set )
	{
	qRH
		sclnjs::rObject *This = NULL;
	qRB
		This = qNEW(sclnjs::rObject);

		tol::Init(*This);
	qRR
    qDELETE(This);
	qRT
	qRE
	}
}

const scli::sInfo &sclnjs::SCLNJSRegister( sclnjs::sRegistrar &Registrar )
{
	static scli::sInfo Info(NAME_LC, NAME_MC, "q37.info");

	Registrar.Register( ReturnArgument_ );                                          // 0
	Registrar.Register( parser::OnData, parser::OnEnd, parser::Parse );             // 1 … 3
	Registrar.Register( stream::upstream::OnData, stream::upstream::OnEnd, stream::downstream::Read, stream::_Set ); // 4 … 7
	Registrar.Register( console_::OnData, console_::OnEnd );                        // 8 … 9
	Registrar.Register( stream_::OnData, stream_::OnEnd, stream_::Read, stream_::Set );            // 10 … 13
	Registrar.Register(dummy_::Read, dummy_::Set);  // 14 … 15

	return Info;
}
