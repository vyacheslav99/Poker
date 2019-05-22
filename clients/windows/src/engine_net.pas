{ Принцип работы сетевого модуля такой:
  И на стороне сервера и на стороне клиента будут работать оба компонента netServer и netClient.
  netServer и там и там будет прослушивать заданный порт и принимать подключения из сети, обрабатывать полученные команды
  и загружать полученные данные. Никаких ответов обратно клиенту сервер слать не будет, считаем, что все операции прошли успешно.
  netClient и там и там будет коннектиться к серверу на заданный порт только в момент отправки команды/данных, передавать ее
  и отключаться. Никаких ответов от сервера не ждем.
  Т.е. если нужно что-то отправить, хоть от сервера - клиенту, хоть наоборот - от клиента - серверу, действуем одинаково:
  netClient локальный коннектиться к netServer удаленному и отсылает данные, а netServer и там и там все время работает только на прием.
  Соотв. при возникновении ошибок в момент выполнения этих операций ругаемся, что связь прервана и запускаем процедуру
  отключения (можно будет ввести на этот случай неск. попыток выполнить операцию и таймаут между попытками, все эти параметры
  вынести в настройки, но пользователю не давать редактировать - только в настроечном файле).
  Механизм поддержки связи такой (опять же и на стороне клиента и на стороне сервера он один и тот же):
  переменная счетчик хранит число (секунды). По таймеру, раз в 1000 мс (т.е. каждую сек.) это число
  уменьшается на единицу. Как только оно стало 0, происходит попытка соединиться с сервером (т.е. netClient тупо выполняет connect
  к netServer на той стороне и сразу отключается). Если коннект не прошел, то выполняем процедуру при обрыве связи.
  В зависимости, клиент это или сервер будут выполняться соотв. действия по прерыванию игры и т.д. Если коннект прошел,
  число снова устанавливается в макс значение (оно будет задаваться в настройках, но в интерфейсе настроек его менять
  будет нельзя - тока в файле, по умолчанию 20 (сек)). Кроме этого при любых операциях связи клиента с сервером и передачах
  данных этот счетчик будет сбрасываться - т.к. если обмен данными прошел, то связь есть и нет смысла его еще раз проверять
  в этот промежуток времени.
  В режиме разработки сервер и клиент будут прослушивать разные порты, чтобы можно было на одной машине запускать и сервер
  и клиент. Сделаем для сервера порт, заданный в настройках, а для клиента - этот порт + 1.
}

unit engine_net;

interface

uses
  Windows, Messages, SysUtils, Variants, Classes, Dialogs, MemTableDataEh, Db, MemTableEh, engine, settings, utils, network;

const
  // сетевые команды:
  // сигналы о поступлении (а с др. стороны - об отправке) данных (т.е. далее за сигналом идет блок соотв. данных, к-рые надо принять)
  NET_ACCEPT_PLAYER = 'mem_accept_player'; // нужно принять данные игрока
  NET_ACCEPT_PARTY = 'str_accept_party'; // нужно принять данные партии (состава игроков текущей игры)
  // запросы на получение данных - т.е. по данному запросу надо будет передать обратно соотв. данные
  NET_GET_PLAYER = 'get_player'; // нужно передать данные игрока
  NET_GET_PARTY = 'get_party'; // нужно передать данные партии (состава игроков текущей игры)
  // прочие команды, не требующие ответа, но к-рые нужно обработать
  NET_CMD_MESS_ERROR = 'cmd_error'; // сообщение об ошибке на той стороне - надо будет засветить его пользователю (само сообщение идет сразу за командой)
  NET_CMD_DISCONNECT = 'cmd_disconnect'; // с той стороны отключаются от игры

type
  TSynchGameParamsProc = procedure of object;
  TTablePosition = (tpLeft, tpRight, tpCenter);

  TClient = record
    Used: boolean;
    IP: string;
    Id: string;
    Index: integer;
    PartyIdx: integer;
    Position: TTablePosition;
  end;
  TClients = array [0..1] of TClient;

  TGame = class(TCustomGame)
  private
    dmNetwork: TdmNetwork;
    function GetPort: integer;
    procedure SetPort(const Value: integer);
    function GetHost: string;
    procedure SetHost(const Value: string);
    function GetLastMessage: string;
    procedure SetLastMessage(const Value: string);
  protected
    FActive: boolean;
    function OpenAsServer: boolean;
    function OpenAsClient: boolean;
    function TryConnect(IP: string; var Err: string): boolean;
    function SendData(Command, RecipientIp: string; Data: TMemoryStream): boolean;
    function SendPlayer(ClientIp: string; Id: string): boolean; virtual;
    function AcceptPlayer(ClientIp: string; Data: TMemoryStream): boolean; virtual; abstract;
    function SendParty(ClientIp: string): boolean; virtual;
    function AcceptParty(Data: string): boolean; virtual;
    procedure TestConnect; virtual; abstract;
    procedure ServerExecute(ACommand, StrData, RemoteIp: string; MemData: TMemoryStream); virtual; abstract;
  public
    SynchGameParams: TSynchGameParamsProc;
    constructor Create(AStatTbl: TMemTableEh; ADrawProc: TDrawProc; ASetProc: TSetProc; ASetMsgProc: TSetMessageProc);
    destructor Destroy; override;
    function Open(PlayerId: string): boolean; virtual; abstract;
    procedure Close(SendMsg: boolean = false); virtual;
    function Active: boolean;

    property LastMessage: string read GetLastMessage write SetLastMessage;
    property Port: integer read GetPort write SetPort;
    property Host: string read GetHost write SetHost;
  end;

  TGameServer = class(TGame)
  private
    Clients: TClients;
    procedure DelClient(Index: integer);
    procedure OnClientDisconnect(ClientIp: string; ErrMessage: string = '');
  protected
    function AcceptPlayer(ClientIp: string; Data: TMemoryStream): boolean; override; //отправка: Client.SendPlayer
    function SendParty(ClientIp: string): boolean; override; // прием: Client.AcceptParty
    procedure TestConnect; override;
    procedure ServerExecute(ACommand, StrData, RemoteIp: string; MemData: TMemoryStream); override;
  public
    function Open(PlayerId: string): boolean; override;
    procedure Close(SendMsg: boolean = false); override;
    procedure DoSendParty;
  end;

  TGameClient = class(TGame)
  private
    procedure OnServerDisconnect(ErrMessage: string = '');
  protected
    function AcceptPlayer(ClientIp: string; Data: TMemoryStream): boolean; override;
    function AcceptParty(Data: string): boolean; override; // отправка: Server.SendParty
    procedure TestConnect; override;
    procedure ServerExecute(ACommand, StrData, RemoteIp: string; MemData: TMemoryStream); override;
    procedure DoAfterConnect(PlayerId: string);
  public
    function Open(PlayerId: string): boolean; override;
    procedure Close(SendMsg: boolean = false); override;
  end;

implementation

//uses start;

{ TGame }

function TGame.AcceptParty(Data: string): boolean;
begin
  result := true;
end;

function TGame.Active: boolean;
begin
  result := FActive;
end;

procedure TGame.Close(SendMsg: boolean);
begin
  dmNetwork.CloseConnect;
  FActive := false;
end;

constructor TGame.Create(AStatTbl: TMemTableEh; ADrawProc: TDrawProc; ASetProc: TSetProc; ASetMsgProc: TSetMessageProc);
begin
  inherited Create(AStatTbl, ADrawProc, ASetProc, ASetMsgProc);
  dmNetwork := TdmNetwork.Create(nil);
  dmNetwork.OnTestConnect := TestConnect;
  dmNetwork.OnServerExecute := ServerExecute;
end;

destructor TGame.Destroy;
begin
  dmNetwork.Free;
  inherited Destroy;
end;

function TGame.GetHost: string;
begin
  result := dmNetwork.Host;
end;

function TGame.GetLastMessage: string;
begin
  result := dmNetwork.LastMessage;
end;

function TGame.GetPort: integer;
begin
  result := dmNetwork.Port;
end;

function TGame.OpenAsClient: boolean;
begin
  if Active then Close;
  Host := FSettings.ServerIp;
  Port := FSettings.PortNumber;
  FActive := dmNetwork.Open(false);
  result := FActive;
end;

function TGame.OpenAsServer: boolean;
begin
  if Active then Close;
  Host := FSettings.ServerIp;
  Port := FSettings.PortNumber;
  FActive := dmNetwork.Open(true);
  result := FActive;
end;

function TGame.SendData(Command, RecipientIp: string; Data: TMemoryStream): boolean;
begin
  result := dmNetwork.SendData(Command, RecipientIp, Data);
end;

function TGame.SendParty(ClientIp: string): boolean;
begin
  result := true;
end;

function TGame.SendPlayer(ClientIp, Id: string): boolean;
var
  m: TMemoryStream;
  fs: TFileStream;
  pi: integer;

begin
  // отправка данных игрока
  result := false;
  try
    pi := FindPlayerById(Id, Players);
    if pi = -1 then raise Exception.Create('Не найден игрок с id "' + Id + '"');

    m := TMemoryStream.Create;
    try
      // игрок
      m.Write(Players[pi], SizeOf(TPlayer));
      // картинка
      if FileExists(FSettings.DataDir + USER_DATA_DIR + Players[pi].FaceFile) then
      try
        fs := TFileStream.Create(FSettings.DataDir + USER_DATA_DIR + Players[pi].FaceFile, fmOpenRead);
        m.CopyFrom(fs, fs.Size);
      finally
        fs.Free;
      end;

      m.Seek(0, soFromBeginning);
      result := SendData(NET_ACCEPT_PLAYER + PARAMS_DELIM + IntToStr(m.Size), ClientIp, m);
    finally
      m.Free;
    end;
  except
    on e: Exception do LastMessage := e.ClassName + ' : ' + e.Message;
  end;
end;

procedure TGame.SetHost(const Value: string);
begin
  dmNetwork.Host := Value;
end;

procedure TGame.SetLastMessage(const Value: string);
begin
  dmNetwork.LastMessage := Value;
end;

procedure TGame.SetPort(const Value: integer);
begin
  dmNetwork.Port := Value;
end;

function TGame.TryConnect(IP: string; var Err: string): boolean;
begin
  result := dmNetwork.TryConnect(IP, Err);
end;

{ TGameServer }

procedure TGameServer.Close(SendMsg: boolean);
var
  i: integer;

begin
  for i := 0 to Length(Clients) - 1 do
  begin
    if SendMsg and Clients[i].Used and (Clients[i].IP <> '') then SendData(NET_CMD_DISCONNECT, Clients[i].IP, nil);
    DelClient(i);
  end;

  inherited Close;
end;

procedure TGameServer.DelClient(Index: integer);
begin
  if (Index < 0) or (Index > Length(Clients) - 1) then exit;

  Clients[Index].Used := false;
  Clients[Index].IP := '';
  Clients[Index].Id := '';
  Clients[Index].Index := -1;
  Clients[Index].PartyIdx := -1;
end;

procedure TGameServer.OnClientDisconnect(ClientIp, ErrMessage: string);
var
  i: integer;

begin
  // действия при отключении клиента: убрать отключившегося игрока из партии
  for i := 0 to Length(Clients) - 1 do
    if Clients[i].IP = ClientIp then
    begin
      if Started then
      begin
        // если игра уже в процессе прерываем и даем возможность сохранить
        MessageDlg('Игрок ' + Players[Clients[i].Index].Name + ' (' + Clients[i].IP + ') вышел из игры. ' +
          'Вы можете отложить партию и продолжить позже или бросить ее.', mtInformation, [mbOK], 0);

        HoldGame;
      end else
      begin
        // еще не начата - просто очищаем данные игрока в партии
        // удаляем из партии
        Party[Clients[i].PartyIdx].Index := -1;
        // обновим стартовую форму и отправляем изменения в списке всем клиентам
        if Assigned(SynchGameParams) then SynchGameParams;
        DoSendParty;
        {if FStartDialog.Visible then
        begin
          case Clients[i].Position of
            tpLeft: FStartDialog.cbPartnerLeft.KeyValue := Null;
            tpRight: FStartDialog.cbPartnerRight.KeyValue := Null;
          end;
        end;}

        // удаляем клиента из списка клиентов
        DelClient(i);
      end;
    end;

  if ErrMessage <> '' then MessageDlg(ErrMessage, mtError, [mbOK], 0);
end;

function TGameServer.Open(PlayerId: string): boolean;
begin
  result := OpenAsServer;
end;

procedure TGameServer.DoSendParty;
var
  i: integer;

begin
  // рассылка данных партии всем клиентам (выполняется по таймеру, пока открыта форма начала игры)
  for i := 0 to Length(Clients) - 1 do
    if Clients[i].Used and (Clients[i].IP <> '') then SendParty(Clients[i].IP);
end;

function TGameServer.AcceptPlayer(ClientIp: string; Data: TMemoryStream): boolean;
var
  fs: TFileStream;
  pl: TPlayer;
  pi, i, c: integer;
  added: boolean;

begin
  // прием данных игрока от клиента на сервере при подключении клиента, добавление этого игрока в партию
  result := false;
  try
    // игрок
    if not Assigned(Data) then exit;
    Data.Read(pl, SizeOf(TPlayer));
    if pl.Id = '' then raise Exception.Create('Переданы пустые данные игрока!');

    // добавляем игрока в список или обновляем его данные, если он там уже есть
    pl.Control := ctHumanRemote;
    pi := FindPlayerById(pl.Id, Players);
    if pi = -1 then
    begin
      pi := Length(Players);
      SetLength(Players, Length(Players) + 1);
    end else
    begin
      // нельзя подсоединяться одним из локальных игроков
      if Players[pi].Control in [ctHumanLocal, ctRobot] then
        raise Exception.Create('Нельзя подключаться от имени ' + Players[pi].Name + ' - это один из локальных игроков сервера!');

      // проверим, нет ли уже среди подключившихся этого же игрока
      c := 0;
      for i := 0 to Length(Clients) - 1 do
      begin
        if Clients[i].Used then Inc(c);
        if Clients[i].Used and (Clients[i].Id = pl.Id) then
        begin
          if (Clients[i].IP <> ClientIp) then
            raise Exception.Create('Игрок ' + pl.Name + ' уже присоединился к игре с другого IP (' + Clients[i].IP + ')!')
          else
            raise Exception.Create('Игрок ' + pl.Name + ' уже присоединился к игре с вашего IP (' + Clients[i].IP + ')!');
        end;
      end;
      if c > 1 then raise Exception.Create('Не осталось свободных мест для присоединения к игре.');
    end;
    Players[pi] := pl;
    // теперь можно сохранять картинку
    if ((Data.Size - SizeOf(TPlayer)) > 0) and (pl.FaceFile <> '') then
    try
      fs := TFileStream.Create(FSettings.DataDir + USER_DATA_DIR + pl.FaceFile, fmCreate);
      fs.CopyFrom(Data, Data.Size - SizeOf(TPlayer));
    finally
      fs.Free;
    end;

    // добавляем игрока в партию
    if SavePlayers then
    begin
      added := false;
      // сначала проверим - если игрок с таким id уже в партии - ничего делать не надо
      for i := 0 to 1 do
        if (Party[i].Index <> -1) then
          if (Player[i].Id = pl.Id) then
          begin
            added := true;
            break;
          end;

      // если еще нет, то добавим в первую пустую ячейку
      if not added then
        for i := 0 to 1 do
          if (Party[i].Index = -1) then
          begin
            Party[i].Index := pi;

            // добавляем в список клиентов
            for c := 0 to Length(Clients) - 1 do
              if not Clients[c].Used then
              begin
                Clients[c].Used := true;
                Clients[c].IP := ClientIp;
                Clients[c].Id := pl.Id;
                Clients[c].Index := pi;
                Clients[c].PartyIdx := i;
                Clients[c].Position := TTablePosition(i);
                added := true;
                break;
              end;

            break;
          end;

      if not added then raise Exception.Create('Не осталось свободных мест для присоединения к игре.');
      result := added;

      if result then
      begin
        if Assigned(SynchGameParams) then SynchGameParams;
        DoSendParty;
      end;
    end;
  except
    on e: Exception do LastMessage := e.ClassName + ' : ' + e.Message;
  end;
end;

function TGameServer.SendParty(ClientIp: string): boolean;
var
  i: integer;
  cmd, s: string;

begin
  // отправка данных партии игроков (сервер -> клиент)
  result := inherited SendParty(ClientIp);
  
  result := false;
  try
    cmd := '';
    for i := 0 to Length(Party) - 1 do
    begin
      if Party[i].Index = -1 then s := ''
      else s := Player[i].Id;

      if cmd = '' then cmd := s
      else cmd := cmd + REC_WORD_DELIM + s;
    end;

    result := SendData(NET_ACCEPT_PARTY + PARAMS_DELIM + cmd, ClientIp, nil);
  except
    on e: Exception do LastMessage := e.ClassName + ' : ' + e.Message;
  end;
end;

procedure TGameServer.ServerExecute(ACommand, StrData, RemoteIp: string; MemData: TMemoryStream);
var
  res: boolean;
  
begin
  res := true;
  
  if ACommand = NET_ACCEPT_PLAYER then
  begin
    // принимаем игрока (сервер <- клиент)
    res := AcceptPlayer(RemoteIp, MemData);
  end else

  if ACommand = NET_GET_PLAYER then
  begin
    // отправляем игрка (сервер -> клиент)
    res := SendPlayer(RemoteIp, StrData);
  end else

  if ACommand = NET_GET_PARTY then
  begin
    // отправляем список и расположение игроков в партии (сервер -> клиент)
    res := SendParty(RemoteIp);
  end else

  if ACommand = NET_CMD_DISCONNECT then
  begin
    // при отключении клиента
    OnClientDisconnect(RemoteIp);
  end else

  if ACommand = NET_CMD_MESS_ERROR then
  begin
    // показать сообщение об ошибке, возникшей с той стороны
    MessageDlg(StrData, mtError, [mbOK], 0);
  end

  else res := true; // чтоб не светить пустые сообщения об ошибакх

  if not res then SendData(NET_CMD_MESS_ERROR + PARAMS_DELIM + LastMessage, RemoteIp, nil);
end;

procedure TGameServer.TestConnect;
var
  i, n: integer;
  err: string;
  r: boolean;

begin
  if not FActive then exit;

  for i := 0 to Length(Clients) - 1 do
  begin
    r := true;
    if Clients[i].Used then
    begin
      for n := 0 to FSettings.AttemptConnectCount - 1 do
      begin
        r := TryConnect(Clients[i].IP, err);
        if r then break;
        Sleep(FSettings.AttemptConnectInterval);
      end;

      // если соединения не было - выполняем процедуру отключения
      if not r then OnClientDisconnect(Clients[i].IP, err);
    end;
  end;
end;

{ TGameClient }

function TGameClient.AcceptParty(Data: string): boolean;
var
  idxL, idxR, idxC: integer;
  idL, idR, idC: string;

begin
  // получение и сохранение списка игроков партии (игровой клиент <- сервер)
  result := inherited AcceptParty(Data);

  result := false;
  try
    idxL := -1;
    idxR := -1;
    idxC := -1;

    idL := ExtractWordEx(1, Data, [REC_WORD_DELIM], []);
    idR := ExtractWordEx(2, Data, [REC_WORD_DELIM], []);
    idC := ExtractWordEx(3, Data, [REC_WORD_DELIM], []);

    if idL <> '' then idxL := FindPlayerById(idL, Players);
    if idR <> '' then idxR := FindPlayerById(idR, Players);
    if idC <> '' then idxC := FindPlayerById(idC, Players);

    // если одного из игроков нет на клиенте, запрашиваем его на сервере (ждать получения не будем,
    // просто при след. обновлении партии он уже загрузится)
    if (idxL = -1) and (idL <> '') then SendData(NET_GET_PLAYER + PARAMS_DELIM + idL, Host, nil);
    if (idxR = -1) and (idR <> '') then SendData(NET_GET_PLAYER + PARAMS_DELIM + idR, Host, nil);
    if (idxC = -1) and (idC <> '') then SendData(NET_GET_PLAYER + PARAMS_DELIM + idC, Host, nil);

    // расствляем игроков
    if (idxL <> -1) and (idL = Player[2].Id) then
    begin
      // на сервере мой игрок слева (индекс 0), значит
      // в позицию 0 (лево) ставим правого, в позицию 1 (право) - центрального
      Party[0].Index := idxR;
      Party[1].Index := idxC;
    end;
    if (idxR <> -1) and (idR = Player[2].Id) then
    begin
      // на сервере мой игрок справа (индекс 1), значит
      // в позицию 0 ставим центрального, в позицию 1 - левого
      Party[0].Index := idxC;
      Party[1].Index := idxL;
    end;

    // расставляем игроков на форме (точнее сбросим тех, что нет. Расставляются они по таймеру на форме сами)
    {if FStartDialog.Visible then
    begin
      if Party[0].Index = -1 then FStartDialog.cbPartnerLeft.KeyValue := Null;
      if Party[1].Index = -1 then  FStartDialog.cbPartnerRight.KeyValue := Null;
    end;}
    result := true;
    // расставляем игроков на форме
    if result and Assigned(SynchGameParams) then SynchGameParams;
  except
    on e: Exception do LastMessage := e.ClassName + ' : ' + e.Message;
  end;
end;

function TGameClient.AcceptPlayer(ClientIp: string; Data: TMemoryStream): boolean;
var
  fs: TFileStream;
  pl: TPlayer;
  pi: integer;

begin
  // прием игрока от сервера на клиенте, добавление/обновление игрока на клиенте (клиентская сторона)
  result := false;
  try
    if not Assigned(Data) then exit;
    Data.Read(pl, SizeOf(TPlayer));
    if pl.Id = '' then raise Exception.Create('Переданы пустые данные игрока!');
    if pl.Id = Player[2].Id then raise Exception.Create('Нельзя грузить собственного игрока!');

    // добавляем игрока в список или обновляем его данные, если он там уже есть
    if pl.Control = ctHumanLocal then pl.Control := ctHumanRemote;
    pi := FindPlayerById(pl.Id, Players);
    if pi = -1 then
    begin
      pi := Length(Players);
      SetLength(Players, Length(Players) + 1);
    end else
    begin
      // не будем перезаписывать данные локальных игроков
      if Players[pi].Control in [ctHumanLocal, ctRobot] then
        raise Exception.Create('Нельзя перезаписать игрока ' + Players[pi].Name + ' - это один из локальных игроков!');
    end;
    Players[pi] := pl;

    // теперь можно сохранить картинку
    if ((Data.Size - SizeOf(TPlayer)) > 0) and (pl.FaceFile <> '') then
    try
      fs := TFileStream.Create(FSettings.DataDir + USER_DATA_DIR + pl.FaceFile, fmCreate);
      fs.CopyFrom(Data, Data.Size - SizeOf(TPlayer));
    finally
      fs.Free;
    end;

    result := SavePlayers;
    if result and Assigned(SynchGameParams) then SynchGameParams;
  except
    on e: Exception do LastMessage := e.ClassName + ' : ' + e.Message;
  end;
end;

procedure TGameClient.Close(SendMsg: boolean);
begin
  if SendMsg then SendData(NET_CMD_DISCONNECT, Host, nil);
  inherited Close;
end;

procedure TGameClient.DoAfterConnect(PlayerId: string);
var
  r: boolean;

begin
  if FActive then r := SendPlayer(Host, PlayerId);
  if r then r := SendData(NET_GET_PARTY, Host, nil);

  if (not r) then
  begin
    Close(true);
    MessageDlg('Ошибка подключения к серверу!'#13#10 + LastMessage, mtError, [mbOK], 0);
  end;
end;

procedure TGameClient.OnServerDisconnect(ErrMessage: string);
var
  s: string;
  
begin
  // действия при отключении сервера: закрываем игру, закрываем окно начала игры
  if Started then HoldGame;
  Close;

  if ErrMessage = '' then
    s := 'Сервер ' + Host + ' закрыл соединение.'
  else
    s := s + 'Ошибка: '#13#10 + ErrMessage;

  MessageDlg(s, mtInformation, [mbOK], 0);
end;

function TGameClient.Open(PlayerId: string): boolean;
begin
  result := OpenAsClient;
  DoAfterConnect(PlayerId);
  result := Active;
end;

procedure TGameClient.ServerExecute(ACommand, StrData, RemoteIp: string; MemData: TMemoryStream);
var
  res: boolean;

begin
  res := true;
  
  if ACommand = NET_ACCEPT_PLAYER then
  begin
    // принимаем игрока (клиент <- сервер)
    res := AcceptPlayer(RemoteIp, MemData);
  end else

  if ACommand = NET_ACCEPT_PARTY then
  begin
    // получаем список и расположение игроков в партии (клиент <- сервер)
    res := AcceptParty(StrData);
  end else

  if ACommand = NET_CMD_DISCONNECT then
  begin
    // при отключении клиента
    OnServerDisconnect;
  end else

  if ACommand = NET_CMD_MESS_ERROR then
  begin
    // показать сообщение об ошибке, возникшей с той стороны
    MessageDlg(StrData, mtError, [mbOK], 0);
  end

  else res := true; // чтоб не светить пустые сообщения об ошибакх

  if not res then SendData(NET_CMD_MESS_ERROR + PARAMS_DELIM + LastMessage, RemoteIp, nil);
end;

procedure TGameClient.TestConnect;
var
  i, n: integer;
  err: string;
  r: boolean;

begin
  if not FActive then exit;
  r := true;

  for n := 0 to FSettings.AttemptConnectCount - 1 do
  begin
    r := TryConnect(Host, err);
    if r then break;
    Sleep(FSettings.AttemptConnectInterval);
  end;

  // если соединения не было - выполняем процедуру отключения
  if not r then OnServerDisconnect(err);
end;

end.
