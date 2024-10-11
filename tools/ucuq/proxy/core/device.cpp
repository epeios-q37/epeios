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


#include "device.h"

#include "registry.h"

#include "sclm.h"

#include "lstcrt.h"
#include "str.h"
#include "idxbtq.h"

using namespace device;

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

    void Display(const sTie &Tie)
    {
      cio::COut << "T: ";

      if ( Tie.Token != qNIL )
        cio::COut << Strings(Tie.Token);

      cio::COut << "\tI: ";

      if ( Tie.Id != qNIL )
        cio::COut << Strings(Tie.Id);

      cio::COut << "\tTT: ";

      if ( Tie.TrueToken != qNIL )
        cio::COut << Strings(Tie.TrueToken);

      cio::COut << "\tCC: ";

      if ( Tie.Caller != qNIL )
        cio::COut << *Tie.Caller;
    }

    lstbch::qLBUNCHw(sTie, sRow) Ties;

    void DisplayTies(void)
    {
      sRow Row = Ties.First();

      while ( Row != qNIL ) {
        cio::COut << *Row << '\t';

        Display(Ties(Row));

        cio::COut << txf::nl << txf::commit;

        Row = Ties.Next(Row);
      }
    }

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

    sCRow_ GetCaller(sRow Row)
    {
      if ( Row == qNIL )
        qRGnr();

      sTie Tie = Ties(Row);

      if ( Tie.Caller == qNIL )
        qRGnr();

      return Tie.Caller;
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
      sRow Row)
    {
      Index_.Allocate(Ties.Extent());

      if ( IndexRoot_ == qNIL )
        IndexRoot_ = Row;
      else {
        bso::sBool Cont = true;
        idxbtq::qISEEKERs(sRow) Seeker;

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

    sRow SearchInIndex(
      const str::dString &Token,
      const str::dString &Id)
    {
      sRow Row = IndexRoot_;
      bso::sBool Cont = Row != qNIL;
      idxbtq::qISEEKERs(sRow) Seeker;

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
        
    void RemoveFromIndex(sRow Row)
    {
      IndexRoot_ = Index_.Delete(Row, IndexRoot_);
    }
  }

  common::rCallers Callers_;
}

namespace {
  sRow New_(
    const dSelector &Selector,
    sck::rRWDriver *Driver)
  {
    seeker_::sTie Tie;

    Tie.Init();

    Tie.Token = seeker_::Strings.New(Selector.Token);
    Tie.Id = seeker_::Strings.New(Selector.Id);
    Tie.Caller = Callers_.New(Driver);

    return seeker_::Ties.Add(Tie);
  }

  namespace {
    bso::sBool GetTrueTokenAndId_(
      const str::dString &Token,
      str::dString &TrueToken,
      str::dString &Id)
    {
      sRow Row = seeker_::SearchInIndex(Token, str::Empty);

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

  sRow Get_(const dSelector &Selector)
  {
    sRow Row = qNIL;
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

  void Withdraw_(sRow Row)
  {
    seeker_::sTie Tie = seeker_::Ties(Row);

    if ( Tie.Token == qNIL )
      qRFwk();

    if ( Tie.Id == qNIL )
      qRFwk();

    if ( Tie.Caller == qNIL )
      qRFwk();

    seeker_::Strings.Remove(Tie.Token);
    seeker_::Strings.Remove(Tie.Id);

    Callers_.Withdraw(Tie.Caller);

    seeker_::RemoveFromIndex(Row);

    seeker_::Ties.Remove(Row);
  }
}

eAnswer device::GetAnswer(
  flw::rRFlow &Flow,
  const common::gTracker *Tracker)
{
  bso::sU8 Answer = a_Undefined;

  common::Get(Flow, Answer, Tracker);

  if ( Answer > a_amount )
    qRGnr();

  return (eAnswer)Answer;
}

sRow device::New(
  const dSelector &Selector,
  sck::rRWDriver *Driver)
{
  sRow Row = qNIL;
qRH;
  mtx::rHandle Locker;
qRB;
  Locker.InitAndLock(Mutex_);

  Row = Get_(Selector);

  if ( Row != qNIL )
    Withdraw_(Row);

  Row = New_(Selector, Driver);

  seeker_::UpdateIndex(Selector.Token, Selector.Id, Row);

  cio::COut << "New" << txf::nl;

  seeker_::DisplayTies();
qRR;
qRT;
qRE;
  return Row;
}

common::rCaller *device::Hire(
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
    Caller = Callers_.Hire(seeker_::GetCaller(Row), UserDiscriminator);
qRR;
qRT;
qRE;
  return Caller;
}

void device::Withdraw(sRow Row)
{
qRH;
  mtx::rHandle Locker;
qRB;
  Locker.InitAndLock(Mutex_);
  
  Withdraw_(Row);

  cio::COut << "Withdraw:" << txf::nl;

  seeker_::DisplayTies();
qRR;
qRT;
qRE;
}

void device::Withdraw(const dSelector &Selector)
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

void device::Withdraw(const str::dString &Token)
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

bso::sBool device::CreateVToken(
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
  } else
    Row == qNIL;

  cio::COut << "Create vtoken" << txf::nl;

  seeker_::DisplayTies();
qRR;
qRT;
qRE;
  return Row != qNIL;
}

bso::sBool device::DeleteVToken(const str::dString &Token)
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
  
  cio::COut << "Delete vtoken" << txf::nl;

  seeker_::DisplayTies();
  qRR;
qRT;
qRE;
  return Row != qNIL;
}

qGCTOR(device)
{
  Mutex_ = mtx::Create();
  Callers_.Init();
  seeker_::Init();
}

qGDTOR(device) {
  if ( Mutex_ != mtx::Undefined )
    mtx::Delete(Mutex_, true);
}
