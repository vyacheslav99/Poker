unit start;

interface

uses
  Windows, Messages, SysUtils, Variants, Classes, Graphics, Controls, Forms,
  Dialogs, utils, MemTableDataEh, Db, DBGridEhGrouping, GridsEh, DBGridEh, MemTableEh, ExtCtrls,
  StdCtrls, Buttons, settings, ComCtrls, ToolWin, ActnList, Mask, DBCtrlsEh, DBLookupEh, Spin,
  engine, engine_net;

type
  TFStartDialog = class(TForm)
    Panel1: TPanel;
    btnStart: TBitBtn;
    btnCancel: TBitBtn;
    mtRobots: TMemTableEh;
    dsoRobots: TDataSource;
    mtRobotsNAME: TStringField;
    mtRobotsALL: TIntegerField;
    mtRobotsCOMPLETED: TIntegerField;
    mtRobotsINTERRUPTED: TIntegerField;
    mtRobotsWINNED: TIntegerField;
    mtRobotsFAILED: TIntegerField;
    mtRobotsSCORES: TIntegerField;
    GroupBox1: TGroupBox;
    GroupBox2: TGroupBox;
    Label1: TLabel;
    cbPartnerLeft: TDBLookupComboboxEh;
    Label2: TLabel;
    cbPartnerRight: TDBLookupComboboxEh;
    Label3: TLabel;
    Label4: TLabel;
    chbOptAsc: TCheckBox;
    chbOptDesc: TCheckBox;
    chbOptEven: TCheckBox;
    chbOptNotEven: TCheckBox;
    chbOptNoTrump: TCheckBox;
    chbOptDark: TCheckBox;
    chbOptGold: TCheckBox;
    chbOptMizer: TCheckBox;
    chbOptBrow: TCheckBox;
    chbNoJoker: TCheckBox;
    chbJokerMinorLear: TCheckBox;
    chbJokerMajorLear: TCheckBox;
    Label7: TLabel;
    edMultBrow: TSpinEdit;
    edPlayer: TEdit;
    Label6: TLabel;
    edMultDark: TSpinEdit;
    Label12: TLabel;
    edPassPoints: TSpinEdit;
    Panel2: TPanel;
    Label5: TLabel;
    rbnDeck36: TRadioButton;
    rbnDeck54: TRadioButton;
    Panel3: TPanel;
    Label13: TLabel;
    rbnGameShort: TRadioButton;
    rbnGameLong: TRadioButton;
    Label8: TLabel;
    Label9: TLabel;
    cbPenalty: TComboBox;
    mtRobotsID: TStringField;
    chbStrongJoker: TCheckBox;
    mtRobotsDIFFICULTY: TIntegerField;
    btnSavedGames: TButton;
    tmrRefreshNetStatus: TTimer;
    mtRobotsTOTAL: TIntegerField;
    procedure btnStartClick(Sender: TObject);
    procedure btnCancelClick(Sender: TObject);
    procedure tmrRefreshNetStatusTimer(Sender: TObject);
    procedure FormClose(Sender: TObject; var Action: TCloseAction);
    procedure cbPartnerLeftChange(Sender: TObject);
  private
    r_ok: boolean;
    GameObj: TGame;
    procedure SetToControls(ASetPlayers: boolean = true);
    procedure GetFromControls;
    function CheckGameParams(var Msg: string): boolean;
    procedure SetGameType(Value: TGameType);
    procedure RefreshDataSet;
    procedure RefreshPlayers;
  public
    IsGameLoaded: boolean;
    procedure DoSynchGameParams;
    function Execute(PlayerId: string; AGame: TGame; ADisabled: boolean = false): boolean;
  end;

var
  FStartDialog: TFStartDialog;

implementation

{$R *.dfm}

uses main;

{ TFStartDialog }

procedure TFStartDialog.btnCancelClick(Sender: TObject);
begin
  Close;
end;

procedure TFStartDialog.btnStartClick(Sender: TObject);
var
  err: string;

begin
  // тут надо сделать проверку, что все настроено верно
  if not CheckGameParams(err) then
  begin
    Application.MessageBox(pchar(err), 'ошибка', MB_OK + MB_ICONERROR);
    exit;
  end;

  r_ok := true;
  Close;
end;

procedure TFStartDialog.cbPartnerLeftChange(Sender: TObject);
var
  idx: integer;

begin
  // рассылаем изменения в составе партии клиентам
  if GameObj.GameType = gtServer then
  begin
    if (Sender = cbPartnerLeft) and (not VarIsNull(cbPartnerLeft.KeyValue)) then
    begin
      idx := FindPlayerById(cbPartnerLeft.KeyValue, GameObj.Players);
      if idx > -1 then GameObj.Party[0].Index := idx;
    end;

    if (Sender = cbPartnerRight) and (not VarIsNull(cbPartnerRight.KeyValue)) then
    begin
      idx := FindPlayerById(cbPartnerRight.KeyValue, GameObj.Players);
      if idx > -1 then GameObj.Party[1].Index := idx;
    end;

    TGameServer(GameObj).DoSendParty;
  end;
end;

function TFStartDialog.CheckGameParams(var Msg: string): boolean;
begin
  result := false;
  Msg := '';
  if VarIsNull(cbPartnerLeft.KeyValue) then Msg := 'Не выбран партнер слева'
  else if VarIsNull(cbPartnerRight.KeyValue) then Msg := 'Не выбран партнер справа'
  else if (cbPartnerLeft.KeyValue = cbPartnerRight.KeyValue) then Msg := 'Слева и справа один и тот же игрок';
  if ((not rbnDeck36.Checked) and (not rbnDeck54.Checked)) then rbnDeck36.Checked := true;
  if ((not rbnGameShort.Checked) and (not rbnGameLong.Checked)) then rbnGameShort.Checked := true;

  result := Msg = '';
end;

procedure TFStartDialog.DoSynchGameParams;
begin
  // обновляем список игроков в лукапах
  RefreshDataSet;
  // обновляем выбранных игроков
  RefreshPlayers;
end;

function TFStartDialog.Execute(PlayerId: string; AGame: TGame; ADisabled: boolean): boolean;
var
  idx: integer;
  err: string;

begin
  result := false;
  r_ok := false;
  GameObj := AGame;

  SetGameType(AGame.GameType);

  // заполняем список юзеров
  mtRobots.Close;
  mtRobots.CreateDataSet;
  mtRobots.EmptyTable;
  RefreshDataSet;

  if not ADisabled then AGame.Party[2].Index := FindPlayerById(PlayerId, AGame.Players);
  if AGame.Party[2].Index > -1 then edPlayer.Text := AGame.Players[AGame.Party[2].Index].Name;
  SetToControls(not ADisabled);

  tmrRefreshNetStatus.Enabled := (not ADisabled) and (AGame.GameType in [gtServer, gtClient]);

  if ADisabled then
  begin
    Caption := 'Договоренности';
    cbPartnerLeft.KeyValue := AGame.Players[AGame.Party[0].Index].Id;
    cbPartnerRight.KeyValue := AGame.Players[AGame.Party[1].Index].Id;
    cbPartnerLeft.Text := AGame.Players[AGame.Party[0].Index].Name;
    cbPartnerRight.Text := AGame.Players[AGame.Party[1].Index].Name;
    btnCancel.Caption := 'Закрыть';
  end else
  if AGame.GameType = gtServer then
  begin
    cbPartnerLeft.KeyValue := Null;
    cbPartnerRight.KeyValue := Null;
  end;

  if AGame.GameType = gtClient then ADisabled := true;

  btnStart.Enabled := not ADisabled;
  GroupBox1.Enabled := not ADisabled;
  GroupBox2.Enabled := not ADisabled;
  btnSavedGames.Enabled := (not ADisabled) and (AGame.GameType = gtServer);
  {if btnSavedGames.Enabled then Height := 430
  else Height := 400;}

  ShowModal;
  result := r_ok;
  if (not ADisabled) and result then
  begin
    // проверить параметры еще раз
    if not CheckGameParams(err) then
    begin
      result := false;
      raise Exception.Create(err);
    end;

    if not VarIsNull(cbPartnerLeft.KeyValue) then
    begin
      idx := FindPlayerById(cbPartnerLeft.KeyValue, AGame.Players);
      if idx > -1 then AGame.Party[0].Index := idx;
    end;
    if not VarIsNull(cbPartnerRight.KeyValue) then
    begin
      idx := FindPlayerById(cbPartnerRight.KeyValue, AGame.Players);
      if idx > -1 then AGame.Party[1].Index := idx;
    end;

    GetFromControls;
  end;
end;

procedure TFStartDialog.FormClose(Sender: TObject; var Action: TCloseAction);
begin
  tmrRefreshNetStatus.Enabled := false;
end;

procedure TFStartDialog.GetFromControls;
begin
  FSettings.LastPartnerLeft := iif(VarIsNull(cbPartnerLeft.KeyValue), '', cbPartnerLeft.KeyValue);
  FSettings.LastPartnerRight := iif(VarIsNull(cbPartnerRight.KeyValue), '', cbPartnerRight.KeyValue);
  FSettings.GameOptions := [];
  if chbOptAsc.Checked then FSettings.GameOptions := FSettings.GameOptions + [goAsc];
  if chbOptDesc.Checked then FSettings.GameOptions := FSettings.GameOptions + [goDesc];
  if chbOptEven.Checked then FSettings.GameOptions := FSettings.GameOptions + [goEven];
  if chbOptNotEven.Checked then FSettings.GameOptions := FSettings.GameOptions + [goNotEven];
  if chbOptNoTrump.Checked then FSettings.GameOptions := FSettings.GameOptions + [goNoTrump];
  if chbOptDark.Checked then FSettings.GameOptions := FSettings.GameOptions + [goDark];
  if chbOptGold.Checked then FSettings.GameOptions := FSettings.GameOptions + [goGold];
  if chbOptMizer.Checked then FSettings.GameOptions := FSettings.GameOptions + [goMizer];
  if chbOptBrow.Checked then FSettings.GameOptions := FSettings.GameOptions + [goBrow];
  if rbnDeck36.Checked then FSettings.Deck := dsz36
  else FSettings.Deck := dsz54;
  FSettings.JokerMajorLear := chbJokerMajorLear.Checked;
  FSettings.JokerMinorLear := chbJokerMinorLear.Checked;
  FSettings.NoJoker := chbNoJoker.Checked;
  FSettings.StrongJoker := chbStrongJoker.Checked;
  FSettings.MultDark := edMultDark.Value;
  FSettings.MultBrow := edMultBrow.Value;
  FSettings.PassPoints := edPassPoints.Value;
  if rbnGameLong.Checked then FSettings.LongGame := true
  else FSettings.LongGame := false;
  FSettings.PenaltyMode := cbPenalty.ItemIndex;
  FSettings.SaveToFile;
end;

procedure TFStartDialog.RefreshDataSet;
var
  id: string;
  i: integer;

begin
  if mtRobots.Active and (not mtRobots.IsEmpty) then id := mtRobotsID.AsString;

  try
    try
      mtRobots.DisableControls;
      for i := 0 to Length(GameObj.Players) - 1 do
      begin
        if (GameObj.Players[i].Control = ctRobot) then
        begin
          if not mtRobots.Locate('ID', GameObj.Players[i].Id, []) then mtRobots.Append
          else continue;
          mtRobotsID.AsString := GameObj.Players[i].Id;
          mtRobotsNAME.AsString := GameObj.Players[i].Name;
          mtRobotsDIFFICULTY.AsInteger := iif(GameObj.Players[i].Control = ctRobot, Ord(GameObj.Players[i].Difficulty), Ord(dfUndefined));
          mtRobotsALL.AsInteger := GameObj.Players[i].cAll;
          mtRobotsCOMPLETED.AsInteger := GameObj.Players[i].cCompleted;
          mtRobotsINTERRUPTED.AsInteger := GameObj.Players[i].cInterrupted;
          mtRobotsWINNED.AsInteger := GameObj.Players[i].cWinned;
          mtRobotsFAILED.AsInteger := GameObj.Players[i].cFailed;
          mtRobotsSCORES.AsInteger := GameObj.Players[i].cScores;
          mtRobotsTOTAL.AsInteger := GameObj.Players[i].cTotal;
          mtRobots.Post;
        end;

        if ((GameObj.GameType in [gtServer, gtClient]) and (GameObj.Players[i].Control = ctHumanRemote)) then
        begin
          if mtRobots.Locate('ID', GameObj.Players[i].Id, []) then mtRobots.Edit
          else mtRobots.Append;
          mtRobotsID.AsString := GameObj.Players[i].Id;
          mtRobotsNAME.AsString := GameObj.Players[i].Name;
          mtRobotsDIFFICULTY.AsInteger := iif(GameObj.Players[i].Control = ctRobot, Ord(GameObj.Players[i].Difficulty), Ord(dfUndefined));
          mtRobotsALL.AsInteger := GameObj.Players[i].cAll;
          mtRobotsCOMPLETED.AsInteger := GameObj.Players[i].cCompleted;
          mtRobotsINTERRUPTED.AsInteger := GameObj.Players[i].cInterrupted;
          mtRobotsWINNED.AsInteger := GameObj.Players[i].cWinned;
          mtRobotsFAILED.AsInteger := GameObj.Players[i].cFailed;
          mtRobotsSCORES.AsInteger := GameObj.Players[i].cScores;
          mtRobotsTOTAL.AsInteger := GameObj.Players[i].cTotal;
          mtRobots.Post;
        end;
      end;
    finally
      if id <> '' then mtRobots.Locate('ID', id, [])
      else mtRobots.First;

      mtRobots.EnableControls;
    end;
  except

  end;
end;

procedure TFStartDialog.RefreshPlayers;
begin
  // обновляем выбранных игроков
  if (GameObj.Party[0].Index <> -1) then
  begin
    if (GameObj.Player[0].Id <> cbPartnerLeft.KeyValue) then cbPartnerLeft.KeyValue := GameObj.Player[0].Id;
  end else
    cbPartnerLeft.KeyValue := Null;

  if (GameObj.Party[1].Index <> -1) then
  begin
    if (GameObj.Player[1].Id <> cbPartnerRight.KeyValue) then cbPartnerRight.KeyValue := GameObj.Player[1].Id;
  end else
    cbPartnerRight.KeyValue := Null;
end;

procedure TFStartDialog.SetGameType(Value: TGameType);
begin
  case Value of
    gtLocal:
    begin
      Caption := 'Новая игра';
      GroupBox1.Enabled := true;
      GroupBox2.Enabled := true;
      btnStart.Enabled := true;
      btnSavedGames.Enabled := false;
    end;
    gtServer:
    begin
      Caption := 'Новая игра (создать сервер)';
      GroupBox1.Enabled := true;
      GroupBox2.Enabled := true;
      btnStart.Enabled := true;
      btnSavedGames.Enabled := true;
    end;
    gtClient:
    begin
      Caption := 'Присоединиться к игре';
      GroupBox1.Enabled := false;
      GroupBox2.Enabled := false;
      btnStart.Enabled := false;
      btnSavedGames.Enabled := false;
    end;
  end;
end;

procedure TFStartDialog.SetToControls(ASetPlayers: boolean);
begin
  if ASetPlayers then
  begin
    cbPartnerLeft.KeyValue := FSettings.LastPartnerLeft;
    cbPartnerRight.KeyValue := FSettings.LastPartnerRight;
  end;
  chbOptAsc.Checked := goAsc in FSettings.GameOptions;
  chbOptDesc.Checked := goDesc in FSettings.GameOptions;
  chbOptEven.Checked := goEven in FSettings.GameOptions;
  chbOptNotEven.Checked := goNotEven in FSettings.GameOptions;
  chbOptNoTrump.Checked := goNoTrump in FSettings.GameOptions;
  chbOptDark.Checked := goDark in FSettings.GameOptions;
  chbOptGold.Checked := goGold in FSettings.GameOptions;
  chbOptMizer.Checked := goMizer in FSettings.GameOptions;
  chbOptBrow.Checked := goBrow in FSettings.GameOptions;
  if FSettings.Deck = dsz36 then rbnDeck36.Checked := true
  else rbnDeck54.Checked := true;
  chbJokerMajorLear.Checked := FSettings.JokerMajorLear;
  chbJokerMinorLear.Checked := FSettings.JokerMinorLear;
  chbNoJoker.Checked := FSettings.NoJoker;
  chbStrongJoker.Checked := FSettings.StrongJoker;
  edMultDark.Value := FSettings.MultDark;
  edMultBrow.Value := FSettings.MultBrow;
  edPassPoints.Value := FSettings.PassPoints;
  if FSettings.LongGame then rbnGameLong.Checked := true
  else rbnGameShort.Checked := true;
  cbPenalty.ItemIndex := FSettings.PenaltyMode;
end;

procedure TFStartDialog.tmrRefreshNetStatusTimer(Sender: TObject);
var
  i: integer;
  
begin
  TTimer(Sender).Enabled := false;
  try
    // если произошел дисконнект клиента или сервер обрубился, то закрываем - игры не будет
    if not GameObj.Active then Close;
    // клиенту надо периодически обновляться
    if GameObj.GameType = gtClient then RefreshPlayers;
  finally
    TTimer(Sender).Enabled := Visible and (GameObj.GameType in [gtServer, gtClient]);
  end;
end;

end.
