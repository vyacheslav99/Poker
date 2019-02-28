unit network;

interface

uses
  Windows, Messages, SysUtils, Classes, Sockets, IdBaseComponent, IdComponent, IdCustomTCPServer, IdTCPServer, IdTCPConnection,
  IdTCPClient, IdContext, {SyncObjs,} Graphics, Variants, ExtCtrls, Dialogs, settings, utils;

type
  TTestConnectProc = procedure of object;
  TServerExecuteProc = procedure(ACommand, StrData, RemoteIp: string; MemData: TMemoryStream) of object;

  TdmNetwork = class(TDataModule)
    MainServer: TIdTCPServer;
    MainClient: TIdTCPClient;
    TestClient: TIdTCPClient;
    tmrPing: TTimer;
    procedure MainServerExecute(AContext: TIdContext);
    procedure DataModuleCreate(Sender: TObject);
    procedure DataModuleDestroy(Sender: TObject);
    procedure tmrPingTimer(Sender: TObject);
  private
    //section: TCriticalSection;
    FActive: boolean;
    PingTime: integer;
    function AcceptData(Conn: TIdTCPConnection; Data: TMemoryStream; sz: Int64): boolean;
  public
    OnTestConnect: TTestConnectProc;
    OnServerExecute: TServerExecuteProc;
    LastMessage: string;
    Host: string;
    Port: integer;
    procedure CloseConnect;
    function Open(AsServer: boolean): boolean;
    function Active: boolean;
    function SendData(Command, RecipientIp: string; Data: TMemoryStream): boolean;
    function TryConnect(IP: string; var Err: string): boolean;
  end;

implementation

{$R *.dfm}

{ TdmNetwork }

function TdmNetwork.AcceptData(Conn: TIdTCPConnection; Data: TMemoryStream; sz: Int64): boolean;
begin
  // прием данных
  result := false;
  try
    if not Assigned(Data) then exit;
    Conn.IOHandler.ReadStream(Data, sz);
    Data.Seek(0, soFromBeginning);
    result := true;
  except
    on e: Exception do LastMessage := e.ClassName + ' : ' + e.Message;
  end;
end;

function TdmNetwork.Active: boolean;
begin
  result := FActive;
end;

procedure TdmNetwork.CloseConnect;
begin
  FActive := false;
  tmrPing.Enabled := false;
  PingTime := FSettings.PingInterval;

  try
    if MainClient.Connected then MainClient.Disconnect;
    if TestClient.Connected then TestClient.Disconnect;
    if MainServer.Active then
    begin
      MainServer.Scheduler.ActiveYarns.Clear;
      MainServer.Active := false;
    end;
  except
    // ничего не нужно
  end;
end;

procedure TdmNetwork.DataModuleCreate(Sender: TObject);
begin
  //section := TCriticalSection.Create;
end;

procedure TdmNetwork.DataModuleDestroy(Sender: TObject);
begin
  //section.Free;
end;

function TdmNetwork.Open(AsServer: boolean): boolean;
begin
  CloseConnect;

  if FSettings.UseExtraPortNumber then
  begin
    if AsServer then
    begin
      MainServer.Bindings.Items[0].Port := Port;
      MainClient.Port := FSettings.ExtraPortNumber;
    end else
    begin
      MainServer.Bindings.Items[0].Port := FSettings.ExtraPortNumber;
      MainClient.Port := Port;
    end;
  end else
  begin
    MainServer.Bindings.Items[0].Port := Port;
    MainClient.Port := Port;
  end;
  TestClient.Port := MainClient.Port;

  try
    MainServer.Active := true;
    FActive := MainServer.Active;
  except
    on e: Exception do LastMessage := e.ClassName + ' : ' + e.Message;
  end;

  tmrPing.Enabled := FActive;
  result := FActive;
end;

function TdmNetwork.SendData(Command, RecipientIp: string; Data: TMemoryStream): boolean;
begin
  // отправка данных
  if not FActive then exit;

  result := false;
  try
    try
      while MainClient.Connected do ;
      MainClient.Host := RecipientIp;
      MainClient.Connect;
      if not MainClient.Connected then exit;
      MainClient.Socket.WriteLn(Command);

      if Assigned(Data) then
      begin
        Data.Seek(0, soFromBeginning);
        MainClient.Socket.Write(Data, Data.Size);
      end;
      result := true;
      PingTime := FSettings.PingInterval;
    finally
      MainClient.Disconnect;
    end
  except
    on e: Exception do LastMessage := e.ClassName + ' : ' + e.Message;
  end;
end;

procedure TdmNetwork.MainServerExecute(AContext: TIdContext);
var
  hash, cmd, str_data: string;
  ms: TMemoryStream;
  res: boolean;

begin
  PingTime := FSettings.PingInterval;
  hash := AContext.Connection.Socket.ReadLn;
  cmd := ExtractWordEx(1, hash, [PARAMS_DELIM], []);
  str_data := ExtractWordEx(2, hash, [PARAMS_DELIM], []);

  try
    ms := TMemoryStream.Create;
    try
      res := true;
      if Pos('mem_accept_', cmd) > 0 then
        res := AcceptData(AContext.Connection, ms, StrToInt64(str_data));

      if {res and} Assigned(OnServerExecute) then OnServerExecute(cmd, str_data, AContext.Connection.Socket.Binding.PeerIP, ms)
      {else SendData(NET_CMD_MESS_ERROR + PARAMS_DELIM + LastMessage, AContext.Connection.Socket.Binding.PeerIP, nil)};
    finally
      if Assigned(ms) then ms.Free;
    end;
  except
    on e: Exception do LastMessage := e.ClassName + ' : ' + e.Message;
  end;
end;

procedure TdmNetwork.tmrPingTimer(Sender: TObject);
begin
  tmrPing.Enabled := false;
  try
    Dec(PingTime);
    if PingTime <= 0 then
    begin
      PingTime := FSettings.PingInterval;
      if Assigned(OnTestConnect) then OnTestConnect;
    end;
  finally
    tmrPing.Enabled := FActive;
  end;
end;

function TdmNetwork.TryConnect(IP: string; var Err: string): boolean;
begin
  result := false;
  Err := '';
  try
    TestClient.Host := IP;
    TestClient.Connect;
    result := TestClient.Connected;
  except
    on e: Exception do Err := e.ClassName + ' : ' + e.Message;
  end;
  TestClient.Disconnect;
end;

end.
