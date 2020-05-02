/*
	Copyright (C) 2015 Claude SIMON (http://q37.info/contact/).

	This file is part of XDHWebQ.

	XDHWebQ is free software: you can redistribute it and/or
	modify it under the terms of the GNU Affero General Public License as
	published by the Free Software Foundation, either version 3 of the
	License, or (at your option) any later version.

	XDHWebQ is distributed in the hope that it will be useful,
	but WITHOUT ANY WARRANTY; without even the implied warranty of
	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
	Affero General Public License for more details.

	You should have received a copy of the GNU Affero General Public License
	along with XDHWebQ. If not, see <http://www.gnu.org/licenses/>.
*/

#include "xdhwebq.h"

#include "registry.h"

#include "sclt.h"
#include "scle.h"

#include "xdwmain.h"

#include "csdbns.h"
#include "csdcmn.h"
#include "err.h"
#include "cio.h"
#include "epsmsc.h"
#include "xpp.h"
#include "fnm.h"
#include "flf.h"
#include "mtk.h"
#include "websck.h"
#include "xdhutl.h"

using cio::CErr;
using cio::COut;
using cio::CIn;

SCLI_DEF( xdhwebq, NAME_LC, NAME_MC );

namespace {
	void PrintHeader_( void )
	{
		COut << NAME_MC " V" VERSION << " (" WEBSITE_URL ")" << txf::nl;
		COut << "Copyright (C) " COPYRIGHT << txf::nl;
		COut << txf::pad << "Build : " __DATE__ " " __TIME__ << " (" << cpe::GetDescription() << ')' << txf::nl;
	}
}

namespace {
	namespace {
		typedef csdbns::cProcessing cProcessing_;

		qENUM( State_ ) {
            sProlog,
            sRegular,
            s_amount,
            s_Undefined
		};

		struct rData {
			eState_ State;
			str::wString Token;
//			xdwmain::sRow Row;
			void reset( bso::sBool P = true )
			{
                State = s_Undefined;
                Token.reset( P );
//                Row = qNIL;
			}
			qCDTOR(rData);
			void Init(void)
			{
                State = s_Undefined;
                Token.Init();
//                Row = qNIL;
			}
		};

		namespace {
            void HandleProlog_(
                xdwmain::rAgent &Agent,
                fdr::rRWDriver &Driver,
                rData &Data )
            {
            qRH
                qCBUFFERh Buffer;
                flw::rDressedRWFlow<> Flow;
                str::wString Head;
            qRB
                Flow.Init(Driver);
                Head.Init();
                if ( !Agent.GetHead(Data.Token, Head) )
                    sclm::MGetValue(registry::definition::ErrorHead, Head);
                Flow.Write(Head.Convert(Buffer), Head.Amount());
                Flow.Commit();
            qRR
            qRT
            qRE
            }
		}

        namespace {
            namespace {
                namespace {
                    bso::sBool Extract_(
                        const str::dString &Digest,
                        str::dString &Id,
                        str::dString &Action)
                    {
                        bso::sBool ActionInProgress = false;
                    qRH;
                        xdhutl::wEventAbstract Abstract;
                    qRB;
                        Abstract.Init();
                        if ( xdhutl::FetchEventAbstract(Digest, Id, Abstract) ) {
                            if ( xdhutl::IsPredefined( Abstract.Action() ) )
                                qRVct();
                            else if ( Abstract.Action() == xdhutl::a_User ) {
                                // 'Id' is already set.
                                Action = Abstract.UserAction;
                                ActionInProgress = true;
                            } else
                                qRGnr();
                        }
                    qRR;
                    qRT;
                    qRE;
                        return ActionInProgress;
                    }
                }

                void Handle_(
                    const str::dString &Digest,
                    xdwmain::rSession &Session )
                {
                qRH;
                    str::string Id, Action;
                    qCBUFFERh IdBuffer, ActionBuffer;
                qRB;
                    tol::Init(Id, Action);

                    if ( Extract_(Digest, Id, Action) )
                        Session.Launch(Id.Convert(IdBuffer), Action.Convert(ActionBuffer));
                qRR;
                qRT;
                qRE;
                }
            }

            void HandleRegular_(
                xdwmain::rAgent &Agent,
                fdr::rRWDriver &Driver,
                rData &Data)
            {
            qRH
                websck::rFlow Flow;
                xdwmain::rSession Session;
                str::wString Digest, Script;
                xdhcmn::cSession *Callback = NULL;
            qRB
                Callback = Agent.FetchSessionCallback();

                if ( Callback == NULL )
                    qRGnr();

                Flow.Init(Driver, websck::mWithTerminator);
                Session.Init(Callback, Driver, "", Data.Token);

                if ( Agent.IsValid(Data.Token) )
                    Session.Launch("","");
                else {
                    Script.Init();
                    sclm::MGetValue(registry::definition::ErrorScript, Script);
                    Session.Execute(Script);
                }

                while ( true ) {
                    Digest.Init();
                    if ( !websck::GetMessage(Flow,Digest) )
                        break;
                    Flow.Dismiss();
                    Handle_(Digest, Session);
                    Flow.Write("StandBy", 7);
                    Flow.Commit();
                }
            qRR
            qRT
                if ( Callback != NULL )
                    Agent.DismissSessionCallback(Callback);
            qRE
            }
		}

		class sProcessing
		: public cProcessing_
		{
		private:
			qRMV( xdwmain::rAgent, A_, Agent_ );
		protected:
			void *CSDSCBPreProcess(
				fdr::rRWDriver *Driver,
				const ntvstr::char__ *Origin ) override
			{
                rData *Data = NULL;
			qRH
                websck::wHeader Header;
                websck::rRFlow Flow;
			qRB
                if ( ( Data = new rData ) == NULL )
                    qRAlc();

                Data->Init();

                Header.Init();

                if ( websck::Handshake(*Driver, Header) ) {
                    Flow.Init(*Driver, websck::mWithTerminator);
                    websck::GetMessage(Flow, Data->Token);
                    Data->State = sRegular;
                } else if ( Header.FirstLine == "XDH web prolog" ) {
                    if ( websck::GetValue(str::wString("Token"), Header, Data->Token ) )
                        Data->State = sProlog;
                } else {
                    Data->State = s_Undefined;
                }
			qRR
			qRT
			qRE
				return Data;
			}
			csdscb::action__ CSDSCBProcess(
				fdr::rRWDriver *Driver,
				void *UP ) override
			{

                if ( UP == NULL )
                    qRGnr();

                rData &Data = *(rData *)UP;


                switch ( Data.State ) {
                case sProlog:
                    HandleProlog_(A_(), *Driver, Data);
                    break;
                case sRegular:
                    HandleRegular_(A_(), *Driver, Data);
                    break;
                default:
                    qRGnr();
                    break;
                }

				return csdscb::aStop;
			}
			virtual bso::sBool CSDSCBPostProcess( void *UP ) override
			{
                if ( UP == NULL )
                    qRGnr();

                rData *Data = (rData *)UP;

#if 0
                if ( Data->Row != qNIL )
                    xdwmain::Remove(Data->Row, Data->Token);
#endif
                delete Data;

				return true;
			}
		public:
			void reset( bso::bool__ P = true )
			{
				Agent_ = NULL;
			}
			E_CVDTOR( sProcessing );
			void Init( xdwmain::rAgent &Agent )
			{
				Agent_ = &Agent;
			}
		};

	}

	void Process_( void )
	{
	qRH
		xdwmain::rAgent Agent;
		str::wString Identification, ModuleFilename;
		TOL_CBUFFER___ IdentificationBuffer;
		csdbns::server___ Server;
		sProcessing Callback;
		qCBUFFERh Buffer;
	qRB
		Identification.Init( NAME_LC " V" VERSION " Build " __DATE__ " " __TIME__ " - " );
		Identification.Append( cpe::GetDescription() );

		ModuleFilename.Init();
		sclm::MGetValue( registry::parameter::ModuleFilename, ModuleFilename );

		Agent.Init( xdhcmn::mMultiUser, ModuleFilename, dlbrry::n_Default, Identification.Convert( Buffer ) );

		Callback.Init( Agent );

		Server.Init( sclm::MGetU16( registry::parameter::Service ), Callback );
		Server.Process( NULL );
	qRR
	qRT
	qRE
	}
}

const scli::sInfo &sclt::SCLTInfo( void )
{
	return xdhwebq::Info;
}

#define C( name )\
	else if ( Command == #name )\
		name##_()

int sclt::SCLTMain(
	const str::dString &Command,
	const sclt::fOddities &Oddities )
{
	int ExitValue = EXIT_FAILURE;
qRH
qRB
	if ( Command == "Version" )
		PrintHeader_();
	else if ( Command == "License" )
		epsmsc::PrintLicense( NAME_MC );
	C( Process );
	else
		qRGnr();

	ExitValue = EXIT_SUCCESS;
qRR
qRT
qRE
	return ExitValue;
}
