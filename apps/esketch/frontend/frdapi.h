/* DON'T MODIFY : computer-generated file ! */
/*
	API from : esketchbkd V20200307 Build Mar 11 2020 14:49:17 - GNU/Linux;Clang 6.0.0;AMD64

	This file was generated using BARq 20200307 (Build Mar 11 2020 10:02:33 GNU/Linux;Clang 6.0.0;AMD64)
*/

#ifndef ESKETCH__INC
# define ESKETCH__INC

# define ESKETCH_TARGET "esketch"
# define ESKETCH_API_VERSION "1"

# include "fblfrd.h"
# include "cpe.h"

namespace esketch {

	namespace {
		typedef fblfrd::frontend_depot__ _frontend_depot__;
	}

	class fStatics
	: public _frontend_depot__
	{
	private:
		fblfrd::object__ _ID;
		fblfrd::command__ _Commands[3];
	public:
		void reset( bso::bool__ P = true )
		{
			_frontend_depot__::reset( P );
			_ID = FBLFRD_UNDEFINED_OBJECT;
		}
		E_CVDTOR( fStatics )
		void Init( fblfrd::frontend___ &Frontend )
		{
			fblfrd::commands_details CommandsDetails;
			fblfrd::command_detail CommandDetail;
			fblfrd::id16s Commands;

			fblfrd::id8__ Parameters[] = {
				25, 0, 
				25, 0, 
				0, 
			};

			_frontend_depot__::Init( Frontend );

			_ID = FBLFRD_MASTER_OBJECT;
			CommandsDetails.Init();

			CommandDetail.Init();
			CommandDetail.Name = "LoadSetupOfId_1";;
			CommandDetail.Casts.Append( Parameters + 0, 2 );
			CommandsDetails.Append( CommandDetail );

			CommandDetail.Init();
			CommandDetail.Name = "LoadSetupContent_1";;
			CommandDetail.Casts.Append( Parameters + 2, 2 );
			CommandsDetails.Append( CommandDetail );

			CommandDetail.Init();
			CommandDetail.Name = "SKTTest_1";;
			CommandDetail.Casts.Append( Parameters + 4, 1 );
			CommandsDetails.Append( CommandDetail );


			Commands.Init();
			this->Frontend().GetCommands( FBLFRD_MASTER_TYPE, CommandsDetails, Commands );
			Commands.Recall( 0, 3, _Commands );
		}
		void LoadSetupOfId_1( 
			const fblfrd::string_ &In1 ) const
		{
			Frontend().PushHeader( _ID, Commands()[0] );
			Frontend().StringIn( In1 );

			Frontend().EndOfInParameters();


			Frontend().Handle();
		}
		void LoadSetupContent_1( 
			const fblfrd::string_ &In1 ) const
		{
			Frontend().PushHeader( _ID, Commands()[1] );
			Frontend().StringIn( In1 );

			Frontend().EndOfInParameters();


			Frontend().Handle();
		}
		void SKTTest_1( void ) const
		{
			Frontend().PushHeader( _ID, Commands()[2] );

			Frontend().EndOfInParameters();


			Frontend().Handle();
		}
		const fblfrd::command__ *Commands( void ) const
		{
			return _Commands;
		}
	};

	class fSKTMyObjectCommon
	: public _frontend_depot__
	{
	private:
		fblfrd::id16__ _ID;
		fblfrd::command__ _Commands[2];
	public:
		void reset( bso::bool__ P = true )
		{
			_frontend_depot__::reset( P );
			_ID = FBLFRD_UNDEFINED_OBJECT;
		}
		E_CVDTOR( fSKTMyObjectCommon )
		void Init( fblfrd::frontend___ &Frontend )
		{
			fblfrd::commands_details CommandsDetails;
			fblfrd::command_detail CommandDetail;
			fblfrd::id16s Commands;

			fblfrd::id8__ Parameters[] = {
				25, 0, 25, 
				0, 
			};

			_frontend_depot__::Init( Frontend );

			_ID = this->Frontend().GetType( str::string( "MyObject" ) );

			CommandsDetails.Init();

			CommandDetail.Init();
			CommandDetail.Name = "ToUC_1";;
			CommandDetail.Casts.Append( Parameters + 0, 3 );
			CommandsDetails.Append( CommandDetail );

			CommandDetail.Init();
			CommandDetail.Name = "Test_1";;
			CommandDetail.Casts.Append( Parameters + 3, 1 );
			CommandsDetails.Append( CommandDetail );


			Commands.Init();
			this->Frontend().GetCommands( _ID, CommandsDetails, Commands );
			Commands.Recall( 0, 2, _Commands );
		}
		fblfrd::object__ GetNewObject( void )
		{
			return Frontend().GetNewObject( _ID );
		}
		void RemoveObject( fblfrd::object__ Object )
		{
			Frontend().RemoveObject( Object );
		}
		const fblfrd::command__ *Commands( void ) const
		{
			return _Commands;
		}
	};

	class rSKTMyObject
	{
	private:
		fblfrd::object__ _ID;
		fSKTMyObjectCommon *Common_;
	public:
		void reset( bso::bool__ P = true )
		{
			if ( P == true )
				if ( ( Common_ != NULL ) && ( _ID != FBLFRD_UNDEFINED_OBJECT ) && Common_->Frontend().IsConnected() )
					Common_->RemoveObject( _ID );

			Common_ = NULL;
			_ID = FBLFRD_UNDEFINED_OBJECT;
		}
		rSKTMyObject( void )
		{
			reset( false );
		}
		~rSKTMyObject( void )
		{
			reset();
		}
		fblfrd::object__ ID( void ) const
		{
			return _ID;
		}
		void Init( fSKTMyObjectCommon &Common )
		{
			Common_ = &Common;

			_ID = Common_->GetNewObject();
		}
		void ToUC_1( 
			const fblfrd::string_ &In1,
			fblfrd::string_ &Out1 ) const
		{
			Common_->Frontend().PushHeader( _ID, Common_->Commands()[0] );
			Common_->Frontend().StringIn( In1 );

			Common_->Frontend().EndOfInParameters();

			Common_->Frontend().StringOut( Out1 );

			Common_->Frontend().Handle();
		}
		void Test_1( void ) const
		{
			Common_->Frontend().PushHeader( _ID, Common_->Commands()[1] );

			Common_->Frontend().EndOfInParameters();


			Common_->Frontend().Handle();
		}
	};

}

#endif //#ifndef esketch__INC
