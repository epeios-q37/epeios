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

#ifndef MTX__INC
# define MTX__INC

# define MTX_NAME		"MTX"

# if defined( E_DEBUG ) && !defined( MTX_NODBG )
#  define MTX_DBG
# endif

// MuTeX


# include "bso.h"
# include "cpe.h"
# include "tol.h"

# ifdef system
#  define MTX_SYSTEM_BUFFER_ system
#  undef system
# endif

#include <mutex>	// Before 'tol.h', otherwise they may be some conflict.

# ifdef MTX_SYSTEM_BUFFER_
#  define system MTX_SYSTEM_BUFFER_
#  undef MTX_SYSTEM_BUFFER_
# endif


/***************/
/***** OLD *****/
/***************/

# define MTX__INVALID_HANDLER	NULL	// Internal use.
# define MTX_INVALID_HANDLER	MTX__INVALID_HANDLER	// For users.

namespace mtx {

	qENUM( State_ )
	{
		sFree,
		sLocked,
		sReleased,
		sDisabled,
		s_amount,
		s_Undefined
	};

	//t A mutex handler.
	typedef struct _mutex__ {
	private:
		std::mutex Lock_;
		eState_ State_;
	private:
		bso::bool__ IsReleased_( void ) const
		{
			return State_ == sReleased;
		}
		bso::bool__ IsDisabled_( void ) const
		{
			return State_ == sDisabled;
		}
		bso::bool__ IsLocked_( void ) const
		{
			return State_ == sLocked;
		}
	public:
#ifdef MTX__CONTROL
		void Release( void )
		{
			Lock_.lock();

			State_ = sReleased;

			Lock_.unlock();
		}
		bso::bool__ IsReleased( void ) const
		{
			return IsReleased_();
		}
#endif
		bso::bool__ IsDisabled( void ) const
		{
			return IsDisabled_();
		}
		bso::bool__ IsLocked( void )
		{
			bso::sBool Return = false;

			Lock_.lock();
#ifdef MTX__CONTROL
			if ( IsReleased_() ) {
				Lock_.unlock();
				qRFwk();
			}
#endif
			if ( IsDisabled_() ) {
				Lock_.unlock();
				return false;
			}

			Return = IsLocked_();

			Lock_.unlock();

			return Return;
		}
		bso::bool__ TryToLock( void )
		{
			Lock_.lock();
#ifdef MTX__CONTROL
			if ( IsReleased_() ) {
				Lock_.unlock();
				qRFwk();
			}
#endif
			if ( IsDisabled_() ) {
				Lock_.unlock();
				return true;
			}

			if ( IsLocked_() ) {
				Lock_.unlock();
				return false;
			}

			State_ = sLocked;

			Lock_.unlock();

			return true;
		}
		bso::sBool Unlock( qRPN )
		{
			Lock_.lock();

			if ( IsDisabled_() ) {
				Lock_.unlock();
				return true;
			}

			if ( !IsLocked_() ) {
				Lock_.unlock();

				if ( ErrHandling == err::hThrowException )
					qRFwk();
				else
					return false;
			}

			State_ = sFree;

			Lock_.unlock();

			return true;
		}
		_mutex__( bso::bool__ Disabled )
		{
			State_ = Disabled ? sDisabled : sFree;
		}
		~_mutex__( void )
		{
#ifdef MTX__CONTROL
			Release();
#endif
		}
	} *handler___;

	E_CDEF( handler___, Undefined, NULL );

	//f Return a new mutex handler.
	inline handler___ Create( bso::bool__ Disabled = false )	// Si True, utilisation dans un contexte mono-thread.
	{
		handler___ Handler;
		
		if ( ( Handler = new _mutex__( Disabled ) ) == NULL )
			qRAlc();

		return Handler;
	}

	inline bso::bool__ IsLocked( handler___ Handler )
	{
#ifdef MTX_DBG
		if ( Handler == NULL )
			qRFwk();
#endif
		return Handler->IsLocked();
	}


	inline bso::bool__ TryToLock( handler___ Handler)
	{
#ifdef MTX_DBG
		if ( Handler == NULL )
			qRFwk();
#endif
		return Handler->TryToLock();
	}

	void Defer_( void );

	// Wait until mutex unlocked.
	inline bso::sBool WaitUntilUnlocked_(
		handler___ Handler,
		tol::sDelay Timeout ) // If == '0' or lock succeed, returns always 'true', or returns false after 'Timeout' ms.
	{
		tol::sTimer Timer;
		bso::sBool NoTimeout = true;

		Timer.Init( Timeout );

		Timer.Launch();

		while( !TryToLock( Handler ) && ( NoTimeout = !Timer.IsElapsed() ) )
			Defer_();

		return NoTimeout;
	}

	// Lock 'Handler'. Blocks until lock succeed or after 'Timeout' ms.
	inline bso::sBool Lock(
		handler___ Handler,
		tol::sDelay Timeout = 0 ) // If == '0' or lock succeed, returns always 'true', or returns false after 'Timeout' ms.
	{
#ifdef MTX_DBG
		if ( Handler == NULL )
			qRFwk();
#endif
		if ( !TryToLock( Handler ) )
			return WaitUntilUnlocked_( Handler, Timeout );
		else
			return true;
	}

	//f Unlock 'Handler'.
	inline bso::sBool Unlock(
		handler___ Handler,
		qRPD )
	{
#ifdef MTX_DBG
		if ( Handler == NULL )
			qRFwk();
#endif
		return Handler->Unlock( ErrHandling );
	}

	//f Delete the mutex of handler 'Handler'.
	inline void Delete(
		handler___ Handler,
		bso::bool__ EvenIfLocked = false )
	{
#ifdef MTX_DBG
		if ( Handler == NULL )
			qRFwk();

		if ( Handler->IsLocked() && !EvenIfLocked )
			qRFwk();
#endif
		delete Handler;
	}

/*
	enum state__ {
		sUnlocked,
		sLocked,
		s_amount,
		s_Undefined
	};
*/
	class mutex___
	{
	private:
		qPMV( _mutex__, H_, Handler_ );
		void _UnlockIfInitializedAndLocked( void )
		{
			if ( Handler_ != NULL )
				mtx::Unlock( Handler_, err::hUserDefined );	// Ignore error if already unlocked;
		}
	public:
		void reset( bool P = true )
		{
			if ( P )
				_UnlockIfInitializedAndLocked();

			Handler_ = NULL;

		}
		E_CDTOR( mutex___ );
		void Init( handler___ Handler )
		{
			_UnlockIfInitializedAndLocked();
			
			Handler_ = Handler;
		}
		void InitAndLock( handler___ Handler )
		{
			Init( Handler );
			Lock();
		}
		bso::bool__ TryToLock( void )
		{
			return mtx::TryToLock( H_() );
		}
		bso::sBool Lock( tol::sDelay Timeout = 0 ) // If == '0' or lock succeed, returns always 'true', or returns false after 'Timeout' ms.
		{
			return mtx::Lock( H_() );
		}
		bso::sBool Unlock( qRPD )
		{
			return mtx::Unlock( H_(), ErrHandling );
		}
	};
}

/***************/
/***** NEW *****/
/***************/

namespace mtx {
	typedef mutex___ rMutex;
	typedef handler___ rHandler;
}

#endif
