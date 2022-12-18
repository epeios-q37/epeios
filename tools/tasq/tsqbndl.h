/*
	Copyright (C) 2022 Claude SIMON (http://q37.info/contact/).

	This file is part of the 'TASq' tool.

    'TASq' is free software: you can redistribute it and/or modify it
    under the terms of the GNU Affero General Public License as published
    by the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    'TASq' is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with 'TASq'.  If not, see <http://www.gnu.org/licenses/>.
*/

// TaSQ BuNDLe

#ifndef TSQBNDL_INC_
# define TSQBNDL_INC_

# include "tsqtsk.h"

namespace tsqbndl {
  typedef tsqtsk::sRow sTRow;
  using tsqtsk::sTask;
  typedef tsqtsk::dXTasks dTasks;

  typedef tsqstrng::sRow sSRow;
  using tsqstrng::dStrings;

  using tsqstts::sStatus;
  typedef tsqstts::sRow sCRow;
  using tsqstts::dStatutes;

  class dBundle
  {
  private:
    sSRow Add_(const str::dString &String)
    {
      sSRow Row = Strings.New();

      Strings(Row) = String;

      StoreStatics_();

      return Row;
    }
    const sTask GetTask_(sTRow Row) const
    {
      sTask Task;

      Task.Init();

      Tasks.Recall(Row, Task);

      return Task;
    }
  protected:
    virtual void StoreStatics_(void) = 0;
  public:
    struct s
    {
      qASd::s AS;
      dStrings::s Strings;
      dTasks::s Tasks;
      dStatutes::s Statutes;
      sTRow RootTask;
    } &S_;
    dStrings Strings;
    dTasks Tasks;
    dStatutes Statutes;
    dBundle(s &S)
    : S_(S),
      Strings(S.Strings),
      Tasks(S.Tasks),
      Statutes(S.Statutes)
    {}
    void reset(bso::sBool P = true)
    {
      tol::reset(P, Strings, Tasks, Statutes);
      S_.RootTask = qNIL;
    }
    void plug(qASd *AS)
    {
      tol::plug(AS, Strings, Tasks, Statutes);
    }
    dBundle &operator =(const dBundle &B)
    {
      Strings = B.Strings;
      Tasks = B.Tasks;
      Statutes = B.Statutes;
      S_.RootTask = B.S_.RootTask;

      return *this;
    }
    void Init(void)
    {
      sTask Task;
      tol::Init(Strings, Tasks, Statutes);
      Task.Init();
      S_.RootTask = Tasks.Add(Task);
    }
    void Flush(void)
    {
      Strings.Flush();
    }
    sTRow RootTask(void) const
    {
      if ( S_.RootTask == qNIL )
        qRGnr();

      return S_.RootTask;
    }
    bso::sBool IsRoot(sTRow Row) const
    {
      return Row == RootTask();
    }
    sTRow Add(
      const str::dString &Title,
      const str::dString &Description,
      const sStatus &Status,
      sTRow Row = qNIL)
    {
      sTask Task;
      sTRow New = qNIL;

      if ( Row == qNIL )
        Row = S_.RootTask;

      Task.Init();

      Task.Title = Add_(Title);

      if ( Description.Amount() )
        Task.Description = Add_(Description);

      if ( Status.Type != tsqstts::t_Default )
        Task.Status = Statutes.Add(Status);

      New = Tasks.Add(Task);

      Tasks.BecomeLast(New, Row);

      StoreStatics_();

      return New;
    }
    sTRow Add(
      const str::dString &Title,
      const sStatus &Status,
      sTRow Row)
    {
      return Add(Title, str::Empty, Status, Row);
    }
    sTRow UpdateTaskDescription(
      sTRow Row,
      const str::dString &Description)
    {
      sTask Task;

      Task.Init();

      Task = GetTask_(Row);

      if ( Description.Amount() ) {
        if ( Task.Description == qNIL )
          Task.Description = Add_(Description);
        else
          Strings(Task.Description) = Description;
      } else if ( Task.Description != qNIL ) {
          Strings.Remove(Task.Description);
          Task.Description = qNIL;
      }

      Tasks.Store(Task, Row);

      StoreStatics_();

      return Row;
    }
    sTRow UpdateTaskStatus(
      sTRow Row,
      const sStatus &Status)
    {
      sTask Task;

      Task.Init();

      Task = GetTask_(Row);

      if ( Task.Status == qNIL )
        Task.Status = Statutes.New();

      Statutes.Store(Status, Task.Status);

      Tasks.Store(Task, Row);

      StoreStatics_();

      return Row;
    }
    void Get(
      sTRow Row,
      str::dString &Title,
      str::dString &Description,
      sStatus &Status) const
    {
      sTask Task;

      Task.Init();

      Task = GetTask_(Row);

      Strings.Recall(Task.Title, Title);

      if ( Task.Description != qNIL )
        Strings.Recall(Task.Description, Description);

      if ( Task.Status != qNIL )
        Statutes.Recall(Task.Status, Status);
    }
    void Set(
      const str::dString &Title,
      const str::dString &Description,
      sTRow Row)
      {
        sTask Task;

        Task.Init();

        Task = GetTask_(Row);

        Strings.Store(Title, Task.Title);

        if ( Task.Description == qNIL) {
          Task.Description = Strings.New();
          Tasks.Store(Task, Row);
        }

        Strings.Store(Description, Task.Description);

        StoreStatics_();
      }
    };

  class rXBundle
  : public dBundle
  {
  private:
    qASd AS_;
  protected:
    virtual void StoreStatics_(void) override;
  public:
    struct s
    : public dBundle::s
    {
     qASd::s AS;
    } S_;
    rXBundle()
    : dBundle(S_),
      AS_(S_.AS)
    {}
    void reset(bso::sBool P = true)
    {
      dBundle::reset(P);
      AS_.reset(P);
    }
    void plug(uys::sHook &Hook)
    {
      AS_.plug(Hook);
      dBundle::plug(&AS_);
    }
    qDTOR(rXBundle);
    void Init(void)
    {
      AS_.Init();
      dBundle::Init();
    }
    void Immortalize(void)
    {
      Flush();
      reset(false);
    }
};

  // Returns true if db exists.
  bso::sBool Initialize(const fnm::rName &Name);

  void Immortalize(void);

  typedef mtx::rHandle hGuard;

  rXBundle &Get(hGuard &Guard);

  const rXBundle &CGet(hGuard &Guard);
}

#endif
