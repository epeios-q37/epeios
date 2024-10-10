/*
  Copyright (C) 2024 Claude SIMON (http://q37.info/contact/).

  This file is part of the 'UCUq' toolkit.

  'UCUq' is free software: you can redistribute it and/or modify it
  under the terms of the GNU Affero General Public License as published
  by the Free Software Foundation, either version 3 of the License, or
  (at your option) any later version.

  'UCUq' is distributed in the hope that it will be useful,
  but WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
  GNU Affero General Public License for more details.

  You should have received a copy of the GNU Affero General Public License
  along with 'UCUq'.  If not, see <http://www.gnu.org/licenses/>.
*/


#include "backend.h"

#include "registry.h"

#include "sclm.h"

#include "lstcrt.h"
#include "str.h"
#include "idxbtq.h"

using namespace backend;

namespace {
  mtx::rMutex Mutex_ = mtx::Undefined; // To protect the too below members;


  namespace seeker_ {
    typedef common::sRow sCRow_; // Caller row.

    namespace {
      qROW(SRow_); // String row
    }

    str::wLStrings<sSRow_> Strings;
  
    struct sTie {
    public:
      sSRow_
        Token,
        Id,         // if both 'Id' and 'TrueToken' != 'qNIL',
                    // 'Token' is a virtual token refering to
                    // a unique device.
        TrueToken;  // If != 'qNIL', 'Token' is a virtual token.
      sCRow_ Caller;
      void reset(bso::sBool = true)
      {
        Token = Id = TrueToken = qNIL;
        Caller = qNIL;
      }
      qCTOR(sTie);
      void Init(void)
      {
        Token = Id = TrueToken = qNIL;
        Caller = qNIL;
      }
    };

    lstbch::qLBUNCHw(sTie, sRow) Ties;

    namespace {
      idxbtq::qINDEXw(sRow) Index_;
      sRow IndexRoot_;
    }

    void Init(void)
    {
      tol::Init(seeker_::Strings, Ties, Index_);
      IndexRoot_ = qNIL;
    }

    const str::dString &GetToken(sRow Row)
    {
      if ( Row == qNIL )
        qRGnr();

      sTie Tie = Ties(Row);

      if ( Tie.Token == qNIL )
        qRGnr();

      return Strings(Tie.Token);
    }

    const str::dString &GetId(sRow Row)
    {
      if ( Row == qNIL )
        qRGnr();

      sTie Tie = Ties(Row);

      if ( Tie.Id == qNIL )
        return str::Empty;
      else
        return Strings(Tie.Id);
    }

    namespace {
      bso::sSign Compare_(
        const str::dString &Token,
        const str::dString &Id,
        sRow Row)
      {
        bso::sSign Sign = str::Compare(Token, GetToken(Row));

        switch ( Sign ) {
        case -1:
        case 1:
          break;
        case 0:
          if ( Id.Amount() )
            Sign = str::Compare(Id, GetId(Row));
          break;
        default:
          qRUnx();
          break;
        }

        return Sign;
      }
    }

    void UpdateIndex(
      const str::dString &Token,
      const str::dString &Id,
      sTRow Row)
    {
      Index_.Allocate(Ties.Extent());

      if ( IndexRoot_ == qNIL )
        IndexRoot_ = Row;
      else {
        bso::sBool Cont = true;
        idxbtq::qISEEKERs(sTRow) Seeker;

        Seeker.Init(Index_, IndexRoot_);

        while ( Cont ) {
          switch ( Compare_(Token, Id, Seeker.GetCurrent()) ) {
          case -1:
          case 0:
            if ( Seeker.SearchLesser() == qNIL ) {
              IndexRoot_ = Index_.BecomeLesser(Row, Seeker.GetCurrent(), IndexRoot_);
              Cont = false;
            }
            break;
          case 1:
            if ( Seeker.SearchGreater() == qNIL ) {
              IndexRoot_ = Index_.BecomeGreater(Row, Seeker.GetCurrent(), IndexRoot_);
              Cont = false;
            }
            break;
          default:
            qRGnr();
            break;
          }
        }

        IndexRoot_ = Index_.Balance(IndexRoot_);
      }
    }

    sTRow SearchInIndex(
      const str::dString &Token,
      const str::dString &Id)
    {
      sTRow Row = IndexRoot_;
      bso::sBool Cont = Row != qNIL;
      idxbtq::qISEEKERs(sTRow) Seeker;

      Seeker.Init(Index_, IndexRoot_);

      while ( Cont ) {
        switch ( Compare_(Token, Id, Row) ) {
        case -1:
          Row = Seeker.SearchLesser();
          break;
        case 0:
          Cont = false;
          break;
        case 1:
          Row = Seeker.SearchGreater();
          break;
        default:
          qRGnr();
          break;
        }

        Cont &= Cont && ( Row != qNIL);
      }

      return Row;
    }
        
    void RemoveFromIndex(sTRow Row)
    {
      IndexRoot_ = Index_.Delete(Row, IndexRoot_);
    }
  }

  common::rCallers Backends_;
}

namespace {
  sRow New_(
    const dSelector &Selector,
    sck::rRWDriver *Driver)
  {
    seeker_::sTie Tie;

    sRow Row = Backends_.New(Driver);

    Tie.Init();

    Tie.Token = seeker_::Strings.New(Selector.Token);
    Tie.Id = seeker_::Strings.New(Selector.Id);

    seeker_::Ties.Add(Tie);

    return Row;
  }

  namespace {
    bso::sBool GetTrueTokenAndId_(
      const str::dString &Token,
      str::dString &TrueToken,
      str::dString &Id)
    {
      seeker_::sTRow Row = seeker_::SearchInIndex(Token, str::Empty);

      if ( Row != qNIL ) {
        seeker_::sTie Tie = seeker_::Ties(Row);

        if ( Tie.TrueToken != qNIL ) {
          TrueToken = seeker_::Strings(Tie.TrueToken);

          if ( Tie.Id != qNIL )
            Id = seeker_::Strings(Tie.Id);
        } else
          Row = qNIL;
      }

      return Row != qNIL;
    }
  }

  seeker_::sTRow Get_(const dSelector &Selector)
  {
    seeker_::sTRow Row = qNIL;
  qRH;
    str::wString
      TrueToken,
      Id;
  qRB;
    tol::Init(TrueToken, Id);

    if ( GetTrueTokenAndId_(Selector.Token, TrueToken, Id) ) {
      if ( !Selector.Id.Amount() != !Id.Amount() )
        Row = seeker_::SearchInIndex(TrueToken, Id.Amount() ? Id : Selector.Id);
    } else if ( Selector.Id.Amount() )
      Row = seeker_::SearchInIndex(Selector.Token, Selector.Id);
  qRR;
  qRT;
  qRE;
    return Row;
  }

  void Withdraw_(seeker_::sTRow Row)
  {
    seeker_::sTie Tie = seeker_::Ties(Row);

    seeker_::Strings.Remove(Tie.Token);
    seeker_::Strings.Remove(Tie.Id);

    seeker_::Ties.Remove(Row);

    Backends_.Withdraw(*Row);
  }

}

eAnswer backend::GetAnswer(
  flw::rRFlow &Flow,
  const common::gTracker *Tracker)
{
  bso::sU8 Answer = a_Undefined;

  common::Get(Flow, Answer, Tracker);

  if ( Answer > a_amount )
    qRGnr();

  return (eAnswer)Answer;
}

sRow backend::New(
  const dSelector &Selector,
  sck::rRWDriver *Driver)
{
  sRow Row = qNIL;
qRH;
  mtx::rHandle Locker;
  seeker_::sTRow TRow = qNIL;
qRB;
  Locker.InitAndLock(Mutex_);

  TRow = Get_(Selector);

  if ( Row != qNIL )
    Withdraw_(TRow);

  Row = New_(Selector, Driver);

  seeker_::UpdateIndex(Selector.Token, Selector.Id, TRow);
qRR;
qRT;
qRE;
  return Row;
}

common::rCaller *backend::Hire(
  const dSelector &Selector,
  const void *UserDiscriminator)
{
  common::rCaller *Caller = NULL;
qRH;
  mtx::rHandle Locker;
  sRow Row = qNIL;
qRB;
  Locker.InitAndLock(Mutex_);

  Row = Get_(Selector);

  Locker.Unlock();

  if ( Row != qNIL )
    Caller = Backends_.Hire(*Row, UserDiscriminator);
qRR;
qRT;
qRE;
  return Caller;
}

void backend::Withdraw(sRow Row)
{
qRH;
  mtx::rHandle Locker;
qRB;
  Locker.InitAndLock(Mutex_);
  
  Withdraw_(Row);
qRR;
qRT;
qRE;
}

void backend::Withdraw(const dSelector &Selector)
{
qRH;
  mtx::rHandle Locker;
  sRow Row = qNIL;
qRB;
  Locker.InitAndLock(Mutex_);

  Row = Get_(Selector);

  if ( Row != qNIL )
    Withdraw_(Row);
qRR;
qRT;
qRE;
}

void backend::Withdraw(const str::dString &Token)
{
qRH;
  mtx::rHandle Locker;
  sRow Row = qNIL;
qRB;
  Locker.InitAndLock(Mutex_);

  Row = seeker_::Ties.First();

  while ( Row != qNIL ) {
    if ( seeker_::Strings(seeker_::Ties(Row).Token ) == Token )
      Withdraw_(Row);

    Row = seeker_::Ties.Next(Row);
  }
  qRR;
  qRT;
  qRE;
}

bso::sBool backend::CreateVToken(
  const str::dString &Token,
  const str::dString &TrueToken,
  const str::dString &Id)
{
  sRow Row = qNIL; 
qRH;
 ;
  mtx::rHandle Locker;
qRB;
  Locker.InitAndLock(Mutex_);

  Row = seeker_::SearchInIndex(Token, str::Empty);

  if ( Row == qNIL ) {
    seeker_::sTie Tie;

    Tie.Init();

    Tie.Token = seeker_::Strings.New(Token);
    Tie.TrueToken = seeker_::Strings.New(TrueToken);

    if ( Id.Amount() )
      Tie.Id = seeker_::Strings.New(Id);

    Row = seeker_::Ties.Add(Tie);

    seeker_::UpdateIndex(Token, str::Empty, Row);
  }
  else
    Row == qNIL;
qRR;
qRT;
qRE;
  return Row != qNIL;
}

bso::sBool backend::DeleteVToken(const str::dString &Token)
{
  sRow Row = qNIL;
qRH;
  mtx::rHandle Locker;
qRB;
  Locker.InitAndLock(Mutex_);

  Row = seeker_::SearchInIndex(Token, str::Empty);

  if ( Row != qNIL ) {
    seeker_::sTie Tie = seeker_::Ties(Row);

    if ( Tie.TrueToken != qNIL ) {
      seeker_::Strings.Remove(Tie.Token);
      seeker_::Strings.Remove(Tie.TrueToken);

      if ( Tie.Id != qNIL )
        seeker_::Strings.Remove(Tie.Id);

      seeker_::RemoveFromIndex(Row);

      seeker_::Ties.Remove(Row);
    }
  }
qRR;
qRT;
qRE;
  return Row != qNIL;
}

qGCTOR(backend)
{
  Mutex_ = mtx::Create();
  Backends_.Init();
  seeker_::Init();
}

qGDTOR(backend) {
  if ( Mutex_ != mtx::Undefined )
    mtx::Delete(Mutex_, true);
}
